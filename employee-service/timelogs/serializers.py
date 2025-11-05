from rest_framework import serializers
from .models import TimeLog, Shift, DailyTimeTotal
from datetime import datetime

class TimeLogSerializer(serializers.ModelSerializer):
    """Main serializer for TimeLog CRUD"""
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeLog
        fields = [
            'log_id',
            'employee_id',
            'shift',
            'task_type',
            'project_id',
            'appointment_id',
            'description',
            'vehicle',
            'service',
            'log_date',
            'start_time',
            'end_time',
            'duration_seconds',
            'duration',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['log_id', 'employee_id', 'log_date', 'created_at', 'updated_at', 'duration']
    
    def get_duration(self, obj):
        return obj.duration_formatted
    
    def validate(self, data):
        """Validate that the appropriate ID is provided based on task_type"""
        task_type = data.get('task_type')
        
        if task_type == 'project':
            if not data.get('project_id'):
                raise serializers.ValidationError({
                    'project_id': 'project_id is required when task_type is project'
                })
        elif task_type == 'appointment':
            if not data.get('appointment_id'):
                raise serializers.ValidationError({
                    'appointment_id': 'appointment_id is required when task_type is appointment'
                })
        
        return data


class TimeLogStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating only the status field - employees can only change status"""
    class Meta:
        model = TimeLog
        fields = ['status']
    
    def validate_status(self, value):
        """Validate that the status is valid"""
        valid_statuses = ['not_started', 'inprogress', 'paused', 'completed']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value


class TimeLogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing"""
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeLog
        fields = [
            'log_id', 
            'task_type',
            'project_id',
            'appointment_id',
            'description', 
            'vehicle', 
            'service', 
            'duration', 
            'status', 
            'log_date',
            'start_time'
        ]
    
    def get_duration(self, obj):
        return obj.duration_formatted


class ShiftSerializer(serializers.ModelSerializer):
    """Shift tracking serializer"""
    time_logs = TimeLogListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shift
        fields = [
            'shift_id',
            'employee_id',
            'shift_date',
            'start_time',
            'end_time',
            'total_hours',
            'is_active',
            'time_logs',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['shift_id', 'created_at', 'updated_at']


class DailyTimeTotalSerializer(serializers.ModelSerializer):
    """Serializer for daily time totals"""
    total_hours_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyTimeTotal
        fields = [
            'id',
            'employee_id',
            'log_date',
            'total_hours',
            'total_hours_formatted',
            'total_seconds',
            'total_tasks',
            'project_tasks_count',
            'appointment_tasks_count',
            'project_hours',
            'appointment_hours',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_hours_formatted(self, obj):
        return obj.total_hours_formatted