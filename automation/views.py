from django.db.models import Prefetch

from automation.models import AutomationCampaign, Step, TriggerEvent, TriggerPage, TriggerList, TriggerSegment, \
    TriggerTime, TriggerEmail, StepSendEmail, StepWait
from automation.serializers import MinimalAutomationCampaignSerializer, RetrieveAutomationCampaignSerializer, \
    TriggerEventSerializer, TriggerPageSerializer, TriggerListSerializer, TriggerSegmentSerializer, \
    TriggerTimeSerializer, StepSerializer, TriggerEmailSerializer, StepSendEmailSerializer, StepWaitSerializer
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
        if self.action in ("list", "create", "partial_update", "update", "delete"):
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


class TriggerEventViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on TriggerEvent objects.

    - api/automation-event-triggers/ (POST): Create a new event trigger in an Automation Campaign
    - api/automation-event-triggers/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific event trigger
    """

    base_model_class = TriggerEvent
    serializer_class = TriggerEventSerializer


class TriggerPageViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on TriggerPage objects.

    - api/automation-page-triggers/ (POST): Create a new page trigger in an Automation Campaign
    - api/automation-page-triggers/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific page trigger
    """

    base_model_class = TriggerPage
    serializer_class = TriggerPageSerializer


class TriggerListViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on TriggerList objects.

    - api/automation-list-triggers/ (POST): Create a new list trigger in an Automation Campaign
    - api/automation-list-triggers/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific list trigger
    """

    base_model_class = TriggerList
    serializer_class = TriggerListSerializer


class TriggerSegmentViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on TriggerSegment objects.

    - api/automation-segment-triggers/ (POST): Create a new segment trigger in an Automation Campaign
    - api/automation-segment-triggers/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific segment trigger
    """

    base_model_class = TriggerSegment
    serializer_class = TriggerSegmentSerializer


class TriggerTimeViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on TriggerTime objects.

    - api/automation-time-triggers/ (POST): Create a new time trigger in an Automation Campaign
    - api/automation-time-triggers/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific time trigger
    """

    base_model_class = TriggerTime
    serializer_class = TriggerTimeSerializer


class TriggerEmailViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on TriggerEmail objects.

    - api/automation-email-triggers/ (POST): Create a new email trigger in an Automation Campaign
    - api/automation-email-triggers/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific email trigger
    """

    base_model_class = TriggerEmail
    serializer_class = TriggerEmailSerializer


class StepViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on Step objects.

    - api/automation-steps/ (POST): Create a new step in a Workspace
    - api/automation-steps/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific step
    """

    base_model_class = Step
    serializer_class = StepSerializer


class StepSendEmailViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on Send-email Step objects.

    - api/automation-sendemail-steps/ (POST): Create a new Send email step in Automation Campaign
    - api/automation-sendemail-steps/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific Send email step
    """

    base_model_class = StepSendEmail
    serializer_class = StepSendEmailSerializer


class StepWaitViewset(WorkspaceViewset):
    """
    Perform all CRUD actions on Wait Step objects.

    - api/automation-wait-steps/ (POST): Create a new Wait step in Automation Campaign
    - api/automation-wait-steps/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific Wait step
    """

    base_model_class = StepWait
    serializer_class = StepWaitSerializer
