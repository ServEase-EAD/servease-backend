"""
Customer Service API Views
Provides CRUD operations and dashboard endpoints for customer management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Customer
from .serializers import (
    CustomerSerializer, CustomerBasicSerializer, CustomerCreateSerializer,
    CustomerUpdateSerializer, CustomerDashboardSerializer
)
from .permissions import IsCustomer, IsOwnerCustomer, IsCustomerOrReadOnly
from .authentication import CustomerJWTAuthentication


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer CRUD operations
    Provides endpoints for customer profile management
    """

    queryset = Customer.objects.all()
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]
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

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            # Allow creation for authenticated users (from registration flow)
            permission_classes = [IsCustomer]
        elif self.action in ['list', 'stats']:
            # Admin-only endpoints (for now allow authenticated customers to see stats)
            permission_classes = [IsCustomer]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'dashboard']:
            # Customer can only access their own profile
            permission_classes = [IsOwnerCustomer]
        else:
            permission_classes = [IsCustomer]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        if hasattr(self.request.user, 'user_id'):
            # Customers can only see their own profile
            return Customer.objects.filter(user_id=self.request.user.user_id)
        return Customer.objects.none()

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

    @action(detail=False, methods=['get'])
    def by_user_id(self, request):
        """
        GET /api/v1/customers/by_user_id/?user_id=12345
        Get customer by user_id
        """
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {'error': 'user_id must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            customer = Customer.objects.get(user_id=user_id)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response(
                {'error': f'Customer with user_id {user_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['delete'])
    def delete_by_user_id(self, request):
        """
        DELETE /api/v1/customers/delete_by_user_id/?user_id=12345
        Delete customer by user_id
        """
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {'error': 'user_id must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            customer = Customer.objects.get(user_id=user_id)
            customer_id = str(customer.id)
            customer_name = customer.full_name
            customer.delete()

            return Response({
                'message': 'Customer deleted successfully',
                'deleted_customer': {
                    'id': customer_id,
                    'user_id': user_id,
                    'name': customer_name
                }
            }, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response(
                {'error': f'Customer with user_id {user_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsCustomer])
def current_customer_profile(request):
    """
    GET /api/v1/customers/profile/
    Get current customer's profile
    """
    try:
        customer = Customer.objects.get(user_id=request.user.user_id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsCustomer])
def update_customer_profile(request):
    """
    PUT/PATCH /api/v1/customers/profile/update/
    Update current customer's profile
    """
    try:
        customer = Customer.objects.get(user_id=request.user.user_id)
        serializer = CustomerUpdateSerializer(
            customer,
            data=request.data,
            partial=request.method == 'PATCH'
        )

        if serializer.is_valid():
            serializer.save()
            # Return full customer data
            response_serializer = CustomerSerializer(customer)
            return Response(response_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsCustomer])
def create_customer_profile(request):
    """
    POST /api/v1/customers/profile/create/
    Create customer profile after registration
    """
    # Add user_id from authenticated user
    profile_data = request.data.copy()
    profile_data['user_id'] = request.user.user_id
    profile_data['email'] = request.user.email

    # Check if profile already exists
    if Customer.objects.filter(user_id=request.user.user_id).exists():
        return Response(
            {'error': 'Customer profile already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CustomerCreateSerializer(data=profile_data)
    if serializer.is_valid():
        customer = serializer.save()
        response_serializer = CustomerSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
