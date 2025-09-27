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

from .models import Customer
from .serializers import (
    CustomerSerializer, CustomerBasicSerializer, CustomerCreateSerializer,
    CustomerUpdateSerializer, CustomerDashboardSerializer
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
    filterset_fields = ['is_verified']
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
        """Basic queryset without prefetch for removed models"""
        return Customer.objects.all()

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

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        GET /api/v1/customers/stats/
        Get customer statistics
        """
        total_customers = Customer.objects.count()
        verified_customers = Customer.objects.filter(is_verified=True).count()

        # New customers in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_customers = Customer.objects.filter(
            created_at__gte=thirty_days_ago).count()

        stats = {
            'total_customers': total_customers,
            'verified_customers': verified_customers,
            'new_customers_last_30_days': new_customers,
            'verification_rate': (verified_customers / total_customers * 100) if total_customers > 0 else 0
        }

        return Response(stats)
