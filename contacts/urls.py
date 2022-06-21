from django.urls import path
from .views import (
    ListCreateContact,
    RetrieveUpdateDestroyContact,
    SetCustomFieldOfContact,
    ListCreateCustomField,
    RetrieveUpdateDestroyCustomField,
    ListCreateList,
    RetrieveUpdateDestroyList,
    ListContactInList,
    CreateContactInList,
    DeleteContactFromList,
    BulkContactCSVImport,
    ListCreateDbToSync,
    RetrieveUpdateDestroyDbToSYnc
)

urlpatterns = [
    path('contacts', ListCreateContact.as_view(), name="listcreatecontact"),
    path('contacts/<uuid:pk>', RetrieveUpdateDestroyContact.as_view(), name="retrieveupdatedestroycontact"),
    path('contacts/<uuid:contact_pk>/set-custom-fields', SetCustomFieldOfContact.as_view(), name="setcustomfieldofcontact"),
    path('custom-fields', ListCreateCustomField.as_view(), name="listcreatecustomfield"),
    path('custom-fields/<int:pk>', RetrieveUpdateDestroyCustomField.as_view(), name="retrieveupdatedestroycustomfield"),
    path('lists', ListCreateList.as_view(), name="listcreatelist"),
    path('lists/<uuid:pk>', RetrieveUpdateDestroyList.as_view(), name="retrieveupdatedestroylist"),
    path('contacts-in-list', ListContactInList.as_view(), name="listcontactinlist"),
    path('add-contact-in-list', CreateContactInList.as_view(), name="createcontactinlist"),
    path('delete-contact-in-list/<int:pk>', DeleteContactFromList.as_view(), name="deletecontactinlist"),
    path('bulk-csv-import', BulkContactCSVImport.as_view(), name="bulkcsvimport"),
    path('sync-db', ListCreateDbToSync.as_view(), name="listcreatedbtosync"),
    path('sync-db/<int:pk>', RetrieveUpdateDestroyDbToSYnc.as_view(), name="retrieveupdatedestroydbtosync"),
]