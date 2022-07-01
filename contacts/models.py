import uuid
from django_celery_beat.models import PeriodicTask, IntervalSchedule
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
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True, related_name='contacts')
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
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True, related_name='customfields')

    def __str__(self):
        return f'{self.type}({self.name})'


class CustomFieldOfContact(models.Model):
    class Meta:
        verbose_name_plural = "Relations Contact <> Custom Field"
        unique_together = ('custom_field', 'contact',)

    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.contact}: {self.custom_field} = {self.value}'


class List(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True, related_name='lists')
    contacts = models.ManyToManyField(Contact, through='ContactInList', related_name='lists')
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


class DatabaseToSync(models.Model):
    class Meta:
        verbose_name_plural = "Databases to sync"
    
    DB_TYPES = [
        ('PG', 'PostgreSQL'),
        ('MY', 'MySQL')
    ]

    type = models.CharField(max_length=2, choices=DB_TYPES)
    db_host = models.CharField(max_length=55)
    db_port = models.CharField(max_length=5, blank=True, null=True)
    db_name = models.CharField(max_length=55)
    db_user = models.CharField(max_length=55)
    db_password = models.CharField(max_length=250)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True, related_name='databasestosync')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class DatabaseRule(models.Model):

    db = models.ForeignKey(DatabaseToSync, on_delete=models.SET_NULL, null=True)
    query = models.TextField()
    column_mapping = models.TextField(null=True)
    list = models.ForeignKey(List, on_delete=models.SET_NULL, null=True)
    beat_task = models.ForeignKey(PeriodicTask, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Segment(models.Model):
    OPERATORS = [
        ('AND', 'And'),
        ('OR', 'Or'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    operator = models.CharField(max_length=3, choices=OPERATORS, default='AND')
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True, related_name='segments')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Condition(models.Model):
    class Meta:
        verbose_name_plural = "Segment Conditions"

    CONDITION_TYPES = [
        ('EMAIL', 'Contact email ... <input_value>'),
        ('CUSTOM FIELD', 'Contact <custom_field> ... <input_value>'),
        ('LIST', 'Contact is in list <input_value>'),
        ('EVENT', 'Contact has triggered event <input_value>'),
        ('PAGE', 'Contact has viewed page <input_value>'),
    ]

    CHECK_TYPES = [
        ('IS', 'is exactly'),
        ('IS NOT', 'is not'),
        ('CONTAINS', 'contains'),
        ('DOES NOT CONTAIN', 'does not contain'),
        ('IS EMPTY', 'empty'),
        ('IS NOT EMPTY', 'not empty'),
        ('EQUALS', 'equals'),
        ('SUPERIOR', 'superior'),
        ('SUPOREQUALS', 'superior or equals'),
        ('INFERIOR', 'inferior'),
        ('INFOREQUALS', 'inferior or equals'),
        ('IS TRUE', 'is true'),
        ('IS FALSE', 'is false'),
        ('AT', 'At this date'),
        ('BEFORE', 'Before this date'),
        ('AFTER', 'After this date'),
        ('LAST', 'In the last...'),
        ('BETWEEN', 'Between ... and ...')
    ]

    CHECK_PERIODS = [
        ('EVER', 'Ever'),
        ('AT', 'At this date'),
        ('BEFORE', 'Before this date'),
        ('AFTER', 'After this date'),
        ('LAST', 'In the last...'),
        ('BETWEEN', 'Between ... and ...')
    ]


    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='conditions')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE, null=True, blank=True)
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES, null=True, blank=True)
    check_type = models.CharField(max_length=20, choices=CHECK_TYPES, null=True, blank=True)
    #Contains value to check or object ID (depending on condition_type)
    input_value = models.TextField( null=True, blank=True)
    #Below fields are For PAGE & EVENT condition_type only
    check_period = models.CharField(max_length=20, choices=CHECK_PERIODS, null=True, blank=True)
    input_at_least = models.IntegerField(null=True, blank=True)
    input_date1 = models.DateField(null=True, blank=True)
    input_date2 = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.condition_type} {self.check_type}: {self.input_value} (Segment: {self.segment})"