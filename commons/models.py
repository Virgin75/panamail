from django.contrib.auth import get_user_model
from django.db import models

from users.models import Workspace


class History(models.Model):
    """Base edit history model used to log all changes to objects."""

    edited_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)


class BaseWorkspace(models.Model):
    """Base model used in all Workspace related models."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)  # TODO: rendre non editable
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    edit_history = models.ManyToManyField(History, blank=True)

    class Meta:
        abstract = True


class Tag(BaseWorkspace):
    """Table used in ManyToMany fields when needed to append tags to an object."""

    name = models.CharField(max_length=50)


class ExportHistory(BaseWorkspace):
    """Table used to log all export requests."""

    STATUS_CHOICES = [
        ('PENDING', 'Export is pending.'),
        ('SUCCESS', 'Export was successful.'),
        ('FAILURE', 'Export failed.'),
    ]
    file = models.FileField(upload_to='exports', null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    query = models.BinaryField(null=True, blank=True)
    export_serializer = models.BinaryField(null=True, blank=True)
