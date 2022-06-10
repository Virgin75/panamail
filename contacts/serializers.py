from rest_framework import serializers
from .models import (
    Contact,
    CustomField,
    CustomFieldOfContact,
    List,
    ContactInList
)

class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = '__all__' 

class CustomFieldOfContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldOfContact
        fields = ['custom_field', 'value', 'updated_at']
        read_only_fields = ['custom_field', 'updated_at']

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

class ContactInListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInList
        fields = '__all__' 
        read_only_fields = ['status']