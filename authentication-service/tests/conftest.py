import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Return a DRF API client instance."""
    return APIClient()


@pytest.fixture
def customer_user(db):
    """Create and return a customer user."""
    user = User.objects.create_user(
        email='customer@test.com',
        password='testpass123',
        first_name='Customer',
        last_name='User',
        user_role='customer',
        phone_number='1234567890'
    )
    return user


@pytest.fixture
def employee_user(db):
    """Create and return an employee user."""
    user = User.objects.create_employee(
        email='employee@test.com',
        password='testpass123',
        first_name='Employee',
        last_name='User',
        phone_number='0987654321'
    )
    return user


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    user = User.objects.create_superuser(
        email='admin@test.com',
        password='testpass123',
        first_name='Admin',
        last_name='User',
        phone_number='1112223333'
    )
    return user


@pytest.fixture
def inactive_user(db):
    """Create and return an inactive user."""
    user = User.objects.create_user(
        email='inactive@test.com',
        password='testpass123',
        first_name='Inactive',
        last_name='User',
        user_role='customer'
    )
    user.is_active = False
    user.save()
    return user


@pytest.fixture
def customer_token(customer_user):
    """Generate JWT token for customer user."""
    refresh = RefreshToken.for_user(customer_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


@pytest.fixture
def employee_token(employee_user):
    """Generate JWT token for employee user."""
    refresh = RefreshToken.for_user(employee_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


@pytest.fixture
def admin_token(admin_user):
    """Generate JWT token for admin user."""
    refresh = RefreshToken.for_user(admin_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


@pytest.fixture
def authenticated_customer_client(api_client, customer_token):
    """Return an API client authenticated as a customer."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token["access"]}')
    return api_client


@pytest.fixture
def authenticated_employee_client(api_client, employee_token):
    """Return an API client authenticated as an employee."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {employee_token["access"]}')
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, admin_token):
    """Return an API client authenticated as an admin."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token["access"]}')
    return api_client


@pytest.fixture
def user_registration_data():
    """Return valid user registration data."""
    return {
        'email': 'newuser@test.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'first_name': 'New',
        'last_name': 'User',
        'phone_number': '5556667777'
    }


@pytest.fixture
def employee_registration_data():
    """Return valid employee registration data."""
    return {
        'email': 'newemployee@test.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'first_name': 'New',
        'last_name': 'Employee',
        'phone_number': '4445556666'
    }
