from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from campaigns.permissions import CheckFKOwnership
from emails.permissions import (
    IsMemberOfWorkspace,
    IsMemberOfWorkspaceObj
)
from users.models import Workspace
from .models import Campaign
from .serializers import CampaignSerializer

class ListCreateCampaign(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace, CheckFKOwnership]
    serializer_class = CampaignSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        return Campaign.objects.filter(workspace=workspace)

class RetrieveUpdateDestroyCampaign(generics.RetrieveUpdateDestroyAPIView):
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = CampaignSerializer
    lookup_field = 'pk'