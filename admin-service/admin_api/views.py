"""
Admin API Views
Provides user management endpoints for admin users
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .permissions import IsAdminUser
from .serializers import (
    UserListSerializer,
    UserSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
    UpdateUserRoleSerializer,
    UserStatsSerializer
)
from .services.auth_service import AuthServiceClient

import logging

logger = logging.getLogger(__name__)


def get_auth_token(request):
    """Extract raw JWT token string from Authorization header"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ', 1)[1]
    # Fallback to DRF JWT parser if header format varies
    try:
        auth = JWTAuthentication()
        header = auth.get_header(request)
        if header is None:
            return None
        raw_token = auth.get_raw_token(header)
        return raw_token.decode() if raw_token else None
    except Exception:
        return None


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_users(request):
    """
    List all users with optional role filtering
    Query params:
        - role: Filter by user role (customer, employee, admin)
    """
    try:
        token = get_auth_token(request)
        if not token:
            return Response(
                {'error': 'Authentication token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        role = request.query_params.get('role', None)

        auth_client = AuthServiceClient()
        users = auth_client.get_all_users(token, role)

        # Normalize response shape: accept either list or paginated dict
        if isinstance(users, dict) and 'results' in users:
            data = users['results']
        elif isinstance(users, list):
            data = users
        else:
            # If auth service returned a non-standard payload, return as-is
            logger.warning(f"Unexpected users payload type: {type(users)}")
            return Response(users, status=status.HTTP_200_OK)

        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_user_detail(request, user_id):
    """Get detailed information about a specific user"""
    try:
        token = get_auth_token(request)
        if not token:
            return Response(
                {'error': 'Authentication token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        auth_client = AuthServiceClient()
        user = auth_client.get_user(token, user_id)
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching user detail: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND if '404' in str(e) else status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_user(request):
    """
    Create a new user
    Body params:
        - email: User email
        - first_name: First name
        - last_name: Last name
        - password1: Password
        - password2: Password confirmation
        - user_role: Role (customer, employee, admin)
        - phone_number: Phone number (optional)
    """
    try:
        serializer = CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = get_auth_token(request)
        if not token:
            return Response(
                {'error': 'Authentication token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        auth_client = AuthServiceClient()
        user = auth_client.create_user(token, serializer.validated_data)
        
        return Response(user, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_user(request, user_id):
    """
    Update user information
    Body params:
        - first_name: First name (optional)
        - last_name: Last name (optional)
        - phone_number: Phone number (optional)
        - is_active: Active status (optional)
    """
    try:
        serializer = UpdateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = get_auth_token(request)
        if not token:
            return Response(
                {'error': 'Authentication token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        auth_client = AuthServiceClient()
        user = auth_client.update_user(token, user_id, serializer.validated_data)
        
        return Response(user, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def change_user_role(request, user_id):
    """
    Change user role
    Body params:
        - user_role: New role (customer, employee, admin)
    """
    try:
        serializer = UpdateUserRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = get_auth_token(request)
        if not token:
            return Response(
                {'error': 'Authentication token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        auth_client = AuthServiceClient()
        user = auth_client.update_user(token, user_id, serializer.validated_data)
        
        return Response({
            'message': f"User role updated to {serializer.validated_data['user_role']}",
            'user': user
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error changing user role: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user(request, user_id):
    """Delete a user"""
    try:
        token = get_auth_token(request)
        if not token:
            return Response(
                {'error': 'Authentication token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        auth_client = AuthServiceClient()
        auth_client.delete_user(token, user_id)
        
        return Response(
            {'message': 'User deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    try:
        token = get_auth_token(request)
        if not token:
            return Response(
                {'error': 'Authentication token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        auth_client = AuthServiceClient()
        result = auth_client.toggle_user_status(token, user_id)
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error toggling user status: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_user_statistics(request):
    """Get user statistics for dashboard"""
    try:
        token = get_auth_token(request)
        if not token:
            return Response(
                {'error': 'Authentication token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        auth_client = AuthServiceClient()
        stats = auth_client.get_user_stats(token)
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching user statistics: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([])  # Allow unauthenticated access for health check
def health_check(request):
    """Health check endpoint - No authentication required"""
    return Response({
        'status': 'healthy',
        'service': 'admin-service'
    }, status=status.HTTP_200_OK)
