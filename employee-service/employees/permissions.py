from rest_framework import permissions

class IsEmployeeOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow admin users full access
        if request.user.is_staff:
            return True
        
        # Allow employees to view and edit their own profile
        return obj.id == request.user.id