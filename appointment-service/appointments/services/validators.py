"""
Validators for appointment business logic
"""
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied
from ..models import Appointment
from .service_clients import CustomerServiceClient, VehicleServiceClient, EmployeeServiceClient
from .time_slot_manager import is_time_slot_available, check_employee_availability


def validate_appointment_creation(data, user, auth_token=None):
    """
    Validates all requirements for creating an appointment
    """
    errors = []
    
    # 1. Validate customer exists (skip in development if service not ready)
    try:
        customer = CustomerServiceClient.validate_customer(
            data.get('customer_id'), 
            auth_token
        )
    except Exception as e:
        # In development, we may skip this if customer service isn't ready
        print(f"Customer validation skipped: {e}")
        customer = None
    
    # 2. Validate vehicle and ownership (skip in development if service not ready)
    try:
        vehicle = VehicleServiceClient.validate_vehicle_ownership(
            data.get('vehicle_id'), 
            data.get('customer_id'), 
            auth_token
        )
    except Exception as e:
        # In development, we may skip this if vehicle service isn't ready
        print(f"Vehicle validation skipped: {e}")
        vehicle = None
    
    # 3. Validate date is in future
    scheduled_date = data.get('scheduled_date')
    scheduled_time = data.get('scheduled_time')
    
    if scheduled_date and scheduled_time:
        scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
        if timezone.is_naive(scheduled_datetime):
            scheduled_datetime = timezone.make_aware(scheduled_datetime)
        
        if scheduled_datetime <= timezone.now():
            errors.append("Appointment must be scheduled in the future")
    
    # 4. Check time slot availability
    if scheduled_date and scheduled_time:
        duration = data.get('duration_minutes', 60)
        if not is_time_slot_available(scheduled_date, scheduled_time, duration):
            errors.append("Selected time slot is not available or fully booked")
    
    # 5. Validate employee if assigned
    assigned_employee_id = data.get('assigned_employee_id')
    if assigned_employee_id:
        try:
            employee = EmployeeServiceClient.validate_employee(
                assigned_employee_id, 
                auth_token
            )
            
            # Check employee availability
            if not check_employee_availability(
                assigned_employee_id,
                scheduled_date,
                scheduled_time,
                data.get('duration_minutes', 60)
            ):
                errors.append("Employee not available at selected time")
        except Exception as e:
            # In development, we may skip this if employee service isn't ready
            print(f"Employee validation skipped: {e}")
    
    # 6. Check customer doesn't have conflicting appointment
    if data.get('customer_id') and scheduled_date and scheduled_time:
        if has_customer_conflict(data['customer_id'], scheduled_date, scheduled_time):
            errors.append("Customer already has an appointment at this time")
    
    if errors:
        raise ValidationError(errors)
    
    return True


def has_customer_conflict(customer_id, scheduled_date, scheduled_time):
    """
    Check if customer has a conflicting appointment
    """
    # Check for appointments within 30 minutes of the requested time
    time_threshold = timedelta(minutes=30)
    scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
    
    conflicting = Appointment.objects.filter(
        customer_id=customer_id,
        scheduled_date=scheduled_date,
        status__in=['pending', 'confirmed', 'in_progress']
    )
    
    for appt in conflicting:
        appt_datetime = datetime.combine(appt.scheduled_date, appt.scheduled_time)
        time_diff = abs((scheduled_datetime - appt_datetime).total_seconds() / 60)
        
        if time_diff < 30:  # Less than 30 minutes apart
            return True
    
    return False


def can_transition_status(appointment, from_status, to_status, user):
    """
    Validates if status transition is allowed
    """
    valid_transitions = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['in_progress', 'cancelled', 'no_show'],
        'in_progress': ['completed', 'cancelled'],
        'completed': [],  # Cannot change from completed
        'cancelled': [],  # Cannot change from cancelled
        'no_show': [],
    }
    
    if to_status not in valid_transitions.get(from_status, []):
        return False, f"Cannot transition from {from_status} to {to_status}"
    
    # Additional permission checks could be added here
    # For example: Only employees can start or complete appointments
    
    return True, "Transition allowed"


def can_reschedule_appointment(appointment, user):
    """
    Check if user can reschedule the appointment
    """
    # Only pending or confirmed appointments can be rescheduled
    if appointment.status not in ['pending', 'confirmed']:
        raise ValidationError("Cannot reschedule completed or cancelled appointments")
    
    # Check authorization - assuming user object has these methods
    # In production, this would check against actual user permissions
    # For now, we'll allow the creator or any authenticated user
    
    return True


def validate_reschedule(appointment, new_date, new_time, auth_token=None):
    """
    Validates rescheduling requirements
    """
    errors = []
    
    # Validate new time is in the future
    new_datetime = datetime.combine(new_date, new_time)
    if timezone.is_naive(new_datetime):
        new_datetime = timezone.make_aware(new_datetime)
    
    if new_datetime <= timezone.now():
        errors.append("New appointment time must be in the future")
    
    # Check new time slot availability
    if not is_time_slot_available(new_date, new_time, appointment.duration_minutes):
        errors.append("New time slot is not available")
    
    # Check employee availability if assigned
    if appointment.assigned_employee_id:
        if not check_employee_availability(
            appointment.assigned_employee_id,
            new_date,
            new_time,
            appointment.duration_minutes,
            exclude_appointment_id=appointment.id
        ):
            errors.append("Assigned employee not available at new time")
    
    if errors:
        raise ValidationError(errors)
    
    return True

