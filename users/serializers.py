from rest_framework import serializers

from commons.serializers import RestrictedPKRelatedFieldWKS
from users import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class MinimalUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'email', 'first_name', 'last_name', 'created_at']


class InvitationSerializer(serializers.ModelSerializer):
    to_workspace = RestrictedPKRelatedFieldWKS()

    class Meta:
        model = models.Invitation
        fields = '__all__'
        read_only_fields = ['created_at', 'id']


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workspace
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'id']


class MemberOfWorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MemberOfWorkspace
        fields = '__all__'
        read_only_fields = ['added_at', 'updated_at']
