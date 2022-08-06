import random
import json
import boto3
from botocore.config import Config

from django_celery_beat.models import PeriodicTask, IntervalSchedule

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings


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
        domains = SenderDomain.objects.filter(workspace=workspace)
        my_config = Config(
            region_name = settings.AWS_REGION_NAME
        )
        aws_client = boto3.client(
            'sesv2',
            config=my_config,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        for domain in domains:
            response = aws_client.get_email_identity(
                EmailIdentity=domain.domain_name
            )
            if response['DkimAttributes']['Status'] == 'SUCCESS':
                domain.status = 'VERIFIED'
            
        return domains
    
    def perform_create(self, serializer, task):
        serializer.save()
        task.args = json.dumps([serializer.validated_data['domain_name']])
        task.enabled = True
        task.save()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        my_config = Config(
            region_name = settings.AWS_REGION_NAME
        )
        aws_client = boto3.client(
            'sesv2',
            config=my_config,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        response = aws_client.create_email_identity(
            EmailIdentity=serializer.validated_data['domain_name'],
            Tags=[
                {
                    'Key': 'workspace',
                    'Value': str(request.data['workspace'])
                },
            ],
            DkimSigningAttributes={
                'NextSigningKeyLength': 'RSA_2048_BIT'
            }
        )
        #Create a periodic task to check everyday if the CNAME is present on DNS record
        schedule = IntervalSchedule(every=12, period=IntervalSchedule.SECONDS)
        schedule.save()
        task = PeriodicTask(
            interval=schedule, 
            name=f'Check domain status for: {serializer.validated_data["domain_name"]} - {random.randint(0,9999)}', 
            task='check_domain_status',
            enabled=False
        )
        task.save()

        self.perform_create(serializer, task)
        headers = self.get_success_headers(serializer.data)
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)


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