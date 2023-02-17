from rest_framework import serializers

from commons.models import Tag
from commons.serializers import WksFieldsSerializer, RestrictedPKRelatedField
from emails.serializers import TagSerializer
from users.models import Workspace
from users.serializers import WorkspaceSerializer
from .models import (
    Contact,
    CustomField,
    CustomFieldOfContact,
    List,
    ContactInList, Segment, GroupOfConditions, Condition, CSVImportHistory,
)


class ContactSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class CustomFieldSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    class Meta:
        model = CustomField
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class CustomFieldOfContactSerializer(serializers.ModelSerializer):
    custom_field = RestrictedPKRelatedField(many=True, read_serializer=CustomFieldSerializer, model=CustomField)

    class Meta:
        model = CustomFieldOfContact
        fields = ['custom_field', 'value_str', 'value_int', 'value_bool', 'value_date']

    def get_value(self, obj):        
        if obj.custom_field.type == 'str':
            return obj.value_str
        elif obj.custom_field.type == 'int':
            return obj.value_int
        elif obj.custom_field.type == 'bool':
            return obj.value_bool
        elif obj.custom_field.type == 'date':
            return obj.value_date


class ListSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    tags = RestrictedPKRelatedField(many=True, read_serializer=TagSerializer, model=Tag)
    contacts_count = serializers.SerializerMethodField(read_only=True)

    def get_contacts_count(self, obj) -> int:  # noqa
        return obj.contact_count

    class Meta:
        model = List
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class ContactInListSerializer(serializers.ModelSerializer):
    contact = RestrictedPKRelatedField(many=False, read_serializer=ContactSerializer, model=Contact)
    list = ListSerializer(many=False, read_only=True)

    class Meta:
        model = ContactInList
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class SegmentBasicSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    tags = RestrictedPKRelatedField(many=True, read_serializer=TagSerializer, model=Tag)
    contacts_count = serializers.SerializerMethodField(read_only=True)

    def get_contacts_count(self, obj) -> int:  # noqa
        return obj.contact_count

    class Meta:
        model = Segment
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class ConditionReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = '__all__'


class GroupOfConditionsSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    segment = RestrictedPKRelatedField(many=False, read_serializer=SegmentBasicSerializer, model=Segment)

    class Meta:
        model = GroupOfConditions
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class ConditionSerializer(serializers.ModelSerializer):
    CustomField = RestrictedPKRelatedField(many=False, read_serializer=CustomFieldSerializer, model=CustomField)

    class Meta:
        model = Condition
        fields = '__all__'
        read_only_fields = ['created_at']


class SegmentReadOnlySerializer(serializers.ModelSerializer, WksFieldsSerializer):
    tags = RestrictedPKRelatedField(many=True, read_serializer=TagSerializer, model=Tag)
    contacts_count = serializers.SerializerMethodField(read_only=True)
    conditions = serializers.SerializerMethodField(read_only=True)

    def get_contacts_count(self, obj) -> int:  # noqa
        return obj.contact_count

    def get_conditions(self, obj) -> list:  # noqa
        res = []
        groups = GroupOfConditions.objects.filter(segment=obj)
        for group in groups:
            group_data = {"id": group.id, "operator": group.operator, "conditions": []}
            res.append(group_data)
            conditions = Condition.objects.filter(group=group)
            for condition in conditions:
                condition_data = ConditionReadOnlySerializer(condition).data
                group_data["conditions"].append(condition_data)
        return res

    class Meta:
        model = Segment
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class ContactCSVImportSerializer(serializers.ModelSerializer):  # noqa
    file = serializers.FileField(required=True)
    update_existing = serializers.BooleanField(default=False)
    mass_unsubscribe = serializers.BooleanField(default=False)
    list = RestrictedPKRelatedField(many=False, read_serializer=ListSerializer, model=List)
    workspace = RestrictedPKRelatedField(many=False, read_serializer=WorkspaceSerializer, model=Workspace)
    # Mapping field should look like this for a 6-column CSV file: (custom fields are referenced with their id)
    # ["email", "first_name", "last_name", "12", "7", "9"]
    mapping = serializers.ListField(child=serializers.CharField(), required=True)

    class Meta:
        model = CSVImportHistory
        fields = ('file', 'update_existing', 'mass_unsubscribe', 'list', 'workspace', 'mapping')
