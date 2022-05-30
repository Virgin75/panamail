from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer, CompanySerializer, InvitationSerializer
from .models import CustomUser, Invitation, Company, Workspace, MemberOfWorkspace, SMTPProvider
from .permissions import IsCompanyAdmin

class SignUpView(generics.CreateAPIView):
    permission_classes = []
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(request.data)
        
        user = get_user_model().objects.create_user(
                    email=serializer.data['email'],
                    password=request.data['password']
        )
        # If there was an invite token in URL we automatically 
        # add the user to the right Company or Workspace.
        invitation_token = request.query_params.get('invitation_token')
        if invitation_token:
            invit_obj = Invitation.objects.get(id=invitation_token)
            if invit_obj.invited_user == serializer.data['email']:
                if invit_obj.type == 'CO':
                    user.company = invit_obj.to_company
                    user.save()
                if invit_obj.type == 'WO':
                    new_member_of_workspace = MemberOfWorkspace(
                        user=user,
                        workspace=Workspace.objects.get(id=invit_obj.to_workspace),
                        rights=invit_obj.role
                    )
                    new_member_of_workspace.save()
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

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
                    print(f"Value 1 : {self.request.user.company.id}")
                    print(f"Value 2 : {serializer.validated_data['to_company'].id}")
                    return Response('You can only invite users to YOUR company.')
        
            if serializer.validated_data['type'] == 'WO': #Workspace type
                user_workspaces = MemberOfWorkspace.objects.filter(user=self.request.user)
                if serializer.validated_data['to_workspace'] in user_workspaces:
                    return Response('You can only invite users to YOUR workspaces.')

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListCreateWorkspaceView(generics.ListCreateAPIView):
    pass

class RetrieveUpdateDestroyWorkspaceView(generics.RetrieveUpdateDestroyAPIView):
    pass

class ListCreateMemberOfWorkspaceView(generics.ListCreateAPIView):
    pass

class RetrieveUpdateDestroyMemberOfWorkspaceView(generics.RetrieveUpdateDestroyAPIView):
    pass

class ListSMTPProviderView(generics.ListAPIView):
    pass