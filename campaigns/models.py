from django.db import models

from commons.models import BaseWorkspace, Tag
from contacts.models import List, Segment, Contact
from emails.models import Email, SenderEmail
from trackerapi.models import Event
from users.models import Workspace


class Campaign(BaseWorkspace):
    """
    A campaign is a set of the following objects:
     - An Email Template
     - A destination List or Segment (email addresses that will receive the campaign)
     - A Sender Email (the email address that will be used to send the campaign)

     A campaign can be sent instantly or scheduled for a later date.
     """
    CAMPAIGN_STATUS = [
        ('DRAFT', "Campaign is in Draft"),
        ('TO VALIDATE', 'Campaign to validate'),
        ('SENDING', 'Campaign being sent'),
        ('SCHEDULED', 'Campaign scheduled'),
        ('SENT', 'Campaign sent'),
    ]
    TO_CHOICES = [
        ('LIST', 'Send to a list'),
        ('SEGMENT', 'Send to a segment'),
    ]

    name = models.CharField(max_length=89)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=15, choices=CAMPAIGN_STATUS, default='DRAFT')
    sender = models.ForeignKey(SenderEmail, on_delete=models.CASCADE, null=True, blank=True)
    to_type = models.CharField(max_length=10, choices=TO_CHOICES, null=True, blank=True)
    to_list = models.ForeignKey(List, on_delete=models.CASCADE, null=True, blank=True)
    to_segment = models.ForeignKey(Segment, on_delete=models.CASCADE, null=True, blank=True)
    email_model = models.ForeignKey(Email, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.TextField(null=True, blank=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    stats = models.ManyToManyField(Contact, through='CampaignActivity')
    # goal = models.ForeignKey(Event, on_delete=models.CASCADE)
    flatten_sending = models.BooleanField(default=False)
    flatten_start_time = models.DateTimeField(blank=True, null=True)
    flatten_end_time = models.DateTimeField(blank=True, null=True)

    def send_emails(self):
        pass

    @property
    def total_contacts(self) -> int:
        """Return the total number of contacts in the campaign. Beware of using select_related() in View."""
        return self.to_list.contact_count if self.to_type == 'LIST' else self.to_segment.contact_count

    def __str__(self):
        return f'{self.name} - {self.status} - Workspace: {self.workspace}'


class CampaignActivity(BaseWorkspace):
    """
    M2M model used to log every actions related to an email sent.

    Actions may be: Sent, Opens, Clicks, Unsubscribes, Bounces or Spam complaints.
    """
    ACTIVITY_TYPES = [
        ('SENT', 'The email was sent'),
        ('OPEN', 'The email was open'),
        ('CLICK', 'The email was clicked'),
        ('UNSUB', 'The contact unsubscribed from the list'),
        ('SPAM', 'The contact marked the campaign as spam'),
        ('BOUNC', 'The email bounced'),
    ]

    action_type = models.CharField(max_length=5, choices=ACTIVITY_TYPES)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    details = models.TextField(null=True, blank=True)
