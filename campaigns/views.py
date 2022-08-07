from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from campaigns.permissions import CheckFKOwnership
from emails.permissions import (
    IsMemberOfWorkspace,
    IsMemberOfWorkspaceObj
)
from users.models import Workspace
from .models import Campaign
from .serializers import CampaignSerializer
from .tasks import send_campaign

class ListCreateCampaign(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfWorkspace, CheckFKOwnership]
    serializer_class = CampaignSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        return Campaign.objects.filter(workspace=workspace)


class RetrieveUpdateDestroyCampaign(generics.RetrieveUpdateDestroyAPIView):
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOfWorkspaceObj, CheckFKOwnership]
    serializer_class = CampaignSerializer
    lookup_field = 'pk'


class SendCampaign(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        user = request.user
        campaign = get_object_or_404(Campaign, id=pk)

        #Check if user belongs to the workspace of the campaign
        workspace = get_object_or_404(Workspace, id=campaign.workspace.id)
        membership = workspace.members.filter(id=user.id)
        if not membership.exists():
            return Response({'error':'You can only send your own campaigns.'})
        
        # Check if important fields are missing before sending
        if campaign.sender is None:
            return Response({'error':'Please select a Sender email.'})
        if campaign.email_model is None:
            return Response({'error':'Please create an email.'})
        if campaign.to_type is None:
            return Response({'error':'Please choose type of recipients (segment or list).'})
        if campaign.to_list is None and campaign.to_segment is None:
            return Response({'error':'Please select a list or segment'})

        # Create the async task to send the campaign at the right time
        if campaign.scheduled_at is None:
            send_campaign.delay(campaign.id)
            campaign.status = 'SENDING'
            campaign.save()
        else:
            send_date = campaign.scheduled_at
            send_campaign.apply_async((campaign.id,), eta=send_date)
            campaign.status = 'SCHEDULED'
            campaign.save()

        return Response({'status':'Your camapign was scheduled successfully.'})