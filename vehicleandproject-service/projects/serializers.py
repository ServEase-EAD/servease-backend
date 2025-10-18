from rest_framework import serializers
from .models import Project
from datetime import datetime

class ProjectSerializer(serializers.ModelSerializer):
    """Main serializer for Project CRUD operations"""

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['project_id', 'vehicle', 'customer_id', 'created_at', 'updated_at']
    
    def validate_expected_completion_date(self, value):
        """Validate that the expected completion date is not in the past"""
        if value < datetime.now().date():
            raise serializers.ValidationError("Expected completion date cannot be in the past")
        return value
    
    def validate_status(self, value):
        """Validate status field"""
        valid_statuses = {'accepted', 'cancelled', 'not_started', 'in_progress', 'completed', 'on_hold'}
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate_title(self, value):
        """Validate title length"""
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value
    
    def validate_description(self, value):
        """Validate description length"""
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long")
        return value
    
    # def validate_vehicle(self, value):
    #     """Ensure the vehicle exists and is active"""
    #     if not value.is_active:
    #         raise serializers.ValidationError("Cannot assign project to an inactive vehicle")
    #     return value
    
    # def validate_customer_id(self, value):
    #     """Basic validation for customer_id format"""
        

    
class ProjectCreateSerializer(serializers.ModelSerializer):
    """Specialized serializer for creating new Projects with minimal fields"""
    
    class Meta:
        model = Project
        fields = [
            'vehicle',
            'title',
            'description',
            'expected_completion_date',
        ]
    
class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Specialized serializer for updating existing Projects with limited fields"""
    
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'expected_completion_date',
            'status',
        ]

class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects with summary info"""
    
    class Meta:
        model = Project
        fields = [
            'project_id',
            'vehicle',
            'customer_id',
            'title',
            'status',
            'description',
            'expected_completion_date',
            'created_at',
        ]
        read_only_fields = fields
