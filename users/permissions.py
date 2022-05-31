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
        user = request.user
        member_of_workspace = MemberOfWorkspace.objects.get(
            user=user,
            workspace=obj
        )

        if member_of_workspace.rights == 'AD':
            return True
        if member_of_workspace.rights == 'ME':
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
            workspace = Workspace.objects.get(id=workspace_id)
            user = request.user

            membership = MemberOfWorkspace.objects.get(
                user=user,
                workspace=workspace
            )
            if membership.rights == 'AD':
                return True

        if request.method == 'GET':
            workspace_id = request.GET.get('workspace_id')
            workspace = Workspace.objects.get(id=workspace_id)
            user = request.user

            membership = MemberOfWorkspace.objects.get(
                user=user,
                workspace=workspace
            )
            if membership.rights == 'AD':
                return True
        
        return False


class CheckMemberOfWorkspaceObjRights(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Only admin of a workspace can retrieve, update, or delete a 
    member of workspace.
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        user = request.user
        try:
            user_in_workspace = MemberOfWorkspace.objects.get(
                user=user,
                workspace=obj.workspace
            )
        except:
            return False

        if user_in_workspace and user_in_workspace.rights == 'AD':
            return True
        return False