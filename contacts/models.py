import uuid
from django.db import models
from django.contrib.auth import get_user_model
from users.models import Workspace

class Contact(models.Model):
    class Meta:
        unique_together = ('email', 'workspace',)

    STATUS = [
    ('SUB', 'Subscribed'),
    ('UNSUB', 'Unsbiscribed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=250)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)
    transac_email_status = models.CharField(max_length=5, choices=STATUS, default='SUB')
    manual_email_status = models.CharField(max_length=5, choices=STATUS, default='SUB')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.email} - Workspace: {self.workspace}'


class CSVImportHistory(models.Model):
    nb_created = models.IntegerField()
    nb_updated = models.IntegerField()
    nb_errors = models.IntegerField()
    error_message = models.TextField()
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.created_at} - Workspace: {self.workspace}'


class CustomField(models.Model):
    class Meta:
        verbose_name_plural = "Custom Fields"

    FIELD_TYPES = [
    ('str', 'String'),
    ('int', 'Integer'),
    ('bool', 'Boolean'),
    ('date', 'Date'),
    ]

    type = models.CharField(max_length=4, choices=FIELD_TYPES)
    name = models.CharField(max_length=100)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.type}({self.name})'


class CustomFieldOfContact(models.Model):
    class Meta:
        verbose_name_plural = "Relations Contact <> Custom Field"
        unique_together = ('custom_field', 'contact',)

    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, blank=True, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.contact}: {self.custom_field} = {self.value}'


class List(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name} from Workspace {self.workspace}"

class ContactInList(models.Model):
    class Meta:
        verbose_name_plural = "Relations Contact <> List"
        unique_together = ('contact', 'list',)

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.contact} is in list {self.list}"



class Segment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    workspace = models.ForeignKey(Workspace, models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class ConditionGroup(models.Model):
    class Meta:
        verbose_name_plural = "Segment Groups of conditions"

    OPERATORS = [
    ('AND', 'And'),
    ('OR', 'Or'),
    ]

    operators = models.CharField(max_length=3, choices=OPERATORS)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.operators}: {self.segment}'


class Condition(models.Model):
    class Meta:
        verbose_name_plural = "Segment Conditions"

    CONDITION_TYPES = [
    ('FIELD', 'Contact field'),
    ('EVENT', 'Event triggered'),
    ('PAGE', 'Page viewed'),
    ]

    CHECK_STR_TYPES = [
    ('IS', 'is'),
    ('IS NOT', 'is not'),
    ('CONTAINS', 'contains'),
    ('DOES NOT CONTAIN', 'does not contain'),
    ('EMPTY', 'empty'),
    ('NOT EMPTY', 'not empty'),
    ]

    CHECK_INT_TYPES = [
    ('EQUALS', 'equals'),
    ('SUPERIOR', 'superior'),
    ('SUPOREQUALS', 'superior or equals'),
    ('INFERIOR', 'inferior'),
    ('INFOREQUALS', 'inferior or equals'),
    ]

    CHECK_BOOL_TYPES = [
    ('IS', 'is true'),
    ('IS NOT', 'is false'),
    ]

    CHECK_DATE_TYPES = [
    ('AT', 'At this date'),
    ('BEFORE', 'Before this date'),
    ('AFTER', 'After this date'),
    ('EVER', 'Ever'),
    ('LAST', 'In the last...'),
    ('BETWEEN', 'Between ... and ...')
    ]

    group = models.ForeignKey(ConditionGroup, on_delete=models.CASCADE)
    type = models.CharField(max_length=5, choices=CONDITION_TYPES)
    email_to_check = models.CharField(max_length=100, null=True, blank=True)
    field_to_check = models.ForeignKey(CustomField, on_delete=models.CASCADE, null=True, blank=True)
    #event_to_check = models.ForeignKey(CustomField, on_delete=models.CASCADE, null=True, blank=True)
    #page_to_check = models.ForeignKey(CustomField, on_delete=models.CASCADE, null=True, blank=True)
    check_condition_str = models.CharField(max_length=20, choices=CHECK_STR_TYPES, null=True, blank=True)
    check_condition_int = models.CharField(max_length=20, choices=CHECK_INT_TYPES, null=True, blank=True)
    check_condition_bool = models.CharField(max_length=20, choices=CHECK_BOOL_TYPES, null=True, blank=True)
    check_condition_date = models.CharField(max_length=20, choices=CHECK_DATE_TYPES, null=True, blank=True)
    input_str = models.CharField(max_length=100, null=True, blank=True)
    input_at_least = models.IntegerField(null=True, blank=True)
    input_date1 = models.DateField(null=True, blank=True)
    input_date2 = models.DateField(null=True, blank=True)