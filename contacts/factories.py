import factory
from factory import fuzzy

from commons import factories
from contacts import models


class ContactFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.Contact

    first_name = factory.Sequence(lambda n: 'First%d' % n)
    last_name = factory.Sequence(lambda n: 'Last%d' % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.first_name)
    transac_email_status = 'SUB'
    manual_email_status = 'SUB'
    workspace = factory.SelfAttribute('..workspace')


class ListFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.List

    name = factory.Sequence(lambda n: 'List %d' % n)
    description = fuzzy.FuzzyText(length=100)
    contacts = factories.RelatedFactoryVariableList('contacts.factories.ContactInListFactory', 'list')
    optin_choice = fuzzy.FuzzyChoice(["single", "double"])


class ContactInListFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.ContactInList

    contact = factory.SubFactory('contacts.factories.ContactFactory')
    list = factory.SubFactory('contacts.factories.ListFactory')
    workspace = factory.SelfAttribute('..workspace')


class CustomFieldFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.CustomField

    name = factory.Sequence(lambda n: 'CustomField %d' % n)
    type = fuzzy.FuzzyChoice(["str", "int", "bool", "date"])
    workspace = factory.SelfAttribute('..workspace')


class CustomFieldOfContactFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.CustomFieldOfContact

    contact = factory.SubFactory('contacts.factories.ContactFactory')
    custom_field = factory.SubFactory('contacts.factories.CustomFieldFactory')
    workspace = factory.SelfAttribute('..workspace')


class SegmentFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.Segment

    name = factory.Sequence(lambda n: 'Segment %d' % n)
    description = fuzzy.FuzzyText(length=100)
    operator = fuzzy.FuzzyChoice(["AND", "OR"])
    workspace = factory.SelfAttribute('..workspace')


class GroupOfConditionsFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.GroupOfConditions

    operator = fuzzy.FuzzyChoice(["AND", "OR"])
    segment = factory.SubFactory('contacts.factories.SegmentFactory')
    workspace = factory.SelfAttribute('..workspace')


class ConditionFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.Condition

    condition_type = "BASIC FIELD"
    basic_field = fuzzy.FuzzyChoice(["FIRST_NAME", "LAST_NAME", "EMAIL"])
    check_type = fuzzy.FuzzyChoice(["IS", "CONTAINS"])
    input_value = fuzzy.FuzzyText(length=8)
    group = factory.SubFactory('contacts.factories.GroupOfConditionsFactory')
    workspace = factory.SelfAttribute('..workspace')


class ContactInSegmentFactory(factories.BaseWorkspaceFactory):
    class Meta:
        model = models.ContactInSegment

    contact = factory.SubFactory('contacts.factories.ContactFactory')
    segment = factory.SubFactory('contacts.factories.SegmentFactory')
    workspace = factory.SelfAttribute('..workspace')
