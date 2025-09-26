"""
Customer Service Models
Handles customer profiles, vehicles, preferences, and related data
"""

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Customer(models.Model):
    """
    Comprehensive customer profile model with personal information
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
    secondary_phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)

    # Address Information
    street_address = models.TextField()
    apartment_unit = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='United States')

    # Customer Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    customer_since = models.DateTimeField(default=timezone.now)

    # Business Information (optional for business customers)
    company_name = models.CharField(max_length=200, blank=True)
    business_tax_id = models.CharField(max_length=50, blank=True)
    is_business_customer = models.BooleanField(default=False)

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

    @property
    def full_address(self):
        address_parts = [self.street_address]
        if self.apartment_unit:
            address_parts[0] += f", {self.apartment_unit}"
        address_parts.extend([self.city, self.state, self.zip_code])
        return ", ".join(address_parts)

    def get_active_vehicles_count(self):
        return self.vehicles.filter(is_active=True).count()


class Vehicle(models.Model):
    """
    Customer vehicle information and ownership details
    """

    FUEL_TYPE_CHOICES = [
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
        ('plug_in_hybrid', 'Plug-in Hybrid'),
        ('natural_gas', 'Natural Gas'),
        ('other', 'Other'),
    ]

    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('cvt', 'CVT'),
        ('semi_automatic', 'Semi-Automatic'),
    ]

    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='vehicles')

    # Vehicle Basic Information
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=30)

    # Vehicle Identification
    vin = models.CharField(max_length=17, unique=True,
                           help_text="Vehicle Identification Number")
    license_plate = models.CharField(max_length=15)
    state_registered = models.CharField(max_length=50, default='')

    # Vehicle Specifications
    engine_size = models.CharField(max_length=20, blank=True)
    fuel_type = models.CharField(
        max_length=20, choices=FUEL_TYPE_CHOICES, default='gasoline')
    transmission = models.CharField(
        max_length=20, choices=TRANSMISSION_CHOICES, default='automatic')

    # Mileage and Condition
    current_mileage = models.IntegerField(default=0)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_mileage = models.IntegerField(null=True, blank=True)

    # Insurance Information
    insurance_company = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    insurance_expiry_date = models.DateField(null=True, blank=True)

    # Registration Information
    registration_expiry_date = models.DateField(null=True, blank=True)

    # Vehicle Status
    is_active = models.BooleanField(default=True)
    is_under_warranty = models.BooleanField(default=False)
    warranty_expiry_date = models.DateField(null=True, blank=True)

    # Service Information
    last_service_date = models.DateTimeField(null=True, blank=True)
    last_service_mileage = models.IntegerField(null=True, blank=True)
    next_service_due_date = models.DateField(null=True, blank=True)
    next_service_due_mileage = models.IntegerField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_vehicles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['vin']),
            models.Index(fields=['license_plate']),
            models.Index(fields=['make', 'model', 'year']),
        ]

    def __str__(self):
        return f"{self.year} {self.make} {self.model} - {self.license_plate}"

    @property
    def vehicle_age(self):
        current_year = timezone.now().year
        return current_year - self.year

    def is_service_due(self):
        """Check if vehicle is due for service based on date or mileage"""
        if self.next_service_due_date and self.next_service_due_date <= timezone.now().date():
            return True
        if self.next_service_due_mileage and self.current_mileage >= self.next_service_due_mileage:
            return True
        return False


class CustomerPreferences(models.Model):
    """
    Customer communication preferences and settings
    """

    CONTACT_METHOD_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call'),
        ('app', 'Mobile App'),
        ('mail', 'Postal Mail'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
    ]

    # Primary relationship
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name='preferences')

    # Communication Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    phone_call_notifications = models.BooleanField(default=False)
    postal_mail_notifications = models.BooleanField(default=False)

    preferred_contact_method = models.CharField(
        max_length=10,
        choices=CONTACT_METHOD_CHOICES,
        default='email'
    )

    # Service Preferences
    preferred_service_time = models.TimeField(null=True, blank=True)
    preferred_service_day = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ],
        blank=True
    )

    # System Preferences
    preferred_language = models.CharField(
        max_length=5, choices=LANGUAGE_CHOICES, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=3, default='USD')

    # Marketing Preferences
    marketing_emails = models.BooleanField(default=False)
    promotional_sms = models.BooleanField(default=False)
    service_reminders = models.BooleanField(default=True)
    appointment_reminders = models.BooleanField(default=True)

    # Privacy Settings
    data_sharing_consent = models.BooleanField(default=False)
    analytics_consent = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_preferences'

    def __str__(self):
        return f"Preferences for {self.customer.full_name}"


class CustomerDocument(models.Model):
    """
    Store customer and vehicle documents
    """

    DOCUMENT_TYPE_CHOICES = [
        ('license', 'Driver\'s License'),
        ('insurance', 'Insurance Document'),
        ('registration', 'Vehicle Registration'),
        ('warranty', 'Warranty Document'),
        ('service_history', 'Service History'),
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('other', 'Other'),
    ]

    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='documents')
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)

    # Document Information
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # File Information
    file_path = models.FileField(upload_to='customer_documents/%Y/%m/')
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)

    # Document Metadata
    is_sensitive = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['document_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.customer.full_name}"

    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False


class CustomerNote(models.Model):
    """
    Internal notes about customers for service team reference
    """

    NOTE_TYPE_CHOICES = [
        ('general', 'General'),
        ('service', 'Service Related'),
        ('billing', 'Billing Related'),
        ('complaint', 'Complaint'),
        ('compliment', 'Compliment'),
        ('follow_up', 'Follow Up'),
    ]

    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='notes')

    # Note Information
    note_type = models.CharField(
        max_length=20, choices=NOTE_TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    content = models.TextField()

    # Note Metadata
    is_important = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    created_by = models.IntegerField(
        help_text="Employee ID who created the note")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['note_type']),
            models.Index(fields=['is_important']),
        ]

    def __str__(self):
        return f"{self.title} - {self.customer.full_name}"
