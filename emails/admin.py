from django.contrib import admin
from .models import (
    SenderDomain,
    SenderEmail,
    Email,
)

admin.site.register(SenderDomain)
admin.site.register(SenderEmail)
admin.site.register(Email)
