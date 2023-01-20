from rest_framework import serializers

from commons.models import Tag
from commons.serializers import RestrictedPKRelatedField, WksFieldsSerializer
from emails import models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class EmailSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    tags = RestrictedPKRelatedField(many=True, read_serializer=TagSerializer, model=Tag)

    class Meta:
        model = models.Email
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')


class SenderDomainSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    class Meta:
        model = models.SenderDomain
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by', 'status')


class SenderEmailSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    domain = RestrictedPKRelatedField(read_serializer=SenderDomainSerializer, model=models.SenderDomain)

    class Meta:
        model = models.SenderEmail
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by', 'status')
