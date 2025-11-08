from rest_framework import permissions

class IsEmployeeOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if user has admin role from JWT token
        user_role = getattr(request.user, 'role', None)
        if user_role == 'admin':
            return True
        
        # Allow admin users (is_staff) full access
        if request.user.is_staff:
            return True
        
        # Allow employees to view and edit their own profile
        return obj.id == request.user.id