from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    Checks the user_role from JWT token payload.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has admin role
        # Our TokenUser has user_role attribute directly
        if hasattr(request.user, 'user_role'):
            return request.user.user_role == 'admin'
        
        # Fallback for token payload
        if hasattr(request.auth, 'payload'):
            user_role = request.auth.payload.get('user_role')
            return user_role == 'admin'
        
        # Final fallback: check if user is superuser
        return getattr(request.user, 'is_superuser', False)
