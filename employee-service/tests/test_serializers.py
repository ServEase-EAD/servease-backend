"""
Unit tests for employee service serializers.
"""
import pytest
from datetime import date, timedelta
from django.utils import timezone
from employees.serializers import (
    EmployeeProfileSerializer,
    ChangePasswordSerializer,
    AssignedTaskSerializer
)
from timelogs.serializers import (
    TimeLogSerializer,
    TimeLogStatusUpdateSerializer,
    TimeLogListSerializer,
    ShiftSerializer,
    DailyTimeTotalSerializer
)


@pytest.mark.django_db
class TestEmployeeProfileSerializer:
    """Tests for EmployeeProfileSerializer."""
    
    def test_serialize_employee(self, sample_employee):
        """Test serializing an employee profile."""
        serializer = EmployeeProfileSerializer(sample_employee)
        data = serializer.data
        
        assert data['id'] == str(sample_employee.id)
        assert data['email'] == sample_employee.user.email
        assert 'full_name' in data
        assert 'first_name' in data
        assert 'last_name' in data
        assert data['phone_number'] == sample_employee.phone_number
    
    def test_get_full_name(self, sample_employee):
        """Test getting full name."""
        serializer = EmployeeProfileSerializer(sample_employee)
        full_name = serializer.data['full_name']
        
        assert full_name == f"{sample_employee.user.first_name} {sample_employee.user.last_name}"
    
    def test_get_first_name(self, sample_employee):
        """Test getting first name."""
        serializer = EmployeeProfileSerializer(sample_employee)
        assert serializer.data['first_name'] == sample_employee.user.first_name
    
    def test_get_last_name(self, sample_employee):
        """Test getting last name."""
        serializer = EmployeeProfileSerializer(sample_employee)
        assert serializer.data['last_name'] == sample_employee.user.last_name
    
    def test_read_only_fields(self, sample_employee):
        """Test that certain fields are read-only."""
        serializer = EmployeeProfileSerializer(sample_employee)
        read_only = serializer.Meta.read_only_fields
        
        assert 'id' in read_only
        assert 'email' in read_only
        assert 'specialization' in read_only
        assert 'hourly_rate' in read_only
    
    def test_update_allowed_fields(self, sample_employee, employee_update_data):
        """Test updating allowed fields."""
        serializer = EmployeeProfileSerializer(
            sample_employee, 
            data=employee_update_data, 
            partial=True
        )
        assert serializer.is_valid()
        
        updated = serializer.save()
        assert updated.phone_number == employee_update_data['phone_number']
        assert updated.address_line1 == employee_update_data['address_line1']
        assert updated.city == employee_update_data['city']
    
    def test_validate_phone_number_valid(self, sample_employee):
        """Test validating a valid phone number."""
        data = {'phone_number': '+12345678900'}
        serializer = EmployeeProfileSerializer(sample_employee, data=data, partial=True)
        assert serializer.is_valid()
    
    def test_validate_phone_number_too_short(self, sample_employee):
        """Test validation fails for too short phone number."""
        data = {'phone_number': '+1234'}
        serializer = EmployeeProfileSerializer(sample_employee, data=data, partial=True)
        assert not serializer.is_valid()
        assert 'phone_number' in serializer.errors
    
    def test_validate_gender_valid(self, sample_employee):
        """Test validating valid gender values."""
        for gender in ['Male', 'Female', 'Other']:
            data = {'gender': gender}
            serializer = EmployeeProfileSerializer(sample_employee, data=data, partial=True)
            assert serializer.is_valid()
    
    def test_validate_gender_invalid(self, sample_employee):
        """Test validation fails for invalid gender."""
        data = {'gender': 'Invalid'}
        serializer = EmployeeProfileSerializer(sample_employee, data=data, partial=True)
        assert not serializer.is_valid()
        assert 'gender' in serializer.errors


@pytest.mark.django_db
class TestChangePasswordSerializer:
    """Tests for ChangePasswordSerializer."""
    
    def test_validate_current_password_correct(self, test_user, api_client):
        """Test validation with correct current password."""
        test_user.set_password('oldpass123')
        test_user.save()
        
        api_client.force_authenticate(user=test_user)
        request = api_client.request()
        request.user = test_user
        
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123!',
            'confirm_password': 'newpass123!'
        }
        
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        assert serializer.is_valid()
    
    def test_validate_current_password_incorrect(self, test_user, api_client):
        """Test validation fails with incorrect current password."""
        test_user.set_password('oldpass123')
        test_user.save()
        
        api_client.force_authenticate(user=test_user)
        request = api_client.request()
        request.user = test_user
        
        data = {
            'current_password': 'wrongpass',
            'new_password': 'newpass123!',
            'confirm_password': 'newpass123!'
        }
        
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'current_password' in serializer.errors
    
    def test_validate_passwords_match(self, test_user, api_client):
        """Test validation that new passwords match."""
        test_user.set_password('oldpass123')
        test_user.save()
        
        api_client.force_authenticate(user=test_user)
        request = api_client.request()
        request.user = test_user
        
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123!',
            'confirm_password': 'different123!'
        }
        
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestAssignedTaskSerializer:
    """Tests for AssignedTaskSerializer."""
    
    def test_serialize_task(self, sample_task):
        """Test serializing an assigned task."""
        serializer = AssignedTaskSerializer(sample_task)
        data = serializer.data
        
        assert data['title'] == sample_task.title
        assert data['description'] == sample_task.description
        assert data['status'] == sample_task.status
        assert 'employee' in data


