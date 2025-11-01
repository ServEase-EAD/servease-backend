"""
Custom permissions for customer service
"""

from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """
    Permission to only allow customers to access views.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'user_role') and
            request.user.user_role == 'customer'
        )


class IsOwnerCustomer(BasePermission):
    """
    Permission to only allow customers to access their own profile.
    """

    def has_permission(self, request, view):
        # Must be authenticated and be a customer
        if not (request.user and request.user.is_authenticated):
            return False

        if not (hasattr(request.user, 'user_role') and request.user.user_role == 'customer'):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Customer can only access their own profile
        return obj.user_id == request.user.user_id


class IsCustomerOrReadOnly(BasePermission):
    """
    Permission to allow customers to modify their data, others only read access.
    """

    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Write permissions only to customers
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'user_role') and
            request.user.user_role == 'customer'
        )
