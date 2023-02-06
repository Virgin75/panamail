import uuid

from django.db import models
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from commons.models import BaseWorkspace, Tag
from users.models import Workspace


class Contact(BaseWorkspace):
    """Base Contact model representing a single person that we may send email to."""

    STATUS = [
        ('SUB', 'Subscribed'),
        ('UNSUB', 'Unsbiscribed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=250)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    custom_fields = models.ManyToManyField(
        'CustomField', through='CustomFieldOfContact', related_name='contacts', blank=True
    )
    transac_email_status = models.CharField(max_length=5, choices=STATUS, default='SUB')
    manual_email_status = models.CharField(max_length=5, choices=STATUS, default='SUB')

    def __str__(self):
        return f'{self.email} - Workspace: {self.workspace}'

    class Meta:
        unique_together = ('email', 'workspace',)


class CustomField(BaseWorkspace):
    """Custom Field model representing a Contact custom field instance."""

    FIELD_TYPES = [
        ('str', 'String'),
        ('int', 'Integer'),
        ('bool', 'Boolean'),
        ('date', 'Date'),
    ]
    type = models.CharField(max_length=4, choices=FIELD_TYPES)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Custom Fields"
        unique_together = ('name', 'workspace',)

    def __str__(self):
        return f'{self.type}({self.name})'


class CustomFieldOfContact(BaseWorkspace):
    """M2M table storing each custom field value for each contact."""

    class Meta:
        verbose_name_plural = "Relations Contact <> Custom Field"
        unique_together = ('custom_field', 'contact',)

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='fields_value')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value_str = models.TextField(blank=True, null=True)
    value_int = models.IntegerField(blank=True, null=True)
    value_bool = models.BooleanField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.contact} <> {self.custom_field}'
    
    def get_value(self):
        if self.value_int is not None:
            return self.value_int
        if self.value_str is not None:
            return self.value_str
        if self.value_date is not None:
            return self.value_date
        if self.value_bool is not None:
            return self.value_bool


class List(BaseWorkspace):
    """A List gathers many Contacts objects. They are used to facilitate email sending."""

    OPTIN_CHOICES = [
        ('double', 'Double Opt-in'),
        ('single', 'Single Opt-in'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    optin_choice = models.CharField(max_length=10, default='single', choices=OPTIN_CHOICES)
    contacts = models.ManyToManyField(Contact, through='ContactInList', related_name='lists')
    unsubscribed_contacts = models.ManyToManyField(Contact, related_name='unsubscribed_lists', blank=True)
    tags = models.ManyToManyField(Tag, related_name='lists')

    @property
    def contact_count(self):
        return self.contacts.count()

    def __str__(self):
        return f"{self.name} from Workspace {self.workspace}"


class ContactInList(BaseWorkspace):
    class Meta:
        verbose_name_plural = "Relations Contact <> List"
        unique_together = ('contact', 'list',)

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    double_optin_token = models.UUIDField(default=uuid.uuid4, editable=False)
    double_optin_validate_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.contact} is in list {self.list}"


class ContactInListHistory(BaseWorkspace):
    """Store the evolution of a specific List for each day of a calendar year."""

    class Meta:
        verbose_name_plural = "Contact In List History"

    list = models.ForeignKey(List, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total_contacts = models.IntegerField()


class Segment(BaseWorkspace):
    """A Segment is a group of Contacts that is dynamically computed given a list of Conditions."""

    OPERATORS = [
        ('AND', 'And'),
        ('OR', 'Or'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    members = models.ManyToManyField(Contact, through='ContactInSegment', related_name='segments')
    tags = models.ManyToManyField(Tag, related_name='segments')
    operator = models.CharField(max_length=3, choices=OPERATORS, default='AND')

    @property
    def contact_count(self):
        return self.members.count()

    def __str__(self):
        return self.name


class ContactInSegment(BaseWorkspace):
    """M2M table storing each Contact in a Segment."""

    class Meta:
        verbose_name_plural = "Relations Contact <> Segment"
        unique_together = ('contact', 'segment',)

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.contact} is in segment {self.segment}"


class ContactInSegmentHistory(BaseWorkspace):
    """Store the evolution of a specific Segment for each day of a calendar year."""

    class Meta:
        verbose_name_plural = "Contact In Segment History"

    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total_contacts = models.IntegerField()


class Condition(BaseWorkspace):
    """A Condition is a rule that is used to compute a Segment members."""

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
        ('LASTDAYS', 'In the last... days'),
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

    group = models.ForeignKey('GroupOfConditions', on_delete=models.CASCADE, related_name='conditions')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE, null=True, blank=True)
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES, null=True, blank=True)
    check_type = models.CharField(max_length=20, choices=CHECK_TYPES, null=True, blank=True)
    #Contains value to check or object ID (depending on condition_type)
    input_value = models.TextField(null=True, blank=True)
    input_value2 = models.TextField(null=True, blank=True)
    # Below fields are For PAGE & EVENT condition_type only
    check_period = models.CharField(max_length=20, choices=CHECK_PERIODS, null=True, blank=True)
    input_at_least = models.IntegerField(null=True, blank=True)
    in_last_x_days = models.IntegerField(null=True, blank=True)
    input_date1 = models.DateField(null=True, blank=True)
    input_date2 = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.condition_type} {self.check_type}: {self.input_value} (Segment: {self.segment})"


class GroupOfConditions(BaseWorkspace):
    """A GroupOfConditions is a group of Conditions that are combined with an operator (AND/OR)."""

    OPERATORS = [
        ('AND', 'And'),
        ('OR', 'Or'),
    ]
    operator = models.CharField(max_length=3, choices=OPERATORS, default='AND')
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='groups')

    class Meta:
        verbose_name_plural = "Group Conditions"


class CSVImportHistory(models.Model):
    nb_created = models.IntegerField()
    nb_updated = models.IntegerField()
    nb_errors = models.IntegerField()
    error_message = models.TextField()
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.created_at} - Workspace: {self.workspace}'


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
