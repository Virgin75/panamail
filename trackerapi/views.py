from django.shortcuts import get_object_or_404

from commons.authentications import TrackerAPIAuthenticator
from commons.utils import is_date
from commons.views import WorkspaceViewset
from contacts.models import Contact, CustomFieldOfContact
from trackerapi.models import Page, Event, TrackerAPIKey
from trackerapi.serializers import PageSerializer, EventSerializer, TrackerAPIKeySerializer, ContactTrackerAPISerializer


class ApiKeyViewSet(WorkspaceViewset):
    """
    View allowing list, create or delete of a Tracker API key within a Workspace.

    - api/api-keys/?workspace_id=xxx (GET): List all API keys in a Workspace
    - api/api-keys/ (POST): Create a new API key in a Workspace
    - api/api-keys/<api_key_pk>/ (DELETE): Delete a specific API key
    """

    base_model_class = TrackerAPIKey
    serializer_class = TrackerAPIKeySerializer
    ordering_fields = ("created_at",)

    def perform_create(self, serializer):
        """Override perform_create() to set the owner of the API key."""
        serializer.save(owner=self.request.user)


class TrackEventsViewSet(WorkspaceViewset):
    """
    View allowing to send a Track Event (related to a Contact).

    >> Usage : add you Tracker API token in the header of your request such as
    {'Authorization': '<your_token>'}

    Endpoint :
     - api/track-events/ (POST): Send a Track Event to the Tracker API.
    """

    base_model_class = Event
    serializer_class = EventSerializer
    authentication_classes = (TrackerAPIAuthenticator,)
    ordering_fields = ("created_at",)
    search_fields = ("name", "attributes")
    filterset_fields = ("name", "triggered_by_contact")

    def perform_create(self, serializer):
        """Override perform_create() to match email address with a Contact."""
        contact_email = serializer.validated_data["triggered_by_contact"]
        contact = get_object_or_404(Contact, email=contact_email)
        if contact.workspace not in self.request.user.workspaces.all():
            self.permission_denied(self.request)
        serializer.save(triggered_by_contact=contact)


class TrackPagesViewSet(WorkspaceViewset):
    """
    View allowing to send a Track Page (related to a Contact).

    >> Usage : add you Tracker API token in the header of your request such as
    {'Authorization': '<your_token>'}

    Endpoint :
     - api/track-pages/ (POST): Send a Track Event to the Tracker API.
    """

    base_model_class = Page
    serializer_class = PageSerializer
    authentication_classes = (TrackerAPIAuthenticator,)
    ordering_fields = ("created_at",)
    search_fields = ("url",)
    filterset_fields = ("url", "viewed_by_contact")

    def perform_create(self, serializer):
        """Override perform_create() to match email address with a Contact."""
        contact_email = serializer.validated_data["viewed_by_contact"]
        contact = get_object_or_404(Contact, email=contact_email)
        if contact.workspace not in self.request.user.workspaces.all():
            self.permission_denied(self.request)
        serializer.save(viewed_by_contact=contact)


class TrackContactViewSet(WorkspaceViewset):
    """
    View allowing to Create or Update a Contact (add to a List or Change Attributes).

    Endpoints:
     - api/track-contact/ (POST): Create a Contact.
     - api/track-contact/ (PATCH): Update a Contact details.
    """

    base_model_class = Contact
    serializer_class = ContactTrackerAPISerializer
    authentication_classes = (TrackerAPIAuthenticator,)
    ordering_fields = ("created_at", "first_name", "last_name", "email")
    search_fields = ("email", "first_name", "last_name")

    def perform_create(self, serializer):
        """Override perform_create() to set custom fields value or add to a List."""
        contact = serializer.save()
        if "lists" in serializer.validated_data:
            lists = serializer.validated_data["lists"]
            contact.lists.set(lists)
        if "fields" in serializer.validated_data:
            fields = serializer.validated_data["fields"]
            existing_fields = contact.custom_fields.all().values_list("name", "id", flat=True)
            # Revoir la cohérence du for loop
            for key, value in fields.items():
                for existing_field in existing_fields:
                    if key == existing_field["name"]:
                        value_type_filters = {
                            "value_str": value if isinstance(value, str) else None,
                            "value_int": value if isinstance(value, int) else None,
                            "value_bool": value if isinstance(value, bool) else None,
                            "value_date": value if is_date(value) else None,
                        }
                        CustomFieldOfContact.objects.create(
                            contact=contact,
                            custom_field_id=existing_field["id"],
                            created_by=self.request.user,
                            workspace=contact.workspace,
                            **value_type_filters
                        )
                    else:
                        # Custom Field does not exist. Create it.
                        pass
