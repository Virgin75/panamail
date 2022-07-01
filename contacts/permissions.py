from django.shortcuts import get_object_or_404
from rest_framework import permissions
from contacts.models import Contact, List, DatabaseRule, DatabaseToSync, Segment
from users.models import MemberOfWorkspace, Workspace

class IsMemberOfWorkspaceCF(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        contact = get_object_or_404(Contact.objects.select_related('workspace'), id=view.kwargs['contact_pk'])
        membership = contact.workspace.members.filter(id=request.user.id)

        return True if membership.exists() else False


class IsMemberOfWorkspaceCL(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        if request.method == 'GET':
            list = get_object_or_404(List.objects.select_related('workspace'), id=request.GET.get('list_id'))
            
        if request.method == 'POST':
            list = get_object_or_404(List.objects.select_related('workspace'), id=request.POST['list'])
            contact = get_object_or_404(Contact.objects.select_related('workspace'), id=request.POST['contact'])

            #Additional check whether Contact belong to one of my Workspaces
            contact_workspace = get_object_or_404(Workspace, id=contact.workspace.id)
            contact_membership = contact_workspace.members.filter(id=request.user.id)
            if not contact_membership.exists():
                return False

        list_workspace = get_object_or_404(Workspace, id=list.workspace.id)
        list_membership = list_workspace.members.filter(id=request.user.id)
        return True if list_membership.exists() else False
        


class IsMemberOfWorkspaceDB(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        if request.method == 'GET':
            db = get_object_or_404(DatabaseToSync.objects.select_related('workspace'), id=request.GET.get('db_id'))
            
        if request.method == 'POST':
            db = get_object_or_404(DatabaseToSync.objects.select_related('workspace'), id=request.POST['db'])
            list = get_object_or_404(List.objects.select_related('workspace'), id=request.POST['list'])

            #Additional check whether List belong to one of my Workspaces
            list_workspace = get_object_or_404(Workspace, id=list.workspace.id)
            list_membership = list_workspace.members.filter(id=request.user.id)
            if not list_membership.exists():
                return False
        
        db_workspace = get_object_or_404(Workspace, id=db.workspace.id)
        db_membership = db_workspace.members.filter(id=request.user.id)
        return True if db_membership.exists() else False



class IsMemberOfWorkspaceObjCF(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):        
        membership = obj.list.workspace.members.filter(id=request.user.id)
        return True if membership.exists() else False


class IsMemberOfWorkspaceObjDB(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        membership = obj.db.workspace.members.filter(id=request.user.id)
        return True if membership.exists() else False


class HasListAccess(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        list = get_object_or_404(List.objects.select_related('workspace'), id=request.POST['list'])
        membership = list.workspace.members.filter(id=request.user.id)
        return True if membership.exists() else False


class IsMemberOfWorkspaceSC(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        segment = get_object_or_404(Segment.objects.select_related('workspace'), id=view.kwargs['segment_pk'])
        membership = segment.workspace.members.filter(id=request.user.id)

        return True if membership.exists() else False

class IsMemberOfWorkspaceObjC(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Check if user requesting access is member of the Workspace
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        membership = obj.segment.workspace.members.filter(id=request.user.id)
        return True if membership.exists() else False
