import pytest
from django.urls import reverse

from automation.factories import AutomationCampaignFactory, TriggerEventFactory, StepFactory
from automation.models import AutomationCampaign, TriggerEvent, TriggerPage, TriggerList, TriggerSegment, \
    TriggerEmail, TriggerTime
from contacts.factories import ListFactory, SegmentFactory
from emails.factories import EmailFactory
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
    step1 = StepFactory(automation_campaign=automation, workspace=auth_client.workspace, order=1,
                        step_type='SEND_EMAIL')
    step2 = StepFactory(automation_campaign=automation, workspace=auth_client.workspace, order=2, step_type='WAIT')

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
    assert res['steps'][0]['id'] == step1.id
    assert res['steps'][0]['order'] == step1.order
    assert res['steps'][0]['step_type'] == step1.step_type
    assert res['steps'][1]['id'] == step2.id
    assert res['steps'][1]['order'] == step2.order
    assert res['steps'][1]['step_type'] == step2.step_type


@pytest.mark.django_db
def test_create_event_trigger(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace, trigger_type='EVENT')
    url = reverse("automation:automation-event-triggers-list")

    response = auth_client.api.post(url, {
        'name': 'User Registered',
        'automation_campaign': automation.id,
        'with_attributes': {"username": "bvirgin"},
        'workspace': auth_client.workspace.id,
    }, format='json')

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'User Registered'
    assert res['automation_campaign'] == automation.id
    assert automation.trigger == TriggerEvent.objects.get(id=res['id'])


@pytest.mark.django_db
def test_create_page_trigger(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace, trigger_type='PAGE')
    url = reverse("automation:automation-page-triggers-list")

    response = auth_client.api.post(url, {
        'name': 'Pricing page',
        'automation_campaign': automation.id,
        'workspace': auth_client.workspace.id,
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'Pricing page'
    assert res['automation_campaign'] == automation.id
    assert automation.trigger == TriggerPage.objects.get(id=res['id'])


@pytest.mark.django_db
def test_create_list_trigger(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace, trigger_type='LIST')
    list = ListFactory(workspace=auth_client.workspace)

    url = reverse("automation:automation-list-triggers-list")

    response = auth_client.api.post(url, {
        'list': list.id,
        'automation_campaign': automation.id,
        'workspace': auth_client.workspace.id,
    }, format='json')

    res = response.json()
    assert response.status_code == 201
    from contacts.serializers import MinimalListSerializer
    assert res['list'] == MinimalListSerializer(list).data
    assert res['automation_campaign'] == automation.id
    assert automation.trigger == TriggerList.objects.get(id=res['id'])


@pytest.mark.django_db
def test_create_segment_trigger(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace, trigger_type='SEGMENT')
    segment = SegmentFactory(workspace=auth_client.workspace)

    url = reverse("automation:automation-segment-triggers-list")

    response = auth_client.api.post(url, {
        'segment': segment.id,
        'automation_campaign': automation.id,
        'workspace': auth_client.workspace.id,
    })

    res = response.json()
    assert response.status_code == 201
    from contacts.serializers import MinimalSegmentSerializer
    assert res['segment'] == MinimalSegmentSerializer(segment).data
    assert res['automation_campaign'] == automation.id
    assert automation.trigger == TriggerSegment.objects.get(id=res['id'])


@pytest.mark.django_db
def test_create_email_trigger(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace, trigger_type='EMAIL')
    email = EmailFactory(workspace=auth_client.workspace)

    url = reverse("automation:automation-email-triggers-list")

    response = auth_client.api.post(url, {
        'email': email.id,
        'action': 'OPEN',
        'automation_campaign': automation.id,
        'workspace': auth_client.workspace.id,
    })

    res = response.json()
    assert response.status_code == 201
    from emails.serializers import MinimalEmailSerializer
    assert res['email'] == MinimalEmailSerializer(email).data
    assert res['action'] == 'OPEN'
    assert res['automation_campaign'] == automation.id
    assert automation.trigger == TriggerEmail.objects.get(id=res['id'])


@pytest.mark.django_db
def test_create_time_trigger(auth_client):
    automation = AutomationCampaignFactory(workspace=auth_client.workspace, trigger_type='TIME')

    url = reverse("automation:automation-time-triggers-list")

    response = auth_client.api.post(url, {
        'unit': 'DAY',
        'value': 7,
        'automation_campaign': automation.id,
        'workspace': auth_client.workspace.id,
    })

    res = response.json()
    assert response.status_code == 201
    assert res['unit'] == 'DAY' and res['value'] == 7
    assert res['automation_campaign'] == automation.id
    assert automation.trigger == TriggerTime.objects.get(id=res['id'])
