from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from commons.views import WorkspaceViewset
from contacts import models, serializers, tasks
from contacts.models import List, ContactInList


class ContactViewSet(WorkspaceViewset):
    """
    Perform all CRUD actions on Contacts objects.

     - /api/contacts/?workspace_id=XXX (GET): List all contacts of a workspace.
     - /api/contacts/ (POST): Create a new contact.
     - /api/contacts/<pk>/ (GET, PATCH, DELETE): Retrieve, update or delete a specific contact.

     Custom actions:
     - /api/contacts/<pk>/set-custom-field-value/ (POST): Set custom field value of a Contact.
     - /api/contacts/<pk>/unsub_from_list/<list_pk> (POST): Unsub a contact from a specific list.
     - /api/contacts/<pk>/lists/ (GET): Get all lists a Contact belongs to.
     TODO:
    - /api/contacts/<pk>/segments/ (POST)
    - /api/contacts/<pk>/events/ (POST)
    - /api/contacts/<pk>/pages/ (POST)
    """

    base_model_class = models.Contact
    serializer_class = serializers.ContactSerializer
    prefetch_related_fields = ("edit_history",)
    search_fields = ("email", "first_name", "last_name")
    ordering_fields = ("created_at",)

    @action(detail=True, methods=['post'], serializer_class=serializers.CustomFieldOfContactSerializer)
    def set_custom_field_value(self, request, pk):
        """Set custom field value for a specific Contact."""
        contact = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        custom_field_value = serializer.save(contact=contact)
        contact.edit_history.add(edited_by=request.user)
        return Response(status=status.HTTP_201_CREATED, data=self.get_serializer(custom_field_value).data)

    @action(detail=True, methods=['get'], serializer_class=serializers.ListSerializer)
    def lists(self, request, pk):
        """Get all lists a Contact belongs to."""
        contact = self.get_object()
        lists = List.objects.filter(contacts=contact)
        return Response(status=status.HTTP_200_OK, data=self.get_serializer(lists).data)

    @action(detail=True, methods=['post'])
    def unsub_from_list(self, request, pk, list_pk):
        """Mark a contact as unsubscribed from a specific list."""
        list_obj = List.objects.get(pk=list_pk)
        list_obj.unsubscribed_contacts.add(self.get_object())
        return Response(status=status.HTTP_200_OK, data={"status": "Contact unsubscribed from list."})


class CustomFieldViewSet(WorkspaceViewset):
    """
    Perform all CRUD actions on CustomField objects.

     - /api/custom-fields/?workspace_id=XXX (GET): List all custom fields of a workspace.
     - /api/custom-fields/ (POST): Create a new custom field.
     - /api/custom-fields/<pk>/ (GET, PATCH, DELETE): Retrieve, update or delete a specific custom field.
    """

    base_model_class = models.CustomField
    serializer_class = serializers.CustomFieldSerializer
    search_fields = ("name",)
    ordering_fields = ("created_at",)
    filterset_fields = ("type",)


class ListViewSet(WorkspaceViewset, NestedViewSetMixin):
    """
    Perform all CRUD actions on List objects.

     - /api/lists/?workspace_id=XXX (GET): List all lists of a workspace.
     - /api/lists/ (POST): Create a new list.
     - /api/lists/<pk>/ (GET, PATCH, DELETE): Retrieve, update or delete a specific list.

     Custom actions:
     - /api/lists/<pk>/unsubscribed_contacts/ (GET): List of all unsubscribed contacts of a list.
     - /api/lists/<pk>/double-optin/<validation-token> (GET): Public view for user to validate their subscription.
    """

    base_model_class = models.List
    serializer_class = serializers.ListSerializer
    search_fields = ("name",)
    ordering_fields = ("created_at", "name", "contacts_count")
    filterset_fields = ("tags",)

    @action(detail=True, methods=['get'], serializer_class=serializers.ContactSerializer)
    def unsubscribed_contacts(self, request, pk):
        """List of all unsubscribed contacts of a list."""
        list_obj = self.get_object()
        contacts = list_obj.unsubscribed_contacts.all()
        return Response(status=status.HTTP_200_OK, data=self.get_serializer(contacts).data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], authentication_classes=[])
    def double_optin(self, request, pk, validation_token):
        """Public view for user to validate his subscription when the list has double opt-in activated."""
        list_obj = self.get_object()
        contact_in_list = ContactInList.objects.filter(double_optin_token=validation_token)
        contact_in_list.double_optin_validate_date = timezone.now()
        contact_in_list.save()
        return Response(
            status=status.HTTP_200_OK,
            data={
                "status": f"Subscription to the list {list_obj.name} confirmed."
            }
        )


