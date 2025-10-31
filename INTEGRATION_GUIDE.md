# RabbitMQ Notification Integration Guide

## Overview

This guide explains how to send notifications from any microservice to the notification service using RabbitMQ.

---

## Architecture

```
┌─────────────────┐
│ Your Service    │
│ (Appointment,   │
│  Vehicle, etc.) │
└────────┬────────┘
         │
         │ 1. Publish to RabbitMQ
         ▼
┌─────────────────┐
│   RabbitMQ      │
│ Message Queue   │
└────────┬────────┘
         │
         │ 2. Consumer reads
         ▼
┌─────────────────┐
│  Notification   │
│    Service      │
│  - Saves to DB  │
│  - Push WebSocket│
└─────────────────┘
         │
         │ 3. Real-time
         ▼
┌─────────────────┐
│   Frontend      │
└─────────────────┘
```

---

## Step 1: Copy the Publisher File

Copy `notification_publisher.py` to your microservice:

```bash
# From notification-service directory
cp notification-service/notification_publisher.py your-service/notification_publisher.py
```

**File Location:**

```
your-service/
├── manage.py
├── requirements.txt
├── notification_publisher.py  ← Add this file
└── your_app/
    ├── views.py
    └── models.py
```

---

## Step 2: Install Dependencies

Add to your service's `requirements.txt`:

```txt
pika==1.3.2
```

Then install:

```bash
pip install -r requirements.txt
```

---

## Step 3: Configure Environment Variables

Add to your service's `docker-compose.yml`:

```yaml
your-service:
  build: ./your-service
  environment:
    - RABBITMQ_HOST=rabbitmq
    - RABBITMQ_USER=admin
    - RABBITMQ_PASSWORD=admin123
  depends_on:
    - rabbitmq
```

**Or** in your `.env` file:

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin123
```

---

## Step 4: Use in Your Code

### Basic Usage

```python
from notification_publisher import publish_notification

# In your view or business logic
def create_appointment(request):
    # Your business logic here
    appointment = Appointment.objects.create(...)

    # Send notification
    publish_notification(
        recipient_user_id=appointment.customer_id,
        message=f"Your appointment is scheduled for {appointment.date}",
        title="Appointment Confirmed",
        priority="high",
        notification_type="APPOINTMENT"
    )

    return Response({'status': 'created'})
```

### Advanced Usage with Error Handling

```python
from notification_publisher import publish_notification
import logging

logger = logging.getLogger(__name__)

def update_vehicle_status(vehicle_id, new_status):
    # Update vehicle
    vehicle = Vehicle.objects.get(id=vehicle_id)
    old_status = vehicle.status
    vehicle.status = new_status
    vehicle.save()

    # Send notification (non-blocking)
    try:
        success = publish_notification(
            recipient_user_id=vehicle.owner_id,
            message=f"Vehicle {vehicle.plate_number} status: {old_status} → {new_status}",
            title="Vehicle Update",
            priority="medium",
            notification_type="VEHICLE",
            metadata={
                'vehicle_id': str(vehicle_id),
                'old_status': old_status,
                'new_status': new_status
            }
        )

        if not success:
            logger.warning(f"Failed to send notification for vehicle {vehicle_id}")
            # Don't fail the main operation if notification fails

    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        # Continue - notification is not critical

    return vehicle
```

### Bulk Notifications

```python
from notification_publisher import publish_bulk_notifications

def notify_all_customers(message):
    # Get all customer IDs
    customer_ids = Customer.objects.values_list('id', flat=True)

    # Prepare notifications
    notifications = [
        {
            'recipient_user_id': customer_id,
            'message': message,
            'title': 'System Announcement',
            'priority': 'medium',
            'notification_type': 'SYSTEM'
        }
        for customer_id in customer_ids
    ]

    # Send in batch
    count = publish_bulk_notifications(notifications)
    print(f"Sent {count}/{len(notifications)} notifications")
```

### Convenience Functions

```python
from notification_publisher import (
    notify_appointment_created,
    notify_vehicle_status_changed,
    notify_system_alert
)

