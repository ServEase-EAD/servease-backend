from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Employee, AssignedTask


class EmployeeProfileSerializer(serializers.ModelSerializer):
    # Read-only fields from User model
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
            # Additional employee-specific fields
            "specialization",
            "experience_years",
            "hourly_rate",
            "is_available",
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
            # These are managed by admin/HR
            "specialization",
            "experience_years", 
            "hourly_rate",
            "is_available",
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
        """
        Update only the allowed fields for employee profile.
        These are the fields that employees can update themselves.
        """
        # Fields that employees can update themselves
        allowed_fields = [
            'phone_number', 
            'gender', 
            'date_of_birth',
            'address_line1',
            'address_line2',
            'city',
            'postal_code'
        ]
        
        print(f"DEBUG Serializer: Updating employee {instance.id}")
        print(f"DEBUG Serializer: Validated data: {validated_data}")
        
        # Update only allowed fields
        for field in allowed_fields:
            if field in validated_data:
                old_value = getattr(instance, field)
                new_value = validated_data[field]
                print(f"DEBUG Serializer: {field}: '{old_value}' -> '{new_value}'")
                setattr(instance, field, new_value)
        
        instance.save()
        print(f"DEBUG Serializer: Successfully saved employee {instance.id}")
        return instance

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and len(value.strip()) > 0:
            # Remove any spaces or special characters for basic validation
            cleaned = ''.join(filter(str.isdigit, value))
            if len(cleaned) < 9:
                raise serializers.ValidationError("Phone number must be at least 9 digits")
        return value

    def validate_gender(self, value):
        """Validate gender choices"""
        if value and value not in ['Male', 'Female', 'Other']:
            raise serializers.ValidationError("Gender must be Male, Female, or Other")
        return value


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
