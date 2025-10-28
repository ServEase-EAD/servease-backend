from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from .models import Vehicle
from .serializers import (
    VehicleSerializer,
    VehicleCreateSerializer,
    VehicleUpdateSerializer,
    VehicleListSerializer
)
from .permissions import IsCustomer, IsEmployee


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicle CRUD operations

    Provides:
    - GET /api/v1/vehicles/ - List all vehicles
    - POST /api/v1/vehicles/ - Create new vehicle  
    - GET /api/v1/vehicles/{id}/ - Get specific vehicle
    - PUT /api/v1/vehicles/{id}/ - Update vehicle
    - PATCH /api/v1/vehicles/{id}/ - Partial update
    - DELETE /api/v1/vehicles/{id}/ - Delete vehicle
    """

    queryset = Vehicle.objects.all()
    lookup_field = 'vehicle_id'  # Use vehicle_id instead of pk

    # Filtering and searching
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['make', 'model', 'year',
                        'color', 'customer_id', 'is_active']
    search_fields = ['make', 'model', 'vin', 'plate_number']
    ordering_fields = ['created_at', 'year', 'make', 'model']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return VehicleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VehicleUpdateSerializer
        elif self.action == 'list':
            return VehicleListSerializer
        return VehicleSerializer

    def get_permissions(self):
        """RBAC logic"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsCustomer]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['customer_vehicles']:
            permission_classes = [IsAuthenticated, IsEmployee]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user role.
        - Employees (and admins) can see all active vehicles.
        - Customers can only see their own active vehicles.
        - Others receive 403.
        """
        user = self.request.user
        base_qs = Vehicle.objects.filter(is_active=True)

        role = getattr(user, "user_role", None)
        if role in ("employee", "admin"):
            return base_qs
        if role == "customer":
            # Limit to vehicles owned by the authenticated customer
            return base_qs.filter(customer_id=getattr(user, "id", None))

        raise PermissionDenied('Not allowed to access vehicles')

    def create(self, request, *args, **kwargs):
        """Create a new vehicle — auto-assign customer_id from logged-in user"""

        user = request.user
        if not hasattr(user, 'user_role') or user.user_role != 'customer':
            return Response(
                {'error': 'Only customers can create vehicles'},
                status=status.HTTP_403_FORBIDDEN
            )
         # Extract customer_id from JWT token (user.id contains the user_id from the token)
        customer_id = getattr(user, 'id', None)
        if not customer_id:
            return Response(
                {'error': 'Customer ID not found in token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the vehicle with customer_id automatically set
            vehicle = serializer.save(customer_id=customer_id)
            # Return full vehicle details after creation
            response_serializer = VehicleSerializer(vehicle)
            return Response(
                {
                    'message': 'Vehicle created successfully',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating vehicle',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update a vehicle"""
        permission_classes = (IsAuthenticated,)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)

        if serializer.is_valid():
            vehicle = serializer.save()
            response_serializer = VehicleSerializer(vehicle)
            return Response(
                {
                    'message': 'Vehicle updated successfully',
                    'data': response_serializer.data
                }
            )
        return Response(
            {
                'message': 'Vehicle update failed',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a vehicle by customer"""
        """Vehicles with projects cannot be deleted"""
        instance = self.get_object()
        user = request.user

        # Additional check: customers can only delete their own vehicles and employees cannot delete vehicles
        if user.user_role in ['customer', 'employee'] and instance.customer_id != user.id:
            return Response(
                {'error': 'Only customers can delete their own vehicles'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete a vehicle
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Vehicle deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post'])
    def activate(self, request, vehicle_id=None):
        """Activate a deactivated vehicle"""
        permission_classes = (IsAuthenticated,)
        vehicle = self.get_object()
        vehicle.is_active = True
        vehicle.save()

        serializer = VehicleSerializer(vehicle)
        return Response(
            {
                'message': 'Vehicle activated successfully',
                'data': serializer.data
            }
        )

    @action(detail=False, methods=['get'])
    def customer_vehicles(self, request):
        """Get vehicles for a specific customer"""
        permission_classes = (IsAuthenticated,)
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'customer_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicles = self.get_queryset().filter(customer_id=customer_id, is_active=True)
        serializer = VehicleListSerializer(vehicles, many=True)

        return Response(
            {
                'message': f'Vehicles for customer {customer_id}',
                'count': vehicles.count(),
                'data': serializer.data
            }
        )

    @action(detail=False, methods=['get'], url_path='debug-user')
    def debug_user(self, request):
        """Return authenticated user details for debugging"""
        user = request.user
        return Response({
            "id": user.id,
            "email": getattr(user, "email", "No email"),
            "user_role": getattr(user, "user_role", "No role"),
            "is_authenticated": user.is_authenticated,

        })
