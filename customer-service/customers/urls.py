from django.urls import path
from .views import (
    CustomerViewSet, current_customer_profile,
    update_customer_profile, create_customer_profile,
    delete_customer_profile, health_check
)

# Get the viewset instance for explicit URL mapping
customer_viewset = CustomerViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

customer_detail = CustomerViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

customer_dashboard = CustomerViewSet.as_view({
    'get': 'dashboard'
})

customer_increment_service = CustomerViewSet.as_view({
    'post': 'increment_service'
})

customer_by_logical_id = CustomerViewSet.as_view({
    'get': 'retrieve_by_logical_id',
    'put': 'update_by_logical_id',
    'patch': 'partial_update_by_logical_id',
    'delete': 'destroy_by_logical_id'
})

customer_by_user_id = CustomerViewSet.as_view({
    'get': 'by_user_id'
})

customer_check_profile = CustomerViewSet.as_view({
    'post': 'check_profile_exists'
})

urlpatterns = [
    # Health check endpoint (no authentication required)
    path("health/", health_check, name="health-check"),

    # Customer profile endpoints (JWT authenticated)
    path("profile/", current_customer_profile, name="current-customer-profile"),
    path("profile/create/", create_customer_profile,
         name="create-customer-profile"),
    path("profile/update/", update_customer_profile,
         name="update-customer-profile"),
    path("profile/delete/", delete_customer_profile,
         name="delete-customer-profile"),

    # Main customer endpoints (using database ID - legacy)
    path("", customer_viewset, name="customer-list"),
    path("<uuid:pk>/", customer_detail, name="customer-detail"),

    # Customer endpoints using logical ID (user_id from auth service)
    path("logical/<uuid:logical_id>/", customer_by_logical_id, name="customer-by-logical-id"),

    # Custom action endpoints
    path("<uuid:pk>/dashboard/", customer_dashboard, name="customer-dashboard"),
    path("<uuid:pk>/increment_service/", customer_increment_service,
         name="customer-increment-service"),

    # Utilities
    path("by_user_id/", customer_by_user_id, name="customer-by-user-id"),
    path("check_profile_exists/", customer_check_profile,
         name="customer-check-profile"),
]
