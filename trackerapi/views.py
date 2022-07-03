from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from users.models import Workspace
from .models import (
    Event,
    EventAttribute,
    TrackerAPIKey,
    Page,
)
from .serializers import (
    TrackerAPIKeySerializer,
)
from .permissions import(
    IsWorkspaceAdmin,
)


class ListCreateTrackerAPIKey(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceAdmin]
    serializer_class = TrackerAPIKeySerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        return TrackerAPIKey.objects.filter(workspace=workspace)
    
    def perform_create(self, serializer):
        serializer.save()
