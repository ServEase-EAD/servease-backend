from pickle import GET
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from .models import Project, Task
from vehicles.models import Vehicle
from .permissions import IsCustomer, IsEmployee, IsAdmin
import logging

logger = logging.getLogger(__name__)

from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectListSerializer,
    ProjectApprovalSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer
)

# Import notification publisher for admin notifications
from notification_publisher import publish_notification
from .service_clients import AuthServiceClient


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations

    Provides:
    - GET /api/v1/projects/ - List projects (filtered by user role)
    - POST /api/v1/projects/ - Create new project  
    - GET /api/v1/projects/{id}/ - Get specific project
    - PUT /api/v1/projects/{id}/ - Update project
    - PATCH /api/v1/projects/{id}/ - Partial update
    - DELETE /api/v1/projects/{id}/ - Delete project
    
    Access Control:
    - Employees: Can see all projects, can filter by customer_id query parameter
    - Customers: Can only see their own projects (auto-filtered by JWT token)
    
    Query Parameters (for employees):
    - customer_id: Filter projects for specific customer
    - status: Filter by project status
    - vehicle__make: Filter by vehicle make
    - vehicle__model: Filter by vehicle model
    """

    queryset = Project.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'project_id'  # Use project_id instead of pk

    # Filtering and searching
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vehicle__make', 'vehicle__model', 'customer_id']
    search_fields = ['title', 'description',
                     'vehicle__vin', 'vehicle__plate_number']
    ordering_fields = ['created_at', 'expected_completion_date', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ProjectCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        elif self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def get_permissions(self):
        """RBAC logic for projects"""
        if self.action in ['create']:
            permission_classes = [IsAuthenticated, IsCustomer]
        elif self.action in ['update', 'partial_update']:
            # Allow customers, employees, and admins to update projects
            permission_classes = [IsAuthenticated]
        elif self.action in ['destroy']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['customer_projects', 'by_vehicle']:
            permission_classes = [IsAuthenticated, IsCustomer]
        elif self.action in ['change_status']:
            permission_classes = [IsAuthenticated, IsEmployee]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        queryset = Project.objects.all()

        # Admins can see all projects
        if getattr(user, "user_role", None) == "admin":
            return queryset

        # Employees can see projects that have tasks assigned to them
        elif getattr(user, "user_role", None) == "employee":
            employee_id = getattr(user, 'id', None)
            if employee_id:
                # Get project IDs that have tasks assigned to this employee
                from django.db.models import Q
                return queryset.filter(tasks__assigned_employee_id=employee_id).distinct()
            return queryset.none()

        # Customers can only see their own projects (using customer_id from JWT token)
        elif getattr(user, "user_role", None) == "customer":
            return queryset.filter(customer_id=user.id)

        # Default: no access for unauthenticated users
        return queryset.none()

    def create(self, request, *args, **kwargs):
        """Create a new project with automatic customer_id from JWT token"""
        # Get customer_id from JWT token
        user = request.user
        if not hasattr(user, 'user_role') or user.user_role != 'customer':
            return Response(
                {'error': 'Only customers can create projects'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract customer_id from JWT token (user.id contains the user_id from the token)
        customer_id = getattr(user, 'id', None)
        if not customer_id:
            return Response(
                {'error': 'Customer ID not found in token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the request data first
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the project with customer_id and pending approval status
            project = serializer.save(customer_id=customer_id, approval_status='pending')
            
            # Send notifications to all admin users about the new project
            try:
                # Get admin users from authentication service
                admin_users = AuthServiceClient.get_admin_users()
                
                # If we can't get admins from service, use the known admin users as fallback
                if not admin_users or len(admin_users) == 0:
                    logger.warning("Could not fetch admin users from auth service, using fallback list")
                    # Known admin user IDs - only use valid UUIDs
                    known_admin_users = [
                        'ec0e0759-bdd9-4d43-b971-67b5f2a3cbb9',  # dana@gmail.com
                    ]
                    
                    for admin_id in known_admin_users:
                        success = publish_notification(
                            recipient_user_id=admin_id,
                            message=f"New project '{project.title}' has been created by customer and requires approval.",
                            title="New Project Created",
                            priority="high",
                            notification_type="PROJECT",
                            metadata={
                                'project_id': str(project.project_id),
                                'title': project.title,
                                'customer_id': customer_id,
                                'expected_completion_date': project.expected_completion_date.isoformat() if project.expected_completion_date else None
                            }
                        )
                        if success:
                            logger.info(f"✓ Project notification sent to admin {admin_id}")
                        else:
                            logger.error(f"✗ Failed to send project notification to admin {admin_id}")
                else:
                    # Use admin users from service
                    for admin_user in admin_users:
                        admin_id = admin_user.get('id')
                        if admin_id:
                            success = publish_notification(
                                recipient_user_id=admin_id,
                                message=f"New project '{project.title}' has been created by customer and requires approval.",
                                title="New Project Created",
                                priority="high",
                                notification_type="PROJECT",
                                metadata={
                                    'project_id': str(project.project_id),
                                    'title': project.title,
                                    'customer_id': customer_id,
                                    'expected_completion_date': project.expected_completion_date.isoformat() if project.expected_completion_date else None
                                }
                            )
                            if success:
                                logger.info(f"✓ Project notification sent to admin {admin_id}")
                            else:
                                logger.error(f"✗ Failed to send project notification to admin {admin_id}")
                                
            except Exception as e:
                # Don't fail project creation if notifications fail
                logger.error(f"Failed to send admin notifications for project creation: {e}")
            
            # Return full project details after creation
            response_serializer = ProjectSerializer(project)
            return Response(
                {
                    'message': 'Project created successfully and pending admin approval',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating project',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update project - ongoing cannot be edited, pending can be edited by customer"""

        instance = self.get_object()

        # Check if project status allows editing
        if instance.status == 'in_progress':
            return Response(
                {'error': 'Cannot edit project that is currently in progress'},
                status=status.HTTP_403_FORBIDDEN
            )

        # ongoing cannot edit and pending can be edit by customer
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        if serializer.is_valid():
            project = serializer.save()
            response_serializer = ProjectSerializer(project)
            return Response(
                {
                    'message': 'Project updated successfully',
                    'data': response_serializer.data
                }
            )
        return Response(
            {
                'message': 'Error updating project',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete project - pending can be deleted by customer and employee, ongoing cannot be deleted by anyone"""

        instance = self.get_object()
        user = request.user

        # Check if project status allows deletion
        if instance.status == 'in_progress':
            return Response(
                {'error': 'Cannot delete project that is currently in progress'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Only allow deletion for certain statuses
        deletable_statuses = ['not_started', 'cancelled', 'on_hold']
        if instance.status not in deletable_statuses:
            return Response(
                {'error': f'Project with status "{instance.status}" cannot be deleted'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Additional check: customers can only delete their own projects
        # Convert both IDs to strings to handle UUID vs string comparison
        if user.user_role == 'customer' and str(instance.customer_id) != str(user.id):
            return Response(
                {'error': 'You can only delete your own projects'},
                status=status.HTTP_403_FORBIDDEN
            )

        """Delete a project"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Project deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def customer_projects(self, request):
        """Get projects for the authenticated customer"""
        user = request.user
        if not hasattr(user, 'role') or user.role != 'customer':
            return Response(
                {'error': 'Only customers can access their projects'},
                status=status.HTTP_403_FORBIDDEN
            )

        customer_id = getattr(user, 'customer_id', None)
        if not customer_id:
            return Response(
                {'error': 'Customer ID not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        projects = self.get_queryset().filter(customer_id=customer_id)
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_status(self, request, project_id=None):
        """Custom action to change the status of a project"""
        project = self.get_object()
        new_status = request.data.get('status')
        valid_statuses = [choice[0]
                          for choice in Project._meta.get_field('status').choices]

        if new_status not in valid_statuses:
            return Response(
                {'message':
                    f'Status must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        project.status = new_status
        project.save()
        serializer = ProjectSerializer(project)
        return Response(
            {
                'message': 'Project status updated successfully',
                'data': serializer.data
            }
        )

    @action(detail=False, methods=['get'])
    def by_vehicle(self, request):
        """Get projects for a specific vehicle"""
        vehicle_id = request.query_params.get('vehicle_id')
        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        projects = self.get_queryset().filter(vehicle__vehicle_id=vehicle_id)
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectListSerializer(projects, many=True)
        return Response(
            {
                'message': f'Projects for vehicle {vehicle_id}',
                'count': projects.count(),
                'data': serializer.data
            }
        )

    # Note: Admin operations (approve/reject, assign employees) are handled by admin-service
    # This service only provides read access to projects based on user role


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task operations
    
    - Admins: Full CRUD access to tasks (accessed via admin-service proxy)
    - Employees: Read-only access to tasks for their assigned projects
    - Customers: Read-only access to tasks for their own projects
    
    Note: Admin operations should be accessed through admin-service for better control
    """
    
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'task_id'
    
    # Temporarily disabled due to django-filters compatibility issue
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['project', 'status', 'priority']
    # Temporarily disable filters to fix django-filters compatibility issue
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['status', 'priority', 'assigned_employee_id']
    # search_fields = ['title', 'description']
    # ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def get_permissions(self):
        """RBAC logic for tasks - Admin only for write operations"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter tasks based on user permissions - READ ONLY"""
        user = self.request.user
        queryset = Task.objects.select_related('project').all()
        
        # Admins can see all tasks (but create/update/delete via admin-service)
        if getattr(user, "user_role", None) == "admin":
            return queryset
        
        # Employees can see tasks assigned to them directly
        elif getattr(user, "user_role", None) == "employee":
            employee_id = getattr(user, 'id', None)
            if employee_id:
                return queryset.filter(assigned_employee_id=employee_id)
            return queryset.none()
        
        # Customers can see tasks for their projects
        elif getattr(user, "user_role", None) == "customer":
            customer_id = getattr(user, 'id', None)
            if customer_id:
                return queryset.filter(project__customer_id=customer_id)
            return queryset.none()
        
        return queryset.none()
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get all tasks for a specific project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = self.get_queryset().filter(project__project_id=project_id)
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TaskSerializer(tasks, many=True)
        return Response(
            {
                'message': f'Tasks for project {project_id}',
                'count': tasks.count(),
                'data': serializer.data
            }
        )
