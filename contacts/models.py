from django.db import models
from django.contrib.auth import get_user_model
from users.models import Workspace

class Contact(models.Model):
    STATUS = [
    ('SUB', 'Subscribed'),
    ('UNSUB', 'Unsbiscribed'),
    ]

    email = models.CharField(max_length=250)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    trasac_email_status = models.CharField(max_length=5, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.email} - Workspace: {self.workspace}'

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
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.type}({self.name})'


class CustomFieldOfContact(models.Model):
    class Meta:
        verbose_name_plural = "Relations Contact <> Custom Field"

    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.contact}: {self.custom_field} = {self.value}'


class List(models.Model):
    name = models.CharField(max_length=100)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

class ContactInList(models.Model):
    class Meta:
        verbose_name_plural = "Relations Contact <> List"
    
    STATUS = [
    ('SUB', 'Subscribed'),
    ('UNSUB', 'Unsbiscribed'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    status = models.CharField(max_length=5, choices=STATUS)
    added_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name



class Segment(models.Model):
    name = models.CharField(max_length=100)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
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