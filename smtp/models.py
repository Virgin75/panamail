from django.db import models


class Smtp(models.Model):
    SMTP_CHOICES = [
        ('SES', "Amazon Web Service SES"),
        ('SMTP', "Custom SMTP Provider")
    ]
    active = models.CharField(choices=SMTP_CHOICES, max_length=4)


class AwsSes(models.Model):
    name = models.CharField(default="SES", unique=True, max_length=50)
    region = ""
    password = ""
