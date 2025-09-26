"""
Customer Service API Views
Provides CRUD operations and dashboard endpoints for customer management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Customer, Vehicle, CustomerPreferences, CustomerDocument, CustomerNote
from .serializers import (
    CustomerSerializer, CustomerBasicSerializer, CustomerCreateSerializer,
    CustomerUpdateSerializer, CustomerDashboardSerializer,
    VehicleSerializer, CustomerPreferencesSerializer,
    CustomerDocumentSerializer, CustomerNoteSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer CRUD operations
    Provides endpoints for customer profile management
    """

    queryset = Customer.objects.all()
    # For development - change to IsAuthenticated for production
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_verified',
                        'state', 'is_business_customer']
    search_fields = ['first_name', 'last_name',
                     'email', 'phone', 'company_name']
    ordering_fields = ['first_name', 'last_name',
                       'created_at', 'customer_since']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CustomerCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CustomerUpdateSerializer
        elif self.action == 'list':
            return CustomerBasicSerializer
        elif self.action == 'dashboard':
            return CustomerDashboardSerializer
        return CustomerSerializer

    def get_queryset(self):
        """Optimize queries with prefetch_related"""
        queryset = Customer.objects.select_related('preferences').prefetch_related(
            'vehicles',
            Prefetch('documents', queryset=CustomerDocument.objects.filter(
                is_active=True)),
            Prefetch('notes', queryset=CustomerNote.objects.filter(
                is_important=True))
        )
        return queryset

    def create(self, request, *args, **kwargs):
        """Create new customer with enhanced response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()

        # Return full customer data
        response_serializer = CustomerSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """
        GET /api/v1/customers/{id}/dashboard/
        Returns comprehensive dashboard data for a customer
        """
        customer = self.get_object()
        serializer = CustomerDashboardSerializer(customer)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'patch'])
    def preferences(self, request, pk=None):
        """
        GET/PUT/PATCH /api/v1/customers/{id}/preferences/
        Manage customer preferences
        """
        customer = self.get_object()
        preferences, created = CustomerPreferences.objects.get_or_create(
            customer=customer)

        if request.method == 'GET':
            serializer = CustomerPreferencesSerializer(preferences)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = CustomerPreferencesSerializer(
                preferences, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def vehicles(self, request, pk=None):
        """
        GET /api/v1/customers/{id}/vehicles/
        Get all vehicles for a customer
        """
        customer = self.get_object()
        vehicles = customer.vehicles.filter(is_active=True)
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def service_history(self, request, pk=None):
        """
        GET /api/v1/customers/{id}/service-history/
        Get customer's service history (placeholder for integration with vehicle service)
        """
        customer = self.get_object()

        # This would integrate with vehicle-service microservice
        # For now, return structure that would be populated by service calls
        service_history = {
            'customer_id': str(customer.id),
            'total_services': 0,
            'total_spent': 0.00,
            'last_service_date': customer.last_service_date,
            'services': [],  # Would be populated from vehicle-service API
            'upcoming_services': []
        }

        return Response(service_history)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        GET /api/v1/customers/{id}/documents/
        Get customer documents with optional filtering
        """
        customer = self.get_object()
        documents = customer.documents.filter(is_active=True)

        # Filter by document type if provided
        doc_type = request.query_params.get('type')
        if doc_type:
            documents = documents.filter(document_type=doc_type)

        # Filter by vehicle if provided
        vehicle_id = request.query_params.get('vehicle_id')
        if vehicle_id:
            documents = documents.filter(vehicle_id=vehicle_id)

        serializer = CustomerDocumentSerializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        POST /api/v1/customers/{id}/verify/
        Mark customer as verified
        """
        customer = self.get_object()
        customer.is_verified = True
        customer.save()

        return Response({
            'message': 'Customer verified successfully',
            'customer_id': str(customer.id),
            'is_verified': customer.is_verified
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        POST /api/v1/customers/{id}/deactivate/
        Deactivate customer account
        """
        customer = self.get_object()
        customer.is_active = False
        customer.save()

        return Response({
            'message': 'Customer deactivated successfully',
            'customer_id': str(customer.id),
            'is_active': customer.is_active
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        GET /api/v1/customers/stats/
        Get customer statistics
        """
        total_customers = Customer.objects.count()
        active_customers = Customer.objects.filter(is_active=True).count()
        verified_customers = Customer.objects.filter(is_verified=True).count()
        business_customers = Customer.objects.filter(
            is_business_customer=True).count()

        # New customers in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_customers = Customer.objects.filter(
            created_at__gte=thirty_days_ago).count()

        stats = {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'verified_customers': verified_customers,
            'business_customers': business_customers,
            'new_customers_last_30_days': new_customers,
            'verification_rate': (verified_customers / total_customers * 100) if total_customers > 0 else 0,
            'business_customer_rate': (business_customers / total_customers * 100) if total_customers > 0 else 0
        }

        return Response(stats)


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicle CRUD operations
    Manages customer vehicles
    """

    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    # For development - change to IsAuthenticated for production
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'make',
                        'fuel_type', 'is_active', 'is_under_warranty']
    search_fields = ['make', 'model', 'vin', 'license_plate']
    ordering_fields = ['make', 'model', 'year', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter by customer if provided"""
        queryset = Vehicle.objects.select_related('customer')
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset

    def perform_create(self, serializer):
        """Ensure customer is set for new vehicles"""
        customer_id = self.request.data.get('customer_id')
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            serializer.save(customer=customer)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def update_mileage(self, request, pk=None):
        """
        POST /api/v1/vehicles/{id}/update-mileage/
        Update vehicle mileage
        """
        vehicle = self.get_object()
        new_mileage = request.data.get('mileage')

        if not new_mileage or not isinstance(new_mileage, int):
            return Response(
                {'error': 'Valid mileage value required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_mileage < vehicle.current_mileage:
            return Response(
                {'error': 'New mileage cannot be less than current mileage'},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle.current_mileage = new_mileage
        vehicle.save()

        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def service_status(self, request, pk=None):
        """
        GET /api/v1/vehicles/{id}/service-status/
        Get detailed service status for vehicle
        """
        vehicle = self.get_object()

        status_info = {
            'vehicle_id': str(vehicle.id),
            'is_service_due': vehicle.is_service_due(),
            'last_service_date': vehicle.last_service_date,
            'last_service_mileage': vehicle.last_service_mileage,
            'next_service_due_date': vehicle.next_service_due_date,
            'next_service_due_mileage': vehicle.next_service_due_mileage,
            'current_mileage': vehicle.current_mileage,
            'service_interval_remaining': None
        }

        # Calculate remaining service interval
        if vehicle.next_service_due_mileage:
            status_info['service_interval_remaining'] = (
                vehicle.next_service_due_mileage - vehicle.current_mileage
            )

        return Response(status_info)


class CustomerDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer Document management
    """

    queryset = CustomerDocument.objects.all()
    serializer_class = CustomerDocumentSerializer
    # For development - change to IsAuthenticated for production
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['customer', 'vehicle', 'document_type', 'is_active']
    search_fields = ['title', 'description']

    def get_queryset(self):
        """Filter documents by customer"""
        queryset = CustomerDocument.objects.select_related(
            'customer', 'vehicle')
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        GET /api/v1/documents/expiring-soon/
        Get documents expiring within 30 days
        """
        thirty_days_from_now = timezone.now().date() + timedelta(days=30)
        expiring_docs = self.get_queryset().filter(
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gte=timezone.now().date(),
            is_active=True
        )

        serializer = self.get_serializer(expiring_docs, many=True)
        return Response(serializer.data)


class CustomerNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer Notes management
    """

    queryset = CustomerNote.objects.all()
    serializer_class = CustomerNoteSerializer
    # For development - change to IsAuthenticated for production
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['customer', 'note_type', 'is_important', 'is_private']
    search_fields = ['title', 'content']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter notes by customer"""
        queryset = CustomerNote.objects.select_related('customer')
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset

    def perform_create(self, serializer):
        """Set created_by field from request user"""
        # This would be set from the authenticated user's employee ID
        # For now, using a placeholder
        created_by = getattr(self.request.user, 'employee_id', 1)
        serializer.save(created_by=created_by)
