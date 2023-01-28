"""from rest_framework import serializers
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

class EventAttributeSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = EventAttribute
        fields = ['key', 'value', 'type']
    
    def get_value(self, obj):    
        if obj.type == 'str':
            return obj.value_str
        elif obj.type == 'int':
            return obj.value_int
        elif obj.type == 'bool':
            return obj.value_bool
        elif obj.type == 'date':
            return obj.value_date

class EventSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['name', 'triggered_at', 'triggered_by_contact', 'attributes', 'workspace']
        read_only_fields = ['triggered_at', 'workspace', 'triggered_by_contact', 'attributes']
    
    def get_attributes(self, obj):
        attributes = EventAttributeSerializer(obj.attributes.all(), many=True)
        return attributes.data"""
