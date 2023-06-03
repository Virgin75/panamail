import pytest
from django.urls import reverse

from automation.factories import AutomationCampaignFactory, TriggerEventFactory
from automation.models import AutomationCampaign
from users.factories import WorkspaceFactory
from users.serializers import MinimalUserSerializer


@pytest.mark.django_db
def test_create_automation_campaign(auth_client):
    url = reverse("automation:automations-list")

    response = auth_client.api.post(url, {
        'name': 'Onboarding user journey',
        'description': 'desc',
        'trigger_type': 'EVENT',
        'workspace': auth_client.workspace.id,
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'Onboarding user journey'
    assert res['description'] == 'desc'
    assert res['status'] == 'DRAFT'
    assert res["created_by"] == MinimalUserSerializer(auth_client.user).data
    assert res['workspace'] == str(auth_client.workspace.id)


@pytest.mark.django_db
def test_list_automation_campaign(auth_client):
    url = reverse("automation:automations-list") + f"?workspace_id={auth_client.workspace.id}"

    automation1 = AutomationCampaignFactory(workspace=auth_client.workspace)
    automation2 = AutomationCampaignFactory(workspace=auth_client.workspace)
    automation3 = AutomationCampaignFactory(workspace=WorkspaceFactory())

    response = auth_client.api.get(url)

    res = response.json()
    assert response.status_code == 200
    assert res["count"] == 2
    assert res["results"][0]["name"] == automation1.name
    assert res["results"][1]["name"] == automation2.name
    assert automation3.name not in [res["results"][0]["name"], res["results"][1]["name"]]


@pytest.mark.django_db
def test_update_automation_campaign(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace)
    url = reverse("automation:automations-detail", kwargs={"pk": automation.id})

    response = auth_client.api.patch(url, {
        'name': 'New journey V2',
    })

    res = response.json()
    assert response.status_code == 200
    assert res['name'] == 'New journey V2'


@pytest.mark.django_db
def test_delete_automation_campaign(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace)
    url = reverse("automation:automations-detail", kwargs={"pk": automation.id})

    response = auth_client.api.delete(url)

    assert response.status_code == 204
    assert AutomationCampaign.objects.filter(id=automation.id).count() == 0


@pytest.mark.django_db
def test_retrieve_automation_campaign(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace, trigger_type='EVENT')
    trigger = TriggerEventFactory(automation_campaign=automation, workspace=auth_client.workspace)

    url = reverse("automation:automations-detail", kwargs={"pk": automation.id})

    response = auth_client.api.get(url)

    res = response.json()
    assert response.status_code == 200
    assert res['name'] == automation.name
    assert res['trigger_type'] == automation.trigger_type
    assert res['workspace'] == str(auth_client.workspace.id)
    assert res['trigger']['id'] == trigger.id
    assert res['trigger']['name'] == trigger.name
    assert res['trigger']['with_attributes'] == trigger.with_attributes
    assert res['trigger']['automation_campaign'] == automation.id
