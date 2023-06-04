import factory
from factory import fuzzy

from commons.models import Tag
from emails import models


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: 'Tag %d' % n)
    workspace = factory.SelfAttribute('..workspace')


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Email

    name = factory.Sequence(lambda n: 'Email %d' % n)
    to_field = fuzzy.FuzzyChoice(['{{contact.email}}', '{{event.user_email}}'])
    type = fuzzy.FuzzyChoice(['DESIGN', 'RAW'])
    raw_html = '<html>HW</html>'
    workspace = factory.SelfAttribute('..workspace')


class SenderDomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SenderDomain

    name = factory.Sequence(lambda n: '%d.com' % n)
    status = fuzzy.FuzzyChoice(['NONE', 'VERIFIED', 'WAITING'])


class SenderEmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SenderEmail

    email_address = factory.Sequence(lambda n: '%d@%d.com' % (n, n))
    name = factory.Sequence(lambda n: 'Name %d' % n)
    reply_to = factory.Sequence(lambda n: '%d@%d.com' % (n, n))
    status = fuzzy.FuzzyChoice(['VERIFIED', 'WAITING'])
    domain = factory.SubFactory(SenderDomainFactory)
