import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_role', 'admin')  # Superusers are admins
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)
    
    def create_employee(self, email, password=None, **extra_fields):
        """Create an employee user"""
        extra_fields.setdefault('user_role', 'employee')
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    user_role = models.CharField(
        max_length=10, 
        choices=USER_ROLE_CHOICES, 
        default='customer',
        help_text='The role of the user in the system'
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove username since we're using email as USERNAME_FIELD
    
    objects = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.email} ({self.get_user_role_display()})"
    
    def is_admin(self):
        """Check if user is admin"""
        return self.user_role == 'admin' or self.is_superuser
    
    def is_employee(self):
        """Check if user is employee"""
        return self.user_role == 'employee'
    
    def is_customer(self):
        """Check if user is customer"""
        return self.user_role == 'customer'
    
    class Meta:
        db_table = 'custom_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    
