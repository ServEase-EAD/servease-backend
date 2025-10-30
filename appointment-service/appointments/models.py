import uuid
from django.db import models
from django.utils import timezone


# Appointment Type Choices
APPOINTMENT_TYPE_CHOICES = [
    ('maintenance', 'Regular Maintenance'),
    ('repair', 'Repair'),
    ('inspection', 'Inspection'),
    ('diagnostic', 'Diagnostic'),
    ('emergency', 'Emergency Service'),
]

# Status Choices
STATUS_CHOICES = [
    ('pending', 'Pending Confirmation'),
    ('confirmed', 'Confirmed'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('no_show', 'No Show'),
]


class Appointment(models.Model):
    """Main Appointment model for managing service appointments"""
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Foreign Keys (stored as IDs, validated via API calls)
    customer_id = models.UUIDField(db_index=True)  # References Customer Service
    vehicle_id = models.UUIDField(db_index=True)   # References Vehicle Service
    assigned_employee_id = models.UUIDField(null=True, blank=True, db_index=True)  # References Employee Service
    
    # Appointment Details
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPE_CHOICES)
    scheduled_date = models.DateField(db_index=True)
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    
    # Status Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Additional Information
    service_description = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)  # For employees only
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Metadata
    created_by_user_id = models.UUIDField()  # User who created the appointment
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-scheduled_date', '-scheduled_time']
        indexes = [
            models.Index(fields=['customer_id', 'scheduled_date']),
            models.Index(fields=['assigned_employee_id', 'scheduled_date']),
            models.Index(fields=['status', 'scheduled_date']),
        ]
    
    def __str__(self):
        return f"Appointment {self.id} - {self.appointment_type} on {self.scheduled_date}"
    
    def save(self, *args, **kwargs):
        # Auto-update timestamps based on status
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        super().save(*args, **kwargs)


class TimeSlot(models.Model):
    """Time slot model for managing available appointment times"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_concurrent_appointments = models.IntegerField(default=3)
    
    class Meta:
        db_table = 'time_slots'
        unique_together = ['date', 'start_time']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time}"


class AppointmentHistory(models.Model):
    """History tracking for appointment status changes"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_id = models.UUIDField(db_index=True)
    changed_by_user_id = models.UUIDField()
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    change_reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'appointment_history'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"History: {self.appointment_id} - {self.previous_status} → {self.new_status}"

