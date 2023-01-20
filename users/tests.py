import json

import pytest

USER_EMAIL = 'virgin225@gmail.com'
USER_PASSWORD = 'Azerty123$'
COMPANY_NAME = 'Panamail'
WORKSPACE_NAME = 'Panamail w'


# Test create user (with invitation)
@pytest.mark.django_db
def test_signup_with_invitation(auth_client, user, company, invitation):
    response = auth_client.post(f'/users/signup?invitation_token={invitation.id}', {
        'email': 'invitee@gmail.com',
        'password': 'Azerty123$',
        'first_name': 'fgdfg',
        'last_name': 'gdfgd',
    })
    resp_json = json.loads(response.content)
    print(resp_json)
    assert response.status_code == 200
    assert resp_json['email'] == 'invitee@gmail.com'


# Test retrieve logged in user details
@pytest.mark.django_db
def test_retrieve_user_details(auth_client):
    response = auth_client.get('/users/my-profile')
    resp_json = json.loads(response.content)

    assert response.status_code == 200
    assert resp_json['email'] == USER_EMAIL


# Test create a company
@pytest.mark.django_db
def test_create_company(auth_client):
    response = auth_client.post('/users/companies', {
        'name': 'Panamail Incorporation.',
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['name'] == 'Panamail Incorporation.'

# Test retrieve my company details
@pytest.mark.django_db
def test_retrieve_my_company(auth_client, company, user):
    response = auth_client.get('/users/my-company')
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['name'] == str(company.name)


# Test list my company members
@pytest.mark.django_db
def test_list_company_members(auth_client):
    response = auth_client.get('/users/company-members/')
    resp_json = json.loads(response.content)

    for member in resp_json:
        assert member['company'] == COMPANY_NAME

    assert response.status_code == 200

# Test list workspaces I belong to
@pytest.mark.django_db
def test_list_my_workspaces(auth_client, workspace, workspace_member):
    response = auth_client.get('/users/workspaces')
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json[0]['name'] == WORKSPACE_NAME

# Test create a workspace member
@pytest.mark.django_db
def test_create_workspace_member(auth_client, workspace, workspace_member, user, user2):
    response = auth_client.post('/users/workspaces-members/', {
        'workspace': workspace.id,
        'user': user2.id,
        'rights':'ME'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['user'] == str(user2.id)
    assert resp_json['workspace'] == str(workspace.id)

# Test list workspaces members
@pytest.mark.django_db
def test_list_workspace_members(auth_client, workspace, workspace_member):
    response = auth_client.get(f'/users/workspaces-members/?workspace_id={workspace.id}')
    resp_json = json.loads(response.content)

    assert response.status_code == 200
    assert len(resp_json) >= 1

# Retrieve a workspace details
@pytest.mark.django_db
def test_retrieve_workspace_details(auth_client, workspace, workspace_member):
    response = auth_client.get(f'/users/workspaces/{workspace.id}')
    resp_json = json.loads(response.content)

    assert response.status_code == 200
    assert resp_json['id'] == str(workspace.id)
    assert resp_json['name'] == WORKSPACE_NAME

# Update a member of a workspace
@pytest.mark.django_db
def test_update_workspace_member(auth_client, workspace, workspace_member, user):
    response = auth_client.patch(f'/users/workspaces-members/{workspace_member.id}', {
        'rights':'AD'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['rights'] == 'AD'
    assert resp_json['workspace'] == str(workspace.id)

# Update a workspace
@pytest.mark.django_db
def test_update_workspace(auth_client, workspace, workspace_member, user):
    response = auth_client.patch(f'/users/workspaces/{workspace.id}', {
        'name':'new Name'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['name'] == 'new Name'
    assert resp_json['id'] == str(workspace.id)

# Test create an invitation
@pytest.mark.django_db
def test_create_invitation(auth_client, workspace, workspace_member, company):
    response = auth_client.post('/users/invitations/', {
        'invited_user': 'jean-mouloud@gmail.com',
        'type': 'CO',
        'role':'ME',
        'to_company': company.id
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['invited_user'] == 'jean-mouloud@gmail.com'
    assert resp_json['to_company'] == str(company.id)

# Test update my company
@pytest.mark.django_db
def test_update_my_company(auth_client, company, user):
    response = auth_client.patch('/users/my-company', {
        'website': 'https://www.panamail.io/'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['website'] == 'https://www.panamail.io/'



# Delete my company
@pytest.mark.django_db
def test_delete_my_company(auth_client, workspace, workspace_member, user, user2):
    response = auth_client.delete('/users/my-company')
    assert response.status_code == 204

# Delete a member of a workspace
@pytest.mark.django_db
def test_delete_workspace_member(auth_client, workspace, workspace_member, user, user2):
    response = auth_client.delete(f'/users/workspaces-members/{workspace_member.id}')
    assert response.status_code == 204

# Delete a workspace
@pytest.mark.django_db
def test_delete_workspace(auth_client, workspace, workspace_member, user, user2):
    response = auth_client.delete(f'/users/workspaces/{workspace.id}')
    assert response.status_code == 204
