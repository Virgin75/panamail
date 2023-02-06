from rest_framework import serializers

from commons.serializers import RestrictedPKRelatedField
from contacts.models import Contact, List
from contacts.serializers import ListSerializer
from trackerapi.models import Event, TrackerAPIKey, Page


class TrackerAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerAPIKey
        fields = '__all__'
        read_only_fields = ('token', 'created_at', 'created_by', 'owner')


class PageSerializer(serializers.ModelSerializer):
    viewed_by_contact = serializers.EmailField(source='viewed_by_contact.email')

    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ['created_at']


class EventSerializer(serializers.ModelSerializer):
    triggered_by_contact = serializers.EmailField(source='triggered_by_contact.email')

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['created_at']


class ContactTrackerAPISerializer(serializers.ModelSerializer):
    lists = RestrictedPKRelatedField(many=True, model=List, read_serializer=ListSerializer, required=False)
    fields = serializers.JSONField(required=False)

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['created_at']