class NestedContactInListViewSet(WorkspaceViewset, NestedViewSetMixin):
    """
    Nested List Viewset. Perform all CRUD actions on ContactInList objects.

     - /api/lists/<list_id>/contacts/?workspace_id=XXX (GET): List all contacts of a list.
     - /api/lists/<list_id>/contacts/ (POST): Add a contact to a list.
     - /api/lists/<list_id>/contacts/<pk>/ (DELETE): Remove a contact from a list.

     Custom actions:
     - /api/lists/<list_id>/contacts/csv-import/ (POST): Import Contacts into a List from .csv file.
    """

    base_model_class = models.ContactInList
    queryset = models.ContactInList.objects.all()
    serializer_class = serializers.ContactInListSerializer
    select_related_fields = ("contact", "list")

    parent_obj_type = "list_id"
    parent_obj_url_lookup = "parent_lookup_lists"
    diff_obj_in_post_request = "contact"  # We send contact_id in post request rather than contact_in_list_id

    search_fields = ("contact__email",)
    ordering_fields = ("created_at", "contact__email")
    filterset_fields = ("list",)

    @action(detail=False, methods=['post'], serializer_class=serializers.ContactCSVImportSerializer)
    def csv_import(self, request, pk):
        """Import Contacts into a List from .csv file."""
        # TODO: à tester/corriger
        list_obj = List.objects.get(pk=self.kwargs["parent_lookup_lists"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(list=list_obj)
        tasks.do_csv_import.delay(serializer.instance.id)
        return Response(status=status.HTTP_200_OK, data={"status": "Contacts imported."})


class SegmentViewset(WorkspaceViewset, NestedViewSetMixin):
    """
    Perform all CRUD actions on Segment objects.

     - /api/segments/?workspace_id=XXX (GET): List all segments of a workspace.
     - /api/segments/ (POST): Create a new segment.
     - /api/segments/<pk>/ (GET, PATCH, DELETE): Retrieve, update or delete a specific segment.
        > The GET endpoint retrieve the Segment groups and their associated Conditions.

     Custom actions:
     - /api/segments/<pk>/contacts/ (GET): List all contacts matching with a segment conditions.
    """

    base_model_class = models.Segment
    serializer_class = serializers.SegmentBasicSerializer
    search_fields = ("name",)
    ordering_fields = ("created_at", "name", "contacts_count")
    filterset_fields = ("tags",)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific segment with its groups and conditions."""
        segment = self.get_object()
        serializer = serializers.SegmentReadOnlySerializer(segment)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], serializer_class=serializers.ContactSerializer)
    def contacts(self, request, pk):
        """List of all contacts matching with a segment conditions."""
        segment = self.get_object()
        contacts = segment.members.all()
        return Response(status=status.HTTP_200_OK, data=self.get_serializer(contacts).data)


class NestedGroupConditionsViewSet(WorkspaceViewset, NestedViewSetMixin):
    """
    Nested Segment Viewset. Perform all CRUD actions on GroupConditions objects.
    A GroupConditions object is a group of conditions that are linked to a Segment.

     - /api/segments/<segment_id>/groups/ (POST): Create a new group for a segment.
     - /api/segments/<segment_id>/groups/<pk>/ (GET, PATCH, DELETE): Retrieve, update or delete a specific group.

     Custom actions:
     - /api/segments/<segment_id>/groups/<pk>/conditions/ (POST): Create a Condition within a Group.
     - /api/segments/<segment_id>/groups/<pk>/conditions/<condition_pk> (PATCH, DELETE): Edit or Delete a Condition.
    """

    base_model_class = models.GroupOfConditions
    serializer_class = serializers.GroupOfConditionsSerializer
    queryset = models.GroupOfConditions.objects.all()

    search_fields = ("name",)
    ordering_fields = ("created_at", "name", "contacts_count")
    filterset_fields = ("tags",)

    parent_obj_type = "segment_id"
    parent_obj_url_lookup = "parent_lookup_segments"

    @action(detail=True, methods=['patch', 'delete'], serializer_class=serializers.ConditionSerializer)
    def conditions(self, request, pk, condition_pk):
        """Edit or Delete a condition within a group."""
        group = self.get_object()
        condition = get_object_or_404(models.Condition, pk=condition_pk, group=group)
        serializer = serializers.ConditionSerializer(condition, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @conditions.mapping.post
    def add_condition(self, request, pk):
        """Create a new condition within a group."""
        group = self.get_object()
        serializer = serializers.ConditionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(group=group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


"""
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
    lookup_field = 'pk'"""
