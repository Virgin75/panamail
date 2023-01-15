from rest_framework import serializers
from .models import (
    SenderEmail,
    SenderDomain,
    Email,
    Tag
)
from commons.serializers import RestrictedPKRelatedField


class EmailSerializer(serializers.ModelSerializer):
    tags = RestrictedPKRelatedField(many=True)

    class Meta:
        model = Email
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SenderDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = SenderDomain
        fields = '__all__' 
        read_only_fields = ['status']


class SenderEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SenderEmail
        fields = '__all__' 
        read_only_fields = ['status']