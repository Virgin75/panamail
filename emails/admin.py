from django.contrib import admin
from .models import (
    Template,
    Email,
)

admin.site.register(Template)
admin.site.register(Email)
