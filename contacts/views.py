from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import (
    ContactSerializer,
    CustomFieldSerializer,
    ListSerializer,
    ContactInListSerializerRead,
    ContactInListSerializerWrite
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
from .permissions import (
    IsMemberOfWorkspaceCF, 
    IsMemberOfWorkspaceCL,
    IsMemberOfWorkspaceObjCF
)

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


class SetCustomFieldOfContact(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceCF]

    def post(self, request, contact_pk, format=None):
        print(contact_pk)
        for field_to_update, value in request.data.items():
            #If custom field of contact exists, update it
            try:
                cf = CustomFieldOfContact.objects.get(
                    contact=contact_pk,
                    custom_field=int(field_to_update)
                )
                cf.value = value
                cf.save()
            #Else, create it
            except CustomFieldOfContact.DoesNotExist:
                cf = CustomFieldOfContact(
                    contact=get_object_or_404(Contact, id=contact_pk),
                    custom_field=get_object_or_404(CustomField, id=int(field_to_update)),
                    value=value
                )
                cf.save()

        return Response({'status': 'All fields were updated successfully.'})

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


class ListCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = ListSerializer
    pagination_class = x20ResultsPerPage

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return List.objects.filter(workspace=workspace)


class RetrieveUpdateDestroyList(generics.RetrieveUpdateDestroyAPIView):
    queryset = List.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = ListSerializer
    lookup_field = 'pk'


class ListContactInList(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceCL]
    serializer_class = ContactInListSerializerRead
    pagination_class = x20ResultsPerPage

    def get_queryset(self):
        list_id = self.request.GET.get('list_id')
        list = get_object_or_404(List, id=list_id)

        return ContactInList.objects.filter(list=list)


class CreateContactInList(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceCL]
    serializer_class = ContactInListSerializerWrite
    queryset = ContactInList.objects.all()


class DeleteContactFromList(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObjCF]
    serializer_class = ContactInListSerializerRead
    queryset = ContactInList.objects.all()
    lookup_field = 'pk'