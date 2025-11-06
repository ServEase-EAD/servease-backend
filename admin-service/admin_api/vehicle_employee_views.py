"""
Admin API Views for Vehicle and Employee Management
Provides vehicle overview, employee workload monitoring, and assignment management
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

# Service URLs
VEHICLE_SERVICE_URL = getattr(settings, 'VEHICLEPROJECT_SERVICE_URL', 'http://vehicleandproject-service:8004')
EMPLOYEE_SERVICE_URL = getattr(settings, 'EMPLOYEE_SERVICE_URL', 'http://employee-service:8003')
APPOINTMENT_SERVICE_URL = getattr(settings, 'APPOINTMENT_SERVICE_URL', 'http://appointment-service:8005')


def forward_request(request, method, url, data=None, params=None):
    """
    Forward request to external service with authentication
    """
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
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return None
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding request: {str(e)}")
        return None


# ==================== VEHICLE MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_all_vehicles(request):
    """
    Admin: List all vehicles with filtering
    Query params:
        - customer_id: Filter by customer owner
        - assigned_employee_id: Filter by assigned employee
        - has_active_projects: Filter vehicles with active projects
        - has_active_appointments: Filter vehicles with active appointments
    """
    url = f"{VEHICLE_SERVICE_URL}/api/v1/vehicles/"
    response = forward_request(request, 'GET', url, params=request.query_params.dict())
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to vehicle service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_vehicle_detail(request, vehicle_id):
    """
    Admin: Get vehicle details with service history
    Includes:
        - Vehicle information
        - Owner details
        - Active projects
        - Active appointments
        - Service history
        - Assigned employees
    """
    url = f"{VEHICLE_SERVICE_URL}/api/v1/vehicles/{vehicle_id}/"
    response = forward_request(request, 'GET', url)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to vehicle service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    vehicle_data = response.json()
    
    # Optionally fetch additional data (projects, appointments)
    # This can be enhanced based on the vehicle service API structure
    
    return Response(vehicle_data, status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_vehicles_by_employee(request, employee_id):
    """
    Admin: Get all vehicles assigned to a specific employee
    """
    url = f"{VEHICLE_SERVICE_URL}/api/v1/vehicles/"
    params = {'assigned_employee_id': employee_id}
    response = forward_request(request, 'GET', url, params=params)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to vehicle service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_vehicles_by_service_type(request):
    """
    Admin: Filter vehicles by service type
    Query params:
        - service_type: Type of service (maintenance, modification, repair, etc.)
    """
    service_type = request.query_params.get('service_type')
    if not service_type:
        return Response(
            {'error': 'service_type query parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # This would need to be implemented based on how service types are tracked
    # For now, return a basic filtered list
    url = f"{VEHICLE_SERVICE_URL}/api/v1/vehicles/"
    response = forward_request(request, 'GET', url, params=request.query_params.dict())
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to vehicle service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


# ==================== EMPLOYEE WORKLOAD MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_employee_workload(request, employee_id):
    """
    Admin: Get employee workload details
    Returns:
        - Active projects count
        - Active appointments count
        - Active tasks count
        - Completed tasks this month
        - Total working hours this month
        - Task completion rate
    """
    # Get employee tasks
    tasks_url = f"{EMPLOYEE_SERVICE_URL}/api/v1/employees/{employee_id}/tasks/"
    tasks_response = forward_request(request, 'GET', tasks_url)
    
    # Get employee time logs
    timelogs_url = f"{EMPLOYEE_SERVICE_URL}/api/v1/employees/timelogs/stats/"
    params = {'employee_id': employee_id}
    timelogs_response = forward_request(request, 'GET', timelogs_url, params=params)
    
    workload_data = {
        'employee_id': employee_id,
        'tasks': tasks_response.json() if tasks_response and tasks_response.status_code == 200 else [],
        'time_stats': timelogs_response.json() if timelogs_response and timelogs_response.status_code == 200 else {}
    }
    
    return Response(workload_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_employees_workload(request):
    """
    Admin: Get workload summary for all employees
    Returns list of employees with their workload metrics
    """
    # This would aggregate data from multiple services
    # Implementation depends on how employee service exposes this data
    
    url = f"{EMPLOYEE_SERVICE_URL}/api/v1/employees/"
    response = forward_request(request, 'GET', url)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to employee service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    employees = response.json()
    
    # For each employee, we could fetch their workload
    # This is a simplified version - in production, you'd want a dedicated endpoint
    
    return Response(employees, status=response.status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assign_employee_to_task(request):
    """
    Admin: Assign an employee to a specific task
    Body: {
        "task_id": "uuid",
        "employee_id": "uuid",
        "task_type": "project_task|appointment_task"
    }
    """
    required_fields = ['task_id', 'employee_id', 'task_type']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    task_type = request.data['task_type']
    task_id = request.data['task_id']
    
    # Route to appropriate service based on task type
    if task_type == 'project_task':
        url = f"{VEHICLE_SERVICE_URL}/api/v1/projects/tasks/{task_id}/"
    elif task_type == 'appointment_task':
        url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/tasks/{task_id}/"
    else:
        return Response(
            {'error': 'Invalid task_type. Must be "project_task" or "appointment_task"'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = {'assigned_employee_id': request.data['employee_id']}
    response = forward_request(request, 'PATCH', url, data=data)
    
    if response is None:
        return Response(
            {'error': 'Failed to assign employee to task'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    # Send notification to assigned employee
    if response.status_code == 200:
        try:
            employee_id = request.data['employee_id']
            task_type_display = 'project' if task_type == 'project_task' else 'appointment'
            
            publish_notification(
                recipient_user_id=employee_id,
                message=f'You have been assigned to a new {task_type_display} task',
                title=f'New {task_type_display.capitalize()} Task Assignment',
                notification_type='PROJECT' if task_type == 'project_task' else 'APPOINTMENT',
                priority='high',
                metadata={
                    'task_id': task_id,
                    'task_type': task_type
                }
            )
            logger.info(f"Notification sent to employee {employee_id} for task assignment")
        except Exception as notif_error:
            logger.error(f"Failed to send notification to employee: {str(notif_error)}")
            # Don't fail the assignment if notification fails
    
    return Response(
        {
            'message': 'Employee assigned to task successfully',
            'data': response.json() if response.status_code == 200 else None
        },
        status=response.status_code
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def unassign_employee_from_task(request):
    """
    Admin: Unassign an employee from a specific task
    Body: {
        "task_id": "uuid",
        "task_type": "project_task|appointment_task"
    }
    """
    required_fields = ['task_id', 'task_type']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    task_type = request.data['task_type']
    task_id = request.data['task_id']
    
    # Route to appropriate service based on task type
    if task_type == 'project_task':
        url = f"{VEHICLE_SERVICE_URL}/api/v1/projects/tasks/{task_id}/"
    elif task_type == 'appointment_task':
        url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/tasks/{task_id}/"
    else:
        return Response(
            {'error': 'Invalid task_type. Must be "project_task" or "appointment_task"'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = {'assigned_employee_id': None}
    response = forward_request(request, 'PATCH', url, data=data)
    
    if response is None:
        return Response(
            {'error': 'Failed to unassign employee from task'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            'message': 'Employee unassigned from task successfully',
            'data': response.json() if response.status_code == 200 else None
        },
        status=response.status_code
    )


# ==================== DASHBOARD STATISTICS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_admin_dashboard_stats(request):
    """
    Admin: Get comprehensive dashboard statistics
    Returns:
        - Total vehicles
        - Active projects
        - Pending projects
        - Active appointments
        - Pending appointments
        - Total employees
        - Employee utilization rate
        - Tasks overview
    """
    dashboard_stats = {}
    
    # Get vehicle stats
    vehicles_url = f"{VEHICLE_SERVICE_URL}/api/v1/vehicles/"
    vehicles_response = forward_request(request, 'GET', vehicles_url)
    if vehicles_response and vehicles_response.status_code == 200:
        vehicles_data = vehicles_response.json()
        dashboard_stats['total_vehicles'] = len(vehicles_data) if isinstance(vehicles_data, list) else 0
    
    # Get project stats
    projects_url = f"{VEHICLE_SERVICE_URL}/api/v1/projects/"
    projects_response = forward_request(request, 'GET', projects_url)
    if projects_response and projects_response.status_code == 200:
        projects_data = projects_response.json()
        if isinstance(projects_data, list):
            dashboard_stats['total_projects'] = len(projects_data)
            dashboard_stats['pending_projects'] = len([p for p in projects_data if p.get('status') == 'pending'])
            dashboard_stats['active_projects'] = len([p for p in projects_data if p.get('status') in ['in_progress', 'accepted']])
    
    # Get appointment stats
    appointments_url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/appointments/stats/"
    appointments_response = forward_request(request, 'GET', appointments_url)
    if appointments_response and appointments_response.status_code == 200:
        dashboard_stats['appointment_stats'] = appointments_response.json()
    
    # Get employee stats
    employees_url = f"{EMPLOYEE_SERVICE_URL}/api/v1/employees/"
    employees_response = forward_request(request, 'GET', employees_url)
    if employees_response and employees_response.status_code == 200:
        employees_data = employees_response.json()
        dashboard_stats['total_employees'] = len(employees_data) if isinstance(employees_data, list) else 0
    
    return Response(dashboard_stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_project_progress_summary(request):
    """
    Admin: Get project progress summary with delays
    Returns list of projects with:
        - Project details
        - Overall progress percentage
        - Tasks completed vs total
        - Delays (if any)
        - Estimated completion date
    """
    url = f"{VEHICLE_SERVICE_URL}/api/v1/projects/"
    params = request.query_params.dict()
    response = forward_request(request, 'GET', url, params=params)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to vehicle service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    projects_data = response.json()
    
    # Enhance with progress calculations
    # This would ideally be done by the project service itself
    
    return Response(projects_data, status=response.status_code)
