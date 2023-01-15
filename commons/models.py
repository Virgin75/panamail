from django.db import models
from users.models import Workspace
from django.contrib.auth import get_user_model


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
        related_name='created_%(class)ss'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    edit_history = models.ManyToManyField(History, blank=True)

    class Meta:
        abstract = True
