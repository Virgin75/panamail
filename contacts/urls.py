from django.urls import path
from .views import (
    ListCreateContact,
    RetrieveUpdateDestroyContact,
    SetCustomFieldOfContact,
    ListCreateCustomField,
    RetrieveUpdateDestroyCustomField,
    ListCreateList,
    RetrieveUpdateDestroyList
)

urlpatterns = [
    path('contacts', ListCreateContact.as_view(), name="listcreatecontact"),
    path('contacts/<uuid:pk>', RetrieveUpdateDestroyContact.as_view(), name="retrieveupdatedestroycontact"),
    path('contacts/<uuid:contact_pk>/set-custom-fields', SetCustomFieldOfContact.as_view(), name="setcustomfieldofcontact"),
    path('custom-fields', ListCreateCustomField.as_view(), name="listcreatecustomfield"),
    path('custom-fields/<int:pk>', RetrieveUpdateDestroyCustomField.as_view(), name="retrieveupdatedestroycustomfield"),
    path('lists', ListCreateList.as_view(), name="listcreatelist"),
    path('lists/<uuid:pk>', RetrieveUpdateDestroyList.as_view(), name="retrieveupdatedestroylist"),

]