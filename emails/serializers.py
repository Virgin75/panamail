from rest_framework import serializers

from users.serializers import MinimalUserSerializer
from .models import (
    SenderEmail,
    SenderDomain,
    Email,
    Tag
)
from commons.serializers import RestrictedPKRelatedField, HistorySerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class EmailSerializer(serializers.ModelSerializer):
    tags = RestrictedPKRelatedField(many=True, read_serializer=TagSerializer, model=Tag)
    created_by = MinimalUserSerializer(read_only=True)
    edit_history = HistorySerializer(many=True, read_only=True)

    class Meta:
        model = Email
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')


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