from rest_framework import serializers

from commons.models import Tag
from commons.serializers import WksFieldsSerializer, RestrictedPKRelatedField
from contacts.models import List, Segment, Contact
from contacts.serializers import ListSerializer, SegmentBasicSerializer, ContactSerializer
from emails.models import SenderEmail, Email
from emails.serializers import TagSerializer, SenderEmailSerializer, EmailSerializer
from .models import (
    Campaign, CampaignActivity
)


class CampaignSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    tags = RestrictedPKRelatedField(many=True, read_serializer=TagSerializer, model=Tag)
    sender = RestrictedPKRelatedField(read_serializer=SenderEmailSerializer, model=SenderEmail)
    to_list = RestrictedPKRelatedField(read_serializer=ListSerializer, model=List, required=False)
    to_segment = RestrictedPKRelatedField(read_serializer=SegmentBasicSerializer, model=Segment, required=False)
    email_model = RestrictedPKRelatedField(read_serializer=EmailSerializer, model=Email)

    class Meta:
        model = Campaign
        fields = ('id', 'name', 'description', 'tags', 'status', 'sender', 'to_type', 'to_list', 'to_segment',
                  'email_model', 'subject', 'scheduled_at', 'flatten_sending', 'flatten_start_time', 'flatten_end_time',
                  'created_at', 'created_by', 'workspace', 'total_contacts', 'stats')
        read_only_fields = ['created_at', 'created_by']


class CampaignActivitySerializer(serializers.ModelSerializer, WksFieldsSerializer):
    campaign = RestrictedPKRelatedField(read_serializer=CampaignSerializer, model=Campaign)
    contact = RestrictedPKRelatedField(read_serializer=ContactSerializer, model=Contact)

    class Meta:
        model = CampaignActivity
        fields = ('id', 'campaign', 'contact', 'action_type', 'details', 'created_at', 'workspace')
        read_only_fields = ['created_at', 'created_by']
