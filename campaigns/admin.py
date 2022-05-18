from django.contrib import admin
from .models import (
    Sender,
    Campaign,
    CampaignActivity
)

admin.site.register(Sender)
admin.site.register(Campaign)
admin.site.register(CampaignActivity)