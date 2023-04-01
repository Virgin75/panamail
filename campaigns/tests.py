import pytest
from django.urls import reverse

from campaigns.factories import CampaignFactory
from campaigns.models import Campaign
from commons.models import Tag
from contacts.factories import ListFactory
from emails.factories import SenderEmailFactory, SenderDomainFactory, EmailFactory
from users.serializers import MinimalUserSerializer


@pytest.mark.django_db
def test_create_campaign(auth_client):
    url = reverse("campaigns:campaigns-list")
    a = Tag.objects.create(name="a", workspace=auth_client.workspace)
    b = Tag.objects.create(name="b", workspace=auth_client.workspace)
    list = ListFactory(workspace=auth_client.workspace)
    sender = SenderEmailFactory(
        workspace=auth_client.workspace,
        domain=SenderDomainFactory(workspace=auth_client.workspace)
    )
    email = EmailFactory(workspace=auth_client.workspace)

    response = auth_client.api.post(url, {
        'name': 'Newsletter Week 44',
        'subject': 'Re: How are you guys doing?',
        'to_type': 'LIST',
        'to_list': list.pk,
        'sender': sender.pk,
        'email_model': email.pk,
        'workspace': auth_client.workspace.id,
        'tags': [a.id, b.id],
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'Newsletter Week 44'
    assert res['subject'] == 'Re: How are you guys doing?'
    assert res['to_type'] == 'LIST'
    assert res["created_by"] == MinimalUserSerializer(auth_client.user).data
    assert len(res['tags']) == 2
    assert res['workspace'] == str(auth_client.workspace.id)


@pytest.mark.django_db
def test_list_campaigns(auth_client):
    url = reverse("campaigns:campaigns-list")
    CampaignFactory.create_batch(
        5,
        workspace=auth_client.workspace,
        sender=SenderEmailFactory(workspace=auth_client.workspace,
                                  domain=SenderDomainFactory(workspace=auth_client.workspace)),
        email_model=EmailFactory(workspace=auth_client.workspace),
        to_list=ListFactory(workspace=auth_client.workspace),
        to_type='LIST',
    )
    response = auth_client.api.get(url + '?workspace_id=' + str(auth_client.workspace.id))

    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 5
    assert len(res['results']) == 5


@pytest.mark.django_db
def test_update_campaign(auth_client):
    campaign = CampaignFactory(
        workspace=auth_client.workspace,
        sender=SenderEmailFactory(workspace=auth_client.workspace,
                                  domain=SenderDomainFactory(workspace=auth_client.workspace)),
        email_model=EmailFactory(workspace=auth_client.workspace),
        to_list=ListFactory(workspace=auth_client.workspace),
        to_type='LIST',
    )
    url = reverse("campaigns:campaigns-detail", kwargs={'pk': campaign.id})
    response = auth_client.api.patch(url, {
        'name': 'Newsletter Week 45',
    })

    res = response.json()
    assert response.status_code == 200
    assert res['name'] == 'Newsletter Week 45'


@pytest.mark.django_db
def test_delete_campaign(auth_client):
    campaign = CampaignFactory(
        workspace=auth_client.workspace,
        sender=SenderEmailFactory(workspace=auth_client.workspace,
                                  domain=SenderDomainFactory(workspace=auth_client.workspace)),
        email_model=EmailFactory(workspace=auth_client.workspace),
        to_list=ListFactory(workspace=auth_client.workspace),
        to_type='LIST',
    )
    url = reverse("campaigns:campaigns-detail", kwargs={'pk': campaign.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert Campaign.objects.count() == 0


@pytest.mark.django_db
def test_get_campaign(auth_client):
    campaign = CampaignFactory(
        workspace=auth_client.workspace,
        sender=SenderEmailFactory(workspace=auth_client.workspace,
                                  domain=SenderDomainFactory(workspace=auth_client.workspace)),
        email_model=EmailFactory(workspace=auth_client.workspace),
        to_list=ListFactory(workspace=auth_client.workspace),
        to_type='LIST',
    )
    url = reverse("campaigns:campaigns-detail", kwargs={'pk': campaign.id})
    response = auth_client.api.get(url)

    res = response.json()
    assert response.status_code == 200
    assert res['name'] == campaign.name
