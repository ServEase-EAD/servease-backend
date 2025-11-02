"""
Customer Service Serializers
Handles data serialization for REST API endpoints

Note: User credentials (email, name, phone) come from authentication service.
This serializer only handles customer-specific data.
"""

from rest_framework import serializers
from .models import Customer
import requests
from django.conf import settings


class CustomerSerializer(serializers.ModelSerializer):
    """
    Comprehensive customer serializer with user data from auth service.
    Includes read-only fields populated from authentication service.
    Uses user_id as the logical primary identifier.
    """

    # Read-only fields from authentication service
    email = serializers.EmailField(read_only=True, required=False)
    first_name = serializers.CharField(read_only=True, required=False)
    last_name = serializers.CharField(read_only=True, required=False)
    phone_number = serializers.CharField(read_only=True, required=False)
    full_name = serializers.SerializerMethodField(read_only=True)
    full_address = serializers.ReadOnlyField()
    is_business_customer = serializers.ReadOnlyField()

    # Logical consolidation: override id to return user_id
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            # Core fields (id is now user_id logically)
            'id',
            # Auth service fields (read-only)
            'email', 'first_name', 'last_name', 'phone_number', 'full_name',
            # Address fields
            'street_address', 'city', 'state', 'postal_code', 'country', 'full_address',
            # Business fields
            'company_name', 'business_type', 'tax_id', 'is_business_customer',
            # Emergency contact
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            # Status & history
            'is_verified', 'customer_since', 'last_service_date', 'total_services',
            # Preferences
            'preferred_contact_method', 'notification_preferences',
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_since', 'created_at', 'updated_at',
            'total_services', 'full_name', 'full_address', 'is_business_customer'
        ]

    def get_id(self, obj):
        """Return user_id as the logical primary identifier"""
        return str(obj.user_id)

    def get_full_name(self, obj):
        """Get full name from context or return placeholder"""
        context_user = self.context.get('user_data', {})
        first = context_user.get('first_name', '')
        last = context_user.get('last_name', '')
        return f"{first} {last}".strip() if (first or last) else "N/A"

    def validate_user_id(self, value):
        """Validate unique user_id"""
        if self.instance and self.instance.user_id == value:
            return value

        if Customer.objects.filter(user_id=value).exists():
            raise serializers.ValidationError(
                "A customer profile with this user ID already exists.")
        return value


class CustomerBasicSerializer(serializers.ModelSerializer):
    """
    Basic customer serializer for lists and references.
    Minimal fields for performance.
    """

    full_address = serializers.ReadOnlyField()
    is_business_customer = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id', 'user_id', 'street_address', 'city', 'state',
            'full_address', 'company_name', 'is_business_customer',
            'customer_since', 'total_services'
        ]


class CustomerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new customer profiles.
    User must already exist in authentication service.
    """

    class Meta:
        model = Customer
        fields = [
            'user_id', 'street_address', 'city', 'state', 'postal_code', 'country',
            'company_name', 'business_type', 'tax_id',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship',
            'preferred_contact_method', 'notification_preferences'
        ]

    def validate_user_id(self, value):
        """Ensure user_id doesn't already have a customer profile"""
        if Customer.objects.filter(user_id=value).exists():
            raise serializers.ValidationError(
                "A customer profile already exists for this user.")
        return value


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating customer-specific information.
    User credentials should be updated via authentication service.
    """

    class Meta:
        model = Customer
        fields = [
            'street_address', 'city', 'state', 'postal_code', 'country',
            'company_name', 'business_type', 'tax_id',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship',
            'preferred_contact_method', 'notification_preferences'
        ]


class CustomerDashboardSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for customer dashboard data.
    Includes computed fields and summary information.
    """

    full_address = serializers.ReadOnlyField()
    is_business_customer = serializers.ReadOnlyField()
    # These will be populated from auth service in the view
    email = serializers.EmailField(read_only=True, required=False)
    first_name = serializers.CharField(read_only=True, required=False)
    last_name = serializers.CharField(read_only=True, required=False)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'user_id',
            'email', 'first_name', 'last_name', 'full_name',
            'full_address', 'company_name', 'is_business_customer',
            'last_service_date', 'total_services',
            'customer_since', 'is_verified',
            'preferred_contact_method'
        ]

    def get_full_name(self, obj):
        """Get full name from context"""
        context_user = self.context.get('user_data', {})
        first = context_user.get('first_name', '')
        last = context_user.get('last_name', '')
        return f"{first} {last}".strip() if (first or last) else "N/A"


class CustomerWithUserDataSerializer(serializers.ModelSerializer):
    """
    Serializer that combines customer data with user data from auth service.
    Used when we need to return complete customer + user information.
    """

    # User fields from auth service
    user_email = serializers.EmailField(
        source='user_data.email', read_only=True)
    user_first_name = serializers.CharField(
        source='user_data.first_name', read_only=True)
    user_last_name = serializers.CharField(
        source='user_data.last_name', read_only=True)
    user_phone = serializers.CharField(
        source='user_data.phone_number', read_only=True)
    user_role = serializers.CharField(
        source='user_data.user_role', read_only=True)
    user_is_active = serializers.BooleanField(
        source='user_data.is_active', read_only=True)

    full_address = serializers.ReadOnlyField()
    is_business_customer = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id', 'user_id',
            # User data from auth service
            'user_email', 'user_first_name', 'user_last_name', 'user_phone',
            'user_role', 'user_is_active',
            # Customer data
            'street_address', 'city', 'state', 'postal_code', 'country', 'full_address',
            'company_name', 'business_type', 'tax_id', 'is_business_customer',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'is_verified', 'customer_since', 'last_service_date', 'total_services',
            'preferred_contact_method', 'notification_preferences',
            'created_at', 'updated_at'
        ]
