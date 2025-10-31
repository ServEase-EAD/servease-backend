from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'email', 
            'phone_number',
            'address',
            'specialization',
            'experience_years',
            'hourly_rate',
            'is_available',
            'created_at',
            'updated_at'
        ]

class AssignedTaskSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    customer_id = serializers.UUIDField()
    vehicle_id = serializers.UUIDField()
    appointment_type = serializers.CharField()
    scheduled_date = serializers.DateField()
    scheduled_time = serializers.TimeField()
    status = serializers.CharField()
    customer_name = serializers.CharField()
    vehicle_details = serializers.CharField()