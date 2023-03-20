from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, mixins, exceptions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_simplejwt.tokens import RefreshToken

from commons.paginations import x20ResultsPerPage, x10ResultsPerPage
from users.models import CustomUser, Workspace, MemberOfWorkspace, Invitation
from users.serializers import UserSerializer, InvitationSerializer, WorkspaceSerializer, MemberOfWorkspaceSerializer


class UserViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    """
    User viewset to perform following actions :

    - /api/users/<id> (GET, PATCH, DELETE): Retrieve, Update, Destroy a user.
    - /api/users/signup (POST): Create a new user.
        - url params: ?invitation_token=<token> >> if user is invited to a workspace.
    - /api/users/signin (POST): Authenticate an existing user.
    """

    serializer_class = UserSerializer
    pagination_class = x20ResultsPerPage

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ('signin', 'signup'):
            return []
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def signin(self, request):
        user = authenticate(username=request.data['email'], password=request.data['password'])
        refresh = RefreshToken.for_user(user)
        headers = {
            'Set-Cookie': f'access={refresh.access_token}; Max-Age={settings.SECONDS}; SameSite=None; Secure; Path=/;',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Set-Cookie, Content-Type, Content-Length, Authorization, Accept,X-Requested-With"',
        }
        # Check if user has done the onboarding (set up a Workspace)
        workspace_ids = []
        if user.workspaces.all().exists():
            onboarding_done = True
            workspace_ids = user.workspaces.values_list('id', 'name').all()
        else:
            onboarding_done = False
        response = Response(
            {
                'access': str(refresh.access_token),
                'user': {
                    'onboarding_done': onboarding_done,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'workspaces_id': workspace_ids,

            }, headers=headers
        )
        return response

    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        get_user_model().objects.create_user(
            email=serializer.validated_data['email'],
            password=request.data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name']
        )
        user = authenticate(username=serializer.validated_data['email'], password=request.data['password'])
        refresh = RefreshToken.for_user(user)
        headers = {
            'Set-Cookie': f'access={refresh.access_token}; Max-Age={settings.SECONDS}; SameSite=None; Secure; Path=/;',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Set-Cookie, Content-Type, Content-Length, Authorization, Accept,X-Requested-With"',
        }
        # If there was an invite token in URL we automatically
        # add the user to the right Workspace.
        invitation_token = request.query_params.get('invitation_token')
        if invitation_token:
            invit_obj = Invitation.objects.get(id=invitation_token, status="PENDING")
            if invit_obj.invited_user == serializer.validated_data['email']:
                new_member = MemberOfWorkspace(
                    user=user,
                    workspace=Workspace.objects.get(id=invit_obj.to_workspace),
                    rights=invit_obj.role
                )
                new_member.save()
                invit_obj.status = "ACCEPTED"
                invit_obj.save()

        return Response({'access': str(refresh.access_token), 'user': serializer.data}, headers=headers)


class WorkspaceViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    Workspace viewset to perform following actions :

    - /api/workspaces (GET, POST): List all Workspaces current users is in, or create a new one.
    - /api/workspaces/<wks_id> (GET, PATCH, DELETE): Retrieve, Update, Destroy a Workspace.
    - /api/workspaces/<wks_id>/invitation (POST, GET): Invite a new user to a Workspace and list invitations sent.
    """

    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = x20ResultsPerPage

    def get_queryset(self):
        return Workspace.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        workspace = serializer.save()
        workspace.members.add(self.request.user, through_defaults={"rights": "AD"})

    @action(detail=True, methods=['post'], serializer_class=InvitationSerializer)
    def invitation(self, request, pk):
        """Create a new Workspace invitation."""
        workspace = self.get_object()
        if not workspace.members.through.objects.filter(user=request.user, rights="AD").exists():
            raise exceptions.PermissionDenied("You cannot perform this action.")
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()
        if CustomUser.objects.filter(email=invitation.invited_user).exists():
            invitation.status = "ACCEPTED"
            invitation.save()
        return Response(status=status.HTTP_201_CREATED, data=self.get_serializer(invitation).data)

    @invitation.mapping.get
    def list_invitations(self, request, pk):
        """List all Workspaces invitations and their status."""
        workspace = self.get_object()
        invitations = Invitation.objects.filter(to_workspace=workspace)
        serializer = self.get_serializer(invitations, many=True, context={'user': request.user})
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class NestedWorkspaceMembersViewset(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    NestedViewSetMixin
):
    """
    - GET: /api/workspaces/<wks_id>/members: List members of Workspace.
    - PATCH, DELETE: /api/workspaces/<wks_id>/members/<user_id>: Update or delete a Workspace member.
    """

    serializer_class = MemberOfWorkspaceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = x10ResultsPerPage

    def get_queryset(self):
        workspace_id = self.kwargs.get("parent_lookup_workspaces")
        workspace = Workspace.objects.get(id=workspace_id)
        # TODO: check d'ovveride le get queryset plutot que ajouter le check ici
        if self.request.user not in workspace.members.all():
            raise exceptions.PermissionDenied("You cannot perform this action.")
        members = workspace.members.through.objects.filter(workspace=workspace)
        return members

    def get_object(self):
        workspace_id = self.kwargs.get("parent_lookup_workspaces")
        workspace = Workspace.objects.get(id=workspace_id)
        if self.request.user not in workspace.members.all():
            raise exceptions.PermissionDenied("You cannot perform this action.")
        member_id = self.kwargs.get("pk")
        member = workspace.members.through.objects.get(user_id=member_id, workspace=workspace)
        return member
