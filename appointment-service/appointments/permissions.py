"""
Custom permissions for appointments
"""
from rest_framework import permissions


class IsAppointmentOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an appointment or admins to edit it
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin
        # Check if user is admin (you can customize this based on your user model)
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
        
        # Check if user is the creator
        if hasattr(request.user, 'id'):
            return obj.created_by_user_id == request.user.id
        
        return False


class IsEmployeeOrAdmin(permissions.BasePermission):
    """
    Permission for employee or admin only actions
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is admin
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
        
        # Check if user is employee (customize based on your user model)
        if hasattr(request.user, 'role'):
            return request.user.role in ['employee', 'admin']
        
        # Default allow for development
        return True


class CanManageAppointments(permissions.BasePermission):
    """
    Permission for managing appointments (admin/employee)
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins and employees can manage appointments
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
        
        if hasattr(request.user, 'role'):
            return request.user.role in ['employee', 'admin', 'manager']
        
        # For development, allow if authenticated
        return True
    
    def has_object_permission(self, request, view, obj):
        # Same logic as has_permission
        return self.has_permission(request, view)


class IsCustomerOrEmployee(permissions.BasePermission):
    """
    Permission for customer (owner) or employee
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins can access everything
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
        
        # Employees can access all appointments
        if hasattr(request.user, 'role') and request.user.role in ['employee', 'admin']:
            return True
        
        # Customers can only access their own appointments
        if hasattr(request.user, 'id'):
            return str(obj.customer_id) == str(request.user.id)
        
        return False

