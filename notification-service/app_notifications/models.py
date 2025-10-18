from django.db import models
from django.db import models
import uuid

class Notification(models.Model):
    """Stores persistent API notifications"""
    NOTIFICATION_TYPE_CHOICES = [
        ('SYSTEM', 'System Alert'),
        ('APPOINTMENT', 'Appointment Update'),
        ('VEHICLE', 'Vehicle Update'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The user_id of the recipient (links to Auth service)
    recipient_user_id = models.IntegerField(db_index=True)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='OTHER')
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"User {self.recipient_user_id}: {self.message[:50]}..."
# Create your models here.
