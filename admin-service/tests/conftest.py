import pytest
import responses
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AnonymousUser
from unittest.mock import Mock
import uuid


class MockUser:
    """Mock user for testing"""
    def __init__(self, user_id=None, email='test@test.com', user_role='admin', is_authenticated=True):
        self.id = user_id or str(uuid.uuid4())
        self.email = email
        self.user_role = user_role
        self.is_authenticated = is_authenticated
        self.is_superuser = user_role == 'admin'
    
    def __str__(self):
        return self.email


@pytest.fixture
def api_client():
    """Return a DRF API client instance."""
    return APIClient()


@pytest.fixture
def admin_user():
    """Create and return an admin user."""
    return MockUser(user_role='admin', email='admin@test.com')


@pytest.fixture
def employee_user():
    """Create and return an employee user."""
    return MockUser(user_role='employee', email='employee@test.com')


@pytest.fixture
def customer_user():
    """Create and return a customer user."""
    return MockUser(user_role='customer', email='customer@test.com')


@pytest.fixture
def admin_token(admin_user):
    """Generate a mock JWT token for admin user."""
    token = Mock()
    token.payload = {
        'user_id': admin_user.id,
        'email': admin_user.email,
        'user_role': 'admin',
        'exp': 9999999999,
    }
    return 'mock-admin-token-12345'


@pytest.fixture
def employee_token(employee_user):
    """Generate a mock JWT token for employee user."""
    return 'mock-employee-token-67890'


@pytest.fixture
def customer_token(customer_user):
    """Generate a mock JWT token for customer user."""
    return 'mock-customer-token-54321'


@pytest.fixture
def authenticated_admin_client(api_client, admin_user, admin_token):
    """Return an API client authenticated as admin."""
    api_client.force_authenticate(user=admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    return api_client


@pytest.fixture
def authenticated_employee_client(api_client, employee_user, employee_token):
    """Return an API client authenticated as employee."""
    api_client.force_authenticate(user=employee_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {employee_token}')
    return api_client


@pytest.fixture
def authenticated_customer_client(api_client, customer_user, customer_token):
    """Return an API client authenticated as customer."""
    api_client.force_authenticate(user=customer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
    return api_client


@pytest.fixture
def mock_auth_service_url(settings):
    """Return mock auth service URL."""
    settings.AUTH_SERVICE_URL = 'http://localhost:8001'
    return settings.AUTH_SERVICE_URL


@pytest.fixture
def sample_user_data():
    """Return sample user data."""
    return {
        'id': str(uuid.uuid4()),
        'email': 'newuser@test.com',
        'first_name': 'New',
        'last_name': 'User',
        'user_role': 'customer',
        'phone_number': '1234567890',
        'is_active': True,
        'created_at': '2025-11-07T10:00:00Z'
    }


@pytest.fixture
def sample_user_list():
    """Return sample list of users."""
    return [
        {
            'id': str(uuid.uuid4()),
            'email': 'user1@test.com',
            'first_name': 'User',
            'last_name': 'One',
            'user_role': 'customer',
            'is_active': True,
            'created_at': '2025-11-07T10:00:00Z'
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'user2@test.com',
            'first_name': 'User',
            'last_name': 'Two',
            'user_role': 'employee',
            'is_active': True,
            'created_at': '2025-11-07T10:00:00Z'
        }
    ]


@pytest.fixture
def sample_user_stats():
    """Return sample user statistics."""
    return {
        'total_users': 100,
        'total_customers': 70,
        'total_employees': 25,
        'total_admins': 5,
        'active_users': 95,
        'inactive_users': 5
    }


@pytest.fixture
def create_user_data():
    """Return sample data for creating a user."""
    return {
        'email': 'newuser@test.com',
        'first_name': 'New',
        'last_name': 'User',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'user_role': 'customer',
        'phone_number': '1234567890'
    }


@pytest.fixture
def update_user_data():
    """Return sample data for updating a user."""
    return {
        'first_name': 'Updated',
        'last_name': 'Name',
        'phone_number': '9876543210',
        'is_active': True
    }


@pytest.fixture
def enable_responses():
    """Enable responses library for mocking HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps
