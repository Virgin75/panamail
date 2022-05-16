from django.contrib import admin
from .models import (
    Contact, 
    CustomField, 
    CustomFieldOfContact, 
    List,
    ContactInList,
    Segment,
)

admin.site.register(Contact)
admin.site.register(CustomField)
admin.site.register(CustomFieldOfContact)
admin.site.register(List)
admin.site.register(ContactInList)
admin.site.register(Segment)
