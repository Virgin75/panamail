from django.urls import path
from .views import (
    ListCreateCampaign,
    RetrieveUpdateDestroyCampaign,
    SendCampaign
)

urlpatterns = [
    path('campaigns', ListCreateCampaign.as_view(), name="listcreatecampaign"),
    path('campaigns/<int:pk>', RetrieveUpdateDestroyCampaign.as_view(), name="retrieveupdatedestroycampaign"),
    path('campaigns/<int:pk>/send', SendCampaign.as_view(), name="schedulecampaign"),

]