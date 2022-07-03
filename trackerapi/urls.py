from django.urls import path
from .views import (
    ListCreateTrackerAPIKey,
)

urlpatterns = [
    path('keys', ListCreateTrackerAPIKey.as_view(), name="listcreatetrackerapikey"),

]