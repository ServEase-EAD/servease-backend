from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Employee, AssignedTask


class EmployeeProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    last_login = serializers.DateTimeField(source="user.last_login", read_only=True)
    account_created = serializers.DateTimeField(source="user.date_joined", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "gender",
            "date_of_birth",
            "account_created",
            "last_login",
            "is_active",
            "address_line1",
            "address_line2",
            "city",
            "postal_code",
        ]
        read_only_fields = [
            "id",
            "full_name",
            "first_name",
            "last_name",
            "email",
            "account_created",
            "last_login",
            "is_active",
        ]

    def get_full_name(self, obj):
        if obj.user:
            first_name = obj.user.first_name or ''
            last_name = obj.user.last_name or ''
            full_name = f"{first_name} {last_name}".strip()
            return full_name if full_name else obj.user.username
        return 'Unknown'
    
    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else ''
    
    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else ''

    def update(self, instance, validated_data):
        # Only allow updating specific fields (not full_name or employment info)
        allowed_fields = [
            'phone_number', 
            'gender', 
            'date_of_birth',
            'address_line1',
            'address_line2',
            'city',
            'postal_code'
        ]
        
        for field in allowed_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("New passwords do not match")
        validate_password(data["new_password"])
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


# ✅ Add this to fix your missing import
class AssignedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedTask
        fields = "__all__"
