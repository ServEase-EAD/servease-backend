import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserModel:
    """Test suite for CustomUser model."""

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        assert user.email == 'test@test.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.user_role == 'customer'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password('testpass123')

    def test_create_user_without_email(self):
        """Test creating user without email raises ValueError."""
        with pytest.raises(ValueError, match='The Email field must be set'):
            User.objects.create_user(email='', password='testpass123')

    def test_create_employee(self):
        """Test creating an employee user."""
        user = User.objects.create_employee(
            email='employee@test.com',
            password='testpass123',
            first_name='Employee',
            last_name='User'
        )
        assert user.email == 'employee@test.com'
        assert user.user_role == 'employee'
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        assert user.email == 'admin@test.com'
        assert user.user_role == 'admin'
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_create_superuser_without_is_staff(self):
        """Test creating superuser with is_staff=False raises ValueError."""
        with pytest.raises(ValueError, match='Superuser must have is_staff=True'):
            User.objects.create_superuser(
                email='admin@test.com',
                password='testpass123',
                is_staff=False
            )

    def test_create_superuser_without_is_superuser(self):
        """Test creating superuser with is_superuser=False raises ValueError."""
        with pytest.raises(ValueError, match='Superuser must have is_superuser=True'):
            User.objects.create_superuser(
                email='admin@test.com',
                password='testpass123',
                is_superuser=False
            )

    def test_email_is_normalized(self):
        """Test that email is normalized on user creation."""
        user = User.objects.create_user(
            email='test@TEST.COM',
            password='testpass123'
        )
        assert user.email == 'test@test.com'

    def test_email_uniqueness(self):
        """Test that duplicate emails are not allowed."""
        User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email='test@test.com',
                password='differentpass123'
            )

    def test_user_string_representation(self):
        """Test the string representation of user."""
        user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        assert str(user) == 'test@test.com (Customer)'

    def test_is_admin_method(self):
        """Test is_admin method."""
        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        customer = User.objects.create_user(
            email='customer@test.com',
            password='testpass123'
        )
        assert admin.is_admin() is True
        assert customer.is_admin() is False

    def test_is_employee_method(self):
        """Test is_employee method."""
        employee = User.objects.create_employee(
            email='employee@test.com',
            password='testpass123'
        )
        customer = User.objects.create_user(
            email='customer@test.com',
            password='testpass123'
        )
        assert employee.is_employee() is True
        assert customer.is_employee() is False

    def test_is_customer_method(self):
        """Test is_customer method."""
        customer = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            user_role='customer'
        )
        employee = User.objects.create_employee(
            email='employee@test.com',
            password='testpass123'
        )
        assert customer.is_customer() is True
        assert employee.is_customer() is False

    def test_password_is_hashed(self):
        """Test that password is hashed correctly."""
        user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        assert user.password != 'testpass123'
        assert user.check_password('testpass123') is True
        assert user.check_password('wrongpassword') is False

    def test_user_with_phone_number(self):
        """Test creating user with phone number."""
        user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            phone_number='1234567890'
        )
        assert user.phone_number == '1234567890'

    def test_user_timestamps(self):
        """Test that created_at and updated_at are set."""
        user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_role_choices(self):
        """Test different user roles."""
        customer = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            user_role='customer'
        )
        employee = User.objects.create_employee(
            email='employee@test.com',
            password='testpass123'
        )
        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        
        assert customer.user_role == 'customer'
        assert employee.user_role == 'employee'
        assert admin.user_role == 'admin'
