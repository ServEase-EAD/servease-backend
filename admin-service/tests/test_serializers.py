import pytest
from admin_api.serializers import (
    UserSerializer,
    UserListSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
    UpdateUserRoleSerializer,
    UserStatsSerializer
)
import uuid


@pytest.mark.unit
class TestUserSerializer:
    """Test suite for UserSerializer."""

    def test_valid_user_serialization(self, sample_user_data):
        """Test serializing valid user data."""
        serializer = UserSerializer(data=sample_user_data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'newuser@test.com'
        assert serializer.validated_data['user_role'] == 'customer'

    def test_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        data = {'email': 'test@test.com'}
        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'first_name' in serializer.errors

    def test_invalid_email_format(self, sample_user_data):
        """Test validation fails with invalid email."""
        sample_user_data['email'] = 'invalid-email'
        serializer = UserSerializer(data=sample_user_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.unit
class TestUserListSerializer:
    """Test suite for UserListSerializer."""

    def test_valid_user_list_serialization(self, sample_user_data):
        """Test serializing user list data."""
        serializer = UserListSerializer(data=sample_user_data)
        assert serializer.is_valid()

    def test_multiple_users_serialization(self, sample_user_list):
        """Test serializing multiple users."""
        serializer = UserListSerializer(data=sample_user_list, many=True)
        assert serializer.is_valid()
        assert len(serializer.validated_data) == 2


@pytest.mark.unit
class TestCreateUserSerializer:
    """Test suite for CreateUserSerializer."""

    def test_valid_user_creation(self, create_user_data):
        """Test creating user with valid data."""
        serializer = CreateUserSerializer(data=create_user_data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'newuser@test.com'

    def test_password_mismatch(self, create_user_data):
        """Test validation fails when passwords don't match."""
        create_user_data['password2'] = 'differentpass'
        serializer = CreateUserSerializer(data=create_user_data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_password_too_short(self, create_user_data):
        """Test validation fails with short password."""
        create_user_data['password1'] = 'short'
        create_user_data['password2'] = 'short'
        serializer = CreateUserSerializer(data=create_user_data)
        assert not serializer.is_valid()
        assert 'password1' in serializer.errors

    def test_invalid_user_role(self, create_user_data):
        """Test validation fails with invalid user role."""
        create_user_data['user_role'] = 'invalid_role'
        serializer = CreateUserSerializer(data=create_user_data)
        assert not serializer.is_valid()
        assert 'user_role' in serializer.errors

    def test_missing_required_fields(self):
        """Test validation fails with missing fields."""
        data = {'email': 'test@test.com'}
        serializer = CreateUserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'first_name' in serializer.errors
        assert 'password1' in serializer.errors


@pytest.mark.unit
class TestUpdateUserSerializer:
    """Test suite for UpdateUserSerializer."""

    def test_valid_user_update(self, update_user_data):
        """Test updating user with valid data."""
        serializer = UpdateUserSerializer(data=update_user_data)
        assert serializer.is_valid()
        assert serializer.validated_data['first_name'] == 'Updated'

    def test_partial_update(self):
        """Test partial update with only some fields."""
        data = {'first_name': 'NewName'}
        serializer = UpdateUserSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['first_name'] == 'NewName'

    def test_empty_update(self):
        """Test update with empty data."""
        serializer = UpdateUserSerializer(data={})
        assert serializer.is_valid()


@pytest.mark.unit
class TestUpdateUserRoleSerializer:
    """Test suite for UpdateUserRoleSerializer."""

    def test_valid_role_update(self):
        """Test updating role with valid role."""
        data = {'user_role': 'employee'}
        serializer = UpdateUserRoleSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['user_role'] == 'employee'

    def test_invalid_role(self):
        """Test validation fails with invalid role."""
        data = {'user_role': 'invalid_role'}
        serializer = UpdateUserRoleSerializer(data=data)
        assert not serializer.is_valid()
        assert 'user_role' in serializer.errors

    def test_missing_role(self):
        """Test validation fails without role."""
        serializer = UpdateUserRoleSerializer(data={})
        assert not serializer.is_valid()
        assert 'user_role' in serializer.errors


@pytest.mark.unit
class TestUserStatsSerializer:
    """Test suite for UserStatsSerializer."""

    def test_valid_stats_serialization(self, sample_user_stats):
        """Test serializing user statistics."""
        serializer = UserStatsSerializer(data=sample_user_stats)
        assert serializer.is_valid()
        assert serializer.validated_data['total_users'] == 100
        assert serializer.validated_data['total_customers'] == 70

    def test_missing_stats_field(self, sample_user_stats):
        """Test validation fails with missing field."""
        del sample_user_stats['total_users']
        serializer = UserStatsSerializer(data=sample_user_stats)
        assert not serializer.is_valid()
        assert 'total_users' in serializer.errors

    def test_invalid_stats_type(self, sample_user_stats):
        """Test validation fails with invalid data type."""
        sample_user_stats['total_users'] = 'invalid'
        serializer = UserStatsSerializer(data=sample_user_stats)
        assert not serializer.is_valid()
        assert 'total_users' in serializer.errors
