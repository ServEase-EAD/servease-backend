"""
Unit tests for employee service permissions.
"""
import pytest
from unittest.mock import Mock
from employees.permissions import IsEmployeeOwnerOrAdmin


@pytest.mark.django_db
class TestIsEmployeeOwnerOrAdminPermission:
    """Tests for IsEmployeeOwnerOrAdmin permission."""
    
    def test_allows_admin_role(self, sample_employee):
        """Test that user with admin role has permission."""
        request = Mock()
        request.user = Mock()
        request.user.role = 'admin'
        request.user.is_staff = False
        view = Mock()
        
        permission = IsEmployeeOwnerOrAdmin()
        assert permission.has_object_permission(request, view, sample_employee) is True
    
    def test_allows_staff_user(self, sample_employee):
        """Test that staff user has permission."""
        request = Mock()
        request.user = Mock()
        request.user.role = None
        request.user.is_staff = True
        view = Mock()
        
        permission = IsEmployeeOwnerOrAdmin()
        assert permission.has_object_permission(request, view, sample_employee) is True
    
    def test_allows_employee_owner(self, sample_employee):
        """Test that employee can access their own profile."""
        request = Mock()
        request.user = Mock()
        request.user.id = sample_employee.id
        request.user.role = 'employee'
        request.user.is_staff = False
        view = Mock()
        
        permission = IsEmployeeOwnerOrAdmin()
        assert permission.has_object_permission(request, view, sample_employee) is True
    
    def test_denies_different_employee(self, sample_employee, another_employee):
        """Test that employee cannot access another employee's profile."""
        request = Mock()
        request.user = Mock()
        request.user.id = another_employee.id
        request.user.role = 'employee'
        request.user.is_staff = False
        view = Mock()
        
        permission = IsEmployeeOwnerOrAdmin()
        assert permission.has_object_permission(request, view, sample_employee) is False
    
    def test_denies_non_admin_non_owner(self, sample_employee):
        """Test that non-admin and non-owner is denied."""
        request = Mock()
        request.user = Mock()
        request.user.id = 'different-id'
        request.user.role = 'customer'
        request.user.is_staff = False
        view = Mock()
        
        permission = IsEmployeeOwnerOrAdmin()
        assert permission.has_object_permission(request, view, sample_employee) is False
    
    def test_superuser_has_permission(self, sample_employee):
        """Test that superuser (staff) has permission."""
        request = Mock()
        request.user = Mock()
        request.user.id = 'different-id'
        request.user.role = None
        request.user.is_staff = True
        view = Mock()
        
        permission = IsEmployeeOwnerOrAdmin()
        assert permission.has_object_permission(request, view, sample_employee) is True
