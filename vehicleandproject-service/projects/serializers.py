from rest_framework import serializers
from .models import Project, Task
from datetime import datetime, timedelta

class BaseProjectSerializer(serializers.ModelSerializer):
    """Base serializer with common validation methods"""
    
    def validate_expected_completion_date(self, value):
        """Validate that the expected completion date is not in the past"""
        if value < datetime.now().date():
            raise serializers.ValidationError("Expected completion date cannot be in the past")
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
        if len(value) > 1000:
            raise serializers.ValidationError("Description cannot exceed 1000 characters")
        return value
    
    def validate_vehicle(self, value):
        """Validate that the vehicle exists and is available"""
        if not value:
            raise serializers.ValidationError("Vehicle is required")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        expected_date = attrs.get('expected_completion_date')
        if expected_date:
            max_future_date = datetime.now().date() + timedelta(days=365)  # 1 year max
            if expected_date > max_future_date:
                raise serializers.ValidationError({
                    'expected_completion_date': 'Expected completion date cannot be more than 1 year in the future'
                })
        return attrs

class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['task_id', 'created_at', 'updated_at']
    
    def validate_due_date(self, value):
        """Validate that the due date is not in the past"""
        if value and value < datetime.now().date():
            raise serializers.ValidationError("Due date cannot be in the past")
        return value
    
    def validate_title(self, value):
        """Validate title length"""
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value


class ProjectSerializer(BaseProjectSerializer):
    """Main serializer for Project CRUD operations"""
    tasks = TaskSerializer(many=True, read_only=True)
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['project_id', 'vehicle', 'customer_id', 'created_at', 'updated_at']
    
    def get_tasks_count(self, obj):
        """Get the count of tasks for this project"""
        return obj.tasks.count()
    
    def validate_status(self, value):
        """Validate status field"""
        valid_statuses = {'accepted', 'cancelled', 'not_started', 'in_progress', 'completed', 'on_hold'}
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
        # def validate_vehicle(self, value):
    #     """Ensure the vehicle exists and is active"""
    #     if not value.is_active:
    #         raise serializers.ValidationError("Cannot assign project to an inactive vehicle")
    #     return value
    
    # def validate_customer_id(self, value):
    #     """Basic validation for customer_id format"""
        

    
class ProjectCreateSerializer(BaseProjectSerializer):
    """Specialized serializer for creating new Projects with minimal fields"""
    
    class Meta:
        model = Project
        fields = [
            'vehicle',
            'title',
            'description',
            'expected_completion_date',
        ]
    
class ProjectUpdateSerializer(BaseProjectSerializer):
    """Specialized serializer for updating existing Projects with limited fields"""
    
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'expected_completion_date',
            'status',
            'approval_status',
            'assigned_employee_id'
        ]
    
    def validate_status(self, value):
        """Validate status field"""
        valid_statuses = {'accepted', 'cancelled', 'not_started', 'in_progress', 'completed', 'on_hold'}
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value

class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects with summary info"""
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'project_id',
            'vehicle',
            'customer_id',
            'title',
            'status',
            'approval_status',
            'description',
            'expected_completion_date',
            'tasks_count',
            'created_at',
        ]
        read_only_fields = fields
    
    def get_tasks_count(self, obj):
        """Get the count of tasks for this project"""
        return obj.tasks.count()


class ProjectApprovalSerializer(serializers.ModelSerializer):
    """Serializer for admin to approve/reject projects"""
    
    class Meta:
        model = Project
        fields = ['approval_status', 'status']
    
    def validate_approval_status(self, value):
        """Validate approval status"""
        valid_statuses = ['pending', 'approved', 'rejected']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Approval status must be one of: {', '.join(valid_statuses)}")
        return value


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    
    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'priority', 'due_date', 'assigned_employee_id']
    
    def validate_title(self, value):
        """Validate title length"""
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'assigned_employee_id']
