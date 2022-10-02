from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.conf import settings

from .serializers import (
    UserSerializer, 
    CompanySerializer, 
    InvitationSerializer, 
    WorkspaceSerializer,
    MemberOfWorkspaceSerializer,
)
from .models import (
    CustomUser, 
    Invitation, 
    Company, 
    Workspace, 
    MemberOfWorkspace, 
)
from .permissions import (
    IsCompanyAdmin,
    CompanyAdminCreateWorkspace,
    CheckWorkspaceRights,
    CheckMemberOfWorkspaceRights,
    CheckMemberOfWorkspaceObjRights
)

class SignInView(views.APIView):
    permission_classes = []

    def post(self, request, format=None):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(username=email, password=password)
        refresh = RefreshToken.for_user(user)
        #Check if user has done the onboarding (set up a Company & Workspace)
        print(user)
        onboarding_done = True
        if user.company is None or not user.member.all().exists():
            onboarding_done = False
        response = Response(
            {
                'access': str(refresh.access_token), 
                'user': {'onboarding_done': onboarding_done, 'email': user.email, 'first_name': user.first_name, 'last_name':user.last_name}
            }
        )
        return response

class SignUpView(generics.CreateAPIView):
    permission_classes = []
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = get_user_model().objects.create_user(
                    email=serializer.validated_data['email'],
                    password=request.data['password']
        )
        user.first_name = serializer.validated_data['first_name']
        user.last_name = serializer.validated_data['last_name']
        user.save()
        user = authenticate(username=serializer.validated_data['email'], password=request.data['password'])
        refresh = RefreshToken.for_user(user)
        # If there was an invite token in URL we automatically 
        # add the user to the right Company or Workspace.
        invitation_token = request.query_params.get('invitation_token')
        if invitation_token:
            invit_obj = Invitation.objects.get(id=invitation_token)
            if invit_obj.invited_user == serializer.validated_data['email']:
                if invit_obj.type == 'CO':
                    user.company = invit_obj.to_company
                    user.company_role = invit_obj.role
                    user.save()
                    invit_obj.delete()
                if invit_obj.type == 'WO':
                    new_member_of_workspace = MemberOfWorkspace(
                        user=user,
                        workspace=Workspace.objects.get(id=invit_obj.to_workspace),
                        rights=invit_obj.role
                    )
                    new_member_of_workspace.save()
                    invit_obj.delete()
          
        return Response({'access': str(refresh.access_token), 'user': serializer.data}, headers=self.get_success_headers(serializer.data))

class RetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return CustomUser.objects.get(id=self.request.user.id)


class CreateCompanyView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = self.perform_create(serializer)
    
        #After creation of the company we set the user in this company
        user = CustomUser.objects.get(id=request.user.id)
        user.company = company
        user.company_role = 'AD' #Admin
        user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class RetrieveUpdateDestroyCompanyView(generics.RetrieveUpdateDestroyAPIView):
        permission_classes = [IsAuthenticated, IsCompanyAdmin]
        serializer_class = CompanySerializer

        def get_object(self):
            user = self.request.user
            company = user.company
            print(user)
            return company


class CreateInvitationView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    serializer_class = InvitationSerializer
    queryset = Invitation.objects.none()

    def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            if serializer.validated_data['type'] == 'CO': #Company type
                if str(self.request.user.company.id) != str(serializer.validated_data['to_company'].id):
                    return Response('You can only invite users to YOUR company.')
        
            if serializer.validated_data['type'] == 'WO': #Workspace type
                user_workspaces = MemberOfWorkspace.objects.filter(user=self.request.user)
                if serializer.validated_data['to_workspace'] in user_workspaces:
                    return Response('You can only invite users to YOUR workspaces.')

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ListCompanyMembers(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        user_company = self.request.user.company
        users_in_company = CustomUser.objects.filter(company=user_company)
        return users_in_company

class DeleteMemberOfCompany(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    serializer_class = UserSerializer
    lookup_field = 'pk'
    queryset = CustomUser.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        user_company = self.request.user.company
        users_in_company = CustomUser.objects.filter(company=user_company).values_list('id',flat=True)
        if not self.kwargs['pk'] in users_in_company:
            return Response('You can only remove existing users from your company.')
        
        instance.company = None
        instance.save()
        return Response(serializer.data)

class ListCreateWorkspaceView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, CompanyAdminCreateWorkspace]
    serializer_class = WorkspaceSerializer
    
    def get_queryset(self):
        user = self.request.user
        user_workspaces = MemberOfWorkspace.objects.filter(user=user).values_list('workspace')
        my_workspaces = Workspace.objects.filter(id__in=user_workspaces)
        return my_workspaces

    def perform_create(self, serializer):
        user_company = self.request.user.company
        return serializer.save(company=user_company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_workspace = self.perform_create(serializer)

        # Then, add the creator of workspace as a member of the workspace
        created_workspace.members.add(
            request.user,
            through_defaults={'rights': 'AD'}
        )
        created_workspace.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        

class RetrieveUpdateDestroyWorkspaceView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, CheckWorkspaceRights]
    serializer_class = WorkspaceSerializer
    lookup_field = 'pk'
    queryset = Workspace.objects.all()


class ListCreateMemberOfWorkspaceView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, CheckMemberOfWorkspaceRights]
    serializer_class = MemberOfWorkspaceSerializer

    def get_queryset(self):
        workspace_id = self.request.GET.get('workspace_id')
        workspace = Workspace.objects.get(id=workspace_id)

        return MemberOfWorkspace.objects.filter(workspace=workspace)


class RetrieveUpdateDestroyMemberOfWorkspaceView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, CheckMemberOfWorkspaceObjRights]
    serializer_class = MemberOfWorkspaceSerializer
    lookup_field = 'pk'
    queryset = MemberOfWorkspace.objects.all()
