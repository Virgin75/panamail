from django.contrib.auth.hashers import make_password
from collections import OrderedDict
from .encryption_util import encrypt, decrypt
from rest_framework import serializers
from .utils import retrieve_segment_members
from users.serializers import UserSerializer
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
        print(type(obj.value_str))
        if obj.value_str is not None or obj.value_str != '':
            return obj.value_str
        elif obj.value_int is not None:
            return obj.value_int
        elif obj.value_bool is not None:
            return obj.value_bool
        elif obj.value_date is not None:
            return obj.value_date


class ContactSerializer(serializers.ModelSerializer):
    custom_fields = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_custom_fields(self, obj):
        c_fields = CustomFieldOfContact.objects.filter(contact=obj.id)
        key_value = CustomFieldOfContactSerializer(c_fields, many=True)
        return key_value.data


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = '__all__' 
        read_only_fields = ['created_at', 'updated_at']

class ContactInListSerializerRead(serializers.ModelSerializer):
    contact = ContactSerializer(many=False, read_only=True)

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
    class Meta:
        model = Segment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SegmentWithMembersSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Segment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_members(self, obj):
        users = retrieve_segment_members(obj.id)
        key_value = UserSerializer(users, many=True)
        return key_value.data


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = '__all__'
        read_only_fields = ['segment']