from django.urls import path
from .views import (
    ListCreateContact,
    RetrieveUpdateDestroyContact,
    UpdateCustomFieldOfContact,
)

urlpatterns = [
    path('contacts', ListCreateContact.as_view(), name="listcreatecontact"),
    path('contacts/<uuid:pk>', RetrieveUpdateDestroyContact.as_view(), name="retrieveupdatedestroycontact"),
    path('custom-fields-of-contact/<int:pk>', UpdateCustomFieldOfContact.as_view(), name="updatecustomfieldofcontact"),


]