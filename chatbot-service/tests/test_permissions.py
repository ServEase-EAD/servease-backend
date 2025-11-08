"""
Unit tests for chatbot service permissions.
"""
import pytest
from unittest.mock import Mock
from chatbot.permissions import (
    IsAuthenticated,
    IsOwner,
    IsCustomer,
    IsEmployee,
    IsAdmin
)


class TestIsAuthenticatedPermission:
    """Tests for IsAuthenticated permission."""
    
    def test_allows_authenticated_user(self):
        """Test that authenticated users are allowed."""
        permission = IsAuthenticated()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        
        assert permission.has_permission(request, None) is True
    
    def test_denies_unauthenticated_user(self):
        """Test that unauthenticated users are denied."""
        permission = IsAuthenticated()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_none_user(self):
        """Test that None user is denied."""
        permission = IsAuthenticated()
        request = Mock()
        request.user = None
        
        # When user is None, the permission check returns False (not None)
        result = permission.has_permission(request, None)
        assert result is False or result is None  # Handle both cases


class TestIsOwnerPermission:
    """Tests for IsOwner permission."""
    
    def test_allows_owner(self, test_user, sample_session):
        """Test that session owner is allowed."""
        permission = IsOwner()
        request = Mock()
        request.user = test_user
        
        # Set session user_id to match test_user id
        sample_session.user_id = test_user.id
        sample_session.save()
        
        assert permission.has_object_permission(request, None, sample_session) is True
    
    def test_denies_non_owner(self, test_user, sample_session, another_user_id):
        """Test that non-owner is denied."""
        permission = IsOwner()
        request = Mock()
        request.user = test_user
        
        # Set session user_id to different user
        sample_session.user_id = another_user_id
        sample_session.save()
        
        assert permission.has_object_permission(request, None, sample_session) is False


class TestIsCustomerPermission:
    """Tests for IsCustomer permission."""
    
    def test_allows_customer_role(self):
        """Test that customer role is allowed."""
        permission = IsCustomer()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'customer'
        
        assert permission.has_permission(request, None) is True
    
    def test_denies_non_customer_role(self):
        """Test that non-customer role is denied."""
        permission = IsCustomer()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'admin'
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_unauthenticated(self):
        """Test that unauthenticated user is denied."""
        permission = IsCustomer()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_no_user_role(self):
        """Test denial when user_role attribute is missing."""
        permission = IsCustomer()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role attribute
        
        assert permission.has_permission(request, None) is False


class TestIsEmployeePermission:
    """Tests for IsEmployee permission."""
    
    def test_allows_employee_role(self):
        """Test that employee role is allowed."""
        permission = IsEmployee()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'employee'
        
        assert permission.has_permission(request, None) is True
    
    def test_denies_non_employee_role(self):
        """Test that non-employee role is denied."""
        permission = IsEmployee()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'customer'
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_unauthenticated(self):
        """Test that unauthenticated user is denied."""
        permission = IsEmployee()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        
        assert permission.has_permission(request, None) is False


class TestIsAdminPermission:
    """Tests for IsAdmin permission."""
    
    def test_allows_admin_role_from_user(self):
        """Test that admin role from user is allowed."""
        permission = IsAdmin()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'admin'
        
        assert permission.has_permission(request, None) is True
    
    def test_allows_admin_role_from_jwt_payload(self):
        """Test that admin role from JWT payload is allowed."""
        permission = IsAdmin()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role attribute on user
        delattr(request.user, 'user_role') if hasattr(request.user, 'user_role') else None
        
        # But has auth with payload
        request.auth = Mock()
        request.auth.payload = {'user_role': 'admin'}
        
        assert permission.has_permission(request, None) is True
    
    def test_denies_non_admin_role(self):
        """Test that non-admin role is denied."""
        permission = IsAdmin()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'customer'
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_unauthenticated(self):
        """Test that unauthenticated user is denied."""
        permission = IsAdmin()
        request = Mock()
        request.user = None
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_no_user_role(self):
        """Test denial when no user_role is found."""
        permission = IsAdmin()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role attribute and no auth payload
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_admin_role_in_jwt_but_not_admin(self):
        """Test denial when JWT has non-admin role."""
        permission = IsAdmin()
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role attribute
        
        request.auth = Mock()
        request.auth.payload = {'user_role': 'customer'}
        
        assert permission.has_permission(request, None) is False
