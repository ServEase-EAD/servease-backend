from django.urls import path
from .views import (
    CustomerViewSet, current_customer_profile,
    update_customer_profile, create_customer_profile
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

customer_verify = CustomerViewSet.as_view({
    'post': 'verify'
})

customer_stats = CustomerViewSet.as_view({
    'get': 'stats'
})

customer_by_user_id = CustomerViewSet.as_view({
    'get': 'by_user_id'
})

customer_delete_by_user_id = CustomerViewSet.as_view({
    'delete': 'delete_by_user_id'
})

urlpatterns = [
    # Customer profile endpoints (JWT authenticated)
    path("profile/", current_customer_profile, name="current-customer-profile"),
    path("profile/update/", update_customer_profile,
         name="update-customer-profile"),
    path("profile/create/", create_customer_profile,
         name="create-customer-profile"),

    # Main customer endpoints
    path("", customer_viewset, name="customer-list"),
    path("<uuid:pk>/", customer_detail, name="customer-detail"),
    # Handle without trailing slash
    path("<uuid:pk>", customer_detail, name="customer-detail-no-slash"),

    # Custom action endpoints
    path("<uuid:pk>/dashboard/", customer_dashboard, name="customer-dashboard"),
    path("<uuid:pk>/verify/", customer_verify, name="customer-verify"),
    path("stats/", customer_stats, name="customer-stats"),
    path("by_user_id/", customer_by_user_id, name="customer-by-user-id"),
    path("delete_by_user_id/", customer_delete_by_user_id,
         name="customer-delete-by-user-id"),
]