# Appointment notification
notify_appointment_created(
    user_id=123,
    appointment_details={
        'date': '2025-11-05',
        'time': '10:00 AM',
        'service': 'Oil Change'
    }
)

# Vehicle status notification
notify_vehicle_status_changed(
    user_id=123,
    vehicle_id='V-456',
    new_status='Completed'
)

# System alert to multiple users
notify_system_alert(
    user_ids=[1, 2, 3, 4, 5],
    message='System maintenance tonight at 11 PM'
)
```

---

## Step 5: Integration Examples

### Example 1: Appointment Service

**File: `appointment-service/appointments/views.py`**

```python
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer
from notification_publisher import publish_notification

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()

        # Send notification asynchronously via RabbitMQ
        publish_notification(
            recipient_user_id=appointment.customer_id,
            message=f"Your appointment #{appointment.id} is confirmed for {appointment.date}",
            title="Appointment Confirmed",
            priority="high",
            notification_type="APPOINTMENT"
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        appointment = self.get_object()
        serializer = self.get_serializer(appointment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Notify about update
        publish_notification(
            recipient_user_id=appointment.customer_id,
            message="Your appointment has been updated",
            title="Appointment Updated",
            priority="medium",
            notification_type="APPOINTMENT"
        )

        return Response(serializer.data)
```

### Example 2: Vehicle Service

**File: `vehicle-service/vehicles/signals.py`**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vehicle
from notification_publisher import publish_notification

@receiver(post_save, sender=Vehicle)
def vehicle_status_changed(sender, instance, created, **kwargs):
    """Send notification when vehicle status changes"""
    if not created and instance.tracker.has_changed('status'):
        old_status = instance.tracker.previous('status')
        new_status = instance.status

        publish_notification(
            recipient_user_id=instance.owner_id,
            message=f"Vehicle {instance.plate_number} status: {old_status} → {new_status}",
            title="Vehicle Status Update",
            priority="medium",
            notification_type="VEHICLE",
            metadata={
                'vehicle_id': str(instance.id),
                'plate_number': instance.plate_number,
                'old_status': old_status,
                'new_status': new_status
            }
        )
```

### Example 3: Employee Service (Celery Task)

**File: `employee-service/tasks.py`**

```python
from celery import shared_task
from notification_publisher import publish_bulk_notifications

@shared_task
def send_shift_reminders():
    """Send shift reminders to all employees working tomorrow"""
    from .models import Employee, Shift
    from datetime import date, timedelta

    tomorrow = date.today() + timedelta(days=1)
    shifts = Shift.objects.filter(date=tomorrow)

    notifications = [
        {
            'recipient_user_id': shift.employee.user_id,
            'message': f"Reminder: Your shift starts tomorrow at {shift.start_time}",
            'title': "Shift Reminder",
            'priority': 'medium',
            'notification_type': 'SYSTEM'
        }
        for shift in shifts
    ]

    count = publish_bulk_notifications(notifications)
    return f"Sent {count} shift reminders"
```

---

## Best Practices

### 1. **Non-Blocking Operations**

Always treat notifications as non-critical:

```python
def create_order(order_data):
    # Critical: Save order
    order = Order.objects.create(**order_data)

    # Non-critical: Send notification (don't fail if this fails)
    try:
        publish_notification(...)
    except Exception as e:
        logger.error(f"Notification failed: {e}")
        # Continue - order was created successfully

    return order
```

### 2. **Error Handling**

```python
from notification_publisher import publish_notification
import logging

logger = logging.getLogger(__name__)

def safe_notify(user_id, message, **kwargs):
    """Wrapper with error handling"""
    try:
        return publish_notification(
            recipient_user_id=user_id,
            message=message,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Failed to send notification: {e}", exc_info=True)
        return False
```

### 3. **Use Meaningful Titles and Messages**

```python
# ❌ Bad
publish_notification(user_id=1, message="Update")

# ✅ Good
publish_notification(
    recipient_user_id=1,
    message="Your vehicle service is complete and ready for pickup",
    title="Vehicle Ready",
    priority="high"
)
```

### 4. **Include Metadata for Context**

```python
publish_notification(
    recipient_user_id=user_id,
    message="Your appointment is confirmed",
    title="Appointment Confirmed",
    metadata={
        'appointment_id': str(appointment.id),
        'date': appointment.date.isoformat(),
        'time': appointment.time.strftime('%H:%M'),
        'service_type': appointment.service_type
    }
)
```

### 5. **Priority Levels**

Use appropriate priority levels:

- **high**: Urgent actions (payment due, appointment cancelled)
- **medium**: Important updates (status changes, confirmations)
- **low**: Informational (tips, reminders)

---

## Testing

### Test Notification Manually

```python
# In Django shell or management command
from notification_publisher import publish_notification

publish_notification(
    recipient_user_id=1,
    message="Test notification",
    title="Test",
    priority="medium"
)
```

### Test Script

**File: `test_notifications.py`**

```python
from notification_publisher import publish_notification, publish_bulk_notifications

# Test single notification
print("Testing single notification...")
success = publish_notification(
    recipient_user_id=1,
    message="This is a test notification",
    title="Test",
    priority="high"
)
print(f"Result: {'✓ Success' if success else '✗ Failed'}")

# Test bulk notifications
print("\nTesting bulk notifications...")
notifications = [
    {'recipient_user_id': 1, 'message': 'Test 1', 'title': 'Bulk Test 1'},
    {'recipient_user_id': 2, 'message': 'Test 2', 'title': 'Bulk Test 2'},
]
count = publish_bulk_notifications(notifications)
print(f"Sent {count}/{len(notifications)} notifications")
```

Run it:

```bash
python test_notifications.py
```

---

## Troubleshooting

### Issue: "Connection refused"

**Cause:** RabbitMQ is not running or wrong host

**Fix:**

```bash
# Check RabbitMQ is running
docker ps | grep rabbitmq

# Check environment variables
echo $RABBITMQ_HOST

# Ensure service depends on RabbitMQ in docker-compose.yml
```

### Issue: "Authentication failed"

**Cause:** Wrong credentials

**Fix:** Check environment variables match RabbitMQ config

```bash
# Default credentials
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin123
```

### Issue: Notifications not appearing in frontend

**Cause:** Consumer not running or WebSocket disconnected

**Fix:**

```bash
# Check notification service logs
docker logs backend-notification-service-1 | grep "Received notification"

# Should see: "📬 Received notification event"
```

### Issue: "ModuleNotFoundError: No module named 'pika'"

**Cause:** Pika not installed

**Fix:**

```bash
pip install pika==1.3.2
```

---

## Monitoring

### Check RabbitMQ Queue

```bash
# Via Management UI
open http://localhost:15672
# Login: admin / admin123

# Via CLI
docker exec backend-rabbitmq-1 rabbitmqctl list_queues
```

### Check Message Flow

```bash
# Watch consumer logs
docker logs -f backend-notification-service-1 | grep notification
```

---

## Quick Reference

### Import and Send

```python
from notification_publisher import publish_notification

publish_notification(
    recipient_user_id=123,
    message="Your message here",
    title="Title",
    priority="high"  # low, medium, high
)
```

### All Parameters

```python
publish_notification(
    recipient_user_id: int,           # Required
    message: str,                      # Required
    title: Optional[str] = None,
    priority: str = 'medium',          # low, medium, high
    notification_type: str = 'OTHER',  # SYSTEM, APPOINTMENT, VEHICLE, OTHER
    metadata: Optional[Dict] = None
)
```

---

## Summary

1. ✅ Copy `notification_publisher.py` to your service
2. ✅ Add `pika==1.3.2` to `requirements.txt`
3. ✅ Configure RabbitMQ environment variables
4. ✅ Import and use `publish_notification()`
5. ✅ Handle errors gracefully (non-blocking)
6. ✅ Test thoroughly

**That's it!** Your service can now send real-time notifications! 🎉

---

## Need Help?

- **RabbitMQ Docs**: https://www.rabbitmq.com/documentation.html
- **Pika Docs**: https://pika.readthedocs.io/
- **Check Consumer Logs**: `docker logs backend-notification-service-1`
