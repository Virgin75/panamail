from datetime import datetime

import factory
import pytz
from factory import fuzzy

from users import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CustomUser

    first_name = factory.Sequence(lambda n: 'First%d' % n)
    last_name = factory.Sequence(lambda n: 'Last%d' % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.first_name)
    is_active = True
    is_staff = False
    is_superuser = False
    created_at = fuzzy.FuzzyDateTime(pytz.UTC.localize(datetime.now()))
    updated_at = fuzzy.FuzzyDateTime(pytz.UTC.localize(datetime.now()))


class WorkspaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Workspace

    name = factory.Sequence(lambda n: 'Workspace %d' % n)
    address = factory.Sequence(lambda n: 'Address %d' % n)
    auto_utm_field = True
    members = factory.RelatedFactory('users.factories.MemberOfWorkspaceFactory', 'workspace')
    smtp = None
    created_at = fuzzy.FuzzyDateTime(pytz.UTC.localize(datetime.now()))
    updated_at = fuzzy.FuzzyDateTime(pytz.UTC.localize(datetime.now()))


class MemberOfWorkspaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MemberOfWorkspace

    user = factory.SubFactory('users.factories.UserFactory')
    workspace = factory.SubFactory('users.factories.WorkspaceFactory')
    rights = 'ME'
    added_at = fuzzy.FuzzyDateTime(pytz.UTC.localize(datetime.now()))
    updated_at = fuzzy.FuzzyDateTime(pytz.UTC.localize(datetime.now()))


class InvitationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Invitation

    invited_user = factory.Sequence(lambda n: '%d@%d.com' % (n, n))
    to_workspace = factory.SubFactory('users.factories.WorkspaceFactory')
