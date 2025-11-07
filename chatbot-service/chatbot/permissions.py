from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """
    Allow any authenticated user (customer, employee, admin) to access chatbot.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of a session to access it.
    Used as object-level permission.
    """

    def has_object_permission(self, request, view, obj):
        # obj is a ChatSession instance
        # Check if the session belongs to the requesting user
        return obj.user_id == request.user.id


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, "user_role", None) == "customer"
        )


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, "user_role", None) == "employee"
        )


class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users.
    Checks the user_role from JWT token payload.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has admin role from JWT token
        if hasattr(request.user, 'user_role'):
            return request.user.user_role == 'admin'

        # Fallback for token payload
        if hasattr(request.auth, 'payload'):
            user_role = request.auth.payload.get('user_role')
            return user_role == 'admin'

        return False
