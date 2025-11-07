import pytest
from django.test import RequestFactory
from admin_api.permissions import IsAdminUser
from unittest.mock import Mock


@pytest.mark.unit
class TestIsAdminUserPermission:
    """Test suite for IsAdminUser permission class."""

    def setup_method(self):
        """Set up request factory for each test."""
        self.factory = RequestFactory()
        self.permission = IsAdminUser()

    def test_admin_user_has_permission(self, admin_user):
        """Test that admin user has permission."""
        request = self.factory.get('/')
        request.user = admin_user
        request.auth = None
        assert self.permission.has_permission(request, None) is True

    def test_employee_user_no_permission(self, employee_user):
        """Test that employee user does not have permission."""
        request = self.factory.get('/')
        request.user = employee_user
        request.auth = None
        assert self.permission.has_permission(request, None) is False

    def test_customer_user_no_permission(self, customer_user):
        """Test that customer user does not have permission."""
        request = self.factory.get('/')
        request.user = customer_user
        request.auth = None
        assert self.permission.has_permission(request, None) is False

    def test_unauthenticated_user_no_permission(self):
        """Test that unauthenticated user does not have permission."""
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.auth = None
        assert self.permission.has_permission(request, None) is False

    def test_admin_from_token_payload(self):
        """Test admin permission from token payload."""
        request = self.factory.get('/')
        # Create a simple object without user_role
        request.user = type('User', (), {'is_authenticated': True})()
        
        # Mock token with admin role in payload
        request.auth = Mock()
        request.auth.payload = {'user_role': 'admin'}
        
        assert self.permission.has_permission(request, None) is True

    def test_non_admin_from_token_payload(self):
        """Test non-admin permission from token payload."""
        request = self.factory.get('/')
        # Create a simple object without user_role
        request.user = type('User', (), {'is_authenticated': True})()
        
        # Mock token with customer role
        request.auth = Mock()
        request.auth.payload = {'user_role': 'customer'}
        
        assert self.permission.has_permission(request, None) is False

    def test_superuser_has_permission(self):
        """Test that superuser has permission as fallback."""
        request = self.factory.get('/')
        # Create a user object with is_superuser property
        class SuperUser:
            is_authenticated = True
            is_superuser = True
        
        request.user = SuperUser()
        request.auth = None  # No auth token
        
        assert self.permission.has_permission(request, None) is True

    def test_none_user_no_permission(self):
        """Test that None user does not have permission."""
        request = self.factory.get('/')
        request.user = None
        request.auth = None
        assert self.permission.has_permission(request, None) is False
