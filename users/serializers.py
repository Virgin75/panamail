from rest_framework import serializers
from .models import (
    CustomUser, 
    Company, 
    Invitation, 
    Workspace, 
    MemberOfWorkspace,
    SMTPProvider
)

class UserSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(
        many=False, 
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password', 'company', 'company_role', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'company', 'company_role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__' 
        read_only_fields = ['created_at', 'updated_at', 'plan_name']

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__' 
        read_only_fields = ['created_at', 'id']

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = '__all__' 
        read_only_fields = ['created_at', 'updated_at', 'id', 'company']

class MemberOfWorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberOfWorkspace
        fields = '__all__' 
        read_only_fields = ['created_at', 'updated_at']

class SMTPProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPProvider
        fields = '__all__' 
        extra_kwargs = {
            'auth_id': {'write_only': True},
            'auth_password': {'write_only': True},
        }