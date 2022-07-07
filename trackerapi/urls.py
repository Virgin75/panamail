from django.urls import path
from .views import (
    ListCreateTrackerAPIKey,
    DeleteTrackerAPIKey,
    TrackPages,
    TrackEvents,
    ListPages,
    ListEvents,
    CreateContact,
    UpdateDeleteContact,
    CreateOrUpdateContact,
)

urlpatterns = [
    path('keys', ListCreateTrackerAPIKey.as_view(), name="listcreatetrackerapikey"),
    path('keys/<uuid:pk>', DeleteTrackerAPIKey.as_view(), name="deletetrackerapikey"),
    path('track-pages', TrackPages.as_view(), name="createpage"),
    path('track-events', TrackEvents.as_view(), name="createevent"),
    path('pages', ListPages.as_view(), name="listpage"),
    path('events', ListEvents.as_view(), name="listevents"),
    path('contacts', CreateContact.as_view(), name="createcontact"),
    path('contacts/update', UpdateDeleteContact.as_view(), name="updatecontact"),
    path('contacts/create-or-update', CreateOrUpdateContact.as_view(), name="createorupdatecontact"),
    path('contacts/delete', UpdateDeleteContact.as_view(), name="deletecontact"),
]