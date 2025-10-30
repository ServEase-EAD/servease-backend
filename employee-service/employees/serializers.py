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