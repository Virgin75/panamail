from django.db.models import Prefetch

from automation.models import AutomationCampaign, Step
from automation.serializers import MinimalAutomationCampaignSerializer, RetrieveAutomationCampaignSerializer
from commons.views import WorkspaceViewset


class AutomationCampaignViewSet(WorkspaceViewset):
    """
       Perform all CRUD actions on AutomationCampaign objects.

       - api/automations/?workspace_id=xxx (GET): List all automation campaigns in a Workspace
       - api/automations/ (POST): Create a new automation campaign in a Workspace
       - api/automations/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific automation campaign
       """

    base_model_class = AutomationCampaign
    search_fields = ("name", "description")
    ordering_fields = ("name", "created_at", "total_contacts_now", "total_contacts_past")
    filterset_fields = ("status", "trigger_type", "is_repeated")

    def get_serializer_class(self):
        """Return specific serializer depending on Viewset action type."""
        if self.action in ("list", "create", "update", "delete"):
            return MinimalAutomationCampaignSerializer
        if self.action == "retrieve":
            return RetrieveAutomationCampaignSerializer

    def get_select_related_fields(self):
        """Return additional select_related_fields depending on Viewset action type."""
        if self.action == "retrieve":
            return (
                "event_trigger",
                "page_trigger",
                "list_trigger",
                "segment_trigger",
                "time_trigger",
                "email_trigger",
                "workspace"
            )
        return ('workspace',)

    def get_prefetch_related_fields(self):
        """Return additional prefetch_related_fields depending on Viewset action type."""
        if self.action == "retrieve":
            return (
                Prefetch(
                    "steps",
                    queryset=Step.objects.all().select_related("wait_step", "send_email_step",
                                                               "send_email_step__email")),
            )
        return []
