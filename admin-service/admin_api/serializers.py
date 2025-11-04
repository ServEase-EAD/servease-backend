from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """Serializer for user data from authentication service"""
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    user_role = serializers.ChoiceField(choices=['customer', 'employee', 'admin'])
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class UserListSerializer(serializers.Serializer):
    """Simplified serializer for user list"""
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    user_role = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class CreateUserSerializer(serializers.Serializer):
    """Serializer for creating a new user"""
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    user_role = serializers.ChoiceField(choices=['customer', 'employee', 'admin'])
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs


class UpdateUserRoleSerializer(serializers.Serializer):
    """Serializer for updating user role"""
    user_role = serializers.ChoiceField(choices=['customer', 'employee', 'admin'])


class UpdateUserSerializer(serializers.Serializer):
    """Serializer for updating user information"""
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_users = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_employees = serializers.IntegerField()
    total_admins = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
