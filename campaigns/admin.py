from django.contrib import admin
from .models import (
    SenderEmail,
    SenderDomain,
    Campaign,
    CampaignActivity
)

admin.site.register(SenderEmail)
admin.site.register(SenderDomain)
admin.site.register(Campaign)
admin.site.register(CampaignActivity)