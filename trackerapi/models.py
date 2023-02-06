import uuid

from django.db import models

from commons.models import BaseWorkspace
from contacts.models import Workspace, Contact
from users.models import CustomUser


class Page(BaseWorkspace):
    """
    Store Page views by Contact on client's website.

    Track Pages data are mostly used to generate dynamic Segments of Contacts.
    """

    url = models.CharField(max_length=200)  # Or screen name
    viewed_by_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='pages')


class Event(BaseWorkspace):
    """
    Store Events triggered by Contact on client's website.

    Track Pages data are mostly used to generate dynamic Segments of Contacts.
    """

    name = models.CharField(max_length=80)
    triggered_by_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='events')
    attributes = models.JSONField(null=True, blank=True)


class TrackerAPIKey(BaseWorkspace):
    """
    Stores API keys related to a Workspace.

    Each Workspace can have many API keys. An API key is mandatory to send a
    Track Event or Track Page to the Tracker API.
    """

    class Meta:
        verbose_name_plural = "Tracker API keys"

    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='api_keys')
