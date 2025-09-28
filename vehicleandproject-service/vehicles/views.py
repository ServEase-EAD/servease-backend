from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
    # permission_classes = [IsAuthenticated]
    lookup_field = 'vehicle_id'  # Use vehicle_id instead of pk
    
    # Filtering and searching
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['make', 'model', 'year', 'color', 'customer_id', 'is_active']
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
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = Vehicle.objects.all()
        
        # If user has customer role, only show their vehicles
        # This assumes you have user role checking logic
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'customer':
            # Assuming you have a way to get customer_id from user
            customer_id = getattr(user, 'customer_id', None)
            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new vehicle"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            vehicle = serializer.save()
            # Return full vehicle data after creation
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
                'message': 'Vehicle creation failed',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def update(self, request, *args, **kwargs):
        """Update a vehicle"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
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
    
    @action(detail=False, methods=['get'])
    def search_vehicles(self, request):
        """Advanced search for vehicles"""
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'q parameter is required for search'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehicles = self.get_queryset().filter(
            Q(make__icontains=query) |
            Q(model__icontains=query) |
            Q(vin__icontains=query) |
            Q(plate_number__icontains=query)
        ).filter(is_active=True)
        
        serializer = VehicleListSerializer(vehicles, many=True)
        
        return Response(
            {
                'message': f'Search results for "{query}"',
                'count': vehicles.count(),
                'data': serializer.data
            }
        )