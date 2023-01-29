from datetime import datetime

import factory
import pytz
from factory import fuzzy

from commons import models


class BaseWorkspaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BaseWorkspace

    workspace = factory.SubFactory('users.factories.WorkspaceFactory')
    created_by = factory.SubFactory('users.factories.UserFactory')
    created_at = fuzzy.FuzzyDateTime(pytz.UTC.localize(datetime.now()))


class RelatedFactoryVariableList(factory.RelatedFactoryList):  # noqa
    """allows overriding ``size`` during factory usage, e.g. ParentFactory(list_factory__size=4)"""

    def call(self, instance, step, context):
        size = context.extra.pop('size', self.size)
        assert isinstance(size, int)
        return [super(factory.RelatedFactoryList, self).call(instance, step, context) for i in range(size)]
