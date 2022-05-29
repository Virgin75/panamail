from django.db import models
from django.contrib.auth import get_user_model
from users.models import Workspace
from contacts.models import List, Segment
from emails.models import Email

class SenderDomain(models.Model):
    DOMAIN_STATUS = [
        ('VERIFIED', 'Domain has been verified'),
        ('WAITING', 'Domain nameis  yet to be verified'),
    ]

    domain_name = models.CharField(max_length=75)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=DOMAIN_STATUS)

    def __str__(self):
        return f'{self.name} <{self.email_address}>'


class SenderEmail(models.Model):
    SENDER_STATUS = [
        ('VERIFIED', 'Email address can be used as sender'),
        ('WAITING', 'Email address needs yet to be verified'),
    ]

    email_address = models.EmailField(max_length=100)
    name = models.CharField(max_length=50)
    reply_to = models.EmailField(max_length=100)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=SENDER_STATUS)
    domain = models.ForeignKey(SenderDomain, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} <{self.email_address}>'

class Campaign(models.Model):
    CAMPAIGN_STATUS = [
        ('DRAFT', "Campaign is in Draft"),
        ('TO VALIDATE', 'Campaign to validate'),
        ('SCHEDULED', 'Campaign scheduled'),
        ('SENT', 'Campaign sent'),
    ]
    TO_CHOICES = [
        ('LIST', 'Send to a list'),
        ('SEGMENT', 'Send to a segment'),
    ]

    name = models.CharField(max_length=89)
    status = models.CharField(max_length=15, choices=CAMPAIGN_STATUS, default='DRAFT')
    sender = models.ForeignKey(SenderEmail, on_delete=models.CASCADE)
    to_type = models.CharField(max_length=10, choices=TO_CHOICES)
    to_list = models.ForeignKey(List, on_delete=models.CASCADE, null=True, blank=True)
    to_segment = models.ForeignKey(Segment, on_delete=models.CASCADE, null=True, blank=True)
    email_model = models.ForeignKey(Email, on_delete=models.CASCADE)
    subject = models.TextField()
    scheduled_at = models.DateTimeField(blank=True, null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    #goal = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.status} - Workspace: {self.workspace}'


class CampaignActivity(models.Model):
    ACTIVITY_TYPES = [
        ('OPEN', 'The campaign email was open'),
        ('CLICK', 'The campaign email was clicked'),
        ('UNSUB', 'The user unsubscribed from the list'),
        ('SPAM', 'The user marked the campaign as spam'),
        ('BOUNC', 'The email bounced'),
    ]

    type = models.CharField(max_length=5, choices=ACTIVITY_TYPES)
    campaign_name = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user_name = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.type} - by {self.user_name} at {self.created_at}'