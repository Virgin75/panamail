
"""
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


class CreateContact(generics.CreateAPIView):
    permission_classes = [IsTokenValid]
    serializer_class = ContactSerializerAPI
    queryset = Contact.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key = TrackerAPIKey.objects.get(
            token=self.request.data['api_token']
        )
        workspace = api_key.workspace
        contact = self.perform_create(serializer, workspace)

        #Add Contact to list
        list = get_object_or_404(List, id=request.data['list'])
        membership = ContactInList.objects.filter(
            contact=contact,
            list=list
        )
        if not membership.exists():
            ContactInList.objects.create(
                contact=contact,
                list=list
            )
            
        #set custom fields of contact
        json_attr = json.loads(str(request.data['attributes']))
        for key, value in json_attr.items():
            cf = None
            if re.match(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", str(value)):
                cf = CustomFieldOfContact(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact,
                    value_date=value
                )
            elif isinstance(value, bool):
                cf = CustomFieldOfContact(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact,
                    value_bool=value
                )
            elif isinstance(value, int):
                cf = CustomFieldOfContact(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact,
                    value_int=value
                )
            else:
                cf = CustomFieldOfContact(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact,
                    value_str=value
                )
            cf.save()
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, workspace):
        return serializer.save(workspace=workspace)


class UpdateDeleteContact(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsTokenValid, IsTrackedContactInWorkspace]
    serializer_class = ContactSerializerAPI
    queryset = Contact.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        api_key = TrackerAPIKey.objects.get(token=self.request.data['api_token'])
        workspace = api_key.workspace
        instance = get_object_or_404(Contact, email=request.data['contact_email'], workspace=workspace)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        contact = self.perform_update(serializer)
        
        #Add Contact to list
        list = get_object_or_404(List, id=request.data['list'])
        membership = ContactInList.objects.filter(
            contact=contact,
            list=list
        )
        if not membership.exists():
            ContactInList.objects.create(
                contact=contact,
                list=list
            )

        #set custom fields of contact
        json_attr = json.loads(str(request.data['attributes']))
        for key, value in json_attr.items():
            cf = None
            if re.match(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", str(value)):
                cf, created = CustomFieldOfContact.objects.get_or_create(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact
                )
                cf.value_date = value
            elif isinstance(value, bool):
                cf, created = CustomFieldOfContact.objects.get_or_create(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact
                )
                cf.value_bool = value
            elif isinstance(value, int):
                cf, created = CustomFieldOfContact.objects.get_or_create(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact
                )
                cf.value_int = value
            else:
                cf, created = CustomFieldOfContact.objects.get_or_create(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact
                )
                cf.value_str = value
            cf.save()
        return Response(serializer.data)

    def perform_update(self, serializer):
        return serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        api_key = TrackerAPIKey.objects.get(token=self.request.data['api_token'])
        workspace = api_key.workspace
        instance = get_object_or_404(Contact, email=request.data['contact_email'], workspace=workspace)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateOrUpdateContact(APIView):
    permission_classes = [IsTokenValid]

    def post(self, request, format=None):
        data = request.data
        api_key = TrackerAPIKey.objects.get(token=data['api_token'])
        workspace = api_key.workspace
        serialized_contact = ContactSerializerAPI(Contact, data=data)
        serialized_contact.is_valid(raise_exception=True)
        contact, is_created = Contact.objects.get_or_create(
            email=serialized_contact.validated_data['email'],
            workspace=workspace
        )

        #Add Contact to list
        list = get_object_or_404(List, id=data['list'])
        membership = ContactInList.objects.filter(
            contact=contact,
            list=list
        )
        if not membership.exists():
            ContactInList.objects.create(
                contact=contact,
                list=list
            )

        #set custom fields of contact
        json_attr = json.loads(str(data['attributes']))
        for key, value in json_attr.items():
            cf = None
            if re.match(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", str(value)):
                cf, created = CustomFieldOfContact.objects.get_or_create(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact
                )
                cf.value_date = value
            elif isinstance(value, bool):
                cf, created = CustomFieldOfContact.objects.get_or_create(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact
                )
                cf.value_bool = value
            elif isinstance(value, int):
                cf, created = CustomFieldOfContact.objects.get_or_create(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact
                )
                cf.value_int = value
            else:
                cf, created = CustomFieldOfContact.objects.get_or_create(
                    custom_field=get_object_or_404(CustomField, name=key, workspace=workspace),
                    contact=contact
                )
                cf.value_str = value
            cf.save()
        if is_created:
            return Response({'status': 'Contact was created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Contact was updated successfully'}, status=status.HTTP_200_OK)"""
