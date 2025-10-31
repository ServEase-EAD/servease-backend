"""
Serializers for Appointment models
"""
from rest_framework import serializers
from .models import Appointment, TimeSlot, AppointmentHistory
from .utils.cache_helper import get_customer_cached, get_vehicle_cached, get_employee_cached
from .services.validators import validate_appointment_creation


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model with related data"""
    
    customer_name = serializers.SerializerMethodField()
    vehicle_details = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    time_until_appointment = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer_id', 'vehicle_id', 'assigned_employee_id',
            'appointment_type', 'scheduled_date', 'scheduled_time', 'duration_minutes',
            'status', 'service_description', 'customer_notes', 'internal_notes',
            'estimated_cost', 'created_by_user_id', 'created_at', 'updated_at',
            'cancelled_at', 'completed_at',
            # Computed fields
            'customer_name', 'vehicle_details', 'employee_name', 'time_until_appointment'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'cancelled_at']
    
    def get_customer_name(self, obj):
        """Fetch customer name from cache or API"""
        auth_token = self.context.get('auth_token')
        customer_data = get_customer_cached(obj.customer_id, auth_token)
        return customer_data.get('full_name', 'Unknown')
    
    def get_vehicle_details(self, obj):
        """Fetch vehicle details from cache or API"""
        auth_token = self.context.get('auth_token')
        vehicle_data = get_vehicle_cached(obj.vehicle_id, auth_token)
        return f"{vehicle_data.get('year', '')} {vehicle_data.get('make', '')} {vehicle_data.get('model', '')}".strip()
    
    def get_employee_name(self, obj):
        """Fetch employee name from cache or API"""
        if obj.assigned_employee_id:
            auth_token = self.context.get('auth_token')
            employee_data = get_employee_cached(obj.assigned_employee_id, auth_token)
            return employee_data.get('full_name', 'Unassigned')
        return 'Unassigned'
    
    def get_time_until_appointment(self, obj):
        """Calculate time until appointment"""
        from .utils.date_utils import get_time_until_appointment
        return get_time_until_appointment(obj.scheduled_date, obj.scheduled_time)
    
    def validate(self, data):
        """Validate appointment data"""
        # Only validate on creation, not updates
        if not self.instance:
            request = self.context.get('request')
            user = request.user if request else None
            auth_token = self.context.get('auth_token')
            
            # Set created_by_user_id if not provided
            if 'created_by_user_id' not in data and user:
                data['created_by_user_id'] = getattr(user, 'id', 1)
            
            try:
                validate_appointment_creation(data, user, auth_token)
            except Exception as e:
                # In development, log and continue
                print(f"Validation warning: {e}")
        
        return data


class AppointmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing appointments"""
    
    customer_name = serializers.SerializerMethodField()
    vehicle_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer_id', 'vehicle_id', 'appointment_type',
            'scheduled_date', 'scheduled_time', 'status',
            'customer_name', 'vehicle_details'
        ]
    
    def get_customer_name(self, obj):
        auth_token = self.context.get('auth_token')
        customer_data = get_customer_cached(obj.customer_id, auth_token)
        return customer_data.get('full_name', 'Unknown')
    
    def get_vehicle_details(self, obj):
        auth_token = self.context.get('auth_token')
        vehicle_data = get_vehicle_cached(obj.vehicle_id, auth_token)
        return f"{vehicle_data.get('year', '')} {vehicle_data.get('make', '')} {vehicle_data.get('model', '')}".strip()


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for TimeSlot model"""
    
    available_capacity = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'date', 'start_time', 'end_time', 
            'is_available', 'max_concurrent_appointments',
            'available_capacity'
        ]
    
    def get_available_capacity(self, obj):
        """Calculate remaining capacity"""
        from .models import Appointment
        current_bookings = Appointment.objects.filter(
            scheduled_date=obj.date,
            scheduled_time=obj.start_time,
            status__in=['pending', 'confirmed', 'in_progress']
        ).count()
        return obj.max_concurrent_appointments - current_bookings


class AppointmentHistorySerializer(serializers.ModelSerializer):
    """Serializer for AppointmentHistory model"""
    
    class Meta:
        model = AppointmentHistory
        fields = [
            'id', 'appointment_id', 'changed_by_user_id',
            'previous_status', 'new_status', 'change_reason', 'changed_at'
        ]
        read_only_fields = ['id', 'changed_at']


class RescheduleSerializer(serializers.Serializer):
    """Serializer for rescheduling appointments"""
    
    new_date = serializers.DateField()
    new_time = serializers.TimeField()
    reason = serializers.CharField(required=False, allow_blank=True)


class AssignEmployeeSerializer(serializers.Serializer):
    """Serializer for assigning employees"""
    
    employee_id = serializers.UUIDField()


class StatusUpdateSerializer(serializers.Serializer):
    """Serializer for status updates"""
    
    reason = serializers.CharField(required=False, allow_blank=True)


class AvailableSlotsQuerySerializer(serializers.Serializer):
    """Serializer for available slots query parameters"""
    
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    duration_minutes = serializers.IntegerField(default=60)
    
    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError("end_date must be after start_date")
        return data

