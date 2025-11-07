"""
Test fixtures and configuration for customer service tests.
"""
import pytest
import uuid
from rest_framework.test import APIClient
from customers.models import Customer
from datetime import datetime, timedelta
from django.utils import timezone


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


class MockUser:
    """Mock user for testing."""
    def __init__(self, user_id=None, email='test@test.com', role='customer', is_authenticated=True):
        self.id = user_id or str(uuid.uuid4())
        self.user_id = uuid.UUID(user_id) if user_id else uuid.uuid4()
        self.email = email
        self.user_role = role
        self.is_authenticated = is_authenticated
        self.first_name = 'Test'
        self.last_name = 'User'


@pytest.fixture
def customer_user():
    """Create a mock customer user."""
    return MockUser(role='customer')


@pytest.fixture
def employee_user():
    """Create a mock employee user."""
    return MockUser(role='employee')


@pytest.fixture
def admin_user():
    """Create a mock admin user."""
    return MockUser(role='admin')


@pytest.fixture
def customer_factory(db):
    """Factory to create customer profiles."""
    def _create(**kwargs):
        defaults = {
            'user_id': uuid.uuid4(),
            'street_address': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'postal_code': '62701',
            'country': 'USA',
            'preferred_contact_method': 'email',
            'notification_preferences': {},
            'is_verified': False,
            'total_services': 0
        }
        defaults.update(kwargs)
        return Customer.objects.create(**defaults)
    return _create


@pytest.fixture
def sample_customer(customer_factory, customer_user):
    """Create a sample customer for testing."""
    return customer_factory(user_id=customer_user.user_id)


@pytest.fixture
def business_customer(customer_factory):
    """Create a business customer for testing."""
    return customer_factory(
        company_name='Acme Corp',
        business_type='Auto Repair',
        tax_id='12-3456789'
    )


@pytest.fixture
def verified_customer(customer_factory):
    """Create a verified customer for testing."""
    return customer_factory(
        is_verified=True,
        total_services=5,
        last_service_date=timezone.now() - timedelta(days=7)
    )


@pytest.fixture
def customer_data():
    """Sample customer data for creation."""
    return {
        'user_id': str(uuid.uuid4()),
        'street_address': '456 Oak Avenue',
        'city': 'Portland',
        'state': 'OR',
        'postal_code': '97201',
        'country': 'USA',
        'preferred_contact_method': 'email',
        'emergency_contact_name': 'Jane Doe',
        'emergency_contact_phone': '+11234567890',
        'emergency_contact_relationship': 'Spouse'
    }


@pytest.fixture
def business_customer_data():
    """Sample business customer data for creation."""
    return {
        'user_id': str(uuid.uuid4()),
        'street_address': '789 Business Blvd',
        'city': 'Seattle',
        'state': 'WA',
        'postal_code': '98101',
        'country': 'USA',
        'company_name': 'Tech Solutions Inc',
        'business_type': 'IT Services',
        'tax_id': '98-7654321',
        'preferred_contact_method': 'phone'
    }


@pytest.fixture
def update_customer_data():
    """Sample data for updating customer profile."""
    return {
        'street_address': '789 Updated Street',
        'city': 'New City',
        'state': 'CA',
        'postal_code': '90210',
        'preferred_contact_method': 'sms'
    }


@pytest.fixture
def mock_auth_service_response():
    """Mock response from authentication service."""
    return {
        'id': str(uuid.uuid4()),
        'email': 'customer@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': '+11234567890',
        'user_role': 'customer',
        'is_active': True
    }
