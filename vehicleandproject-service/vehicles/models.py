from django.db import models
from django.core.validators import RegexValidator
import uuid
from datetime import datetime


class Vehicle(models.Model):
    # Primary key - using UUID for better security
    vehicle_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the vehicle"
    )
    
    # Vehicle Information
    make = models.CharField(
        max_length=50,
        help_text="Vehicle manufacturer (e.g., Toyota, BMW)"
    )
    
    model = models.CharField(
        max_length=50,
        help_text="Vehicle model (e.g., Camry, X5)"
    )
    
    year = models.IntegerField(
        help_text="Manufacturing year"
    )
    
    color = models.CharField(
        max_length=30,
        help_text="Vehicle color"
    )
    
    # VIN validation (17 characters, alphanumeric)
    vin_validator = RegexValidator(
        regex=r'^[A-HJ-NPR-Z0-9]{17}$',
        message='VIN must be exactly 17 characters and contain only valid characters'
    )
    
    vin = models.CharField(
        blank=False,
        max_length=17,
        unique=True,
        validators=[vin_validator],
        help_text="Vehicle Identification Number (17 characters)"
    )
    
    # Plate number validation (flexible format)
    plate_validator = RegexValidator(
        regex=r'^[A-Z0-9\-\s]{2,10}$',
        message='Plate number must be 2-10 characters with letters, numbers, hyphens, or spaces'
    )
    
    plate_number = models.CharField(
        blank=False,
        max_length=10,
        unique=True,
        validators=[plate_validator],
        help_text="Vehicle license plate number"
    )
    
    # Ownership tracking (link to customer service)
    customer_id = models.IntegerField(
        help_text="Reference to customer who owns this vehicle",
        db_index=True  # Index for faster queries
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Is vehicle still in service")
    
    class Meta:
        db_table = 'vehicles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['make', 'model']),
            models.Index(fields=['year']),
        ]
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.plate_number})"
    
    def get_display_name(self):
        """User-friendly display name"""
        return f"{self.year} {self.make} {self.model}"
    
    @property
    def age(self):
        """Calculate vehicle age"""
        return datetime.now().year - self.year