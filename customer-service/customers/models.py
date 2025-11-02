"""
Customer Service Models
Handles customer-specific profiles and related data for the ServEase platform

This service focuses on customer-specific information (address, company, emergency contacts)
and references the authentication service via user_id for user credentials.
"""

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Customer(models.Model):
    """
    Customer profile model for ServEase-specific data.

    This model stores customer-specific information only.
    User credentials (email, name, phone, password) are managed by the authentication service.
    Link to auth service user via user_id field (UUID).
    """

    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(
        unique=True,
        help_text="UUID linking to authentication service CustomUser.id"
    )

    # Address Information (Customer-specific)
    street_address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address (e.g., '123 Main Street, Apt 4B')"
    )
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='USA')

    # Business Information (optional for business customers)
    company_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Type of business (e.g., 'Auto Repair', 'Fleet Management')"
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Business tax ID or EIN"
    )

    # Emergency Contact (Customer-specific)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(
        max_length=50, blank=True)

    # Customer Status & Service History
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether customer has completed verification process"
    )
    customer_since = models.DateTimeField(
        default=timezone.now,
        help_text="Date when customer profile was created"
    )
    last_service_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date of most recent service appointment"
    )
    total_services = models.IntegerField(
        default=0,
        help_text="Total number of completed services"
    )

    # Preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('sms', 'SMS'),
        ],
        default='email'
    )
    notification_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Customer notification preferences (JSON)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['company_name']),
        ]
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'

    def __str__(self):
        return f"Customer Profile (user_id: {self.user_id})"

    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [
            self.street_address,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, parts))

    @property
    def is_business_customer(self):
        """Check if this is a business customer"""
        return bool(self.company_name)

    def increment_service_count(self):
        """Increment total services counter"""
        self.total_services += 1
        self.last_service_date = timezone.now()
        self.save(update_fields=['total_services',
                  'last_service_date', 'updated_at'])
