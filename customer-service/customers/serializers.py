"""
Customer Service Serializers
Handles data serialization for REST API endpoints
"""

from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Comprehensive customer serializer"""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id', 'user_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'address', 'is_verified', 'customer_since',
            'company_name', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'last_service_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'customer_since', 'created_at', 'updated_at'
        ]

    def validate_email(self, value):
        """Validate unique email"""
        if self.instance and self.instance.email == value:
            return value

        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A customer with this email already exists.")
        return value.lower()

    def validate_user_id(self, value):
        """Validate unique user_id"""
        if self.instance and self.instance.user_id == value:
            return value

        if Customer.objects.filter(user_id=value).exists():
            raise serializers.ValidationError(
                "A customer with this user ID already exists.")
        return value


class CustomerBasicSerializer(serializers.ModelSerializer):
    """Basic customer serializer for lists and references"""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id', 'user_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'address', 'customer_since'
        ]


class CustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new customers"""

    class Meta:
        model = Customer
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'phone',
            'address', 'company_name', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship'
        ]


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer information"""

    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'company_name', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship'
        ]


class CustomerDashboardSerializer(serializers.ModelSerializer):
    """Specialized serializer for customer dashboard data"""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'email', 'phone', 'address', 'last_service_date',
            'customer_since', 'is_verified'
        ]
