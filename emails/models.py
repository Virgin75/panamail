from django.db import models

from commons.models import BaseWorkspace
from users.models import Workspace


class SenderDomain(models.Model):
    DOMAIN_STATUS = [
        ('VERIFIED', 'Domain has been verified'),
        ('WAITING', 'Domain nameis  yet to be verified'),
    ]

    domain_name = models.CharField(max_length=75, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=DOMAIN_STATUS, default='WAITING')

    def __str__(self):
        return f'Domain name: {self.domain_name} ({self.status})'


class SenderEmail(BaseWorkspace):
    SENDER_STATUS = [
        ('VERIFIED', 'Email address can be used as sender'),
        ('WAITING', 'Email address needs yet to be verified'),
    ]

    email_address = models.EmailField(max_length=100)
    name = models.CharField(max_length=50)
    reply_to = models.EmailField(max_length=100)
    status = models.CharField(max_length=10, choices=SENDER_STATUS, default='WAITING')
    domain = models.ForeignKey(SenderDomain, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.name} <{self.email_address}>'


class Tag(BaseWorkspace):
    name = models.CharField(max_length=50)


class Email(BaseWorkspace):
    EMAIL_TYPES = [
        ('DESIGN', "Drag'n'drop designed email"),
        ('RAW', 'Basic WYSIWYG raw text email'),
    ]

    name = models.CharField(max_length=69)
    to_field = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=6, choices=EMAIL_TYPES)
    raw_html = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'{self.name} - Workspace: {self.workspace}'


