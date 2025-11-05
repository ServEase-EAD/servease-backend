from django.db import models
from django.core.validators import RegexValidator
import uuid


class Project(models.Model):
    project_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the project"
    )

    # link to Vehicle by string reference
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.PROTECT,
        related_name='projects'
    )

    # store only customer ID from the customer service
    customer_id = models.UUIDField(
        help_text="Customer ID from customer-service",
        db_index=True,
    )

    # Project Information
    title = models.CharField(
        max_length=100,
        blank=False,
        help_text="Title of the project"
    )

    description = models.TextField(
        blank=False,
        help_text="Detailed description of the project"
    )

    expected_completion_date = models.DateField(
        help_text="Expected completion date of the project"
    )

    PROJECT_STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('cancelled', 'Cancelled'),
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    status = models.CharField(
        max_length=20,
        choices=PROJECT_STATUS_CHOICES,
        default='not_started',
        help_text="Current status of the project"
    )

    # Approval status for admin approval
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        help_text="Admin approval status for the project"
    )

    # Employee assignment - store only employee ID from employee service
    assigned_employee_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Employee ID assigned to this project from employee-service",
        db_index=True,
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    """
    Task model to break down projects into smaller tasks
    Only admins can create and manage tasks
    """
    task_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the task"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Project this task belongs to"
    )

    title = models.CharField(
        max_length=200,
        help_text="Title of the task"
    )

    description = models.TextField(
        help_text="Detailed description of the task"
    )

    TASK_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]

    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default='not_started',
        help_text="Current status of the task"
    )

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the task"
    )

    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Due date for the task"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.title} - {self.title}"
