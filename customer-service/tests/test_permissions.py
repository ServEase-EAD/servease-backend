"""
Unit tests for customer service permissions.
"""
import pytest
from customers.permissions import (
    IsCustomer,
    IsOwnerCustomer,
    IsCustomerOrReadOnly,
    IsAdminOrEmployee,
    IsOwnerOrAdminOrEmployee
)
from unittest.mock import Mock


@pytest.mark.django_db
class TestIsCustomerPermission:
    """Tests for IsCustomer permission."""
    
    def test_allows_authenticated_customer(self, customer_user):
        """Test that authenticated customer has permission."""
        request = Mock()
        request.user = customer_user
        view = Mock()
        
        permission = IsCustomer()
        assert permission.has_permission(request, view) is True
    
    def test_denies_employee(self, employee_user):
        """Test that employee is denied."""
        request = Mock()
        request.user = employee_user
        view = Mock()
        
        permission = IsCustomer()
        assert permission.has_permission(request, view) is False
    
    def test_denies_admin(self, admin_user):
        """Test that admin is denied."""
        request = Mock()
        request.user = admin_user
        view = Mock()
        
        permission = IsCustomer()
        assert permission.has_permission(request, view) is False
    
    def test_denies_unauthenticated(self):
        """Test that unauthenticated user is denied."""
        request = Mock()
        request.user = Mock(is_authenticated=False)
        view = Mock()
        
        permission = IsCustomer()
        assert permission.has_permission(request, view) is False


@pytest.mark.django_db
class TestIsOwnerCustomerPermission:
    """Tests for IsOwnerCustomer permission."""
    
    def test_has_permission_for_customer(self, customer_user):
        """Test that customer has base permission."""
        request = Mock()
        request.user = customer_user
        view = Mock()
        
        permission = IsOwnerCustomer()
        assert permission.has_permission(request, view) is True
    
    def test_denies_permission_for_employee(self, employee_user):
        """Test that employee doesn't have base permission."""
        request = Mock()
        request.user = employee_user
        view = Mock()
        
        permission = IsOwnerCustomer()
        assert permission.has_permission(request, view) is False
    
    def test_has_object_permission_for_owner(self, customer_user, sample_customer):
        """Test that customer can access their own profile."""
        request = Mock()
        request.user = customer_user
        view = Mock()
        
        permission = IsOwnerCustomer()
        assert permission.has_object_permission(request, view, sample_customer) is True
    
    def test_denies_object_permission_for_non_owner(self, customer_factory):
        """Test that customer cannot access another customer's profile."""
        from tests.conftest import MockUser
        customer1 = MockUser(role='customer')
        customer2_profile = customer_factory()
        
        request = Mock()
        request.user = customer1
        view = Mock()
        
        permission = IsOwnerCustomer()
        assert permission.has_object_permission(request, view, customer2_profile) is False


@pytest.mark.django_db
class TestIsCustomerOrReadOnlyPermission:
    """Tests for IsCustomerOrReadOnly permission."""
    
    def test_allows_get_request_for_anyone(self):
        """Test that GET requests are allowed for anyone."""
        request = Mock()
        request.method = 'GET'
        request.user = Mock(is_authenticated=False)
        view = Mock()
        
        permission = IsCustomerOrReadOnly()
        assert permission.has_permission(request, view) is True
    
    def test_allows_post_for_customer(self, customer_user):
        """Test that POST requests are allowed for customers."""
        request = Mock()
        request.method = 'POST'
        request.user = customer_user
        view = Mock()
        
        permission = IsCustomerOrReadOnly()
        assert permission.has_permission(request, view) is True
    
    def test_denies_post_for_non_customer(self, employee_user):
        """Test that POST requests are denied for non-customers."""
        request = Mock()
        request.method = 'POST'
        request.user = employee_user
        view = Mock()
        
        permission = IsCustomerOrReadOnly()
        assert permission.has_permission(request, view) is False
    
    def test_allows_options_request(self):
        """Test that OPTIONS requests are allowed."""
        request = Mock()
        request.method = 'OPTIONS'
        request.user = Mock(is_authenticated=False)
        view = Mock()
        
        permission = IsCustomerOrReadOnly()
        assert permission.has_permission(request, view) is True


