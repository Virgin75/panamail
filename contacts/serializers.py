from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from collections import OrderedDict
from .encryption_util import encrypt, decrypt
from rest_framework import serializers
from .utils import retrieve_segment_members
from users.serializers import UserSerializer
from trackerapi.serializers import EventSerializer, PageSerializer
from .models import (
    Contact,
    CustomField,
    CustomFieldOfContact,
    List,
    ContactInList,
    DatabaseToSync,
    DatabaseRule,
    Segment,
    Condition,
)
from .paginations import x20ResultsPerPage


class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = '__all__' 


class CustomFieldOfContactSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = CustomFieldOfContact
        fields = ['custom_field', 'value', 'updated_at']
        read_only_fields = ['custom_field', 'updated_at']

    def get_value(self, obj):        
        if obj.custom_field.type == 'str':
            return obj.value_str
        elif obj.custom_field.type == 'int':
            return obj.value_int
        elif obj.custom_field.type == 'bool':
            return obj.value_bool
        elif obj.custom_field.type == 'date':
            return obj.value_date


class ContactSerializer(serializers.ModelSerializer):
    custom_fields = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'custom_fields', 'events', 'pages']
    
    def get_custom_fields(self, obj):
        c_fields = CustomFieldOfContact.objects.filter(contact=obj.id)
        key_value = CustomFieldOfContactSerializer(c_fields, many=True)
        return key_value.data
    
    def get_events(self, contact):
        events = contact.workspace.events.all()
        key_value = EventSerializer(events, many=True)
        return key_value.data

    def get_pages(self, contact):
        pages = contact.workspace.pages.all()
        key_value = PageSerializer(pages, many=True)
        return key_value.data


class ContactSerializerAPI(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['workspace', 'created_at', 'updated_at']


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['id', 'name', 'description', 'workspace', 'updated_at', 'created_at']
        read_only_fields = ['created_at', 'updated_at']

class ContactInListSerializerRead(serializers.ModelSerializer):
    contact = ContactSerializerAPI(many=False, read_only=True)

    class Meta:
        model = ContactInList
        fields = '__all__'
        read_only_fields = ['added_at', 'updated_at']


class ContactInListSerializerWrite(serializers.ModelSerializer):
    class Meta:
        model = ContactInList
        fields = '__all__'
        read_only_fields = ['added_at', 'updated_at']

class DatabaseToSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseToSync
        fields = '__all__'
        extra_kwargs = {
            'db_password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('db_password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.db_password = encrypt(password)
        instance.save()
        return instance

    def update(self, inst, validated_data):
        password = validated_data.pop('db_password', None)
        for key, value in validated_data.items():
            setattr(inst, key, value)

        if password is not None:
            inst.db_password = encrypt(password)
        inst.save()
        return inst


class DatabaseRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseRule
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SegmentSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Segment
        fields = ['id', 'name', 'count', 'description', 'operator', 'created_at', 'updated_at', 'workspace']
        read_only_fields = ['created_at', 'updated_at', 'count']
    
    def get_count(self, obj):
        return obj.members.all().count()


class SegmentWithMembersSerializer(serializers.ModelSerializer):
    paginated_members = serializers.SerializerMethodField()

    class Meta:
        model = Segment
        fields = ['id', 'name', 'description', 'paginated_members', 'operator', 'created_at', 'updated_at', 'workspace']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_paginated_members(self, obj):
        p = Paginator(obj.members.all(), 20)
        members = p.page(self.context['request'].GET.get('p'))
        print(members.object_list)
        serializer = ContactSerializerAPI(members.object_list, many=True)
        return {
            'total_pages': p.num_pages,
            'has_next_page': members.has_next(), 
            'members': serializer.data
            }
    

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = '__all__'
        read_only_fields = ['segment']