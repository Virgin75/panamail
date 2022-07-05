import uuid
from django.db import models
from contacts.models import Workspace, Contact
from users.models import CustomUser

class Page(models.Model):
    url = models.CharField(max_length=150) #Or screen name
    viewed_by_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='pages')
    viewed_at = models.DateTimeField(auto_now_add=True, null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='pages', null=True, blank=True)

    def __str__(self):
        return f'Page: {self.url} viewed by {self.viewed_by_contact}'


class Event(models.Model):
    name = models.CharField(max_length=80)
    triggered_by_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='events')
    triggered_at = models.DateTimeField(auto_now_add=True, null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    
    def __str__(self):
        return f'Event: {self.name} triggered by {self.triggered_by_contact} at {self.triggered_at}'


class EventAttribute(models.Model):
    class Meta:
        verbose_name_plural = "Events' attributes"

    FIELD_TYPES = [
        ('str', 'String'),
        ('int', 'Integer'),
        ('bool', 'Boolean'),
        ('date', 'Date'),
    ]

    key = models.CharField(max_length=50)
    value_str = models.TextField(null=True, blank=True)
    value_int = models.IntegerField(null=True, blank=True)
    value_bool = models.BooleanField(null=True, blank=True)
    value_date = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=4, choices=FIELD_TYPES, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attributes')

    def __str__(self):
        return f'Event attribute: "{self.key}": ({self.type})'


class TrackerAPIKey(models.Model):
    class Meta:
        verbose_name_plural = "Tracker API keys"

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='api_keys')
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'API Key for: {self.workspace}'
