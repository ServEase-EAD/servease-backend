from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Employee, AssignedTask


class EmployeeProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    last_login = serializers.DateTimeField(source="user.last_login", read_only=True)
    account_created = serializers.DateTimeField(source="user.date_joined", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "gender",
            "date_of_birth",
            "employee_id",
            "role",
            "department",
            "joining_date",
            "employment_type",
            "supervisor",
            "account_created",
            "last_login",
            "status",
            "access_role",
            "address_line1",
            "address_line2",
            "city",
            "postal_code",
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def update(self, instance, validated_data):
        user = instance.user
        full_name = self.initial_data.get("full_name", "")
        if full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            user.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)
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
