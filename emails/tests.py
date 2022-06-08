import pytest
import json
from .models import Email, SenderDomain, SenderEmail
from rest_framework.test import APIClient

# Test create an email
@pytest.mark.django_db
def test_create_email(auth_client, workspace, workspace_member, user):
    response = auth_client.post('/emails/emails', {
        'name': 'testem.',
        'type': 'RAW',
        'raw_html': '<html>HW</html>',
        'workspace': workspace.id
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['name'] == 'testem.'
    assert resp_json['workspace'] == str(workspace.id)

# Test retrieve an email details
@pytest.mark.django_db
def test_retrieve_email(auth_client, email, workspace, workspace_member, user):
    response = auth_client.get(f"/emails/emails/{email.id}")
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['name'] == email.name
    assert resp_json['raw_html'] == email.raw_html
    assert resp_json['workspace'] == str(workspace.id)

# Test update an email
@pytest.mark.django_db
def test_update_email(auth_client, email, workspace, workspace_member, user):
    response = auth_client.patch(f"/emails/emails/{email.id}", {
        'name': 'new name',
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['name'] == 'new name'

# Test delete an email
@pytest.mark.django_db
def test_delete_email(auth_client, email, workspace, workspace_member, user):
    response = auth_client.delete(f"/emails/emails/{email.id}")
    assert response.status_code == 204

# Test create a sender domain
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
