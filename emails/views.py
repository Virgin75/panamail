from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from .serializers import (
    SenderEmailSerializer, 
    SenderDomainSerializer, 
    EmailSerializer, 
)
from users.models import Workspace
from .models import (
    SenderEmail,
    SenderDomain,
    Email
)

from .permissions import (
    IsMemberOfWorkspace,
    IsMemberOfWorkspaceObj
)

class ListCreateEmail(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = EmailSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return Email.objects.filter(workspace=workspace)


class RetrieveUpdateDestroyEmail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Email.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = EmailSerializer
    lookup_field = 'pk'


class ListCreateSenderDomain(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = SenderDomainSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return SenderDomain.objects.filter(workspace=workspace)


class RetrieveUpdateDestroySenderDomain(generics.RetrieveUpdateDestroyAPIView):
    queryset = SenderDomain.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = SenderDomainSerializer
    lookup_field = 'pk'


class ListCreateSenderEmail(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = SenderEmailSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return SenderEmail.objects.filter(workspace=workspace)


class RetrieveUpdateDestroySenderEmail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SenderEmail.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = SenderEmailSerializer
    lookup_field = 'pk'