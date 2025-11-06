"""
Admin API Views for Project and Task Management
Provides project approval, employee assignment, and task CRUD operations
"""
import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from .permissions import IsAdminUser

import logging

logger = logging.getLogger(__name__)

# Vehicle and Project Service URL
VEHICLEPROJECT_SERVICE_URL = getattr(settings, 'VEHICLEPROJECT_SERVICE_URL', 'http://vehicleandproject-service:8004')


def forward_request_with_auth(request, method, url, data=None, params=None):
    """
    Forward request to vehicleandproject-service with authentication
    """
    # Get authorization header from request
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return None
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding request to vehicleandproject-service: {str(e)}")
        return None


# ==================== PROJECT MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_all_projects(request):
    """
    Admin: List all projects with filtering
    Query params:
        - status: Filter by project status
        - approval_status: Filter by approval status (pending, approved, rejected)
        - customer_id: Filter by customer
        - assigned_employee_id: Filter by assigned employee
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/"
    response = forward_request_with_auth(request, 'GET', url, params=request.query_params.dict())
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_pending_projects(request):
    """
    Admin: Get all projects pending approval
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/"
    params = {'approval_status': 'pending'}
    response = forward_request_with_auth(request, 'GET', url, params=params)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_project_detail(request, project_id):
    """
    Admin: Get specific project details
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/{project_id}/"
    response = forward_request_with_auth(request, 'GET', url)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def approve_project(request, project_id):
    """
    Admin: Approve a project
    Body: {
        "approval_status": "approved",
        "assigned_employee_id": "uuid" (optional)
    }
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/{project_id}/"
    
    # Prepare data for approval
    data = {
        'approval_status': 'approved',
        'status': 'accepted'
    }
    
    # Add employee assignment if provided
    if 'assigned_employee_id' in request.data:
        data['assigned_employee_id'] = request.data['assigned_employee_id']
    
    response = forward_request_with_auth(request, 'PATCH', url, data=data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            'message': 'Project approved successfully',
            'data': response.json() if response.status_code == 200 else None
        },
        status=response.status_code
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def reject_project(request, project_id):
    """
    Admin: Reject a project
    Body: {
        "rejection_reason": "string" (optional)
    }
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/{project_id}/"
    
    data = {
        'approval_status': 'rejected',
        'status': 'cancelled'
    }
    
    response = forward_request_with_auth(request, 'PATCH', url, data=data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            'message': 'Project rejected successfully',
            'data': response.json() if response.status_code == 200 else None
        },
        status=response.status_code
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assign_employee_to_project(request, project_id):
    """
    Admin: Assign an employee to a project
    Body: {
        "assigned_employee_id": "uuid"
    }
    """
    if 'assigned_employee_id' not in request.data:
        return Response(
            {'error': 'assigned_employee_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/{project_id}/"
    data = {
        'assigned_employee_id': request.data['assigned_employee_id']
    }
    
    response = forward_request_with_auth(request, 'PATCH', url, data=data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            'message': 'Employee assigned to project successfully',
            'data': response.json() if response.status_code == 200 else None
        },
        status=response.status_code
    )


# ==================== TASK MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_all_tasks(request):
    """
    Admin: List all tasks with filtering
    Query params:
        - project: Filter by project ID
        - status: Filter by task status
        - priority: Filter by priority
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/"
    response = forward_request_with_auth(request, 'GET', url, params=request.query_params.dict())
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_tasks_by_project(request, project_id):
    """
    Admin: Get all tasks for a specific project
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/by_project/"
    params = {'project_id': project_id}
    response = forward_request_with_auth(request, 'GET', url, params=params)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_task_detail(request, task_id):
    """
    Admin: Get specific task details
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/{task_id}/"
    response = forward_request_with_auth(request, 'GET', url)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_task(request):
    """
    Admin: Create a new task for a project
    Body: {
        "project": "project_uuid",
        "title": "string",
        "description": "string",
        "priority": "low|medium|high|critical",
        "due_date": "YYYY-MM-DD" (optional)
    }
    """
    required_fields = ['project', 'title', 'description']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/"
    response = forward_request_with_auth(request, 'POST', url, data=request.data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_task(request, task_id):
    """
    Admin: Update a task
    Body: {
        "title": "string" (optional),
        "description": "string" (optional),
        "status": "not_started|in_progress|completed|blocked" (optional),
        "priority": "low|medium|high|critical" (optional),
        "due_date": "YYYY-MM-DD" (optional)
    }
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/{task_id}/"
    method = 'PUT' if request.method == 'PUT' else 'PATCH'
    response = forward_request_with_auth(request, method, url, data=request.data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_task(request, task_id):
    """
    Admin: Delete a task
    """
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/{task_id}/"
    response = forward_request_with_auth(request, 'DELETE', url)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {'message': 'Task deleted successfully'},
        status=status.HTTP_204_NO_CONTENT if response.status_code == 204 else response.status_code
    )
