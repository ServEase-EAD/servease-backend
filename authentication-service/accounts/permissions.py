from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Permission class to check if user is an admin.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin()
        )

class IsEmployee(BasePermission):
    """
    Permission class to check if user is an employee.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_employee()
        )

class IsCustomer(BasePermission):
    """
    Permission class to check if user is a customer.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_customer()
        )

class IsEmployeeOrAdmin(BasePermission):
    """
    Permission class to check if user is either an employee or admin.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_employee() or request.user.is_admin())
        )

class IsOwnerOrAdmin(BasePermission):
    """
    Permission class to check if user owns the resource or is an admin.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user and 
            request.user.is_authenticated and 
            (obj == request.user or request.user.is_admin())
        )