@pytest.mark.django_db
class TestTimeLogSerializer:
    """Tests for TimeLogSerializer."""
    
    def test_serialize_timelog(self, sample_timelog):
        """Test serializing a time log."""
        serializer = TimeLogSerializer(sample_timelog)
        data = serializer.data
        
        assert 'log_id' in data
        assert 'employee_id' in data
        assert data['task_type'] == sample_timelog.task_type
        assert data['description'] == sample_timelog.description
        assert 'duration' in data
    
    def test_get_duration_formatted(self, timelog_factory):
        """Test getting formatted duration."""
        timelog = timelog_factory(duration_seconds=7200)  # 2 hours
        serializer = TimeLogSerializer(timelog)
        
        assert serializer.data['duration'] == "02:00:00"
    
    def test_validate_project_task_requires_project_id(self):
        """Test validation requires project_id for project tasks."""
        data = {
            'task_type': 'project',
            'description': 'Project work',
            'start_time': timezone.now().isoformat(),
            'status': 'inprogress'
        }
        
        serializer = TimeLogSerializer(data=data)
        assert not serializer.is_valid()
        assert 'project_id' in serializer.errors
    
    def test_validate_appointment_task_requires_appointment_id(self):
        """Test validation requires appointment_id for appointment tasks."""
        data = {
            'task_type': 'appointment',
            'description': 'Service work',
            'start_time': timezone.now().isoformat(),
            'status': 'inprogress'
        }
        
        serializer = TimeLogSerializer(data=data)
        assert not serializer.is_valid()
        assert 'appointment_id' in serializer.errors
    
    def test_read_only_fields(self):
        """Test that certain fields are read-only."""
        serializer = TimeLogSerializer()
        read_only = serializer.Meta.read_only_fields
        
        assert 'log_id' in read_only
        assert 'employee_id' in read_only
        assert 'log_date' in read_only


@pytest.mark.django_db
class TestTimeLogStatusUpdateSerializer:
    """Tests for TimeLogStatusUpdateSerializer."""
    
    def test_update_status(self, sample_timelog):
        """Test updating time log status."""
        data = {'status': 'completed'}
        serializer = TimeLogStatusUpdateSerializer(sample_timelog, data=data, partial=True)
        
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.status == 'completed'
    
    def test_validate_status_invalid(self, sample_timelog):
        """Test validation fails for invalid status."""
        data = {'status': 'invalid_status'}
        serializer = TimeLogStatusUpdateSerializer(sample_timelog, data=data, partial=True)
        
        assert not serializer.is_valid()
        assert 'status' in serializer.errors


@pytest.mark.django_db
class TestTimeLogListSerializer:
    """Tests for TimeLogListSerializer."""
    
    def test_serialize_timelog_list(self, sample_timelog):
        """Test lightweight serialization for lists."""
        serializer = TimeLogListSerializer(sample_timelog)
        data = serializer.data
        
        assert 'log_id' in data
        assert 'task_type' in data
        assert 'description' in data
        assert 'duration' in data
        assert 'status' in data


@pytest.mark.django_db
class TestShiftSerializer:
    """Tests for ShiftSerializer."""
    
    def test_serialize_shift(self, active_shift):
        """Test serializing a shift."""
        serializer = ShiftSerializer(active_shift)
        data = serializer.data
        
        assert 'shift_id' in data
        assert 'employee_id' in data
        assert data['shift_date'] == str(active_shift.shift_date)
        assert data['is_active'] == active_shift.is_active
    
    def test_serialize_shift_with_timelogs(self, active_shift, timelog_factory):
        """Test serializing shift with time logs."""
        timelog_factory(shift=active_shift)
        timelog_factory(shift=active_shift)
        
        serializer = ShiftSerializer(active_shift)
        data = serializer.data
        
        assert 'time_logs' in data
        assert len(data['time_logs']) == 2


@pytest.mark.django_db
class TestDailyTimeTotalSerializer:
    """Tests for DailyTimeTotalSerializer."""
    
    def test_serialize_daily_total(self, sample_daily_total):
        """Test serializing daily time total."""
        serializer = DailyTimeTotalSerializer(sample_daily_total)
        data = serializer.data
        
        assert 'id' in data
        assert 'employee_id' in data
        assert 'log_date' in data
        assert float(data['total_hours']) == float(sample_daily_total.total_hours)
        assert 'total_hours_formatted' in data
    
    def test_get_total_hours_formatted(self, daily_total_factory):
        """Test getting formatted total hours."""
        total = daily_total_factory(total_hours=12.50)
        serializer = DailyTimeTotalSerializer(total)
        
        assert serializer.data['total_hours_formatted'] == "12.50h"
    
    def test_task_breakdown_fields(self, sample_daily_total):
        """Test task breakdown fields are included."""
        serializer = DailyTimeTotalSerializer(sample_daily_total)
        data = serializer.data
        
        assert 'project_tasks_count' in data
        assert 'appointment_tasks_count' in data
        assert 'project_hours' in data
        assert 'appointment_hours' in data
