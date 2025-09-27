"""
Customer Service URL Configuration
Defines API endpoints for customer management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')

app_name = 'customers'

urlpatterns = [
    # API endpoints
    path('api/v1/', include(router.urls)),

    # Additional custom endpoints can be added here
    # path('api/v1/custom-endpoint/', custom_view, name='custom-endpoint'),
]

"""
Available API Endpoints:

Customer Management:
- GET    /api/v1/customers/                    - List all customers
- POST   /api/v1/customers/                    - Create new customer  
- GET    /api/v1/customers/{id}/               - Get customer details
- PUT    /api/v1/customers/{id}/               - Update customer
- PATCH  /api/v1/customers/{id}/               - Partial update customer
- DELETE /api/v1/customers/{id}/               - Delete customer

Customer Actions:
- GET    /api/v1/customers/{id}/dashboard/     - Customer dashboard data
- POST   /api/v1/customers/{id}/verify/        - Verify customer
- GET    /api/v1/customers/stats/              - Customer statistics

Query Parameters:
- search: Search across relevant fields (first_name, last_name, email, phone, company_name)
- ordering: Sort by specified fields
- Various filters available for each endpoint
"""
