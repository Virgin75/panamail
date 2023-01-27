from rest_framework import serializers

from users.models import CustomUser, Workspace, MemberOfWorkspace, Invitation


class RestrictedPKRelatedFieldWKS(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        queryset = Workspace.objects.filter(members=self.context['user'])
        return queryset


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class MinimalUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'email', 'first_name', 'last_name', 'created_at']


class InvitationSerializer(serializers.ModelSerializer):
    to_workspace = RestrictedPKRelatedFieldWKS()

    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ['created_at', 'id']


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'id']


class MemberOfWorkspaceSerializer(serializers.ModelSerializer):
    from commons.serializers import PKRelatedFieldWithRead
    user = PKRelatedFieldWithRead(read_serializer=MinimalUserSerializer, queryset=CustomUser.objects.all())
    workspace = RestrictedPKRelatedFieldWKS()

    class Meta:
        model = MemberOfWorkspace
        fields = '__all__'
        read_only_fields = ['added_at', 'updated_at']
