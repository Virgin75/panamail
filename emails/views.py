from commons.views import WorkspaceViewset
from emails import serializers, models


class EmailViewset(WorkspaceViewset):
    """Perform all CRUD actions on Emails objects."""

    base_model_class = models.Email
    serializer_class = serializers.EmailSerializer
    prefetch_related_fields = ("tags", "edit_history")
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")
    filterset_fields = ("type", "tags")


class SenderDomainViewset(WorkspaceViewset):
    """Perform all CRUD actions on Sender Domains objects."""

    base_model_class = models.SenderDomain
    serializer_class = serializers.SenderDomainSerializer
    search_fields = ("name",)
    ordering_fields = ("name", "status")
    filterset_fields = ("status",)


class SenderEmailViewset(WorkspaceViewset):
    """Perform all CRUD actions on Sender Email objects."""

    base_model_class = models.SenderEmail
    serializer_class = serializers.SenderEmailSerializer
    search_fields = ("name", "email_address")
    ordering_fields = ("name", "status", "email_address", "reply_to")
    filterset_fields = ("status",)


"""
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
            print(response)
            if response['DkimAttributes']['Status'] == 'SUCCESS':
                domain.status = 'VERIFIED'
                domain.save()
            
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
        #Set custom MAIL FROM in AWS
        resp = aws_client.put_email_identity_mail_from_attributes(
            EmailIdentity=serializer.validated_data['domain_name'],
            MailFromDomain=f"emails.{serializer.validated_data['domain_name']}",
            BehaviorOnMxFailure='USE_DEFAULT_VALUE'
        )       

        #Create a periodic task to check everyday if the CNAME is present on DNS record
        schedule = IntervalSchedule(every=1, period=IntervalSchedule.DAYS)
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
        return Response({'create_domain_identity': response, 'create_mail_from': resp}, status=status.HTTP_201_CREATED, headers=headers)
"""
