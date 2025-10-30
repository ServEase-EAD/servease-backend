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

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
