from django.shortcuts import get_object_or_404
from rest_framework import permissions
from users.models import MemberOfWorkspace, Workspace
from emails.models import SenderEmail, Email
from contacts.models import Segment, List

class CheckFKOwnership(permissions.BasePermission):
    """
    Permission with following rules : 
    --> When someone creates a campaign, check if the foreign keys used
        belongs to his workspace (Segment, List, SenderEmail, Email)
    """
    message = 'You are not allowed to perform this action...'

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
            
        if request.method == 'POST':
            workspace_id = request.POST.get('workspace', None)
            segment_id = request.POST.get('to_segment', None)
            list_id = request.POST.get('to_list', None)
            sender_id = request.POST.get('sender', None)
            email_id = request.POST.get('email_model', None)

            if segment_id is not None:
                segment = get_object_or_404(Segment, id=segment_id)
                if not str(segment.workspace.id) == workspace_id:
                    return False
            if list_id is not None:
                list = get_object_or_404(List, id=list_id)
                if not str(list.workspace.id) == workspace_id:
                    return False
            if sender_id is not None:
                sender = get_object_or_404(SenderEmail, id=sender_id)
                if not str(sender.workspace.id) == workspace_id:
                    return False
            if email_id is not None:
                email = get_object_or_404(Email, id=email_id)
                if not str(email.workspace.id) == workspace_id:
                    return False
            return True