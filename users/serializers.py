from rest_framework import serializers
from .models import CustomUser, Company

class UserSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(
        many=False, 
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password', 'company', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__' 
        read_only_fields = ['created_at', 'updated_at']