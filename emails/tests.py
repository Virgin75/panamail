import pytest
from django.urls import reverse

from commons.models import History
from emails.factories import EmailFactory, SenderDomainFactory, SenderEmailFactory
from emails.models import Tag, SenderDomain, SenderEmail, Email
from users.serializers import MinimalUserSerializer


@pytest.mark.django_db
def test_create_email(auth_client):
    url = reverse("emails:emails-list")
    a = Tag.objects.create(name="a", workspace=auth_client.workspace)
    b = Tag.objects.create(name="b", workspace=auth_client.workspace)

    response = auth_client.api.post(url, {
        'name': 'testem.',
        'type': 'RAW',
        'raw_html': '<html>HW</html>',
        'workspace': auth_client.workspace.id,
        'tags': [a.id, b.id],
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'testem.'
    assert res["created_by"] == MinimalUserSerializer(auth_client.user).data
    assert len(res['tags']) == 2
    assert res['workspace'] == str(auth_client.workspace.id)


@pytest.mark.django_db
def test_retrieve_email(auth_client):
    email = EmailFactory(workspace=auth_client.workspace)
    url = reverse("emails:emails-detail", kwargs={"pk": email.id})
    response = auth_client.api.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['name'] == email.name


@pytest.mark.django_db
def test_update_email(auth_client):
    email = EmailFactory(workspace=auth_client.workspace)
    url = reverse("emails:emails-detail", kwargs={"pk": email.id})
    payload = {
        'name': 'new name',
    }
    response = auth_client.api.patch(url, payload)
    res = response.json()
    assert email.edit_history.first().edited_by.email == auth_client.user.email
    assert response.status_code == 200
    assert res['name'] == payload["name"]


@pytest.mark.django_db
def test_get_email_edit_history(auth_client):
    email = EmailFactory(workspace=auth_client.workspace)
    edits = [History.objects.create(edited_by=auth_client.user) for _ in range(2)]
    email.edit_history.set(edits)
    url = reverse("emails:emails-edit-history", kwargs={"pk": email.id})
    response = auth_client.api.get(url)
    res = response.json()
    assert email.edit_history.first().edited_by.email == auth_client.user.email
    assert response.status_code == 200
    assert res['count'] == 2


@pytest.mark.django_db
def test_delete_email(auth_client):
    email = EmailFactory(workspace=auth_client.workspace)
    url = reverse("emails:emails-detail", kwargs={"pk": email.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert Email.objects.count() == 0


@pytest.mark.django_db
def test_create_sender_domain(auth_client):
    url = reverse("emails:sender-domains-list")

    response = auth_client.api.post(url, {
        'name': 'mysite.com',
        'workspace': auth_client.workspace.id
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'mysite.com'
    assert res['status'] == 'NONE'
    assert res['workspace'] == str(auth_client.workspace.id)


@pytest.mark.django_db
def test_list_sender_domains(auth_client):
    SenderDomainFactory.create_batch(2, workspace=auth_client.workspace)
    url = reverse("emails:sender-domains-list")
    response = auth_client.api.get(url, {
        'workspace_id': auth_client.workspace.id,
    })

    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 2


@pytest.mark.django_db
def test_update_sender_domain(auth_client):
    domain = SenderDomainFactory.create(workspace=auth_client.workspace)
    url = reverse("emails:sender-domains-detail", kwargs={"pk": domain.id})
    payload = {
        'name': 'new name',
    }
    response = auth_client.api.patch(url, payload)
    res = response.json()
    assert domain.edit_history.first().edited_by.email == auth_client.user.email
    assert response.status_code == 200
    assert res['name'] == payload["name"]


@pytest.mark.django_db
def test_delete_sender_domain(auth_client):
    domain = SenderDomainFactory.create(workspace=auth_client.workspace)
    url = reverse("emails:sender-domains-detail", kwargs={"pk": domain.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert SenderDomain.objects.count() == 0


@pytest.mark.django_db
def test_create_sender_email(auth_client):
    domain = SenderDomainFactory.create(workspace=auth_client.workspace)
    url = reverse("emails:sender-emails-list")

    response = auth_client.api.post(url, {
        'email_address': 'contact@mysite.com',
        "name": "Contact",
        "reply_to": "no-reply@mysite.com",
        "domain": domain.id,
        'workspace': auth_client.workspace.id
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'Contact'
    assert res['domain']["id"] == domain.id
    assert res['workspace'] == str(auth_client.workspace.id)


@pytest.mark.django_db
def test_list_sender_emails(auth_client):
    SenderEmailFactory.create_batch(
        2,
        workspace=auth_client.workspace,
        domain=SenderDomainFactory.create(workspace=auth_client.workspace)
    )
    url = reverse("emails:sender-emails-list")
    response = auth_client.api.get(url, {
        'workspace_id': auth_client.workspace.id,
    })

    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 2


@pytest.mark.django_db
def test_update_sender_email(auth_client):
    sender = SenderEmailFactory.create(
        workspace=auth_client.workspace,
        domain=SenderDomainFactory.create(workspace=auth_client.workspace)
    )
    url = reverse("emails:sender-emails-detail", kwargs={"pk": sender.id})
    payload = {
        'name': 'new name',
    }
    response = auth_client.api.patch(url, payload)
    res = response.json()
    assert sender.edit_history.first().edited_by.email == auth_client.user.email
    assert response.status_code == 200
    assert res['name'] == payload["name"]


@pytest.mark.django_db
def test_delete_sender_email(auth_client):
    sender = SenderEmailFactory.create(
        workspace=auth_client.workspace,
        domain=SenderDomainFactory.create(workspace=auth_client.workspace)
    )
    url = reverse("emails:sender-emails-detail", kwargs={"pk": sender.id})

    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert SenderEmail.objects.count() == 0
