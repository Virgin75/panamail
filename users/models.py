import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from smtp.models import Smtp
from .managers import CustomUserManager


class Plan(models.Model):
    name = models.CharField(max_length=20)
    price_ht = models.IntegerField()
    daily_email_limit = models.IntegerField()

    def __str__(self):
        return self.name


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name_plural = "Users"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='uploads', null=True, blank=True)
    address = models.CharField(max_length=125, null=True, blank=True)
    auto_utm_field = models.BooleanField(default=True)
    members = models.ManyToManyField(CustomUser, through='MemberOfWorkspace', related_name='workspaces')
    plan_name = models.ForeignKey(Plan, on_delete=models.CASCADE, blank=True, null=True)
    smtp = models.ForeignKey(Smtp, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name}'


class Invitation(models.Model):

    INVITE_ROLE = [
        ('AD', 'Admin'),
        ('ME', 'Member'),
        ('RO', 'Read-only'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invited_user = models.EmailField(max_length=100)
    to_workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    role = models.CharField(max_length=2, choices=INVITE_ROLE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class MemberOfWorkspace(models.Model):
    class Meta:
        verbose_name_plural = "Relations Users <> Workspace"
        unique_together = ('user', 'workspace',)

    RIGHT_CHOICES = [
        ('AD', 'Admin'),
        ('ME', 'Member'),
        ('RO', 'Read-only'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='member')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    rights = models.CharField(max_length=2, choices=RIGHT_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.user} in workspace: {self.workspace} ({self.rights})'