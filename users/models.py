from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

class Plan(models.Model):
    name = models.CharField(max_length=20)
    price_ht = models.IntegerField()
    daily_email_limit = models.IntegerField()

    def __str__(self):
        return self.name

class Company(models.Model):
    class Meta:
        verbose_name_plural = "Companies"

    BILLING_CHOICES = [
    ('MO', 'monthly'),
    ('YE', 'yearly'),
    ]
    name = models.CharField(max_length=100)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    billing = models.CharField(max_length=2, choices=BILLING_CHOICES)
    website = models.URLField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=125, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.plan})'

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name_plural = "Users"

    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='uploads', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.company})'



class MemberOfWorkspace(models.Model):
    class Meta:
        verbose_name_plural = "Relations Users <> Workspace"

    RIGHT_CHOICES = [
    ('AD','Admin'),
    ('ED','Editor'),
    ('VI','Viewer')
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='member')
    workspace = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rights = models.CharField(max_length=2, choices=RIGHT_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.user} in workspace: {self.workspace} ({self.rights})'