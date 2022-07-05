from rest_framework import serializers
from .models import Event, EventAttribute, TrackerAPIKey, Page

class TrackerAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerAPIKey
        fields = '__all__' 
        read_only_fields = ['token']

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__' 
        read_only_fields = ['viewed_at', 'workspace', 'viewed_by_contact']