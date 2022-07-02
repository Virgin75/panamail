import pytest
import json
from django.contrib.auth import get_user_model
from users.models import Company, Workspace, MemberOfWorkspace, Invitation
from emails.models import Email, SenderDomain, SenderEmail
from contacts.models import Contact, CustomField, List, Segment, ContactInList, Condition
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


USER_EMAIL = 'virgin225@gmail.com'
USER_PASSWORD = 'Azerty123$'
COMPANY_NAME = 'Panamail'
WORKSPACE_NAME = 'Panamail w'

# Fixtures
@pytest.fixture
def company(db):
    return Company.objects.create(name=COMPANY_NAME)

@pytest.fixture
def user(db, company):
    return get_user_model().objects.create(
        email = USER_EMAIL,
        password = USER_PASSWORD,
        company = company,
        company_role = 'AD'
    )

@pytest.fixture
def user2(db, company):
    return get_user_model().objects.create(
        email = 'second@gmail.com',
        password = 'Azerty123$',
        company = company,
        company_role = 'ME'
    )

@pytest.fixture
def invitation(db, user, company):
    return Invitation.objects.create(
        invited_user = 'invitee@gmail.com',
        type = 'CO',
        role = 'ME',
        to_company = company
    )

@pytest.fixture
def workspace(db, company):
    return Workspace.objects.create(
        name=WORKSPACE_NAME,
        company=company
        )

@pytest.fixture
def workspace_member(db, user, workspace):
    return MemberOfWorkspace.objects.create(
        user=user,
        workspace=workspace,
        rights='AD'
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