@pytest.mark.django_db
class TestIsAdminOrEmployeePermission:
    """Tests for IsAdminOrEmployee permission."""
    
    def test_allows_admin(self, admin_user):
        """Test that admin has permission."""
        request = Mock()
        request.user = admin_user
        view = Mock()
        
        permission = IsAdminOrEmployee()
        assert permission.has_permission(request, view) is True
    
    def test_allows_employee(self, employee_user):
        """Test that employee has permission."""
        request = Mock()
        request.user = employee_user
        view = Mock()
        
        permission = IsAdminOrEmployee()
        assert permission.has_permission(request, view) is True
    
    def test_denies_customer(self, customer_user):
        """Test that customer is denied."""
        request = Mock()
        request.user = customer_user
        view = Mock()
        
        permission = IsAdminOrEmployee()
        assert permission.has_permission(request, view) is False
    
    def test_denies_unauthenticated(self):
        """Test that unauthenticated user is denied."""
        request = Mock()
        request.user = Mock(is_authenticated=False)
        view = Mock()
        
        permission = IsAdminOrEmployee()
        assert permission.has_permission(request, view) is False


@pytest.mark.django_db
class TestIsOwnerOrAdminOrEmployeePermission:
    """Tests for IsOwnerOrAdminOrEmployee permission."""
    
    def test_has_permission_for_admin(self, admin_user):
        """Test that admin has base permission."""
        request = Mock()
        request.user = admin_user
        view = Mock()
        
        permission = IsOwnerOrAdminOrEmployee()
        assert permission.has_permission(request, view) is True
    
    def test_has_permission_for_employee(self, employee_user):
        """Test that employee has base permission."""
        request = Mock()
        request.user = employee_user
        view = Mock()
        
        permission = IsOwnerOrAdminOrEmployee()
        assert permission.has_permission(request, view) is True
    
    def test_has_permission_for_customer(self, customer_user):
        """Test that customer has base permission."""
        request = Mock()
        request.user = customer_user
        view = Mock()
        
        permission = IsOwnerOrAdminOrEmployee()
        assert permission.has_permission(request, view) is True
    
    def test_admin_has_object_permission_for_any_customer(self, admin_user, sample_customer):
        """Test that admin can access any customer profile."""
        request = Mock()
        request.user = admin_user
        view = Mock()
        
        permission = IsOwnerOrAdminOrEmployee()
        assert permission.has_object_permission(request, view, sample_customer) is True
    
    def test_employee_has_object_permission_for_any_customer(self, employee_user, sample_customer):
        """Test that employee can access any customer profile."""
        request = Mock()
        request.user = employee_user
        view = Mock()
        
        permission = IsOwnerOrAdminOrEmployee()
        assert permission.has_object_permission(request, view, sample_customer) is True
    
    def test_customer_has_object_permission_for_own_profile(self, customer_user, sample_customer):
        """Test that customer can access their own profile."""
        request = Mock()
        request.user = customer_user
        view = Mock()
        
        permission = IsOwnerOrAdminOrEmployee()
        assert permission.has_object_permission(request, view, sample_customer) is True
    
    def test_customer_denied_object_permission_for_other_profile(self, customer_factory):
        """Test that customer cannot access another customer's profile."""
        from tests.conftest import MockUser
        customer1 = MockUser(role='customer')
        customer2_profile = customer_factory()
        
        request = Mock()
        request.user = customer1
        view = Mock()
        
        permission = IsOwnerOrAdminOrEmployee()
        assert permission.has_object_permission(request, view, customer2_profile) is False
    
    def test_denies_unauthenticated(self):
        """Test that unauthenticated user is denied."""
        request = Mock()
        request.user = Mock(is_authenticated=False)
        view = Mock()
        
        permission = IsOwnerOrAdminOrEmployee()
        assert permission.has_permission(request, view) is False
