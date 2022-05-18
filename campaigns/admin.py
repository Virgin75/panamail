from django.contrib import admin
from .models import (
    Sender,
    Campaign
)

admin.site.register(Sender)
admin.site.register(Campaign)
