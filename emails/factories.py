import factory

from commons import models


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Tag

    name = factory.Sequence(lambda n: 'Tag %d' % n)
    workspace = factory.SelfAttribute('..workspace')
