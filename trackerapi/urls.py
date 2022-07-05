from django.urls import path
from .views import (
    ListCreateTrackerAPIKey,
    TrackPages,
    ListPages,
)

urlpatterns = [
    path('keys', ListCreateTrackerAPIKey.as_view(), name="listcreatetrackerapikey"),
    path('track-pages', TrackPages.as_view(), name="createpage"),
    path('pages', ListPages.as_view(), name="listpage"),

]