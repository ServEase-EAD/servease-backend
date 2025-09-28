from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'', VehicleViewSet, basename='vehicle')

app_name = 'vehicles'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]

# This generates the following URL patterns:
# GET    /api/v1/vehicles/                    - List all vehicles
# POST   /api/v1/vehicles/                    - Create new vehicle
# GET    /api/v1/vehicles/{vehicle_id}/       - Get specific vehicle
# PUT    /api/v1/vehicles/{vehicle_id}/       - Update vehicle (full)
# PATCH  /api/v1/vehicles/{vehicle_id}/       - Update vehicle (partial)
# DELETE /api/v1/vehicles/{vehicle_id}/       - Delete/deactivate vehicle

# Custom actions:
# POST   /api/v1/vehicles/{vehicle_id}/activate/      - Activate vehicle
# GET    /api/v1/vehicles/customer_vehicles/          - Get vehicles by customer
# GET    /api/v1/vehicles/search_vehicles/            - Search vehicles