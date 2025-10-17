from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from .models import Project
from vehicles.models import Vehicle

from .serializers import (
    ProjectSerializer, 
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectListSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations
    
    Provides:
    - GET /api/v1/projects/ - List all projects
    - POST /api/v1/projects/ - Create new project  
    - GET /api/v1/projects/{id}/ - Get specific project
    - PUT /api/v1/projects/{id}/ - Update project
    - PATCH /api/v1/projects/{id}/ - Partial update
    - DELETE /api/v1/projects/{id}/ - Delete project
    """
    
    queryset = Project.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'project_id'  # Use project_id instead of pk
    
    # Filtering and searching
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vehicle__make', 'vehicle__model', 'customer_id']
    search_fields = ['title', 'description', 'vehicle__vin', 'vehicle__plate_number']
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
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = Project.objects.all()
        
        # If user has customer role, only show their projects
        # This assumes you have user role checking logic
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'customer':
            # Assuming you have a way to get customer_id from user
            customer_id = getattr(user, 'customer_id', None)
            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)
            else:
                queryset = queryset.none()  # No customer_id means no access
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new project"""
        serializer = self.get_serializer(data=request.data)
        if serializer .is_valid():
            project = serializer.save()
            # Return full project details after creation
            response_serializer = ProjectSerializer(project)
            return Response(
                {
                    'message': 'Project created successfully',
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
        """Update an existing project"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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
        valid_statuses = [choice[0] for choice in Project._meta.get_field('status').choices]
        
        if new_status not in valid_statuses:
            return Response(
                {'message': f'Status must be one of: {", ".join(valid_statuses)}'},
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
        return Response(serializer.data)
    
    
