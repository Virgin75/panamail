import csv
import json
import random
import base64
from django import db

from django_celery_beat.models import PeriodicTask, IntervalSchedule
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
    SegmentSerializer,
    SegmentWithMembersSerializer,
    ConditionSerializer,
    ContactInListSerializerRead,
    ContactInListSerializerWrite,
    DatabaseToSyncSerializer,
    DatabaseRuleSerializer
)
from users.models import Workspace, MemberOfWorkspace
from .models import (
    Contact,
    CustomField,
    CustomFieldOfContact,
    List,
    ContactInList,
    DatabaseToSync,
    DatabaseRule,
    Segment,
    Condition,
)
from .paginations import x20ResultsPerPage
from emails.permissions import (
    IsMemberOfWorkspace,
    IsMemberOfWorkspaceObj
)
from .permissions import (
    IsMemberOfWorkspaceCF, 
    IsMemberOfWorkspaceCL,
    IsMemberOfWorkspaceObjCF,
    IsMemberOfWorkspaceObjDB,
    IsMemberOfWorkspaceObjC,
    IsMemberOfWorkspaceSC,
    IsMemberOfWorkspaceDB,
    HasListAccess,
)
from .tasks import do_csv_import


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
        for field_to_update, value in request.data.items():
            #If custom field of contact exists, update it
            try:
                cf = CustomFieldOfContact.objects.select_related('custom_field').get(
                    contact=contact_pk,
                    custom_field=int(field_to_update)
                )
                if cf.custom_field.type == 'str':
                    cf.value_str = value
                elif cf.custom_field.type == 'int':
                    cf.value_int = value
                elif cf.custom_field.type == 'bool':
                    cf.value_bool = value
                elif cf.custom_field.type == 'date':
                    cf.value_date = value
                
                cf.save()
                contact = get_object_or_404(Contact, id=contact_pk)
                contact.save()
            #Else, create it
            except CustomFieldOfContact.DoesNotExist:
                field = get_object_or_404(CustomField, id=int(field_to_update))
                contact = get_object_or_404(Contact, id=contact_pk)

                if field.type == 'str':
                    cf = CustomFieldOfContact(
                        contact=contact,
                        custom_field=field,
                        value_str=value
                    )
                elif field.type == 'int':
                    cf = CustomFieldOfContact(
                        contact=contact,
                        custom_field=field,
                        value_int=value
                    )
                elif field.type == 'bool':
                    cf = CustomFieldOfContact(
                        contact=contact,
                        custom_field=field,
                        value_bool=value
                    )
                elif field.type == 'date':
                    cf = CustomFieldOfContact(
                        contact=contact,
                        custom_field=field,
                        value_date=value
                    )

                cf.save()
                contact.save()

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


class BulkContactCSVImport(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace, HasListAccess]

    def post(self, request, format=None):
        
        file = request.FILES['csv_file'].read()
        b64_file = base64.b64encode(file).decode('utf-8')
        
        #Celery task to do the csv import
        do_csv_import.delay(
            b64_file,
            list(json.loads(request.POST['mapping']).values()),
            request.POST['workspace'],
            request.POST['update_existing_contacts'],
            request.POST['list'],
            request.POST['unsub_campaign']
            )

        return Response({'status': 'All contacts are being uploaded.'})


class ListCreateDbToSync(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = DatabaseToSyncSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return DatabaseToSync.objects.filter(workspace=workspace)


class RetrieveUpdateDestroyDbToSync(generics.RetrieveUpdateDestroyAPIView):
    queryset = DatabaseToSync.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = DatabaseToSyncSerializer
    lookup_field = 'pk'


class ListCreateDbRule(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceDB]
    serializer_class = DatabaseRuleSerializer

    def get_queryset(self):
        db_id = self.request.GET.get('db_id')
        db = get_object_or_404(DatabaseToSync, id=db_id)

        return DatabaseRule.objects.filter(db=db)
    
    def perform_create(self, serializer, task):
        db_rule = serializer.save(beat_task=task)
        task.args = json.dumps([serializer.data['db'], db_rule.id])
        task.enabled = True
        task.save()


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #Create the celeby beat task
        unit = request.data['sync_unit']
        period_mapping = {
            'SECONDS': IntervalSchedule.SECONDS,
            'MINUTES': IntervalSchedule.MINUTES,
            'HOURS': IntervalSchedule.HOURS,
            'DAYS': IntervalSchedule.DAYS,
        }
        schedule = IntervalSchedule(every=unit, period=period_mapping[request.data['sync_period']])
        schedule.save()
        task = PeriodicTask(
            interval=schedule, 
            name=f'DB sync task by {request.user} - {random.randint(0,9999)}', 
            task='sync_contacts_from_db',
            enabled=False
        )
        task.save()
        self.perform_create(serializer, task)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RetrieveUpdateDestroyDbRule(generics.RetrieveUpdateDestroyAPIView):
    queryset = DatabaseRule.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObjDB]
    serializer_class = DatabaseRuleSerializer
    lookup_field = 'pk'

class ListCreateSegment(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace]
    serializer_class = SegmentSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return Segment.objects.filter(workspace=workspace)

class RetrieveUpdateDestroySegment(generics.RetrieveUpdateDestroyAPIView):
    queryset = Segment.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj]
    serializer_class = SegmentWithMembersSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = SegmentSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class ListCreateCondition(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceSC]
    serializer_class = ConditionSerializer

    def perform_create(self, serializer):
        segment = Segment.objects.get(id=self.kwargs['segment_pk'])
        serializer.save(segment=segment)

    def get_queryset(self):
        segment = get_object_or_404(Segment, id=self.kwargs['segment_pk'])
        return Condition.objects.filter(segment=segment)


class RetrieveUpdateDestroyCondition(generics.RetrieveUpdateDestroyAPIView):
    queryset = Condition.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObjC]
    serializer_class = ConditionSerializer
    lookup_field = 'pk'
