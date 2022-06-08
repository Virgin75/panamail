import pytest
import json
from django.contrib.auth import get_user_model
from users.models import Company, Workspace, MemberOfWorkspace, Invitation
from emails.models import Email, SenderDomain, SenderEmail
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
def auth_client(db, user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    return client
