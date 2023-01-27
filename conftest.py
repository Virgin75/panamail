import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from contacts.models import Contact, CustomField, List, Segment, ContactInList, Condition
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
def contact(db, workspace):
    return Contact.objects.create(
        email='contact@panamail.com',
        workspace=workspace
    )

@pytest.fixture
def custom_field(db, workspace):
    return CustomField.objects.create(
        type='str',
        name='first_name',
        workspace=workspace
    )

@pytest.fixture
def list(db, workspace):
    return List.objects.create(
        name='Newsletter Client',
        workspace=workspace
    )

@pytest.fixture
def segment(db, workspace):
    return Segment.objects.create(
        name='Active users',
        operator='AND',
        workspace=workspace
    )

@pytest.fixture
def condition(db, workspace, custom_field, segment):
    return Condition.objects.create(
        condition_type='CUSTOM FIELD',
        custom_field=custom_field,
        check_type='IS NOT',
        input_value='Albert',
        segment=segment
    )

@pytest.fixture
def contact_in_list(db, workspace, contact, list):
    return ContactInList.objects.create(
        contact=contact,
        list=list
    )

@pytest.fixture
def auth_client(db, user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    return client
