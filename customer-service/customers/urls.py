"""
Customer Service URL Configuration
Defines API endpoints for customer management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, VehicleViewSet,
    CustomerDocumentViewSet, CustomerNoteViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'documents', CustomerDocumentViewSet, basename='document')
router.register(r'notes', CustomerNoteViewSet, basename='note')

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
- GET    /api/v1/customers/{id}/preferences/   - Get customer preferences
- PUT    /api/v1/customers/{id}/preferences/   - Update customer preferences
- PATCH  /api/v1/customers/{id}/preferences/   - Partial update preferences
- GET    /api/v1/customers/{id}/vehicles/      - Get customer vehicles
- GET    /api/v1/customers/{id}/service-history/ - Get service history
- GET    /api/v1/customers/{id}/documents/     - Get customer documents
- POST   /api/v1/customers/{id}/verify/        - Verify customer
- POST   /api/v1/customers/{id}/deactivate/    - Deactivate customer
- GET    /api/v1/customers/stats/              - Customer statistics

Vehicle Management:
- GET    /api/v1/vehicles/                     - List vehicles
- POST   /api/v1/vehicles/                     - Create new vehicle
- GET    /api/v1/vehicles/{id}/                - Get vehicle details
- PUT    /api/v1/vehicles/{id}/                - Update vehicle
- PATCH  /api/v1/vehicles/{id}/                - Partial update vehicle
- DELETE /api/v1/vehicles/{id}/                - Delete vehicle
- POST   /api/v1/vehicles/{id}/update-mileage/ - Update vehicle mileage
- GET    /api/v1/vehicles/{id}/service-status/ - Get service status

Document Management:
- GET    /api/v1/documents/                    - List documents
- POST   /api/v1/documents/                    - Upload new document
- GET    /api/v1/documents/{id}/               - Get document details
- PUT    /api/v1/documents/{id}/               - Update document
- DELETE /api/v1/documents/{id}/               - Delete document
- GET    /api/v1/documents/expiring-soon/     - Get expiring documents

Note Management:
- GET    /api/v1/notes/                        - List notes
- POST   /api/v1/notes/                        - Create new note
- GET    /api/v1/notes/{id}/                   - Get note details
- PUT    /api/v1/notes/{id}/                   - Update note
- DELETE /api/v1/notes/{id}/                   - Delete note

Query Parameters:
- search: Search across relevant fields
- ordering: Sort by specified fields
- Various filters available for each endpoint
"""
