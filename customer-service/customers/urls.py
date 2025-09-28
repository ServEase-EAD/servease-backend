from django.urls import path
from .views import CustomerViewSet

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

urlpatterns = [
    # Main customer endpoints
    path("", customer_viewset, name="customer-list"),
    path("<uuid:pk>/", customer_detail, name="customer-detail"),

    # Custom action endpoints
    path("<uuid:pk>/dashboard/", customer_dashboard, name="customer-dashboard"),
    path("<uuid:pk>/verify/", customer_verify, name="customer-verify"),
    path("stats/", customer_stats, name="customer-stats"),
    path("by_user_id/", customer_by_user_id, name="customer-by-user-id"),
]
