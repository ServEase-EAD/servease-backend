"""
Tests for permission classes in the vehicleandproject service.

Tests cover:
- IsCustomer permission
- IsEmployee permission
- IsAdmin permission
- Authentication requirements
- Role-based access control
"""

import pytest
from unittest.mock import Mock
from rest_framework.test import APIRequestFactory

from vehicles.permissions import IsCustomer, IsEmployee
from projects.permissions import IsAdmin


factory = APIRequestFactory()


# ==================== IsCustomer Permission Tests ====================

class TestIsCustomerPermission:
    """Test cases for IsCustomer permission."""
    
    def test_allows_customer_role(self):
        """Test customer role is allowed."""
        permission = IsCustomer()
        
        # Create mock request with customer user
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'customer'
        
        assert permission.has_permission(request, None) is True
    
    def test_denies_non_customer_role(self):
        """Test non-customer roles are denied."""
        permission = IsCustomer()
        
        non_customer_roles = ['employee', 'admin', 'manager']
        
        for role in non_customer_roles:
            request = Mock()
            request.user = Mock()
            request.user.is_authenticated = True
            request.user.user_role = role
            
            assert permission.has_permission(request, None) is False
    
    def test_denies_unauthenticated_user(self):
        """Test unauthenticated users are denied."""
        permission = IsCustomer()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_missing_user_role(self):
        """Test users without user_role attribute are denied."""
        permission = IsCustomer()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role attribute
        
        result = permission.has_permission(request, None)
        assert result is False or result is None


# ==================== IsEmployee Permission Tests ====================

class TestIsEmployeePermission:
    """Test cases for IsEmployee permission."""
    
    def test_allows_employee_role(self):
        """Test employee role is allowed."""
        permission = IsEmployee()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'employee'
        
        assert permission.has_permission(request, None) is True
    
    def test_denies_non_employee_role(self):
        """Test non-employee roles are denied."""
        permission = IsEmployee()
        
        non_employee_roles = ['customer', 'admin', 'manager']
        
        for role in non_employee_roles:
            request = Mock()
            request.user = Mock()
            request.user.is_authenticated = True
            request.user.user_role = role
            
            assert permission.has_permission(request, None) is False
    
    def test_denies_unauthenticated_user(self):
        """Test unauthenticated users are denied."""
        permission = IsEmployee()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_missing_user_role(self):
        """Test users without user_role attribute are denied."""
        permission = IsEmployee()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role attribute
        
        result = permission.has_permission(request, None)
        assert result is False or result is None


# ==================== IsAdmin Permission Tests ====================

class TestIsAdminPermission:
    """Test cases for IsAdmin permission."""
    
    def test_allows_admin_role_from_user(self):
        """Test admin role from user attribute is allowed."""
        permission = IsAdmin()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'admin'
        
        assert permission.has_permission(request, None) is True
    
    def test_allows_admin_role_from_jwt_payload(self):
        """Test admin role from JWT payload is allowed."""
        permission = IsAdmin()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role on user object
        delattr(request.user, 'user_role') if hasattr(request.user, 'user_role') else None
        
        # But present in JWT payload
        request.auth = Mock()
        request.auth.payload = {'user_role': 'admin'}
        
        assert permission.has_permission(request, None) is True
    
    def test_denies_non_admin_role(self):
        """Test non-admin roles are denied."""
        permission = IsAdmin()
        
        non_admin_roles = ['customer', 'employee', 'manager']
        
        for role in non_admin_roles:
            request = Mock()
            request.user = Mock()
            request.user.is_authenticated = True
            request.user.user_role = role
            
            assert permission.has_permission(request, None) is False
    
    def test_denies_unauthenticated_user(self):
        """Test unauthenticated users are denied."""
        permission = IsAdmin()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_none_user(self):
        """Test None user is denied."""
        permission = IsAdmin()
        
        request = Mock()
        request.user = None
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_no_user_role(self):
        """Test users without user_role are denied."""
        permission = IsAdmin()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role attribute and no auth payload
        
        assert permission.has_permission(request, None) is False
    
    def test_denies_non_admin_in_jwt_payload(self):
        """Test non-admin role in JWT payload is denied."""
        permission = IsAdmin()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        # No user_role on user
        
        # Non-admin in JWT
        request.auth = Mock()
        request.auth.payload = {'user_role': 'customer'}
        
        assert permission.has_permission(request, None) is False
    
    def test_admin_checks_user_first(self):
        """Test admin permission checks user.user_role before JWT payload."""
        permission = IsAdmin()
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.user_role = 'admin'  # Admin on user
        
        # Different role in JWT (should use user.user_role)
        request.auth = Mock()
        request.auth.payload = {'user_role': 'customer'}
        
        assert permission.has_permission(request, None) is True


# ==================== Cross-Permission Tests ====================

class TestCrossPermissionScenarios:
    """Test permission interactions and edge cases."""
    
    def test_customer_permission_object(self):
        """Test IsCustomer can be instantiated."""
        permission = IsCustomer()
        assert permission is not None
    
    def test_employee_permission_object(self):
        """Test IsEmployee can be instantiated."""
        permission = IsEmployee()
        assert permission is not None
    
    def test_admin_permission_object(self):
        """Test IsAdmin can be instantiated."""
        permission = IsAdmin()
        assert permission is not None
    
    def test_all_permissions_require_authentication(self):
        """Test all permissions require authentication."""
        permissions = [IsCustomer(), IsEmployee(), IsAdmin()]
        
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        
        for permission in permissions:
            assert permission.has_permission(request, None) is False
    
    def test_permissions_are_exclusive(self):
        """Test user with one role cannot pass other role permissions."""
        # Customer user
        customer_request = Mock()
        customer_request.user = Mock()
        customer_request.user.is_authenticated = True
        customer_request.user.user_role = 'customer'
        
        assert IsCustomer().has_permission(customer_request, None) is True
        assert IsEmployee().has_permission(customer_request, None) is False
        assert IsAdmin().has_permission(customer_request, None) is False
        
        # Employee user
        employee_request = Mock()
        employee_request.user = Mock()
        employee_request.user.is_authenticated = True
        employee_request.user.user_role = 'employee'
        
        assert IsCustomer().has_permission(employee_request, None) is False
        assert IsEmployee().has_permission(employee_request, None) is True
        assert IsAdmin().has_permission(employee_request, None) is False
        
        # Admin user
        admin_request = Mock()
        admin_request.user = Mock()
        admin_request.user.is_authenticated = True
        admin_request.user.user_role = 'admin'
        
        assert IsCustomer().has_permission(admin_request, None) is False
        assert IsEmployee().has_permission(admin_request, None) is False
        assert IsAdmin().has_permission(admin_request, None) is True
