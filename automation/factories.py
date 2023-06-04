from random import randint

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


class AutomationCampaignFactoryWithSteps(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AutomationCampaign

    name = factory.Sequence(lambda n: 'name: %d' % n)
    description = factory.Sequence(lambda n: 'Description %d' % n)
    status = "DRAFT"
    trigger_type = fuzzy.FuzzyChoice(['EVENT', 'PAGE', 'LIST', 'SEGMENT', 'TIME', 'EMAIL'])
    is_repeated = fuzzy.FuzzyChoice([True, False])
    workspace = factory.SelfAttribute('..workspace')

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        """Add Steps to AutomationCampaign."""
        for i in range(1, randint(2, 3)):
            step = StepFactory(automation_campaign=self, workspace=self.workspace, order=i, step_type='SEND_EMAIL')
            self.steps.add(step)


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


class StepSendEmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StepSendEmail

    email = factory.SubFactory('emails.factories.EmailFactory')
    step = factory.SubFactory('automation.factories.BareStepFactory')
    workspace = factory.SelfAttribute('..workspace')


class StepWaitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StepWait

    step = factory.SubFactory('automation.factories.BareStepFactory')
    delay = fuzzy.FuzzyInteger(1, 25)
    delay_unit = fuzzy.FuzzyChoice(['days', 'hours', 'weeks', 'minutes'])
    workspace = factory.SelfAttribute('..workspace')


class StepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Step

    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')
    order = 1
    step_type = fuzzy.FuzzyChoice(['SEND_EMAIL', 'WAIT'])

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        """Add Step to AutomationCampaign and create Step content depending on 'step_type'."""
        self.automation_campaign.steps.add(self)

        match self.step_type:
            case 'SEND_EMAIL':
                return StepSendEmailFactory(step=self, workspace=self.workspace)
            case 'WAIT':
                return StepWaitFactory(step=self, workspace=self.workspace)
        return None


class BareStepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Step

    automation_campaign = factory.SubFactory(AutomationCampaignFactory)
    workspace = factory.SelfAttribute('..workspace')
    order = 1
    step_type = fuzzy.FuzzyChoice(['SEND_EMAIL', 'WAIT'])
