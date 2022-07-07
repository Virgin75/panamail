from django.shortcuts import get_object_or_404
from rest_framework import permissions
from contacts.models import Contact
from users.models import MemberOfWorkspace, Workspace
from .models import TrackerAPIKey

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

class IsWorkspaceAdminObj(permissions.BasePermission):
    """
    Permission with following rules : 
    --> Only an admin of the workspace can go any further
    """
    message = 'You are not allowed to perform this action...'

    def has_object_permission(self, request, view, obj):
        workspace = obj.workspace
        membership = workspace.members.through.objects.filter(
            user=request.user,
            rights='AD'
        )
        return True if membership.exists() else False

class IsTokenValid(permissions.BasePermission):
    """
    Permission with following rules : 
    --> The token in data['api_token'] must be valid to proceed
    """
    message = 'Your API token is not valid...'

    def has_permission(self, request, view):
        api_token = TrackerAPIKey.objects.filter(
            token=request.data['api_token']
        )
        return True if api_token.exists() else False

class IsTrackedContactInWorkspace(permissions.BasePermission):
    """
    Permission with following rules : 
    --> The tracked contact must belong to the user Workspace
    """
    message = 'This contact does not belong to your workspace...'

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        else:
            api_key = TrackerAPIKey.objects.get(
                token=request.data['api_token']
            )
            contact = get_object_or_404(
                Contact, 
                email=request.data['contact_email'],
                workspace=api_key.workspace
            )
            return True if contact.workspace.id == api_key.workspace.id else False
        