from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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
        """Filter queryset based on user permissions"""
        user = self.request.user
        queryset = Vehicle.objects.all()

        if getattr(user, "user_role", None) == "customer":
            queryset = queryset.filter(customer_id=user.id)
        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new vehicle — auto-assign customer_id from logged-in user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = request.user.id
        vehicle = serializer.save(customer_id=customer_id)

        response_serializer = VehicleSerializer(vehicle)
        return Response(
            {
                'message': 'Vehicle created successfully',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
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
        """Soft delete a vehicle (mark as inactive)"""
        permission_classes = (IsAuthenticated,)
        instance = self.get_object()
        instance.is_active = False
        instance.save()

        return Response(
            {
                'message': 'Vehicle deactivated successfully'
            },
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
            
            "user_role": getattr(user, "user_role", "No role"),
            "is_authenticated": user.is_authenticated,
            
        })
