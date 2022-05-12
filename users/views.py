from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .models import CustomUser


class SignUpView(generics.CreateAPIView):
    permission_classes = []
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(request.data)
        
        user = get_user_model().objects.create_user(
                    email=serializer.data['email'],
                    password=request.data['password']
                    )
        # Create workspace

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

class RetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return CustomUser.objects.get(id=self.request.user.id)