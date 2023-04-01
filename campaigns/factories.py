import factory
from django.utils import timezone
from factory import fuzzy

from campaigns import models
from contacts.factories import ListFactory, SegmentFactory
from emails.factories import SenderEmailFactory, EmailFactory


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Campaign

    name = factory.Sequence(lambda n: 'Tag %d' % n)
    description = factory.Sequence(lambda n: 'Description %d' % n)
    sender = factory.SubFactory(SenderEmailFactory)
    to_type = fuzzy.FuzzyChoice(['LIST', 'SEGMENT'])
    to_list = factory.SubFactory(ListFactory)
    to_segment = factory.SubFactory(SegmentFactory)
    email_model = factory.SubFactory(EmailFactory)
    subject = factory.Sequence(lambda n: 'Subject %d' % n)
    scheduled_at = fuzzy.FuzzyDateTime(start_dt=timezone.now())
    workspace = factory.SelfAttribute('..workspace')
