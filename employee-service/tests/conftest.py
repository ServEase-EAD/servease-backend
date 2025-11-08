"""
Test fixtures and configuration for employee service tests.
"""
import pytest
import uuid
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from employees.models import Employee, AssignedTask
from timelogs.models import TimeLog, Shift, DailyTimeTotal


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


# User fixtures
@pytest.fixture
def test_user(db):
    """Create a test Django user."""
    user = User.objects.create_user(
        username='testemployee',
        email='test@employee.com',
        password='testpass123',
        first_name='Test',
        last_name='Employee'
    )
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user = User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_superuser=True
    )
    return user


@pytest.fixture
def employee_user(db):
    """Create an employee user."""
    user = User.objects.create_user(
        username='employee',
        email='employee@test.com',
        password='employeepass123',
        first_name='John',
        last_name='Doe'
    )
    return user


# Employee fixtures
@pytest.fixture
def employee_factory(db):
    """Factory to create employee profiles."""
    def _create(**kwargs):
        # Create a user if not provided
        if 'user' not in kwargs:
            user = User.objects.create_user(
                username=f'emp_{uuid.uuid4().hex[:8]}',
                email=f'emp_{uuid.uuid4().hex[:8]}@test.com',
                password='testpass123',
                first_name='Test',
                last_name='Employee'
            )
            kwargs['user'] = user
        
        # Set UUID id if not provided
        if 'id' not in kwargs:
            kwargs['id'] = uuid.uuid4()
        
        defaults = {
            'phone_number': '+1234567890',
            'gender': 'Male',
            'date_of_birth': date(1990, 1, 1),
            'address_line1': '123 Main St',
            'city': 'Springfield',
            'postal_code': '12345',
            'specialization': 'Mechanic',
            'experience_years': 5,
            'hourly_rate': 25.00,
            'is_available': True
        }
        defaults.update(kwargs)
        return Employee.objects.create(**defaults)
    return _create


@pytest.fixture
def sample_employee(employee_factory, test_user):
    """Create a sample employee."""
    return employee_factory(user=test_user, id=test_user.id)


@pytest.fixture
def another_employee(employee_factory):
    """Create another employee for testing."""
    return employee_factory()


# AssignedTask fixtures
@pytest.fixture
def task_factory(db):
    """Factory to create assigned tasks."""
    def _create(employee, **kwargs):
        defaults = {
            'title': 'Test Task',
            'description': 'Test task description',
            'status': 'Pending',
            'due_date': date.today() + timedelta(days=7)
        }
        defaults.update(kwargs)
        return AssignedTask.objects.create(employee=employee, **defaults)
    return _create


@pytest.fixture
def sample_task(sample_employee, task_factory):
    """Create a sample task."""
    return task_factory(sample_employee)


# Shift fixtures
@pytest.fixture
def shift_factory(db):
    """Factory to create shifts."""
    def _create(**kwargs):
        defaults = {
            'employee_id': 1,
            'shift_date': date.today(),
            'start_time': timezone.now(),
            'total_hours': 8.0,
            'is_active': True
        }
        defaults.update(kwargs)
        return Shift.objects.create(**defaults)
    return _create


@pytest.fixture
def active_shift(shift_factory):
    """Create an active shift."""
    return shift_factory(is_active=True)


@pytest.fixture
def completed_shift(shift_factory):
    """Create a completed shift."""
    now = timezone.now()
    return shift_factory(
        start_time=now - timedelta(hours=8),
        end_time=now,
        total_hours=8.0,
        is_active=False
    )


# TimeLog fixtures
@pytest.fixture
def timelog_factory(db):
    """Factory to create time logs."""
    def _create(**kwargs):
        defaults = {
            'employee_id': uuid.uuid4(),
            'task_type': 'appointment',
            'appointment_id': 'APP123',
            'description': 'Oil change service',
            'vehicle': 'Toyota Camry',
            'service': 'Oil Change',
            'start_time': timezone.now(),
            'duration_seconds': 3600,
            'status': 'inprogress'
        }
        defaults.update(kwargs)
        return TimeLog.objects.create(**defaults)
    return _create


@pytest.fixture
def sample_timelog(timelog_factory):
    """Create a sample time log."""
    return timelog_factory()


@pytest.fixture
def completed_timelog(timelog_factory):
    """Create a completed time log."""
    now = timezone.now()
    return timelog_factory(
        start_time=now - timedelta(hours=2),
        end_time=now,
        duration_seconds=7200,
        status='completed'
    )


# DailyTimeTotal fixtures
@pytest.fixture
def daily_total_factory(db):
    """Factory to create daily time totals."""
    def _create(**kwargs):
        defaults = {
            'employee_id': uuid.uuid4(),
            'log_date': date.today(),
            'total_hours': 8.0,
            'total_seconds': 28800,
            'total_tasks': 4,
            'project_tasks_count': 2,
            'appointment_tasks_count': 2,
            'project_hours': 4.0,
            'appointment_hours': 4.0
        }
        defaults.update(kwargs)
        return DailyTimeTotal.objects.create(**defaults)
    return _create


@pytest.fixture
def sample_daily_total(daily_total_factory):
    """Create a sample daily time total."""
    return daily_total_factory()


# Sample data fixtures
@pytest.fixture
def employee_update_data():
    """Sample data for updating employee profile."""
    return {
        'phone_number': '+9876543210',
        'address_line1': '456 Oak Avenue',
        'city': 'Portland',
        'postal_code': '97201'
    }


@pytest.fixture
def task_data():
    """Sample data for creating a task."""
    return {
        'title': 'Engine Repair',
        'description': 'Repair engine issues',
        'status': 'Pending',
        'due_date': (date.today() + timedelta(days=3)).isoformat()
    }


@pytest.fixture
def timelog_data():
    """Sample data for creating a time log."""
    return {
        'task_type': 'appointment',
        'appointment_id': 'APP456',
        'description': 'Brake service',
        'vehicle': 'Honda Civic',
        'service': 'Brake Replacement',
        'start_time': timezone.now().isoformat(),
        'status': 'inprogress'
    }
