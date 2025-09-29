"""
Customer Service Models
Handles customer profiles and related data for the ServEase platform
"""

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Customer(models.Model):
    """
    Customer profile model with personal information
    and relationship to authentication service
    """

    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.IntegerField(
        unique=True, help_text="Links to authentication service user ID")

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)

    # Address Information
    address = models.TextField(
        default='', help_text="Complete address of the customer")

    # Customer Status
    is_verified = models.BooleanField(default=False)
    customer_since = models.DateTimeField(default=timezone.now)

    # Business Information (optional for business customers)
    company_name = models.CharField(max_length=200, blank=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(
        max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_service_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['last_name', 'first_name']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
