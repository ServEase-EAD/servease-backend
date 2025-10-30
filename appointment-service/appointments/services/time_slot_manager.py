"""
Time slot management functions
"""
from datetime import datetime, time, timedelta
from django.conf import settings
from ..models import TimeSlot, Appointment


def is_time_slot_available(date, time_obj, duration_minutes=60):
    """
    Checks if a time slot has capacity for new appointment
    """
    # First, check if there's a defined time slot
    slot = TimeSlot.objects.filter(
        date=date,
        start_time__lte=time_obj,
        end_time__gte=time_obj
    ).first()
    
    if slot:
        # Use configured max concurrent appointments
        if not slot.is_available:
            return False
        max_concurrent = slot.max_concurrent_appointments
    else:
        # If no specific slot defined, use default from settings
        max_concurrent = getattr(settings, 'MAX_CONCURRENT_APPOINTMENTS', 3)
    
    # Count current appointments in this slot
    current_count = Appointment.objects.filter(
        scheduled_date=date,
        scheduled_time=time_obj,
        status__in=['pending', 'confirmed', 'in_progress']
    ).count()
    
    return current_count < max_concurrent


def get_available_slots(start_date, end_date, duration_minutes=60):
    """
    Returns list of available time slots in date range
    """
    available_slots = []
    
    # Get all time slots in the date range
    slots = TimeSlot.objects.filter(
        date__range=[start_date, end_date],
        is_available=True
    )
    
    if slots.exists():
        # Use defined time slots
        for slot in slots:
            current_bookings = Appointment.objects.filter(
                scheduled_date=slot.date,
                scheduled_time=slot.start_time,
                status__in=['pending', 'confirmed', 'in_progress']
            ).count()
            
            if current_bookings < slot.max_concurrent_appointments:
                available_slots.append({
                    'date': slot.date,
                    'start_time': slot.start_time,
                    'end_time': slot.end_time,
                    'available_capacity': slot.max_concurrent_appointments - current_bookings
                })
    else:
        # Generate default time slots if none defined
        available_slots = generate_default_slots(start_date, end_date, duration_minutes)
    
    return available_slots


def generate_default_slots(start_date, end_date, duration_minutes=60):
    """
    Generate default time slots for dates without specific slots
    Default: 9 AM to 5 PM, hourly slots
    """
    available_slots = []
    current_date = start_date
    
    # Business hours: 9 AM to 5 PM
    start_hour = 9
    end_hour = 17
    
    max_concurrent = getattr(settings, 'MAX_CONCURRENT_APPOINTMENTS', 3)
    
    while current_date <= end_date:
        # Skip weekends (optional - can be configured)
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            for hour in range(start_hour, end_hour):
                slot_time = time(hour, 0)
                end_time = time(hour + 1, 0) if hour < 23 else time(23, 59)
                
                # Check current bookings
                current_bookings = Appointment.objects.filter(
                    scheduled_date=current_date,
                    scheduled_time=slot_time,
                    status__in=['pending', 'confirmed', 'in_progress']
                ).count()
                
                if current_bookings < max_concurrent:
                    available_slots.append({
                        'date': current_date,
                        'start_time': slot_time,
                        'end_time': end_time,
                        'available_capacity': max_concurrent - current_bookings
                    })
        
        current_date += timedelta(days=1)
    
    return available_slots


def check_employee_availability(employee_id, date, time_obj, duration_minutes, exclude_appointment_id=None):
    """
    Check if employee has conflicting appointments
    Returns: Boolean
    """
    # Query appointments for this employee on that date
    conflicting_appointments = Appointment.objects.filter(
        assigned_employee_id=employee_id,
        scheduled_date=date,
        status__in=['confirmed', 'in_progress']
    )
    
    # Exclude specific appointment if provided (for rescheduling)
    if exclude_appointment_id:
        conflicting_appointments = conflicting_appointments.exclude(id=exclude_appointment_id)
    
    # Check for time overlaps
    for appt in conflicting_appointments:
        if times_overlap(
            appt.scheduled_time, 
            appt.duration_minutes, 
            time_obj, 
            duration_minutes
        ):
            return False
    
    return True


def times_overlap(time1, duration1, time2, duration2):
    """
    Check if two time periods overlap
    """
    # Convert time to datetime for easier calculation
    date_base = datetime(2000, 1, 1)
    
    start1 = datetime.combine(date_base, time1)
    end1 = start1 + timedelta(minutes=duration1)
    
    start2 = datetime.combine(date_base, time2)
    end2 = start2 + timedelta(minutes=duration2)
    
    # Check overlap
    return (start1 < end2) and (end1 > start2)


def create_time_slots_for_date(date, business_hours_start=9, business_hours_end=17):
    """
    Create time slots for a specific date
    Useful for admin/setup purposes
    """
    created_slots = []
    
    for hour in range(business_hours_start, business_hours_end):
        start_time = time(hour, 0)
        end_time = time(hour + 1, 0) if hour < 23 else time(23, 59)
        
        slot, created = TimeSlot.objects.get_or_create(
            date=date,
            start_time=start_time,
            defaults={
                'end_time': end_time,
                'is_available': True,
                'max_concurrent_appointments': getattr(settings, 'MAX_CONCURRENT_APPOINTMENTS', 3)
            }
        )
        
        if created:
            created_slots.append(slot)
    
    return created_slots

