from django.shortcuts import get_object_or_404
from rest_framework import permissions
from .models import MemberOfWorkspace, Workspace

class IsCompanyAdmin(permissions.BasePermission):
    """
    User level permission to allow only company admin
    to update or delete their company.
    """
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.user.company_role == 'AD':
            return True
        return False

class CheckWorkspaceRights(permissions.BasePermission):
    """
    Object-level permission to only allow admins of workspace 
    to do anything on it. Workspace members can only retrieve the
    workspace details.
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        membership = obj.members.through.objects.filter(
            user=request.user
        )

        if membership.rights == 'AD':
            return True

        if membership.rights == 'ME':
            if request.method == 'GET':
                return True
            elif request.method in ('DELETE', 'PUT', 'PATCH'):
                return False
        return False

class CheckMemberOfWorkspaceRights(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Only admin of a workspace can create a new workspace member
    --> Only admin of a workspace can list its members
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        if request.method == 'POST':
            workspace_id = request.POST['workspace']

        if request.method == 'GET':
            workspace_id = request.GET.get('workspace_id')
        
        workspace = get_object_or_404(Workspace, id=workspace_id)
        membership = workspace.members.through.objects.filter(
                user=request.user,
                rights='AD'
            )
        return True if membership.exists() else False


class CheckMemberOfWorkspaceObjRights(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Only admin of a workspace can retrieve, update, or delete a 
    member of workspace.
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        membership = obj.members.through.objects.filter(
            user=request.user,
            rights='AD'
        )
        return True if membership.exists() else False