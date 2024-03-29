from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import SignupForm, EditForm
from .models import (
    CustomUser,
    Workspace,
    MemberOfWorkspace,
    Invitation
)


class CustomUserAdmin(UserAdmin):
    add_form = SignupForm
    form = EditForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Workspace)
admin.site.register(MemberOfWorkspace)
admin.site.register(Invitation)