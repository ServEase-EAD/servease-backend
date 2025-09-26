"""
Customer Service Serializers
Handles data serialization for REST API endpoints
"""

from rest_framework import serializers
from .models import Customer, Vehicle, CustomerPreferences, CustomerDocument, CustomerNote


class CustomerPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for customer preferences"""

    class Meta:
        model = CustomerPreferences
        fields = [
            'email_notifications', 'sms_notifications', 'push_notifications',
            'phone_call_notifications', 'postal_mail_notifications',
            'preferred_contact_method', 'preferred_service_time',
            'preferred_service_day', 'preferred_language', 'timezone',
            'currency', 'marketing_emails', 'promotional_sms',
            'service_reminders', 'appointment_reminders',
            'data_sharing_consent', 'analytics_consent'
        ]


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for customer vehicles"""

    vehicle_age = serializers.ReadOnlyField()
    is_service_due = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'make', 'model', 'year', 'color', 'vin',
            'license_plate', 'state_registered', 'engine_size',
            'fuel_type', 'transmission', 'current_mileage',
            'purchase_date', 'purchase_mileage', 'insurance_company',
            'insurance_policy_number', 'insurance_expiry_date',
            'registration_expiry_date', 'is_active', 'is_under_warranty',
            'warranty_expiry_date', 'last_service_date',
            'last_service_mileage', 'next_service_due_date',
            'next_service_due_mileage', 'vehicle_age', 'is_service_due',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'vehicle_age', 'created_at', 'updated_at']

    def get_is_service_due(self, obj):
        return obj.is_service_due()

    def validate_vin(self, value):
        """Validate VIN format"""
        if len(value) != 17:
            raise serializers.ValidationError(
                "VIN must be exactly 17 characters long.")
        return value.upper()

    def validate_year(self, value):
        """Validate vehicle year"""
        from django.utils import timezone
        current_year = timezone.now().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Year must be between 1900 and {current_year + 1}."
            )
        return value


class VehicleBasicSerializer(serializers.ModelSerializer):
    """Basic vehicle serializer for nested relationships"""

    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'color', 'license_plate']


class CustomerDocumentSerializer(serializers.ModelSerializer):
    """Serializer for customer documents"""

    file_size_display = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = CustomerDocument
        fields = [
            'id', 'vehicle', 'document_type', 'title', 'description',
            'file_path', 'file_size', 'file_size_display', 'mime_type',
            'is_sensitive', 'expiry_date', 'is_expired', 'is_active',
            'uploaded_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'mime_type', 'uploaded_at', 'updated_at'
        ]

    def get_file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} bytes"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"

    def get_is_expired(self, obj):
        return obj.is_expired()


class CustomerNoteSerializer(serializers.ModelSerializer):
    """Serializer for customer notes"""

    class Meta:
        model = CustomerNote
        fields = [
            'id', 'note_type', 'title', 'content', 'is_important',
            'is_private', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerSerializer(serializers.ModelSerializer):
    """Comprehensive customer serializer with nested relationships"""

    full_name = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    vehicles = VehicleBasicSerializer(many=True, read_only=True)
    preferences = CustomerPreferencesSerializer(read_only=True)
    active_vehicles_count = serializers.SerializerMethodField()
    recent_documents = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'user_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'secondary_phone', 'street_address',
            'apartment_unit', 'city', 'state', 'zip_code', 'country',
            'full_address', 'is_active', 'is_verified', 'customer_since',
            'company_name', 'business_tax_id', 'is_business_customer',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'last_service_date',
            'vehicles', 'preferences', 'active_vehicles_count',
            'recent_documents', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'full_address', 'customer_since',
            'active_vehicles_count', 'recent_documents',
            'created_at', 'updated_at'
        ]

    def get_active_vehicles_count(self, obj):
        return obj.get_active_vehicles_count()

    def get_recent_documents(self, obj):
        recent_docs = obj.documents.filter(is_active=True)[:5]
        return CustomerDocumentSerializer(recent_docs, many=True).data

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
    active_vehicles_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'user_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'city', 'state', 'is_active',
            'active_vehicles_count', 'customer_since'
        ]

    def get_active_vehicles_count(self, obj):
        return obj.get_active_vehicles_count()


class CustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new customers"""

    preferences = CustomerPreferencesSerializer(required=False)

    class Meta:
        model = Customer
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'phone',
            'secondary_phone', 'street_address', 'apartment_unit',
            'city', 'state', 'zip_code', 'country', 'company_name',
            'business_tax_id', 'is_business_customer',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'preferences'
        ]

    def create(self, validated_data):
        """Create customer with preferences"""
        preferences_data = validated_data.pop('preferences', {})
        customer = Customer.objects.create(**validated_data)

        # Create preferences with default values
        CustomerPreferences.objects.create(
            customer=customer, **preferences_data)

        return customer


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer information"""

    preferences = CustomerPreferencesSerializer(required=False)

    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'secondary_phone',
            'street_address', 'apartment_unit', 'city', 'state', 'zip_code',
            'country', 'company_name', 'business_tax_id', 'is_business_customer',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'preferences'
        ]

    def update(self, instance, validated_data):
        """Update customer and preferences"""
        preferences_data = validated_data.pop('preferences', None)

        # Update customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update preferences if provided
        if preferences_data is not None:
            preferences, created = CustomerPreferences.objects.get_or_create(
                customer=instance,
                defaults=preferences_data
            )
            if not created:
                for attr, value in preferences_data.items():
                    setattr(preferences, attr, value)
                preferences.save()

        return instance


class CustomerDashboardSerializer(serializers.ModelSerializer):
    """Specialized serializer for customer dashboard data"""

    full_name = serializers.ReadOnlyField()
    vehicles = VehicleSerializer(many=True, read_only=True)
    preferences = CustomerPreferencesSerializer(read_only=True)
    active_vehicles_count = serializers.SerializerMethodField()
    vehicles_due_for_service = serializers.SerializerMethodField()
    recent_documents = serializers.SerializerMethodField()
    important_notes = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'email', 'phone', 'last_service_date',
            'vehicles', 'preferences', 'active_vehicles_count',
            'vehicles_due_for_service', 'recent_documents', 'important_notes'
        ]

    def get_active_vehicles_count(self, obj):
        return obj.get_active_vehicles_count()

    def get_vehicles_due_for_service(self, obj):
        due_vehicles = [v for v in obj.vehicles.filter(
            is_active=True) if v.is_service_due()]
        return VehicleBasicSerializer(due_vehicles, many=True).data

    def get_recent_documents(self, obj):
        recent_docs = obj.documents.filter(is_active=True)[:3]
        return CustomerDocumentSerializer(recent_docs, many=True).data

    def get_important_notes(self, obj):
        important_notes = obj.notes.filter(
            is_important=True, is_private=False)[:3]
        return CustomerNoteSerializer(important_notes, many=True).data
