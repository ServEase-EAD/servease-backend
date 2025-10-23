from rest_framework.permissions import BasePermission

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
