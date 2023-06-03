import factory
from factory import fuzzy

from automation import models
from contacts.factories import ListFactory, SegmentFactory


class AutomationCampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AutomationCampaign

    name = factory.Sequence(lambda n: 'name: %d' % n)
    description = factory.Sequence(lambda n: 'Description %d' % n)
    status = "DRAFT"
    trigger_type = fuzzy.FuzzyChoice(['EVENT', 'PAGE', 'LIST', 'SEGMENT', 'TIME', 'EMAIL'])
    is_repeated = fuzzy.FuzzyChoice([True, False])
    workspace = factory.SelfAttribute('..workspace')


class TriggerEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TriggerEvent

    name = factory.Sequence(lambda n: '%d' % n)
    with_attributes = {"key": "value"}
    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')


class TriggerPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TriggerPage

    name = factory.Sequence(lambda n: 'name: %d' % n)
    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')


class TriggerListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TriggerList

    list = factory.SubFactory(ListFactory)
    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')


class TriggerSegmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TriggerSegment

    segment = factory.SubFactory(SegmentFactory)
    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')


class TriggerEmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TriggerEmail

    email = factory.SubFactory('emails.factories.EmailFactory')
    action = fuzzy.FuzzyChoice(['SENT', 'OPEN', 'CLICK', 'BOUNC', 'UNSUB', 'SPAM'])
    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')


class TriggerTimeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TriggerTime

    unit = fuzzy.FuzzyChoice(['YEAR', 'DAY', 'WEEK', 'MONTH'])
    value = fuzzy.FuzzyInteger(1, 25)
    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')


class StepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Step

    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')
    order = 1
    step_type = fuzzy.FuzzyChoice(['SEND_EMAIL', 'WAIT'])
