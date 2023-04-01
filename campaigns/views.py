from commons.views import WorkspaceViewset
from .models import Campaign
from .serializers import CampaignSerializer


class CampaignViewSet(WorkspaceViewset):
    """
       Perform all CRUD actions on Campaign objects.

       - api/campaigns/?workspace_id=xxx (GET): List all Campaigns in a Workspace
       - api/campaigns/ (POST): Create a new Campaign in a Workspace
       - api/campaigns/<pk>/ (GET, PATCH, DELETE): Retrieve, Update or delete a specific Campaign
       """

    base_model_class = Campaign
    serializer_class = CampaignSerializer
    prefetch_related_fields = ("tags", "stats")
    select_related_fields = ("sender", "to_list", "to_segment", "email_model")
    search_fields = ("name", "description")
    ordering_fields = ("name", "created_at", "scheduled_at", "status")
    filterset_fields = ("status", "tags")
