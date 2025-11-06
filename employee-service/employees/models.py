from django.db import models
import uuid
from django.contrib.auth.models import User


class Employee(models.Model):
    # Use UUID as primary key to match authentication service user IDs
    # This id represents the user_id from the authentication service
    id = models.UUIDField(primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")

    # Basic Information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Employment Information
    # Note: Employment details are managed through admin/HR system

    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # System Info
    # Note: System information is managed internally

    # Other Details
    specialization = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# ✅ NEW MODEL — AssignedTask
class AssignedTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    completed_at = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.employee.user.username}"
