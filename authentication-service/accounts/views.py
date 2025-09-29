from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .tokens import CustomRefreshToken
from django.db.models import Q

from .serializers import *
from .permissions import IsAdmin, IsEmployeeOrAdmin, IsOwnerOrAdmin
from .models import CustomUser


class UserRegistrationAPIView(GenericAPIView):
    """Customer registration - publicly accessible"""
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = CustomRefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(
            token), "access": str(token.access_token)}
        data["user_role"] = user.user_role
        return Response(data, status=status.HTTP_201_CREATED)


class EmployeeRegistrationAPIView(GenericAPIView):
    """Employee registration - admin only"""
    permission_classes = (IsAdmin,)
    serializer_class = EmployeeRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Return employee data without tokens (admin creates employee accounts)
        response_data = UserDetailSerializer(user).data
        response_data["message"] = "Employee account created successfully"

        return Response(response_data, status=status.HTTP_201_CREATED)


class UserLoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = CustomUserSerializer(user)
        token = CustomRefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(
            token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)


class UserLogoutAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = CustomRefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeListAPIView(ListAPIView):
    """List all employees - admin only"""
    permission_classes = (IsAdmin,)
    serializer_class = UserListSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(user_role='employee').order_by('-created_at')


class UserListAPIView(ListAPIView):
    """List all users - admin only"""
    permission_classes = (IsAdmin,)
    serializer_class = UserListSerializer

    def get_queryset(self):
        role = self.request.query_params.get('role', None)
        queryset = CustomUser.objects.all().order_by('-created_at')

        if role:
            queryset = queryset.filter(user_role=role)

        return queryset


class UserDetailAPIView(RetrieveUpdateDestroyAPIView):
    """Get, update, or delete user details"""
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CustomUser.objects.all()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'GET':
            # Users can view their own profile, admin can view any
            permission_classes = [IsOwnerOrAdmin]
        elif self.request.method in ['PUT', 'PATCH']:
            # Users can update their own profile, admin can update any
            permission_classes = [IsOwnerOrAdmin]
        elif self.request.method == 'DELETE':
            # Only admin can delete users
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_profile(request):
    """Get current user's profile"""
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_current_user_profile(request):
    """Update current user's profile"""
    serializer = CustomUserSerializer(
        request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdmin])
def toggle_user_status(request, user_id):
    """Toggle user active status - admin only"""
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()

        status_text = "activated" if user.is_active else "deactivated"
        return Response({
            "message": f"User {user.email} has been {status_text}",
            "is_active": user.is_active
        })
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_dashboard_stats(request):
    """Get dashboard statistics for admin"""
    total_users = CustomUser.objects.count()
    total_customers = CustomUser.objects.filter(user_role='customer').count()
    total_employees = CustomUser.objects.filter(user_role='employee').count()
    total_admins = CustomUser.objects.filter(user_role='admin').count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    inactive_users = CustomUser.objects.filter(is_active=False).count()

    return Response({
        "total_users": total_users,
        "total_customers": total_customers,
        "total_employees": total_employees,
        "total_admins": total_admins,
        "active_users": active_users,
        "inactive_users": inactive_users
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_token(request):
    """Validate JWT token and return user data - for inter-service communication"""
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken

    try:
        auth = JWTAuthentication()
        header = auth.get_header(request)

        if header is None:
            return Response({'error': 'Authorization header missing'},
                            status=status.HTTP_401_UNAUTHORIZED)

        raw_token = auth.get_raw_token(header)
        if raw_token is None:
            return Response({'error': 'Invalid token format'},
                            status=status.HTTP_401_UNAUTHORIZED)

        validated_token = auth.get_validated_token(raw_token)
        user = auth.get_user(validated_token)

        if not user or not user.is_active:
            return Response({'error': 'User not found or inactive'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Return user data for other services
        return Response({
            'user_id': user.id,
            'email': user.email,
            'user_role': user.user_role,
            'is_active': user.is_active,
            'first_name': getattr(user, 'first_name', ''),
            'last_name': getattr(user, 'last_name', ''),
        })

    except InvalidToken as e:
        return Response({'error': 'Invalid token'},
                        status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': f'Token validation failed: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
