from django.shortcuts import get_object_or_404
from rest_framework import permissions
from contacts.models import Contact, List, DatabaseRule, DatabaseToSync
from users.models import MemberOfWorkspace, Workspace

class IsMemberOfWorkspaceCF(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        obj = Contact.objects.get(id=view.kwargs['contact_pk'])
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

class IsMemberOfWorkspaceCL(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        if request.method == 'GET':
            obj = List.objects.get(id=request.GET.get('list_id'))
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
        if request.method == 'POST':
            user = request.user
            list = get_object_or_404(List, id=request.POST['list'])
            contact = get_object_or_404(Contact, id=request.POST['contact'])

            membership = get_object_or_404(
                MemberOfWorkspace,
                user=user,
                workspace=contact.workspace
            )
            membership = get_object_or_404(
                MemberOfWorkspace,
                user=user,
                workspace=list.workspace
            )
            return True
        
        return False


class IsMemberOfWorkspaceDB(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        if request.method == 'GET':
            obj = DatabaseToSync.objects.get(id=request.GET.get('db_id'))
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
        if request.method == 'POST':
            user = request.user
            db = get_object_or_404(DatabaseToSync, id=request.POST['db'])
            list = get_object_or_404(List, id=request.POST['list'])

            membership = get_object_or_404(
                MemberOfWorkspace,
                user=user,
                workspace=db.workspace
            )
            membership = get_object_or_404(
                MemberOfWorkspace,
                user=user,
                workspace=list.workspace
            )
            return True
        
        return False


class IsMemberOfWorkspaceObjCF(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        workspace_id = obj.list.workspace.id
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

class IsMemberOfWorkspaceObjDB(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        workspace_id = obj.db.workspace.id
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


class HasListAccess(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        list = get_object_or_404(List, id=request.POST['list'])
        workspace_id = list.workspace.id
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
