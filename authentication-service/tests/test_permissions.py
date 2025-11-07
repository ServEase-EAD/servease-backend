import pytest
from django.test import RequestFactory
from accounts.permissions import (
    IsAdmin,
    IsEmployee,
    IsCustomer,
    IsEmployeeOrAdmin,
    IsOwnerOrAdmin
)


@pytest.mark.django_db
class TestIsAdminPermission:
    """Test suite for IsAdmin permission class."""

    def setup_method(self):
        """Set up request factory for each test."""
        self.factory = RequestFactory()
        self.permission = IsAdmin()

    def test_admin_has_permission(self, admin_user):
        """Test that admin user has permission."""
        request = self.factory.get('/')
        request.user = admin_user
        assert self.permission.has_permission(request, None) is True

    def test_employee_no_permission(self, employee_user):
        """Test that employee user does not have permission."""
        request = self.factory.get('/')
        request.user = employee_user
        assert self.permission.has_permission(request, None) is False

    def test_customer_no_permission(self, customer_user):
        """Test that customer user does not have permission."""
        request = self.factory.get('/')
        request.user = customer_user
        assert self.permission.has_permission(request, None) is False

    def test_unauthenticated_no_permission(self):
        """Test that unauthenticated user does not have permission."""
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/')
        request.user = AnonymousUser()
        assert self.permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsEmployeePermission:
    """Test suite for IsEmployee permission class."""

    def setup_method(self):
        """Set up request factory for each test."""
        self.factory = RequestFactory()
        self.permission = IsEmployee()

    def test_employee_has_permission(self, employee_user):
        """Test that employee user has permission."""
        request = self.factory.get('/')
        request.user = employee_user
        assert self.permission.has_permission(request, None) is True

    def test_admin_no_permission(self, admin_user):
        """Test that admin user does not have permission."""
        request = self.factory.get('/')
        request.user = admin_user
        assert self.permission.has_permission(request, None) is False

    def test_customer_no_permission(self, customer_user):
        """Test that customer user does not have permission."""
        request = self.factory.get('/')
        request.user = customer_user
        assert self.permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsCustomerPermission:
    """Test suite for IsCustomer permission class."""

    def setup_method(self):
        """Set up request factory for each test."""
        self.factory = RequestFactory()
        self.permission = IsCustomer()

    def test_customer_has_permission(self, customer_user):
        """Test that customer user has permission."""
        request = self.factory.get('/')
        request.user = customer_user
        assert self.permission.has_permission(request, None) is True

    def test_employee_no_permission(self, employee_user):
        """Test that employee user does not have permission."""
        request = self.factory.get('/')
        request.user = employee_user
        assert self.permission.has_permission(request, None) is False

    def test_admin_no_permission(self, admin_user):
        """Test that admin user does not have permission."""
        request = self.factory.get('/')
        request.user = admin_user
        assert self.permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsEmployeeOrAdminPermission:
    """Test suite for IsEmployeeOrAdmin permission class."""

    def setup_method(self):
        """Set up request factory for each test."""
        self.factory = RequestFactory()
        self.permission = IsEmployeeOrAdmin()

    def test_admin_has_permission(self, admin_user):
        """Test that admin user has permission."""
        request = self.factory.get('/')
        request.user = admin_user
        assert self.permission.has_permission(request, None) is True

    def test_employee_has_permission(self, employee_user):
        """Test that employee user has permission."""
        request = self.factory.get('/')
        request.user = employee_user
        assert self.permission.has_permission(request, None) is True

    def test_customer_no_permission(self, customer_user):
        """Test that customer user does not have permission."""
        request = self.factory.get('/')
        request.user = customer_user
        assert self.permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsOwnerOrAdminPermission:
    """Test suite for IsOwnerOrAdmin permission class."""

    def setup_method(self):
        """Set up request factory for each test."""
        self.factory = RequestFactory()
        self.permission = IsOwnerOrAdmin()

    def test_owner_has_object_permission(self, customer_user):
        """Test that user has permission for their own object."""
        request = self.factory.get('/')
        request.user = customer_user
        assert self.permission.has_object_permission(request, None, customer_user) is True

    def test_admin_has_object_permission(self, admin_user, customer_user):
        """Test that admin has permission for any object."""
        request = self.factory.get('/')
        request.user = admin_user
        assert self.permission.has_object_permission(request, None, customer_user) is True

    def test_other_user_no_object_permission(self, customer_user, employee_user):
        """Test that user does not have permission for other user's object."""
        request = self.factory.get('/')
        request.user = customer_user
        assert self.permission.has_object_permission(request, None, employee_user) is False

    def test_unauthenticated_no_object_permission(self, customer_user):
        """Test that unauthenticated user does not have permission."""
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/')
        request.user = AnonymousUser()
        assert self.permission.has_object_permission(request, None, customer_user) is False
