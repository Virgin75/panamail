from django.contrib import admin
from .models import (
    Contact, 
    CustomField, 
    CustomFieldOfContact, 
    List,
    ContactInList,
    Segment,
    Condition,
    ConditionGroup,
    CSVImportHistory,
    DatabaseToSync,
    DatabaseRule
)

admin.site.register(Contact)
admin.site.register(CustomField)
admin.site.register(CustomFieldOfContact)
admin.site.register(List)
admin.site.register(ContactInList)
admin.site.register(Segment)
admin.site.register(Condition)
admin.site.register(ConditionGroup)
admin.site.register(CSVImportHistory)
admin.site.register(DatabaseToSync)
admin.site.register(DatabaseRule)
