from django.shortcuts import get_object_or_404
from rest_framework import permissions
from users.models import MemberOfWorkspace, Workspace

class IsWorkspaceAdmin(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Only an admin of the workspace can go any further
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        if request.method == 'GET':
            workspace_id = request.GET.get('workspace_id')
            
        if request.method == 'POST':
            workspace_id = request.data['workspace']
        workspace = get_object_or_404(Workspace, id=workspace_id)
        membership = workspace.members.through.objects.filter(
            user=request.user,
            rights='AD'
        )
        return True if membership.exists() else False
        