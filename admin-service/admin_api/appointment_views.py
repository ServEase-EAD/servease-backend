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
import sys
import os

# Add parent directory to path to import notification_publisher
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from notification_publisher import publish_notification

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
    # Extract assigned_employees from request data
    assigned_employees = request.data.get('assigned_employees', [])
    logger.info(f"Approving appointment {appointment_id} with assigned_employees: {assigned_employees}")
    
    # Prepare data for confirm endpoint (without assigned_employees)
    confirm_data = {
        'scheduled_date': request.data.get('scheduled_date'),
        'scheduled_time': request.data.get('scheduled_time'),
    }
    
    # Use the confirm endpoint to approve
    url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/{appointment_id}/confirm/"
    response = forward_appointment_request(request, 'POST', url, data=confirm_data)
    
    if response is None:
        return Response(
            {'error': 'Failed to connect to appointment service'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    # If approval failed, return the error
    if response.status_code not in [200, 201]:
        logger.error(f"Appointment confirmation failed with status {response.status_code}")
        return Response(
            {
                'message': 'Appointment approval failed',
                'data': response.json() if response.content else None
            },
            status=response.status_code
        )
    
    # If assigned_employees provided, assign the first employee
    # (Note: The appointment service only supports single employee assignment)
    if assigned_employees and len(assigned_employees) > 0:
        employee_id = assigned_employees[0]
        logger.info(f"Assigning employee {employee_id} to appointment {appointment_id}")
        assign_url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/{appointment_id}/assign/"
        assign_data = {'employee_id': employee_id}
        
        assign_response = forward_appointment_request(request, 'POST', assign_url, data=assign_data)
        
        if assign_response and assign_response.status_code == 200:
            logger.info(f"Employee {employee_id} assigned successfully to appointment {appointment_id}")
            # Send notification to assigned employee
            try:
                appointment_date = request.data.get('scheduled_date', 'upcoming')
                appointment_time = request.data.get('scheduled_time', '')
                
                publish_notification(
                    recipient_user_id=employee_id,
                    message=f'You have been assigned to an appointment scheduled for {appointment_date} {appointment_time}',
                    title='New Appointment Assignment',
                    notification_type='APPOINTMENT',
                    priority='high',
                    metadata={
                        'appointment_id': appointment_id,
                        'scheduled_date': appointment_date,
                        'scheduled_time': appointment_time
                    }
                )
                logger.info(f"Notification sent to employee {employee_id} for appointment assignment")
            except Exception as notif_error:
                logger.error(f"Failed to send notification to employee {employee_id}: {str(notif_error)}")
            
            # Return the updated appointment data from assign response
            try:
                assign_data_response = assign_response.json()
                logger.info(f"Assign response data: {assign_data_response}")
                if 'appointment' in assign_data_response:
                    return Response(
                        {
                            'message': 'Appointment approved and employee assigned successfully',
                            'data': assign_data_response['appointment']
                        },
                        status=status.HTTP_200_OK
                    )
            except Exception as e:
                logger.error(f"Error parsing assign response: {str(e)}")
        else:
            logger.warning(f"Failed to assign employee to appointment {appointment_id}. Status: {assign_response.status_code if assign_response else 'None'}")
    else:
        logger.info(f"No employees to assign for appointment {appointment_id}")
    
    # Return the appointment data from confirm response
    try:
        response_data = response.json()
        appointment_data = response_data.get('appointment', response_data.get('data', None))
        return Response(
            {
                'message': 'Appointment approved successfully',
                'data': appointment_data
            },
            status=response.status_code
        )
    except Exception as e:
        logger.error(f"Error parsing confirm response: {str(e)}")
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
    
    # Send notification to each assigned employee
    if response.status_code == 200:
        try:
            employee_ids = request.data.get('employee_ids', [])
            appointment_date = request.data.get('scheduled_date', 'upcoming')
            appointment_time = request.data.get('scheduled_time', '')
            
            for employee_id in employee_ids:
                try:
                    publish_notification(
                        recipient_user_id=employee_id,
                        message=f'You have been assigned to an appointment scheduled for {appointment_date} {appointment_time}',
                        title='New Appointment Assignment',
                        notification_type='APPOINTMENT',
                        priority='high',
                        metadata={
                            'appointment_id': appointment_id,
                            'scheduled_date': appointment_date,
                            'scheduled_time': appointment_time
                        }
                    )
                    logger.info(f"Notification sent to employee {employee_id} for appointment assignment")
                except Exception as notif_error:
                    logger.error(f"Failed to send notification to employee {employee_id}: {str(notif_error)}")
                    # Don't fail the assignment if notification fails
        except Exception as e:
            logger.error(f"Error sending appointment assignment notifications: {str(e)}")
    
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
    
    # Send notification to assigned employee if specified
    if response.status_code == 201 and 'assigned_employee_id' in request.data:
        try:
            employee_id = request.data['assigned_employee_id']
            task_title = request.data['title']
            
            publish_notification(
                recipient_user_id=employee_id,
                message=f'You have been assigned to a new appointment task: {task_title}',
                title='New Appointment Task Assignment',
                notification_type='APPOINTMENT',
                priority='high',
                metadata={
                    'appointment_id': appointment_id,
                    'task_title': task_title,
                    'task_description': request.data.get('description', '')
                }
            )
            logger.info(f"Notification sent to employee {employee_id} for appointment task assignment")
        except Exception as notif_error:
            logger.error(f"Failed to send notification to employee: {str(notif_error)}")
            # Don't fail the task creation if notification fails
    
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
