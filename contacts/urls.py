from django.urls import path
from .views import (
    ListCreateContact,
    RetrieveUpdateDestroyContact,
    UpdateCustomFieldOfContact,
    ListCreateCustomField,
    RetrieveUpdateDestroyCustomField
)

urlpatterns = [
    path('contacts', ListCreateContact.as_view(), name="listcreatecontact"),
    path('contacts/<uuid:pk>', RetrieveUpdateDestroyContact.as_view(), name="retrieveupdatedestroycontact"),
    path('custom-fields-of-contact/<int:pk>', UpdateCustomFieldOfContact.as_view(), name="updatecustomfieldofcontact"),
    path('custom-fields', ListCreateCustomField.as_view(), name="listcreatecustomfield"),
    path('custom-fields/<int:pk>', RetrieveUpdateDestroyCustomField.as_view(), name="retrieveupdatedestroycustomfield"),

]