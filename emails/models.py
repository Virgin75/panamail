from django.db import models
from django.contrib.auth import get_user_model
from users.models import Workspace

class SenderDomain(models.Model):
    DOMAIN_STATUS = [
        ('VERIFIED', 'Domain has been verified'),
        ('WAITING', 'Domain nameis  yet to be verified'),
    ]

    domain_name = models.CharField(max_length=75)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=DOMAIN_STATUS, default='WAITING')

    def __str__(self):
        return f'Domain name: {self.domain_name}'


class SenderEmail(models.Model):
    SENDER_STATUS = [
        ('VERIFIED', 'Email address can be used as sender'),
        ('WAITING', 'Email address needs yet to be verified'),
    ]

    email_address = models.EmailField(max_length=100)
    name = models.CharField(max_length=50)
    reply_to = models.EmailField(max_length=100)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=SENDER_STATUS, default='WAITING')
    domain = models.ForeignKey(SenderDomain, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.name} <{self.email_address}>'


class Email(models.Model):
    EMAIL_TYPES = [
    ('DESIGN', "Drag'n'drop designed email"),
    ('RAW', 'Basic WYSIWYG raw text email'),
    ]

    name = models.CharField(max_length=69)
    to_field = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=6, choices=EMAIL_TYPES)
    raw_html = models.TextField()
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} - Workspace: {self.workspace}'
