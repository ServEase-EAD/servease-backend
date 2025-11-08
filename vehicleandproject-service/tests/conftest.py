"""
Pytest configuration and fixtures for vehicleandproject service tests.

This module provides reusable fixtures for testing vehicles, projects, and tasks.
"""

import pytest
import uuid
from datetime import datetime, timedelta, date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from faker import Faker

from vehicles.models import Vehicle
from projects.models import Project, Task

fake = Faker()


# ==================== Django Setup ====================

@pytest.fixture(scope='session')
def django_db_setup():
    """Setup test database."""
    pass


# ==================== User Fixtures ====================

@pytest.fixture
def test_user(db):
    """Create a test customer user."""
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    user.user_role = 'customer'
    user.save()
    return user


@pytest.fixture
def employee_user(db):
    """Create an employee user."""
    User = get_user_model()
    user = User.objects.create_user(
        username='employeeuser',
        email='employee@example.com',
        password='emppass123',
        first_name='Employee',
        last_name='User'
    )
    user.user_role = 'employee'
    user.save()
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    User = get_user_model()
    user = User.objects.create_superuser(
        username='adminuser',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )
    user.user_role = 'admin'
    user.save()
    return user


@pytest.fixture
def customer_user_id():
    """Generate a customer UUID for testing."""
    return uuid.uuid4()


@pytest.fixture
def employee_user_id():
    """Generate an employee UUID for testing."""
    return uuid.uuid4()


# ==================== API Client Fixtures ====================

