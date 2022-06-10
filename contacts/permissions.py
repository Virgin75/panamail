from django.shortcuts import get_object_or_404
from rest_framework import permissions
from contacts.models import Contact
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