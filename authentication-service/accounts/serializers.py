from .models import CustomUser
from rest_framework import serializers
from django.contrib.auth import authenticate

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "user_role", "phone_number", "created_at", "is_active")

class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "phone_number", "password1", "password2")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        password1 = attrs.get('password1', "")
        password2 = attrs.get('password2', "")
        
        if password1 != password2:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if len(password1) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        # Regular registration creates customers by default
        validated_data['user_role'] = 'customer'
        return CustomUser.objects.create_user(password=password, **validated_data)

class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "phone_number", "password1", "password2")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        password1 = attrs.get('password1', "")
        password2 = attrs.get('password2', "")
        
        if password1 != password2:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if len(password1) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        # Create employee account
        return CustomUser.objects.create_employee(password=password, **validated_data)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data.get('email'), password=data.get('password'))
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users with basic info"""
    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "user_role", "is_active", "created_at")

class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed user information"""
    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "user_role", "phone_number", "is_active", "created_at", "updated_at", "last_login")
