import pytest
from django.contrib.auth import get_user_model
from accounts.serializers import (
    UserRegistrationSerializer,
    EmployeeRegistrationSerializer,
    UserLoginSerializer,
    CustomUserSerializer,
    UserListSerializer,
    UserDetailSerializer
)

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    """Test suite for UserRegistrationSerializer."""

    def test_valid_registration_data(self):
        """Test serializer with valid registration data."""
        data = {
            'email': 'newuser@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '1234567890'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'newuser@test.com'
        assert user.user_role == 'customer'
        assert user.check_password('testpass123')

    def test_password_mismatch(self):
        """Test validation fails when passwords don't match."""
        data = {
            'email': 'newuser@test.com',
            'password1': 'testpass123',
            'password2': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_password_too_short(self):
        """Test validation fails when password is too short."""
        data = {
            'email': 'newuser@test.com',
            'password1': 'short',
            'password2': 'short',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        data = {
            'email': 'newuser@test.com',
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password1' in serializer.errors
        assert 'password2' in serializer.errors

    def test_invalid_email_format(self):
        """Test validation fails with invalid email format."""
        data = {
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.django_db
class TestEmployeeRegistrationSerializer:
    """Test suite for EmployeeRegistrationSerializer."""

    def test_valid_employee_registration(self):
        """Test serializer creates employee with correct role."""
        data = {
            'email': 'employee@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Employee',
            'last_name': 'User',
            'phone_number': '9876543210'
        }
        serializer = EmployeeRegistrationSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'employee@test.com'
        assert user.user_role == 'employee'
        assert user.check_password('testpass123')

    def test_employee_password_validation(self):
        """Test password validation for employee registration."""
        data = {
            'email': 'employee@test.com',
            'password1': 'testpass123',
            'password2': 'wrongpass',
            'first_name': 'Employee',
            'last_name': 'User'
        }
        serializer = EmployeeRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors


@pytest.mark.django_db
class TestUserLoginSerializer:
    """Test suite for UserLoginSerializer."""

    def test_valid_login_credentials(self, customer_user):
        """Test serializer with valid login credentials."""
        data = {
            'email': 'customer@test.com',
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data == customer_user

    def test_invalid_password(self, customer_user):
        """Test login fails with incorrect password."""
        data = {
            'email': 'customer@test.com',
            'password': 'wrongpassword'
        }
        serializer = UserLoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_nonexistent_user(self):
        """Test login fails with non-existent user."""
        data = {
            'email': 'nonexistent@test.com',
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        assert not serializer.is_valid()

    def test_inactive_user_login(self, inactive_user):
        """Test login fails for inactive user."""
        data = {
            'email': 'inactive@test.com',
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestCustomUserSerializer:
    """Test suite for CustomUserSerializer."""

    def test_serializer_fields(self, customer_user):
        """Test serializer contains correct fields."""
        serializer = CustomUserSerializer(customer_user)
        data = serializer.data
        assert 'id' in data
        assert 'email' in data
        assert 'first_name' in data
        assert 'last_name' in data
        assert 'user_role' in data
        assert 'phone_number' in data
        assert 'created_at' in data
        assert 'is_active' in data
        assert 'password' not in data

    def test_serializer_data_accuracy(self, customer_user):
        """Test serializer returns accurate data."""
        serializer = CustomUserSerializer(customer_user)
        data = serializer.data
        assert data['email'] == 'customer@test.com'
        assert data['first_name'] == 'Customer'
        assert data['last_name'] == 'User'
        assert data['user_role'] == 'customer'


@pytest.mark.django_db
class TestUserListSerializer:
    """Test suite for UserListSerializer."""

    def test_list_serializer_fields(self, customer_user):
        """Test list serializer contains correct fields."""
        serializer = UserListSerializer(customer_user)
        data = serializer.data
        assert 'id' in data
        assert 'email' in data
        assert 'first_name' in data
        assert 'last_name' in data
        assert 'user_role' in data
        assert 'is_active' in data
        assert 'created_at' in data

    def test_multiple_users_serialization(self, customer_user, employee_user, admin_user):
        """Test serializing multiple users."""
        users = [customer_user, employee_user, admin_user]
        serializer = UserListSerializer(users, many=True)
        assert len(serializer.data) == 3


@pytest.mark.django_db
class TestUserDetailSerializer:
    """Test suite for UserDetailSerializer."""

    def test_detail_serializer_fields(self, customer_user):
        """Test detail serializer contains all fields."""
        serializer = UserDetailSerializer(customer_user)
        data = serializer.data
        assert 'id' in data
        assert 'email' in data
        assert 'first_name' in data
        assert 'last_name' in data
        assert 'user_role' in data
        assert 'phone_number' in data
        assert 'is_active' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'last_login' in data

    def test_detail_serializer_update(self, customer_user):
        """Test updating user through serializer."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '1111111111'
        }
        serializer = UserDetailSerializer(customer_user, data=data, partial=True)
        assert serializer.is_valid()
        updated_user = serializer.save()
        assert updated_user.first_name == 'Updated'
        assert updated_user.last_name == 'Name'
        assert updated_user.phone_number == '1111111111'
