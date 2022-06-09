from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import (
    ContactSerializer,
    CustomFieldSerializer,
    CustomFieldOfContactSerializer,
    ListSerializer,
    ContactInListSerializer
)
from users.models import Workspace
from .models import (
    Contact,
    CustomField,
    CustomFieldOfContact,
    List,
    ContactInList
)
from .paginations import x20ResultsPerPage
from emails.permissions import (
    IsMemberOfWorkspace,
    IsMemberOfWorkspaceObj
)
from .permissions import IsMemberOfWorkspaceObjCustomField

class ListCreateContact(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = ContactSerializer
    pagination_class = x20ResultsPerPage

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return Contact.objects.filter(workspace=workspace)


class RetrieveUpdateDestroyContact(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = ContactSerializer
    lookup_field = 'pk'


class UpdateCustomFieldOfContact(generics.UpdateAPIView):
    queryset = CustomFieldOfContact.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObjCustomField]
    serializer_class = CustomFieldOfContactSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        #Update the Contact instance, so that last update date is changed accordingly
        contact_id = instance.contact.id
        contact = Contact.objects.get(id=contact_id)
        contact.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ListCreateCustomField(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = CustomFieldSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return CustomField.objects.filter(workspace=workspace)


class RetrieveUpdateDestroyCustomField(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomField.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = CustomFieldSerializer
    lookup_field = 'pk'
