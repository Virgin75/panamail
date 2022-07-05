from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from contacts.models import Contact
from users.models import Workspace
from contacts.paginations import x20ResultsPerPage
from .models import (
    Event,
    EventAttribute,
    TrackerAPIKey,
    Page,
)
from .serializers import (
    TrackerAPIKeySerializer,
    PageSerializer,
)
from emails.permissions import IsMemberOfWorkspace
from .permissions import(
    IsWorkspaceAdmin,
    IsTokenValid,
    IsTrackedContactInWorkspace,
)


class ListCreateTrackerAPIKey(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceAdmin]
    serializer_class = TrackerAPIKeySerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        return TrackerAPIKey.objects.filter(workspace=workspace)
    
    

class TrackPages(generics.CreateAPIView):
    permission_classes = [IsTokenValid, IsTrackedContactInWorkspace]
    serializer_class = PageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key = TrackerAPIKey.objects.get(
            token=self.request.data['api_token']
        )
        contact = get_object_or_404(
                Contact, 
                email=request.data['contact_email'],
                workspace=api_key.workspace
        )
        self.perform_create(serializer, api_key.workspace, contact)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, workspace, contact):
        serializer.save(workspace=workspace, viewed_by_contact=contact)


class ListPages(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = PageSerializer
    pagination_class = x20ResultsPerPage

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        return Page.objects.filter(workspace=workspace)