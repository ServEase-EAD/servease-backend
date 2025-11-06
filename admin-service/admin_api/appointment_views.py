"""
Admin API Views for Appointment Management
Provides appointment approval, employee assignment, and task tracking
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

# Appointment Service URL
APPOINTMENT_SERVICE_URL = getattr(settings, 'APPOINTMENT_SERVICE_URL', 'http://appointment-service:8005')


def forward_appointment_request(request, method, url, data=None, params=None):
    """
    Forward request to appointment-service with authentication
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
        logger.error(f"Error forwarding request to appointment-service: {str(e)}")
        return None


# ==================== APPOINTMENT MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_all_appointments(request):
    """
    Admin: List all appointments with filtering
    Query params:
        - status: Filter by appointment status
        - approval_status: Filter by approval status (pending, approved, rejected)
        - customer_id: Filter by customer
        - employee_id: Filter by assigned employee
        - category: Filter by appointment category
        - date_from: Filter appointments from this date
        - date_to: Filter appointments until this date
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/"
    response = forward_appointment_request(request, 'GET', url, params=request.query_params.dict())
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_pending_appointments(request):
    """
    Admin: Get all appointments pending approval
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/"
    params = {'status': 'pending'}
    response = forward_appointment_request(request, 'GET', url, params=params)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_appointment_detail(request, appointment_id):
    """
    Admin: Get specific appointment details including tasks
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/{appointment_id}/"
    response = forward_appointment_request(request, 'GET', url)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def approve_appointment(request, appointment_id):
    """
    Admin: Approve an appointment
    Body: {
        "scheduled_date": "YYYY-MM-DD",
        "scheduled_time": "HH:MM:SS",
        "assigned_employees": ["employee_id1", "employee_id2"] (optional)
    }
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/{appointment_id}/confirm/"
    
    # Use the confirm endpoint to approve
    response = forward_appointment_request(request, 'POST', url, data=request.data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            'message': 'Appointment approved successfully',
            'data': response.json() if response.status_code in [200, 201] else None
        },
        status=response.status_code
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def reject_appointment(request, appointment_id):
    """
    Admin: Reject an appointment
    Body: {
        "cancellation_reason": "string"
    }
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/{appointment_id}/cancel/"
    
    data = request.data if request.data else {}
    response = forward_appointment_request(request, 'POST', url, data=data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            'message': 'Appointment rejected successfully',
            'data': response.json() if response.status_code == 200 else None
        },
        status=response.status_code
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def assign_employees_to_appointment(request, appointment_id):
    """
    Admin: Assign one or more employees to an appointment
    Body: {
        "employee_ids": ["employee_id1", "employee_id2"]
    }
    """
    if 'employee_ids' not in request.data:
        return Response(
            {'error': 'employee_ids is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/{appointment_id}/assign/"
    response = forward_appointment_request(request, 'POST', url, data=request.data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            'message': 'Employees assigned to appointment successfully',
            'data': response.json() if response.status_code == 200 else None
        },
        status=response.status_code
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_appointment_task(request, appointment_id):
    """
    Admin: Create a task for an appointment
    Body: {
        "title": "string",
        "description": "string",
        "assigned_employee_id": "uuid",
        "estimated_duration": 120 (minutes),
        "priority": "low|medium|high|critical"
    }
    """
    required_fields = ['title', 'description']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Add appointment_id to the task data
    task_data = {**request.data, 'appointment_id': appointment_id}
    
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/tasks/"
    response = forward_appointment_request(request, 'POST', url, data=task_data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_appointment_tasks(request, appointment_id):
    """
    Admin: Get all tasks for a specific appointment
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/tasks/"
    params = {'appointment_id': appointment_id}
    response = forward_appointment_request(request, 'GET', url, params=params)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_appointment_task(request, task_id):
    """
    Admin: Update an appointment task
    Body: {
        "title": "string" (optional),
        "description": "string" (optional),
        "assigned_employee_id": "uuid" (optional),
        "status": "not_started|in_progress|completed|blocked" (optional),
        "priority": "low|medium|high|critical" (optional)
    }
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/tasks/{task_id}/"
    response = forward_appointment_request(request, 'PATCH', url, data=request.data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(response.json(), status=response.status_code)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_appointment_task(request, task_id):
    """
    Admin: Delete an appointment task
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/tasks/{task_id}/"
    response = forward_appointment_request(request, 'DELETE', url)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {'message': 'Task deleted successfully'},
        status=status.HTTP_204_NO_CONTENT if response.status_code == 204 else response.status_code
    )


# ==================== APPOINTMENT STATISTICS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_appointment_statistics(request):
    """
    Admin: Get appointment statistics
    Returns:
        - Total appointments
        - Pending appointments
        - Approved appointments
        - Completed appointments
        - Cancelled appointments
        - Appointments by category
    """
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/stats/"
    response = forward_appointment_request(request, 'GET', url)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    # Check if response has content before trying to parse JSON
    if response.status_code == 200:
        try:
            return Response(response.json(), status=response.status_code)
        except:
            # If stats endpoint doesn't exist, return default stats
            return Response({
                'total_appointments': 0,
                'pending_appointments': 0,
                'confirmed_appointments': 0,
                'completed_appointments': 0,
                'cancelled_appointments': 0,
                'message': 'Statistics endpoint not available in appointment service'
            }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Failed to get statistics from appointment service'},
            status=response.status_code
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def reschedule_appointment(request, appointment_id):
    """
    Admin: Reschedule an appointment
    Body: {
        "scheduled_date": "YYYY-MM-DD",
        "scheduled_time": "HH:MM:SS",
        "reason": "string" (optional)
    }
    """
    required_fields = ['scheduled_date', 'scheduled_time']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/{appointment_id}/reschedule/"
    response = forward_appointment_request(request, 'POST', url, data=request.data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response(
        {
            'message': 'Appointment rescheduled successfully',
            'data': response.json() if response.status_code == 200 else None
        },
        status=response.status_code
    )
