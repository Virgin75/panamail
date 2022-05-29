from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, 
    Plan, 
    Company, 
    Workspace, 
    MemberOfWorkspace,
    SMTPProvider,)
from .forms import SignupForm, EditForm

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

admin.site.register(SMTPProvider)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Plan)
admin.site.register(Company)
admin.site.register(Workspace)
admin.site.register(MemberOfWorkspace)