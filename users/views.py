from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer, CompanySerializer
from .models import CustomUser, Company, Workspace, MemberOfWorkspace, SMTPProvider


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
        user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class RetrieveUpdateDestroyCompanyView(generics.RetrieveUpdateDestroyAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = CompanySerializer

        def get_object(self):
            user = self.request.user
            company = user.company
            return company

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