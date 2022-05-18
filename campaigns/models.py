from django.db import models
from django.contrib.auth import get_user_model
from users.models import Workspace
from contacts.models import List, Segment
from emails.models import Email

class Sender(models.Model):
    email_address = models.EmailField(max_length=100)
    name = models.CharField(max_length=50)
    reply_to = models.EmailField(max_length=100)

    def __str__(self):
        return f'{self.name} <{self.email_address}>'

class Campaign(models.Model):
    CAMPAIGN_STATUS = [
        ('DRAFT', "Drag'n'drop designed email"),
        ('TO VALIDATE', 'Basic WYSIWYG raw text email'),
        ('SCHEDULED', 'Basic WYSIWYG raw text email'),
        ('SENT', 'Basic WYSIWYG raw text email'),
    ]
    TO_CHOICES = [
        ('LIST', 'Send to a list'),
        ('SEGMENT', 'Send to a segment'),
    ]

    name = models.CharField(max_length=89)
    status = models.CharField(max_length=15, choices=CAMPAIGN_STATUS, default='DRAFT')
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE)
    to_type = models.CharField(max_length=10, choices=TO_CHOICES)
    to_list = models.ForeignKey(List, on_delete=models.CASCADE)
    to_segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    email_model = models.ForeignKey(Email, on_delete=models.CASCADE)
    subject = models.TextField()
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    #goal = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.status} - Workspace: {self.workspace}'
