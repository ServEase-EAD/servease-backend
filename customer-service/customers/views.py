"""
Customer Service API Views
Provides CRUD operations and dashboard endpoints for customer-specific data.

This service manages customer-specific information (address, emergency contacts, preferences).
User credentials are managed by the authentication service.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.conf import settings

from .models import Customer
from .serializers import (
    CustomerSerializer, CustomerBasicSerializer, CustomerCreateSerializer,
    CustomerUpdateSerializer, CustomerDashboardSerializer,
    CustomerWithUserDataSerializer
)
from .permissions import IsCustomer, IsOwnerCustomer, IsOwnerOrAdminOrEmployee
from .authentication import CustomerJWTAuthentication, get_user_data_from_auth_service


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /api/v1/customers/health/
    Health check endpoint - no authentication required
    """
    return Response({
        'status': 'healthy',
        'service': 'customer-service',
        'timestamp': timezone.now().isoformat(),
        'version': '2.0.0',
        'description': 'Customer-specific data service (integrated with auth service)'
    }, status=status.HTTP_200_OK)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer profile CRUD operations.

    Manages customer-specific data while user credentials are handled by auth service.
    Each customer profile is linked to a user in the authentication service via user_id.
    """

    queryset = Customer.objects.all()
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_verified', 'city', 'state', 'country']
    search_fields = ['city', 'state', 'company_name', 'street_address']
    ordering_fields = ['created_at', 'customer_since', 'total_services']
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
        elif self.action == 'with_user_data':
            return CustomerWithUserDataSerializer
        return CustomerSerializer

    def get_permissions(self):
        """Define permissions based on action"""
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['retrieve_by_logical_id', 'update_by_logical_id', 'partial_update_by_logical_id']:
            # Allow admins/employees to access any customer, or customers to access their own
            permission_classes = [IsOwnerOrAdminOrEmployee]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'dashboard']:
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

    def get_serializer_context(self):
        """Add user data from auth service to serializer context"""
        context = super().get_serializer_context()

        # Add authenticated user data to context for serializers
        if hasattr(self.request, 'user') and hasattr(self.request.user, 'user_id'):
            context['user_data'] = {
                'user_id': self.request.user.user_id,
                'email': self.request.user.email,
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
            }

        return context

    def create(self, request, *args, **kwargs):
        """
        Create new customer profile.
        User must already exist in authentication service.
        """
        # Automatically use authenticated user's ID
        profile_data = request.data.copy()
        profile_data['user_id'] = request.user.user_id

        serializer = self.get_serializer(data=profile_data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()

        # Return full customer data with user info
        response_serializer = CustomerSerializer(
            customer, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Get customer profile with user data from auth service"""
        customer = self.get_object()

        # Fetch user data from authentication service
        user_data = get_user_data_from_auth_service(customer.user_id)

        context = self.get_serializer_context()
        if user_data:
            context['user_data'] = user_data

        serializer = CustomerSerializer(customer, context=context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """
        GET /api/v1/customers/{id}/dashboard/
        Returns comprehensive dashboard data for a customer
        """
        customer = self.get_object()

        # Fetch user data from auth service
        user_data = get_user_data_from_auth_service(customer.user_id)

        context = self.get_serializer_context()
        if user_data:
            context['user_data'] = user_data

        serializer = CustomerDashboardSerializer(customer, context=context)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def increment_service(self, request, pk=None):
        """
        POST /api/v1/customers/{id}/increment_service/
        Increment service counter (called by appointment service)
        """
        customer = self.get_object()
        customer.increment_service_count()

        return Response({
            'message': 'Service count incremented',
            'customer_id': str(customer.id),
            'total_services': customer.total_services,
            'last_service_date': customer.last_service_date
        })

    @action(detail=False, methods=['get'])
    def by_user_id(self, request):
        """
        GET /api/v1/customers/by_user_id/?user_id=<uuid>
        Get customer profile by user_id (inter-service communication)
        """
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            customer = Customer.objects.get(user_id=user_id)

            # Fetch user data from auth service
            user_data = get_user_data_from_auth_service(customer.user_id)
            context = {'user_data': user_data} if user_data else {}

            serializer = CustomerSerializer(customer, context=context)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response(
                {'error': f'Customer profile not found for user_id {user_id}'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def check_profile_exists(self, request):
        """
        POST /api/v1/customers/check_profile_exists/
        Check if customer profile exists for user_id
        Body: {"user_id": "<uuid>"}
        """
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required in request body'},
                status=status.HTTP_400_BAD_REQUEST
            )

        exists = Customer.objects.filter(user_id=user_id).exists()

        response_data = {
            'user_id': user_id,
            'profile_exists': exists
        }

        if exists:
            customer = Customer.objects.get(user_id=user_id)
            response_data['customer_id'] = str(customer.id)

        return Response(response_data)

    # New logical ID methods for unified ID access
    def retrieve_by_logical_id(self, request, logical_id=None):
        """
        GET /api/v1/customers/logical/<uuid:logical_id>/
        Get customer profile by logical ID (user_id from auth service)
        """
        try:
            customer = Customer.objects.get(user_id=logical_id)
            
            # Extract auth token from request to pass to auth service
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            auth_token = None
            if auth_header.startswith('Bearer '):
                auth_token = auth_header.split(' ')[1]
            
            # Fetch user data from auth service with authentication
            user_data = self._get_user_data_with_auth(logical_id, auth_token)
            if user_data:
                customer.user_data = user_data
            else:
                # Provide default user data if auth service call fails
                customer.user_data = {
                    'email': '',
                    'first_name': '',
                    'last_name': '',
                    'phone_number': '',
                    'user_role': 'customer',
                    'is_active': True
                }
            
            serializer = CustomerWithUserDataSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _get_user_data_with_auth(self, user_id, auth_token=None):
        """
        Fetch user data from auth service with authentication token.
        """
        try:
            import requests
            auth_service_url = getattr(
                settings, 'AUTH_SERVICE_URL', 'http://authentication-service:8001')
            
            headers = {}
            if auth_token:
                headers['Authorization'] = f'Bearer {auth_token}'
            
            # Call auth service user detail endpoint
            response = requests.get(
                f'{auth_service_url}/api/v1/auth/admin/users/{user_id}/',
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch user data from auth service: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            print(f"Error fetching user data from auth service: {e}")
            return None


    def update_by_logical_id(self, request, logical_id=None):
        """
        PUT /api/v1/customers/logical/<uuid:logical_id>/
        Update customer profile by logical ID (user_id from auth service)
        """
        try:
            customer = Customer.objects.get(user_id=logical_id)
            serializer = CustomerUpdateSerializer(customer, data=request.data)

            if serializer.is_valid():
                serializer.save()
                # Return updated data with user info
                response_serializer = CustomerWithUserDataSerializer(customer)
                return Response(response_serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def partial_update_by_logical_id(self, request, logical_id=None):
        """
        PATCH /api/v1/customers/logical/<uuid:logical_id>/
        Partial update customer profile by logical ID (user_id from auth service)
        """
        try:
            customer = Customer.objects.get(user_id=logical_id)
            serializer = CustomerUpdateSerializer(
                customer, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                # Return updated data with user info
                response_serializer = CustomerWithUserDataSerializer(customer)
                return Response(response_serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy_by_logical_id(self, request, logical_id=None):
        """
        DELETE /api/v1/customers/logical/<uuid:logical_id>/
        Delete customer profile by logical ID (user_id from auth service)
        """
        try:
            customer = Customer.objects.get(user_id=logical_id)
            customer_data = CustomerSerializer(customer).data
            customer.delete()

            return Response({
                'message': 'Customer profile deleted successfully',
                'deleted_customer': customer_data
            }, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsCustomer])
def current_customer_profile(request):
    """
    GET /api/v1/customers/profile/
    Get current authenticated customer's profile
    """
    try:
        customer = Customer.objects.get(user_id=request.user.user_id)

        # Fetch user data from auth service
        user_data = get_user_data_from_auth_service(customer.user_id)
        context = {'user_data': user_data} if user_data else {}

        serializer = CustomerSerializer(customer, context=context)
        return Response(serializer.data)
    except Customer.DoesNotExist:
        return Response(
            {
                'error': 'Customer profile not found',
                'message': 'Please create your customer profile first',
                'user_id': str(request.user.user_id)
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsCustomer])
def update_customer_profile(request):
    """
    PUT/PATCH /api/v1/customers/profile/update/
    Update current customer's profile

    Note: To update user credentials (email, name, phone), use the authentication service.
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

            # Return full customer data with user info
            user_data = get_user_data_from_auth_service(customer.user_id)
            context = {'user_data': user_data} if user_data else {}
            response_serializer = CustomerSerializer(customer, context=context)

            return Response(response_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer profile not found. Please create profile first.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsCustomer])
def create_customer_profile(request):
    """
    POST /api/v1/customers/profile/create/
    Create customer profile for authenticated user

    This should be called after user registration in the authentication service.
    """
    # Check if profile already exists
    if Customer.objects.filter(user_id=request.user.user_id).exists():
        return Response(
            {'error': 'Customer profile already exists for this user'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prepare profile data with user_id from authenticated user
    profile_data = request.data.copy()
    profile_data['user_id'] = request.user.user_id

    serializer = CustomerCreateSerializer(data=profile_data)
    if serializer.is_valid():
        customer = serializer.save()

        # Return full customer data with user info
        user_data = {
            'user_id': request.user.user_id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        context = {'user_data': user_data}
        response_serializer = CustomerSerializer(customer, context=context)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsCustomer])
def delete_customer_profile(request):
    """
    DELETE /api/v1/customers/profile/delete/
    Delete current customer's profile

    Note: This only deletes the customer profile, not the user account.
    To delete user account, use the authentication service.
    """
    try:
        customer = Customer.objects.get(user_id=request.user.user_id)
        customer_id = str(customer.id)
        user_id = str(customer.user_id)
        customer.delete()

        return Response({
            'message': 'Customer profile deleted successfully',
            'customer_id': customer_id,
            'user_id': user_id,
            'note': 'User account still exists in authentication service'
        }, status=status.HTTP_200_OK)

    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
