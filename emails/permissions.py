from django.shortcuts import get_object_or_404
from rest_framework import permissions
from users.models import MemberOfWorkspace, Workspace

class IsMemberOfWorkspace(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Only a member of the workspace can go any further
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        if request.method == 'GET':
            workspace_id = request.GET.get('workspace_id')
            workspace = get_object_or_404(Workspace, id=workspace_id)
            user = request.user

            membership = get_object_or_404(
                MemberOfWorkspace,
                user=user,
                workspace=workspace
            )
            if membership.user == user:
                return True

        if request.method == 'POST':
            workspace_id = request.POST['workspace']
            workspace = get_object_or_404(Workspace, id=workspace_id)
            user = request.user

            membership = get_object_or_404(
                MemberOfWorkspace,
                user=user,
                workspace=workspace
            )
            if membership.user == user:
                return True
        
        return False

class IsMemberOfWorkspaceObj(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting Email info is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        workspace_id = obj.workspace.id
        workspace = get_object_or_404(Workspace, id=workspace_id)
        user = request.user

        membership = get_object_or_404(
            MemberOfWorkspace,
            user=user,
            workspace=workspace
        )
        if membership.user == user:
            return True
        
        return False