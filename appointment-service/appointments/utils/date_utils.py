"""
Date and time utility functions
"""
from datetime import datetime, time, timedelta
from django.utils import timezone


def is_business_hours(time_obj):
    """
    Check if time is within business hours (9 AM - 5 PM)
    """
    business_start = time(9, 0)
    business_end = time(17, 0)
    return business_start <= time_obj <= business_end


def is_weekend(date_obj):
    """
    Check if date is a weekend (Saturday or Sunday)
    """
    return date_obj.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def get_next_business_day(date_obj):
    """
    Get the next business day (skip weekends)
    """
    next_day = date_obj + timedelta(days=1)
    while is_weekend(next_day):
        next_day += timedelta(days=1)
    return next_day


def get_business_days_between(start_date, end_date):
    """
    Get list of business days between two dates
    """
    business_days = []
    current_date = start_date
    
    while current_date <= end_date:
        if not is_weekend(current_date):
            business_days.append(current_date)
        current_date += timedelta(days=1)
    
    return business_days


def format_appointment_datetime(date_obj, time_obj):
    """
    Format appointment date and time for display
    """
    datetime_obj = datetime.combine(date_obj, time_obj)
    return datetime_obj.strftime("%B %d, %Y at %I:%M %p")


def get_time_until_appointment(appointment_date, appointment_time):
    """
    Get time remaining until appointment
    """
    appointment_datetime = datetime.combine(appointment_date, appointment_time)
    if timezone.is_naive(appointment_datetime):
        appointment_datetime = timezone.make_aware(appointment_datetime)
    
    now = timezone.now()
    delta = appointment_datetime - now
    
    if delta.total_seconds() < 0:
        return "Past due"
    
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    if days > 0:
        return f"{days} day{'s' if days > 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"


def is_same_day(datetime1, datetime2):
    """
    Check if two datetimes are on the same day
    """
    return datetime1.date() == datetime2.date()


def get_week_start_end(date_obj):
    """
    Get the start (Monday) and end (Sunday) of the week for a given date
    """
    # Get Monday of the week
    start = date_obj - timedelta(days=date_obj.weekday())
    # Get Sunday of the week
    end = start + timedelta(days=6)
    return start, end

