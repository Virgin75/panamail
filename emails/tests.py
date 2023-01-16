import pytest
import json
from django.urls import reverse
from emails.models import Email, Tag
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


#TODO
@pytest.mark.django_db
def test_create_sender_domain(auth_client, workspace, workspace_member, user):
    response = auth_client.post('/emails/sender-domains', {
        'domain_name': 'panam.io',
        'workspace': workspace.id
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['domain_name'] == 'panam.io'
    assert resp_json['workspace'] == str(workspace.id)

# Test retrieve a sender domain
@pytest.mark.django_db
def test_retrieve_sender_domain(auth_client, sender_domain, workspace, workspace_member, user):
    response = auth_client.get(f"/emails/sender-domains/{sender_domain.id}")
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['domain_name'] == sender_domain.domain_name
    assert resp_json['workspace'] == str(workspace.id)

# Test update a sender domain
@pytest.mark.django_db
def test_update_sender_domain(auth_client, sender_domain, workspace, workspace_member, user):
    response = auth_client.patch(f"/emails/sender-domains/{sender_domain.id}", {
        'domain_name': 'new name dn',
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['domain_name'] == 'new name dn'

# Test delete a sender domain
@pytest.mark.django_db
def test_delete_sender_domain(auth_client, sender_domain, workspace, workspace_member, user):
    response = auth_client.delete(f"/emails/sender-domains/{sender_domain.id}")
    assert response.status_code == 204


# Test create a sender email
@pytest.mark.django_db
def test_create_sender_email(auth_client, sender_domain, workspace, workspace_member, user):
    response = auth_client.post('/emails/sender-emails', {
        'name': 'Contact',
        'email_address': 'contact@pana.io',
        'reply_to': 'contact@pana.io',
        'domain': sender_domain.id,
        'workspace': workspace.id
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['email_address'] == 'contact@pana.io'
    assert resp_json['workspace'] == str(workspace.id)

# Test retrieve a sender email
@pytest.mark.django_db
def test_retrieve_sender_email(auth_client, sender_email, workspace, workspace_member, user):
    response = auth_client.get(f"/emails/sender-emails/{sender_email.id}")
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['email_address'] == sender_email.email_address
    assert resp_json['workspace'] == str(workspace.id)

# Test update a sender email
@pytest.mark.django_db
def test_update_sender_email(auth_client, sender_email, workspace, workspace_member, user):
    response = auth_client.patch(f"/emails/sender-emails/{sender_email.id}", {
        'reply_to': 'noreply@none.com',
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['reply_to'] == 'noreply@none.com'

# Test delete a sender email
@pytest.mark.django_db
def test_delete_sender_email(auth_client, sender_email, workspace, workspace_member, user):
    response = auth_client.delete(f"/emails/sender-emails/{sender_email.id}")
    assert response.status_code == 204
