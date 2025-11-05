from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

class Shift(models.Model):
    """Employee daily shift tracking"""
    shift_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.IntegerField(db_index=True, help_text="Reference to employee from auth service")
    
    shift_date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True, help_text="Is shift currently active")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shifts'
        ordering = ['-shift_date', '-start_time']
        indexes = [
            models.Index(fields=['employee_id', 'shift_date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Shift {self.shift_date} - Employee {self.employee_id}"


class TimeLog(models.Model):
    """Individual time log entries for tasks"""
    STATUS_CHOICES = [
        ('inprogress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('project', 'Project Task'),
        ('appointment', 'Service Appointment'),
    ]
    
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.UUIDField(db_index=True, help_text="Reference to employee")
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='time_logs', null=True, blank=True)
    
    # Task type and references
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='appointment', help_text="Type of task")
    project_id = models.CharField(max_length=100, null=True, blank=True, help_text="Reference to project if task_type is project")
    appointment_id = models.CharField(max_length=100, null=True, blank=True, help_text="Reference to appointment if task_type is appointment")
    
    # Task details
    description = models.TextField(help_text="Task description")
    vehicle = models.CharField(max_length=200, help_text="Vehicle being serviced", blank=True)
    service = models.CharField(max_length=200, help_text="Type of service", blank=True)
    
    # Time tracking
    log_date = models.DateField(help_text="Date of the log entry", db_index=True, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inprogress')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'time_logs'
        ordering = ['-log_date', '-start_time']
        indexes = [
            models.Index(fields=['employee_id', '-log_date']),
            models.Index(fields=['employee_id', 'log_date']),
            models.Index(fields=['status']),
            models.Index(fields=['task_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.task_type} - {self.description}"
    
    @property
    def duration_formatted(self):
        """Return duration in format like '2.5h'"""
        if self.duration_seconds > 0:
            hours = self.duration_seconds / 3600
            return f"{hours:.1f}h"
        return "0h"
    
    def save(self, *args, **kwargs):
        """Override save to automatically set log_date from start_time"""
        if self.start_time:
            self.log_date = self.start_time.date()
        super().save(*args, **kwargs)


class DailyTimeTotal(models.Model):
    """Daily time totals aggregated per employee"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.UUIDField(db_index=True, help_text="Reference to employee")
    log_date = models.DateField(help_text="Date of the time logs")
    
    # Aggregated totals
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Total hours worked on this date")
    total_seconds = models.IntegerField(default=0, help_text="Total seconds worked on this date")
    total_tasks = models.IntegerField(default=0, help_text="Total number of tasks/logs for this date")
    
    # Task type breakdown
    project_tasks_count = models.IntegerField(default=0, help_text="Number of project tasks")
    appointment_tasks_count = models.IntegerField(default=0, help_text="Number of appointment tasks")
    project_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    appointment_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_time_totals'
        ordering = ['-log_date']
        unique_together = ['employee_id', 'log_date']
        indexes = [
            models.Index(fields=['employee_id', '-log_date']),
            models.Index(fields=['log_date']),
        ]
    
    def __str__(self):
        return f"Employee {self.employee_id} - {self.log_date}: {self.total_hours}h"
    
    @property
    def total_hours_formatted(self):
        """Return total hours in formatted string"""
        return f"{self.total_hours:.2f}h"

