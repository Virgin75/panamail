from django.db import models
from django.contrib.auth import get_user_model
from users.models import Workspace

class Template(models.Model):
    name = models.CharField(max_length=69)
    raw_html = models.TextField()
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} - Workspace: {self.workspace}'


class Email(models.Model):
    EMAIL_TYPES = [
    ('DESIGN', "Drag'n'drop designed email"),
    ('RAW', 'Basic WYSIWYG raw text email'),
    ]

    name = models.CharField(max_length=69)
    type = models.CharField(max_length=6, choices=EMAIL_TYPES)
    raw_html = models.TextField()
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} - Workspace: {self.workspace}'