@pytest.fixture
def api_client():
    """Create a basic API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(test_user):
    """Create an authenticated API client for customer."""
    client = APIClient()
    refresh = RefreshToken.for_user(test_user)
    refresh['user_role'] = 'customer'
    refresh['user_id'] = str(uuid.uuid4())
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def employee_client(employee_user):
    """Create an authenticated API client for employee."""
    client = APIClient()
    refresh = RefreshToken.for_user(employee_user)
    refresh['user_role'] = 'employee'
    refresh['user_id'] = str(uuid.uuid4())
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def admin_client(admin_user):
    """Create an authenticated API client for admin."""
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    refresh['user_role'] = 'admin'
    refresh['user_id'] = str(uuid.uuid4())
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


# ==================== Vehicle Fixtures ====================

@pytest.fixture
def vehicle_factory(db):
    """Factory for creating vehicle instances."""
    def create_vehicle(**kwargs):
        # Generate unique VIN if not provided
        if 'vin' not in kwargs:
            kwargs['vin'] = f'VIN{uuid.uuid4().hex[:14].upper()}'  # 17 chars: VIN + 14 hex chars
        
        # Generate unique plate if not provided  
        if 'plate_number' not in kwargs:
            kwargs['plate_number'] = f'P{uuid.uuid4().hex[:6].upper()}'  # 7 chars total
        
        defaults = {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'color': 'Silver',
            'customer_id': uuid.uuid4(),
            'is_active': True,
        }
        defaults.update(kwargs)
        return Vehicle.objects.create(**defaults)
    return create_vehicle


@pytest.fixture
def sample_vehicle(vehicle_factory, customer_user_id):
    """Create a sample vehicle for testing."""
    return vehicle_factory(
        make='Honda',
        model='Accord',
        year=2019,
        color='Blue',
        vin='1HGBH41JXMN109186',
        plate_number='XYZ789',
        customer_id=customer_user_id
    )


@pytest.fixture
def multiple_vehicles(vehicle_factory, customer_user_id):
    """Create multiple vehicles for testing."""
    vehicles = []
    vins = ['1HGCM82633A123456', '2T3ZFREV1HW123456', '3VW2B7AJ8KM123456']
    plates = ['AAA111', 'BBB222', 'CCC333']
    
    for i, (vin, plate) in enumerate(zip(vins, plates)):
        vehicle = vehicle_factory(
            make=fake.company(),
            model=f'Model{i+1}',
            year=2020 + i,
            color=fake.color_name(),
            vin=vin,
            plate_number=plate,
            customer_id=customer_user_id
        )
        vehicles.append(vehicle)
    
    return vehicles


@pytest.fixture
def inactive_vehicle(vehicle_factory, customer_user_id):
    """Create an inactive vehicle for testing."""
    return vehicle_factory(
        make='Ford',
        model='F-150',
        year=2015,
        color='Black',
        vin='1FTFW1ET5BFC12345',
        plate_number='OLD123',
        customer_id=customer_user_id,
        is_active=False
    )


@pytest.fixture
def valid_vehicle_data(customer_user_id):
    """Sample valid vehicle data for POST requests."""
    return {
        'make': 'BMW',
        'model': 'X5',
        'year': 2022,
        'color': 'White',
        'vin': 'WBAFR7C50BC123456',
        'plate_number': 'BMW999',
        'customer_id': str(customer_user_id),
    }


# ==================== Project Fixtures ====================

@pytest.fixture
def project_factory(db):
    """Factory for creating project instances."""
    def create_project(**kwargs):
        # Create a vehicle if not provided
        if 'vehicle' not in kwargs:
            vehicle = Vehicle.objects.create(
                make='Toyota',
                model='Camry',
                year=2020,
                color='Silver',
                vin=f'TEST{uuid.uuid4().hex[:13].upper()}',
                plate_number=f'T{uuid.uuid4().hex[:5].upper()}',
                customer_id=uuid.uuid4(),
            )
            kwargs['vehicle'] = vehicle
        
        defaults = {
            'customer_id': uuid.uuid4(),
            'title': 'Sample Project',
            'description': 'This is a sample project description with sufficient length.',
            'expected_completion_date': date.today() + timedelta(days=30),
            'status': 'not_started',
            'approval_status': 'pending',
        }
        defaults.update(kwargs)
        return Project.objects.create(**defaults)
    return create_project


@pytest.fixture
def sample_project(project_factory, sample_vehicle, customer_user_id):
    """Create a sample project for testing."""
    return project_factory(
        vehicle=sample_vehicle,
        customer_id=customer_user_id,
        title='Engine Repair',
        description='Complete engine overhaul and timing belt replacement.',
        expected_completion_date=date.today() + timedelta(days=14),
        status='not_started',
        approval_status='pending'
    )


@pytest.fixture
def approved_project(project_factory, sample_vehicle, customer_user_id):
    """Create an approved project for testing."""
    return project_factory(
        vehicle=sample_vehicle,
        customer_id=customer_user_id,
        title='Oil Change Service',
        description='Regular oil change and filter replacement service.',
        expected_completion_date=date.today() + timedelta(days=7),
        status='in_progress',
        approval_status='approved'
    )


@pytest.fixture
def completed_project(project_factory, sample_vehicle, customer_user_id):
    """Create a completed project for testing."""
    return project_factory(
        vehicle=sample_vehicle,
        customer_id=customer_user_id,
        title='Brake Replacement',
        description='Replaced front and rear brake pads and rotors.',
        expected_completion_date=date.today() - timedelta(days=1),
        status='completed',
        approval_status='approved'
    )


@pytest.fixture
def valid_project_data(sample_vehicle):
    """Sample valid project data for POST requests."""
    return {
        'vehicle': sample_vehicle.vehicle_id,
        'title': 'Transmission Service',
        'description': 'Full transmission fluid flush and filter replacement service.',
        'expected_completion_date': (date.today() + timedelta(days=21)).isoformat(),
    }


# ==================== Task Fixtures ====================

@pytest.fixture
def task_factory(db):
    """Factory for creating task instances."""
    def create_task(**kwargs):
        # Create a project if not provided
        if 'project' not in kwargs:
            vehicle = Vehicle.objects.create(
                make='Toyota',
                model='Camry',
                year=2020,
                color='Silver',
                vin=f'TASK{uuid.uuid4().hex[:13].upper()}',
                plate_number=f'TSK{uuid.uuid4().hex[:4].upper()}',
                customer_id=uuid.uuid4(),
            )
            project = Project.objects.create(
                vehicle=vehicle,
                customer_id=uuid.uuid4(),
                title='Test Project',
                description='Test project for task creation.',
                expected_completion_date=date.today() + timedelta(days=30),
            )
            kwargs['project'] = project
        
        defaults = {
            'title': 'Sample Task',
            'description': 'Sample task description',
            'status': 'not_started',
            'priority': 'medium',
            'due_date': date.today() + timedelta(days=7),
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)
    return create_task


@pytest.fixture
def sample_task(task_factory, sample_project, employee_user_id):
    """Create a sample task for testing."""
    return task_factory(
        project=sample_project,
        title='Remove Engine Cover',
        description='Carefully remove engine cover and inspect components.',
        status='not_started',
        priority='high',
        due_date=date.today() + timedelta(days=3),
        assigned_employee_id=employee_user_id
    )


@pytest.fixture
def completed_task(task_factory, approved_project, employee_user_id):
    """Create a completed task for testing."""
    return task_factory(
        project=approved_project,
        title='Drain Old Oil',
        description='Drain old oil and remove old filter.',
        status='completed',
        priority='medium',
        due_date=date.today(),
        assigned_employee_id=employee_user_id,
        duration_seconds=1800  # 30 minutes
    )


@pytest.fixture
def multiple_tasks(task_factory, sample_project, employee_user_id):
    """Create multiple tasks for testing."""
    tasks = []
    task_data = [
        {'title': 'Inspect Engine', 'priority': 'high', 'status': 'completed'},
        {'title': 'Replace Parts', 'priority': 'critical', 'status': 'in_progress'},
        {'title': 'Test Drive', 'priority': 'medium', 'status': 'not_started'},
        {'title': 'Final Cleanup', 'priority': 'low', 'status': 'not_started'},
    ]
    
    for data in task_data:
        task = task_factory(
            project=sample_project,
            assigned_employee_id=employee_user_id,
            **data
        )
        tasks.append(task)
    
    return tasks


@pytest.fixture
def valid_task_data(sample_project, employee_user_id):
    """Sample valid task data for POST requests."""
    return {
        'project': sample_project.project_id,
        'title': 'Quality Check',
        'description': 'Perform final quality inspection.',
        'priority': 'high',
        'due_date': (date.today() + timedelta(days=5)).isoformat(),
        'assigned_employee_id': str(employee_user_id),
    }


# ==================== Mock Data Fixtures ====================

@pytest.fixture
def invalid_vin_data():
    """Invalid VIN examples for validation testing."""
    return [
        'SHORT',  # Too short
        '12345678901234567890',  # Too long
        'ABCDEFGHIJK123IOQ',  # Contains invalid chars (I, O, Q)
        '12345-67890-12345',  # Invalid format
    ]


@pytest.fixture
def invalid_plate_data():
    """Invalid plate number examples for validation testing."""
    return [
        'A',  # Too short
        'ABCDEFGHIJK',  # Too long
        'abc@123',  # Invalid characters
        '   ',  # Only spaces
    ]
