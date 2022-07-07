import json
import re
from datetime import datetime
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
    EventSerializer,
)
from emails.permissions import IsMemberOfWorkspace
from .permissions import(
    IsWorkspaceAdmin,
    IsTokenValid,
    IsTrackedContactInWorkspace,
    IsWorkspaceAdminObj,
)


class ListCreateTrackerAPIKey(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceAdmin]
    serializer_class = TrackerAPIKeySerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        return TrackerAPIKey.objects.filter(workspace=workspace)

class DeleteTrackerAPIKey(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceAdminObj]
    serializer_class = TrackerAPIKeySerializer
    lookup_field = 'pk'
    queryset = TrackerAPIKey.objects.all()
    
    
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

   
class TrackEvents(generics.CreateAPIView):
    permission_classes = [IsTokenValid, IsTrackedContactInWorkspace]
    serializer_class = EventSerializer

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
        event = self.perform_create(serializer, api_key.workspace, contact)
        #set attributes of the event
        json_attr = json.loads(str(request.data['attributes']))
        for key, value in json_attr.items():
            ea = None
            if re.match(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", str(value)):
                ea = EventAttribute(
                    event=event,
                    key=key,
                    type='date',
                    value_date=value
                )
            elif isinstance(value, bool):
                ea = EventAttribute(
                    event=event,
                    key=key,
                    type='bool',
                    value_bool=value
                )
            elif isinstance(value, int):
                ea = EventAttribute(
                    event=event,
                    key=key,
                    type='int',
                    value_int=value
                )
            else:
                ea = EventAttribute(
                    event=event,
                    key=key,
                    type='str',
                    value_str=value
                )
            ea.save()
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, workspace, contact):
        return serializer.save(workspace=workspace, triggered_by_contact=contact)

class ListEvents(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = EventSerializer
    pagination_class = x20ResultsPerPage

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        return Event.objects.filter(workspace=workspace)
