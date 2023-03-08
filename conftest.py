from dataclasses import dataclass

import django_rq
import pytest
from django.contrib.auth import get_user_model
from fakeredis import FakeStrictRedis, FakeRedis
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Workspace, MemberOfWorkspace

USER_EMAIL = 'virgin225@gmail.com'
USER_PASSWORD = 'Azerty123$'
COMPANY_NAME = 'Panamail'
WORKSPACE_NAME = 'Panamail w'


# Fixtures
@pytest.fixture
def user(db):
    return get_user_model().objects.create(email=USER_EMAIL, password=USER_PASSWORD)


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
def workspace(db):
    return Workspace.objects.create(name=WORKSPACE_NAME)


@pytest.fixture
def workspace2(db):
    return Workspace.objects.create(name="2nd wks")


@pytest.fixture
def workspace_member(db, user, workspace):
    return MemberOfWorkspace.objects.create(user=user, workspace=workspace, rights='AD')


@pytest.fixture
def workspace_member2(db, user2, workspace2):
    return MemberOfWorkspace.objects.create(user=user2, workspace=workspace2, rights='ME')


@dataclass
class AuthenticatedClient:
    """Data class returning value for an auth client, to use in tests."""
    api: any
    user: any
    workspace: any


@pytest.fixture
def auth_client(db, user, workspace, workspace_member):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))
    django_rq.queues.get_redis_connection = FakeRedisConn()
    return AuthenticatedClient(client, user, workspace)


class FakeRedisConn:
    """Singleton FakeRedis connection."""

    def __init__(self):
        self.conn = None

    def __call__(self, _, strict):
        if not self.conn:
            self.conn = FakeStrictRedis() if strict else FakeRedis()
        return self.conn
