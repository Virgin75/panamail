import pytest
from django.urls import reverse

from users.factories import InvitationFactory
from users.models import Workspace, CustomUser, MemberOfWorkspace
from users.serializers import MinimalUserSerializer

USER_EMAIL = 'virgin225@gmail.com'
USER_PASSWORD = 'Azerty123$'
COMPANY_NAME = 'Panamail'
WORKSPACE_NAME = 'Panamail w'


@pytest.mark.django_db
def test_create_user(auth_client):
    url = reverse("users:users-signup")

    response = auth_client.api.post(url, {
        'email': 'dd@gmail.com',
        'first_name': 'Dummies',
        'last_name': 'Durant',
        'password': "Azerty123$",
    })

    res = response.json()
    assert response.status_code == 200
    assert len(res['access']) >= 10
    assert res['user']['email'] == 'dd@gmail.com'


@pytest.mark.django_db
def test_create_user_with_invite_token(auth_client):
    url = reverse("users:users-signup")
    invitation = InvitationFactory(to_workspace=auth_client.workspace)

    response = auth_client.api.post(url, {
        'email': 'dd@gmail.com',
        'first_name': 'Dummies',
        'last_name': 'Durant',
        'password': "Azerty123$",
    }, **{"QUERY_STRING": f"invitation_token={str(invitation.id)}"})

    res = response.json()
    assert response.status_code == 200
    assert len(res['access']) >= 10
    assert res['user']['email'] == 'dd@gmail.com'


@pytest.mark.django_db
def test_signin_user(auth_client, user2):
    url = reverse("users:users-signin")
    new_user = user2
    response = auth_client.api.post(url, {
        'email': new_user.email,
        'password': "Azerty123$",
    })

    res = response.json()
    assert response.status_code == 200
    assert len(res['access']) >= 10


@pytest.mark.django_db
def test_update_user(auth_client, user2):
    url = reverse("users:users-detail", kwargs={'pk': auth_client.user.id})
    response = auth_client.api.patch(url, {
        'first_name': "Louis",
    })

    res = response.json()
    assert response.status_code == 200
    assert res['first_name'] == "Louis"

    # Test update other user (not allowed)
    url = reverse("users:users-detail", kwargs={'pk': user2.id})
    response = auth_client.api.patch(url, {
        'first_name': "Louis",
    })
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_user(auth_client):
    url = reverse("users:users-detail", kwargs={'pk': auth_client.user.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert CustomUser.objects.count() == 0


@pytest.mark.django_db
def test_create_workspace(auth_client):
    url = reverse("users:workspaces-list")
    response = auth_client.api.post(url, {
        'name': 'Panamail inc.',
    })

    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'Panamail inc.'


@pytest.mark.django_db
def test_list_workspaces(auth_client):
    url = reverse("users:workspaces-list")
    response = auth_client.api.get(url)

    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 1
    assert res['results'][0]['name'] == auth_client.workspace.name


@pytest.mark.django_db
def test_update_workspace(auth_client):
    url = reverse("users:workspaces-detail", kwargs={'pk': auth_client.workspace.id})
    response = auth_client.api.patch(url, {
        'name': 'Panazz inc.',
    })

    res = response.json()
    assert response.status_code == 200
    assert res['name'] == 'Panazz inc.'


@pytest.mark.django_db
def test_delete_workspace(auth_client):
    url = reverse("users:workspaces-detail", kwargs={'pk': auth_client.workspace.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert Workspace.objects.count() == 0


@pytest.mark.django_db
def test_send_workspace_invitation(auth_client):
    url = reverse("users:workspaces-invitation", kwargs={'pk': auth_client.workspace.id})
    response = auth_client.api.post(url, {
        'to_workspace': str(auth_client.workspace.id),
        'invited_user': 'jp@aol.com',
        'role': 'ME'
    })

    res = response.json()
    assert response.status_code == 201
    assert len(res['id']) >= 10


@pytest.mark.django_db
def test_list_workspace_invitations(auth_client):
    invitation = InvitationFactory(to_workspace=auth_client.workspace)
    url = reverse("users:workspaces-invitation", kwargs={'pk': auth_client.workspace.id})
    response = auth_client.api.get(url)

    res = response.json()
    assert response.status_code == 200
    assert res["count"] == 1
    assert res["results"][0]["id"] == str(invitation.id)


@pytest.mark.django_db
def test_list_members_of_workspace(
        auth_client, workspace2, workspace_member2
):
    url = reverse("users:workspaces-members-list", kwargs={
        'parent_lookup_workspaces': str(auth_client.workspace.id),
    })
    response = auth_client.api.get(url)

    res = response.json()
    assert response.status_code == 200
    assert res["count"] == 1
    assert res["results"][0].get("user") == MinimalUserSerializer(auth_client.user).data

    # Test with another workspace (with no access)
    url = reverse("users:workspaces-members-list", kwargs={
        'parent_lookup_workspaces': str(workspace2.id),
    })
    response = auth_client.api.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_wokspace_member(
        auth_client, workspace2, workspace_member2
):
    url = reverse("users:workspaces-members-detail", kwargs={
        'parent_lookup_workspaces': str(auth_client.workspace.id),
        'pk': auth_client.user.id
    })
    response = auth_client.api.patch(url, {
        'role': 'AD'
    })

    res = response.json()
    assert response.status_code == 200
    assert res["rights"] == "AD"

    # Test with another workspace (with no access)
    url = reverse("users:workspaces-members-detail", kwargs={
        'parent_lookup_workspaces': str(workspace2.id),
        'pk': workspace_member2.user.id
    })
    response = auth_client.api.patch(url, {
        'role': 'AD'
    })
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_workspace_member(auth_client):
    url = reverse("users:workspaces-members-detail", kwargs={
        'parent_lookup_workspaces': str(auth_client.workspace.id),
        'pk': auth_client.user.id
    })
    response = auth_client.api.delete(url)

    assert response.status_code == 204
    assert MemberOfWorkspace.objects.count() == 0
