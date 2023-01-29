import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from contacts.models import Contact, List
from emails.models import Email, SenderDomain, SenderEmail
from users.models import Workspace, MemberOfWorkspace, Invitation

USER_EMAIL = 'virgin225@gmail.com'
USER_PASSWORD = 'Azerty123$'
COMPANY_NAME = 'Panamail'
WORKSPACE_NAME = 'Panamail w'

# Fixtures
@pytest.fixture
def user(db):
    return get_user_model().objects.create(
        email=USER_EMAIL,
        password=USER_PASSWORD,
    )


@pytest.fixture
def user2(db):
    email = "huhik@klk.fr"
    password = "Azerty123$"
    user2 = get_user_model().objects.create_user(
        email=email,
        password=password,
    )
    return user2


@pytest.fixture
def invitation(db, user, workspace):
    return Invitation.objects.create(
        invited_user='invitee@gmail.com',
        role='ME',
        to_workspace=workspace
    )


@pytest.fixture
def workspace(db):
    return Workspace.objects.create(
        name=WORKSPACE_NAME,
    )


@pytest.fixture
def workspace2(db):
    return Workspace.objects.create(
        name="2nd wks",
    )


@pytest.fixture
def workspace_member(db, user, workspace):
    return MemberOfWorkspace.objects.create(
        user=user,
        workspace=workspace,
        rights='AD'
    )


@pytest.fixture
def workspace_member2(db, user2, workspace2):
    return MemberOfWorkspace.objects.create(
        user=user2,
        workspace=workspace2,
        rights='ME'
    )


@pytest.fixture
def email(db, workspace):
    return Email.objects.create(
        name='Test email',
        type='RAW',
        raw_html='<strong>LOL</strong>',
        workspace=workspace
    )


@pytest.fixture
def list(db, workspace):
    return List.objects.create(
        name='Test list',
        description='Test description',
        workspace=workspace,
    )


@pytest.fixture
def list2(db, workspace2):
    return List.objects.create(
        name='Test list',
        description='Test description',
        workspace=workspace2,
    )


@pytest.fixture
def lists(db, workspace):
    return List.objects.bulk_create(
        [
            List(
                name=f'List n°{i}',
                description='Test description',
                workspace=workspace,
            ) for i, _ in enumerate(range(3))
        ]
    )


@pytest.fixture
def contacts(db, workspace, list, user):
    contacts = Contact.objects.bulk_create(
        [
            Contact(
                email=f'a{i}@free.com',
                workspace=workspace,
            ) for i, _ in enumerate(range(3))
        ]
    )
    # Also create Contacts that won't be added in list
    Contact.objects.bulk_create(
        [
            Contact(
                email=f'b{i}@free.com',
                workspace=workspace,
            ) for i, _ in enumerate(range(2))
        ]
    )

    list.contacts.set(
        contacts,
        through_defaults={"workspace_id": workspace.id, "created_by": user})
    return contacts


@pytest.fixture
def contacts2(db, workspace2, list2, user2):
    contacts = Contact.objects.bulk_create(
        [
            Contact(
                email=f'a{i}@free.com',
                workspace=workspace2,
            ) for i, _ in enumerate(range(3))
        ]
    )
    list2.contacts.set(
        contacts,
        through_defaults={"workspace_id": workspace2.id, "created_by": user2})
    return contacts


@pytest.fixture
def sender_domain(db, workspace):
    return SenderDomain.objects.create(
        domain_name='panamail.com',
        workspace=workspace
    )


@pytest.fixture
def sender_email(db, workspace, sender_domain):
    return SenderEmail.objects.create(
        email_address='contact@panamail.com',
        reply_to='contact@panamail.com',
        name='Contact',
        domain=sender_domain,
        workspace=workspace
    )


@pytest.fixture
def auth_client(db, user, workspace, workspace_member):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    return client
