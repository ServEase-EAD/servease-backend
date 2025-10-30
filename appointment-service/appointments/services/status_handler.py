"""
Status transition and update handlers
"""
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from ..models import Appointment, AppointmentHistory
from .validators import can_transition_status
from .service_clients import NotificationServiceClient


def update_appointment_status(appointment_id, new_status, user, reason="", auth_token=None):
    """
    Updates appointment status and creates history record
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        raise ValidationError("Appointment not found")
    
    # Validate transition
    can_transition, message = can_transition_status(
        appointment, 
        appointment.status, 
        new_status, 
        user
    )
    
    if not can_transition:
        raise ValidationError(message)
    
    old_status = appointment.status
    appointment.status = new_status
    
    # Update timestamp fields based on new status
    if new_status == 'completed' and not appointment.completed_at:
        appointment.completed_at = timezone.now()
    elif new_status == 'cancelled' and not appointment.cancelled_at:
        appointment.cancelled_at = timezone.now()
    
    appointment.save()
    
    # Create history record
    create_history_record(
        appointment_id=appointment_id,
        changed_by_user_id=getattr(user, 'id', 0),
        previous_status=old_status,
        new_status=new_status,
        change_reason=reason
    )
    
    # Send notification
    try:
        NotificationServiceClient.send_appointment_notification(
            appointment, 
            new_status, 
            auth_token
        )
    except Exception as e:
        # Log but don't fail
        print(f"Notification sending failed: {e}")
    
    return appointment


def create_history_record(appointment_id, changed_by_user_id, previous_status, new_status, change_reason=""):
    """
    Creates an appointment history record
    """
    history = AppointmentHistory.objects.create(
        appointment_id=appointment_id,
        changed_by_user_id=changed_by_user_id,
        previous_status=previous_status,
        new_status=new_status,
        change_reason=change_reason
    )
    return history


def reschedule_appointment(appointment_id, new_date, new_time, user, auth_token=None):
    """
    Reschedules an existing appointment with validation
    """
    from .validators import can_reschedule_appointment, validate_reschedule
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        raise ValidationError("Appointment not found")
    
    # Check if can reschedule
    can_reschedule_appointment(appointment, user)
    
    # Validate new time
    validate_reschedule(appointment, new_date, new_time, auth_token)
    
    # Store old values for history
    old_date = appointment.scheduled_date
    old_time = appointment.scheduled_time
    
    # Update appointment
    appointment.scheduled_date = new_date
    appointment.scheduled_time = new_time
    appointment.save()
    
    # Create history record
    create_history_record(
        appointment_id=appointment_id,
        changed_by_user_id=getattr(user, 'id', 0),
        previous_status=appointment.status,
        new_status=appointment.status,
        change_reason=f"Rescheduled from {old_date} {old_time} to {new_date} {new_time}"
    )
    
    # Send notification
    try:
        NotificationServiceClient.send_appointment_notification(
            appointment, 
            'rescheduled', 
            auth_token
        )
    except Exception as e:
        print(f"Notification sending failed: {e}")
    
    return appointment


def assign_employee(appointment_id, employee_id, user, auth_token=None):
    """
    Assigns an employee to an appointment
    """
    from .service_clients import EmployeeServiceClient
    from .time_slot_manager import check_employee_availability
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        raise ValidationError("Appointment not found")
    
    # Validate employee exists
    try:
        EmployeeServiceClient.validate_employee(employee_id, auth_token)
    except Exception as e:
        print(f"Employee validation skipped: {e}")
    
    # Check employee availability
    if not check_employee_availability(
        employee_id,
        appointment.scheduled_date,
        appointment.scheduled_time,
        appointment.duration_minutes
    ):
        raise ValidationError("Employee not available at this time")
    
    old_employee = appointment.assigned_employee_id
    appointment.assigned_employee_id = employee_id
    appointment.save()
    
    # Create history record
    create_history_record(
        appointment_id=appointment_id,
        changed_by_user_id=getattr(user, 'id', 0),
        previous_status=appointment.status,
        new_status=appointment.status,
        change_reason=f"Employee assigned: {old_employee} -> {employee_id}"
    )
    
    return appointment

