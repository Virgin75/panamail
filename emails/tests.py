import pytest
from django.urls import reverse

from emails.models import Tag, SenderDomain, SenderEmail
from users.serializers import MinimalUserSerializer


@pytest.mark.django_db
def test_create_email(auth_client, workspace, workspace_member, user):
    url = reverse("emails:emails-list")
    a = Tag.objects.create(name="a", workspace=workspace)
    b = Tag.objects.create(name="b", workspace=workspace)

    response = auth_client.post(url, {
        'name': 'testem.',
        'type': 'RAW',
        'raw_html': '<html>HW</html>',
        'workspace': workspace.id,
        'tags': [a.id, b.id],
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'testem.'
    assert res["created_by"] == MinimalUserSerializer(user).data
    assert len(res['tags']) == 2
    assert res['workspace'] == str(workspace.id)


@pytest.mark.django_db
def test_retrieve_email(auth_client, email, workspace, workspace_member, user):
    url = reverse("emails:emails-detail", kwargs={"pk": email.id})
    response = auth_client.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['name'] == email.name


@pytest.mark.django_db
def test_update_email(auth_client, email, workspace, workspace_member, user):
    url = reverse("emails:emails-detail", kwargs={"pk": email.id})
    payload = {
        'name': 'new name',
    }
    response = auth_client.patch(url, payload)
    res = response.json()
    assert email.edit_history.first().edited_by.email == user.email
    assert response.status_code == 200
    assert res['name'] == payload["name"]


@pytest.mark.django_db
def test_delete_email(auth_client, email, workspace, workspace_member, user):
    url = reverse("emails:emails-detail", kwargs={"pk": email.id})
    response = auth_client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_create_sender_domain(auth_client, workspace, workspace_member, user):
    url = reverse("emails:sender-domains-list")

    response = auth_client.post(url, {
        'name': 'mysite.com',
        'workspace': workspace.id
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'mysite.com'
    assert res['status'] == 'NONE'
    assert res['workspace'] == str(workspace.id)


@pytest.mark.django_db
def test_list_sender_domains(auth_client, workspace, workspace_member, user):
    [SenderDomain.objects.create(name=f"test{i}", workspace=workspace) for i, _ in enumerate(range(2))]
    url = reverse("emails:sender-domains-list")
    response = auth_client.get(url, {
        'workspace_id': workspace.id,
    })

    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 2


@pytest.mark.django_db
def test_update_sender_domain(auth_client, email, workspace, workspace_member, user):
    s = [SenderDomain.objects.create(name=f"test{i}", workspace=workspace) for i, _ in enumerate(range(2))]
    url = reverse("emails:sender-domains-detail", kwargs={"pk": s[0].id})
    payload = {
        'name': 'new name',
    }
    response = auth_client.patch(url, payload)
    res = response.json()
    assert s[0].edit_history.first().edited_by.email == user.email
    assert response.status_code == 200
    assert res['name'] == payload["name"]


@pytest.mark.django_db
def test_delete_sender_domain(auth_client, email, workspace, workspace_member, user):
    s = [SenderDomain.objects.create(name=f"test{i}", workspace=workspace) for i, _ in enumerate(range(2))]
    url = reverse("emails:sender-domains-detail", kwargs={"pk": s[0].id})
    response = auth_client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_create_sender_email(auth_client, workspace, workspace_member, user):
    s = SenderDomain.objects.create(name="test", workspace=workspace)
    url = reverse("emails:sender-emails-list")

    response = auth_client.post(url, {
        'email_address': 'contact@mysite.com',
        "name": "Contact",
        "reply_to": "no-reply@mysite.com",
        "domain": s.id,
        'workspace': workspace.id
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'Contact'
    assert res['domain']["id"] == s.id
    assert res['workspace'] == str(workspace.id)


@pytest.mark.django_db
def test_list_sender_emails(auth_client, workspace, workspace_member, user):
    s = SenderDomain.objects.create(name="test", workspace=workspace)
    SenderEmail.objects.create(
        workspace=workspace, name="Contact", email_address="a@a.fr", reply_to="b@a.fr", domain=s
    )
    url = reverse("emails:sender-emails-list")
    response = auth_client.get(url, {
        'workspace_id': workspace.id,
    })

    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 1


@pytest.mark.django_db
def test_update_sender_email(auth_client, email, workspace, workspace_member, user):
    s = SenderDomain.objects.create(name="test", workspace=workspace)
    e = SenderEmail.objects.create(
        workspace=workspace, name="Contact", email_address="a@a.fr", reply_to="b@a.fr", domain=s
    )
    url = reverse("emails:sender-emails-detail", kwargs={"pk": e.id})
    payload = {
        'name': 'new name',
    }
    response = auth_client.patch(url, payload)
    res = response.json()
    assert e.edit_history.first().edited_by.email == user.email
    assert response.status_code == 200
    assert res['name'] == payload["name"]


@pytest.mark.django_db
def test_delete_sender_email(auth_client, email, workspace, workspace_member, user):
    s = SenderDomain.objects.create(name="test", workspace=workspace)
    e = SenderEmail.objects.create(
        workspace=workspace, name="Contact", email_address="a@a.fr", reply_to="b@a.fr", domain=s
    )
    url = reverse("emails:sender-emails-detail", kwargs={"pk": e.id})

    response = auth_client.delete(url)
    assert response.status_code == 204
