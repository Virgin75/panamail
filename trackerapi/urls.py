from django.urls import path
from .views import (
    ListCreateTrackerAPIKey,
    DeleteTrackerAPIKey,
    TrackPages,
    TrackEvents,
    ListPages,
    ListEvents,
)

urlpatterns = [
    path('keys', ListCreateTrackerAPIKey.as_view(), name="listcreatetrackerapikey"),
    path('keys/<uuid:pk>', DeleteTrackerAPIKey.as_view(), name="deletetrackerapikey"),
    path('track-pages', TrackPages.as_view(), name="createpage"),
    path('pages', ListPages.as_view(), name="listpage"),
    path('track-events', TrackEvents.as_view(), name="createevent"),
    path('events', ListEvents.as_view(), name="listevents"),
]