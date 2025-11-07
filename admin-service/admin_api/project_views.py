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
import sys
import os

# Add parent directory to path to import notification_publisher
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from notification_publisher import publish_notification

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
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=30)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            return None
        
        return response
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout forwarding request to vehicleandproject-service: {str(e)} (URL: {url})")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error forwarding request to vehicleandproject-service: {str(e)} (URL: {url})")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding request to vehicleandproject-service: {str(e)} (URL: {url})")
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
    Admin: Approve a project with tasks and employee assignments
    
    Body: {
        "tasks": [
            {
                "title": "string",
                "description": "string",
                "assigned_employee_id": "uuid",
                "priority": "low|medium|high|critical" (optional, defaults to "medium"),
                "due_date": "YYYY-MM-DD" (optional)
            }
        ]
    }
    
    Note: Tasks must be created and employees assigned BEFORE approval.
    Once approved, the task structure is locked.
    """
    tasks = request.data.get('tasks', [])
    
    if not tasks or len(tasks) == 0:
        return Response(
            {'error': 'At least one task with an assigned employee is required to approve a project'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate all tasks have required fields
    for i, task in enumerate(tasks):
        if 'title' not in task or not task['title']:
            return Response(
                {'error': f'Task {i+1}: title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'assigned_employee_id' not in task or not task['assigned_employee_id']:
            return Response(
                {'error': f'Task {i+1}: assigned_employee_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Step 1: Create all tasks first
    created_tasks = []
    tasks_url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/"
    
    for task in tasks:
        task_data = {
            'project': project_id,
            'title': task['title'],
            'description': task.get('description', ''),
            'assigned_employee_id': task['assigned_employee_id'],
            'priority': task.get('priority', 'medium'),
        }
        
        if 'due_date' in task:
            task_data['due_date'] = task['due_date']
        
        task_response = forward_request_with_auth(request, 'POST', tasks_url, data=task_data)
        
        if task_response is None:
            # Rollback: delete created tasks if any
            for created_task in created_tasks:
                delete_url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/{created_task['task_id']}/"
                forward_request_with_auth(request, 'DELETE', delete_url)
            
            return Response(
                {'error': 'Failed to connect to project service while creating tasks'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        if task_response.status_code != 201:
            # Rollback: delete created tasks
            for created_task in created_tasks:
                delete_url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/{created_task['task_id']}/"
                forward_request_with_auth(request, 'DELETE', delete_url)
            
            try:
                error_data = task_response.json()
                logger.error(f"Failed to create task: {error_data}")
                return Response(
                    {
                        'error': f'Failed to create task: {task["title"]}',
                        'details': error_data
                    },
                    status=task_response.status_code
                )
            except:
                return Response(
                    {'error': f'Failed to create task: {task["title"]}'},
                    status=task_response.status_code
                )
        
        try:
            created_task = task_response.json()
            created_tasks.append(created_task)
            
            # Send notification to assigned employee
            try:
                employee_id = task['assigned_employee_id']
                project_title = request.data.get('project_title', 'a project')
                
                publish_notification(
                    recipient_user_id=employee_id,
                    message=f'You have been assigned to a new project task: {task["title"]}',
                    title='New Project Task Assignment',
                    notification_type='PROJECT',
                    priority='high',
                    metadata={
                        'project_id': project_id,
                        'task_id': created_task.get('id') or created_task.get('task_id'),
                        'task_title': task['title'],
                        'project_title': project_title
                    }
                )
                logger.info(f"Notification sent to employee {employee_id} for task assignment")
            except Exception as notif_error:
                logger.error(f"Failed to send notification to employee: {str(notif_error)}")
                # Don't fail the task creation if notification fails
                
        except:
            # Rollback
            for created_task in created_tasks:
                delete_url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/{created_task['task_id']}/"
                forward_request_with_auth(request, 'DELETE', delete_url)
            
            return Response(
                {'error': 'Failed to parse task creation response'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Step 2: Approve the project
    project_url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/{project_id}/"
    approval_data = {
        'approval_status': 'approved',
        'status': 'accepted'
    }
    
    approval_response = forward_request_with_auth(request, 'PATCH', project_url, data=approval_data)
    
    if approval_response is None:
        # Rollback: delete created tasks
        for created_task in created_tasks:
            delete_url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/{created_task['task_id']}/"
            forward_request_with_auth(request, 'DELETE', delete_url)
        
        return Response(
            {'error': 'Failed to connect to project service while approving'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    logger.info(f"Approve project response status: {approval_response.status_code}")
    
    if approval_response.status_code == 200:
        try:
            project_data = approval_response.json()
            return Response(
                {
                    'message': 'Project approved successfully with tasks and employee assignments',
                    'data': {
                        'project': project_data,
                        'tasks': created_tasks
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error parsing approval response JSON: {str(e)}")
            # Note: Tasks are created and project is approved, but response parsing failed
            return Response(
                {
                    'message': 'Project approved but response parsing failed',
                    'data': {
                        'tasks': created_tasks
                    }
                },
                status=status.HTTP_200_OK
            )
    else:
        # Rollback: delete created tasks since approval failed
        for created_task in created_tasks:
            delete_url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/{created_task['task_id']}/"
            forward_request_with_auth(request, 'DELETE', delete_url)
        
        try:
            error_data = approval_response.json()
            logger.error(f"Project approval failed: {error_data}")
            return Response(
                {
                    'error': 'Failed to approve project',
                    'details': error_data
                },
                status=approval_response.status_code
            )
        except:
            logger.error(f"Project approval failed with status {approval_response.status_code}")
            return Response(
                {'error': 'Failed to approve project'},
                status=approval_response.status_code
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
    Admin: Assign an employee to a project (via tasks)
    
    Note: Employees are assigned to projects through tasks, not directly.
    This endpoint creates a task for the project and assigns the employee to it.
    
    Body: {
        "assigned_employee_id": "uuid",
        "task_title": "string" (optional, defaults to "Main Project Task"),
        "task_description": "string" (optional),
        "priority": "low|medium|high|critical" (optional, defaults to "medium")
    }
    """
    if 'assigned_employee_id' not in request.data:
        return Response(
            {'error': 'assigned_employee_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create a task for the project and assign the employee to it
    url = f"{VEHICLEPROJECT_SERVICE_URL}/api/v1/projects/tasks/"
    data = {
        'project': project_id,
        'assigned_employee_id': request.data['assigned_employee_id'],
        'title': request.data.get('task_title', 'Main Project Task'),
        'description': request.data.get('task_description', 'Primary task for project completion'),
        'priority': request.data.get('priority', 'medium')
    }
    
    response = forward_request_with_auth(request, 'POST', url, data=data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to project service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    if response.status_code == 201:
        # Send notification to assigned employee
        try:
            employee_id = request.data['assigned_employee_id']
            task_title = request.data.get('task_title', 'Main Project Task')
            
            publish_notification(
                recipient_user_id=employee_id,
                message=f'You have been assigned to project task: {task_title}',
                title='New Project Assignment',
                notification_type='PROJECT',
                priority='high',
                metadata={
                    'project_id': project_id,
                    'task_title': task_title,
                    'task_description': request.data.get('task_description', '')
                }
            )
            logger.info(f"Notification sent to employee {employee_id} for project assignment")
        except Exception as notif_error:
            logger.error(f"Failed to send notification to employee: {str(notif_error)}")
            # Don't fail the assignment if notification fails
        
        return Response(
            {
                'message': 'Employee assigned to project via task successfully',
                'data': response.json()
            },
            status=status.HTTP_200_OK
        )
    else:
        try:
            error_data = response.json()
            return Response(
                {
                    'error': 'Failed to assign employee to project',
                    'details': error_data
                },
                status=response.status_code
            )
        except:
            return Response(
                {'error': 'Failed to assign employee to project'},
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
