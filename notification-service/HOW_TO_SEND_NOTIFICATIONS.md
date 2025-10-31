# How to Send Notifications from Other Services

This guide explains how any microservice in the ServEase architecture can send notifications to users through RabbitMQ.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Notification Types](#notification-types)
- [Best Practices](#best-practices)
- [Error Handling](#error-handling)

---

## 🚀 Quick Start

### 1. Copy the Publisher File

Copy `notification_publisher.py` from the notification service to your microservice:

```bash
cp notification-service/notification_publisher.py your-service/
```

### 2. Install Dependencies

Add to your `requirements.txt`:

```txt
pika==1.3.2
```

Install:

```bash
pip install pika
```

### 3. Set Environment Variables

Add to your `.env` or `docker-compose.yml`:

```env
Refer the ENV file guide for these data
```

### 4. Send a Notification

```python
from notification_publisher import publish_notification

# Send a notification to a user
publish_notification(
    recipient_user_id='bcee5755-2c9f-4c0a-8720-1592b75edf96',
    message='Your appointment has been confirmed for tomorrow at 10:00 AM',
    title='Appointment Confirmed'
)
```

**That's it!** The notification will be:

- ✅ Sent to RabbitMQ
- ✅ Processed by the notification service
- ✅ Saved to the database
- ✅ Delivered in real-time via WebSocket to the user

---

## 📦 Prerequisites

Before integrating notifications, ensure:

1. **RabbitMQ is running** in your Docker Compose setup
2. **Notification service is running** to consume messages
3. **User IDs are UUIDs** (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
4. **Environment variables are configured** for RabbitMQ connection

---

## 🔧 Installation

### Step 1: Copy the Publisher Module

The `notification_publisher.py` file is a **standalone module** with no dependencies on the notification service internals.

**Location:** `notification-service/notification_publisher.py`

**Copy to your service:**

```bash
# Example: Copy to appointment service
cp notification-service/notification_publisher.py appointment-service/
```

### Step 2: Install pika Library

Add to your `requirements.txt`:

```txt
pika==1.3.2
```

Then install:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Update your service's `.env` file:

```env
# RabbitMQ Configuration
Refer the ENV file guide for these data
```

Or add to `docker-compose.yml`:

```yaml
your-service:
  environment:
    - RABBITMQ_HOST=rabbitmq
    - RABBITMQ_PORT=5672
    - RABBITMQ_USER=admin
    - RABBITMQ_PASSWORD=admin123
    - RABBITMQ_QUEUE=notification_events
```

---

## 💡 Usage Examples

### Example 1: Simple Notification

```python
from notification_publisher import publish_notification

# Send a basic notification
publish_notification(
    recipient_user_id='bcee5755-2c9f-4c0a-8720-1592b75edf96',
    message='Your vehicle service is complete!',
    title='Service Complete'
)
```

### Example 2: Appointment Service

```python
from notification_publisher import publish_notification

def confirm_appointment(appointment):
    """Send notification when appointment is confirmed"""
    publish_notification(
        recipient_user_id=appointment.customer_id,
        message=f'Your appointment has been confirmed for {appointment.date} at {appointment.time}',
        title='Appointment Confirmed',
        notification_type='APPOINTMENT',
        priority='high',
        metadata={
            'appointment_id': str(appointment.id),
            'date': str(appointment.date),
            'time': str(appointment.time),
            'service_type': appointment.service_type
        }
    )
```

### Example 3: Vehicle Service

```python
from notification_publisher import publish_notification

def notify_maintenance_due(vehicle, customer_id):
    """Send maintenance reminder notification"""
    publish_notification(
        recipient_user_id=customer_id,
        message=f'Your {vehicle.make} {vehicle.model} is due for maintenance. Schedule your appointment today!',
        title='Maintenance Due',
        notification_type='VEHICLE',
        priority='medium',
        metadata={
            'vehicle_id': str(vehicle.id),
            'vehicle_make': vehicle.make,
            'vehicle_model': vehicle.model,
            'last_service_date': str(vehicle.last_service_date)
        }
    )
```

### Example 4: Employee Service

```python
from notification_publisher import publish_notification

def notify_new_assignment(employee_id, project_name):
    """Notify employee of new project assignment"""
    publish_notification(
        recipient_user_id=employee_id,
        message=f'You have been assigned to project: {project_name}',
        title='New Project Assignment',
        notification_type='PROJECT',
        priority='high',
        metadata={
            'project_name': project_name,
            'assignment_date': str(datetime.now())
        }
    )
```

### Example 5: Customer Service

```python
from notification_publisher import publish_notification

def welcome_new_customer(customer_id, first_name):
    """Send welcome notification to new customer"""
    publish_notification(
        recipient_user_id=customer_id,
        message=f'Welcome to ServEase, {first_name}! We\'re excited to serve you.',
        title='Welcome',
        notification_type='OTHER',
        priority='low'
    )
```

### Example 6: Bulk Notifications

```python
from notification_publisher import publish_bulk_notifications

def notify_all_customers_of_promotion(customer_ids):
    """Send promotional notification to multiple customers"""
    notifications = [
        {
            'recipient_user_id': customer_id,
            'message': '🎉 Special Offer: 20% off on all services this week!',
            'title': 'Special Promotion',
            'notification_type': 'OTHER',
            'priority': 'medium'
        }
        for customer_id in customer_ids
    ]

    publish_bulk_notifications(notifications)
```

---

## 📝 Notification Types

The notification service supports the following types:

| Type          | Use Case                          | Example                                                 |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `APPOINTMENT` | Appointment-related notifications | Confirmations, reminders, cancellations                 |
| `VEHICLE`     | Vehicle service notifications     | Maintenance due, service complete, inspection reminders |
| `PROJECT`     | Project-related notifications     | Assignments, updates, completions                       |
| `PAYMENT`     | Payment notifications             | Successful payments, failed payments, receipts          |
| `SYSTEM`      | System notifications              | Account updates, security alerts                        |
| `OTHER`       | General notifications             | Promotions, announcements, welcome messages             |

**Usage:**

```python
publish_notification(
    recipient_user_id='...',
    message='...',
    title='...',
    notification_type='APPOINTMENT'  # Use one of the types above
)
```

---

## 🎯 Priority Levels

Set notification priority to control urgency:

| Priority | Use Case                           |
| -------- | ---------------------------------- |
| `low`    | Non-urgent information, promotions |
| `medium` | Standard notifications, reminders  |
| `high`   | Important updates, confirmations   |
| `urgent` | Critical alerts, security issues   |

**Usage:**

```python
publish_notification(
    recipient_user_id='...',
    message='Security alert: New login detected',
    title='Security Alert',
    priority='urgent'
)
```

---

## ⚙️ API Reference

### `publish_notification()`

Send a single notification to a user.

**Parameters:**

- `recipient_user_id` (str, required): UUID of the user to receive the notification
- `message` (str, required): The notification message content
- `title` (str, optional): Notification title/category
- `priority` (str, optional): Priority level - `'low'`, `'medium'`, `'high'`, `'urgent'` (default: `'medium'`)
- `notification_type` (str, optional): Type of notification - `'APPOINTMENT'`, `'VEHICLE'`, `'PROJECT'`, `'PAYMENT'`, `'SYSTEM'`, `'OTHER'` (default: `'OTHER'`)
- `metadata` (dict, optional): Additional data as JSON object (default: `{}`)

**Returns:** `bool` - `True` if published successfully, `False` otherwise

**Example:**

```python
success = publish_notification(
    recipient_user_id='bcee5755-2c9f-4c0a-8720-1592b75edf96',
    message='Your appointment has been confirmed',
    title='Appointment Confirmed',
    priority='high',
    notification_type='APPOINTMENT',
    metadata={'appointment_id': '123', 'date': '2025-11-01'}
)
```

### `publish_bulk_notifications()`

Send multiple notifications at once.

**Parameters:**

- `notifications` (list, required): List of notification dictionaries, each containing the same fields as `publish_notification()`

**Returns:** `bool` - `True` if all published successfully, `False` otherwise

**Example:**

```python
notifications = [
    {
        'recipient_user_id': 'user-id-1',
        'message': 'Message 1',
        'title': 'Title 1'
    },
    {
        'recipient_user_id': 'user-id-2',
        'message': 'Message 2',
        'title': 'Title 2'
    }
]

success = publish_bulk_notifications(notifications)
```

### Convenience Functions

#### `notify_appointment_confirmed()`

```python
notify_appointment_confirmed(
    customer_id='bcee5755-2c9f-4c0a-8720-1592b75edf96',
    date='2025-11-01',
    time='10:00 AM',
    service_type='Oil Change'
)
```

#### `notify_vehicle_service_complete()`

```python
notify_vehicle_service_complete(
    customer_id='bcee5755-2c9f-4c0a-8720-1592b75edf96',
    vehicle_make='Toyota',
    vehicle_model='Camry'
)
```

#### `notify_payment_success()`

```python
notify_payment_success(
    customer_id='bcee5755-2c9f-4c0a-8720-1592b75edf96',
    amount=150.00,
    receipt_number='RCP-12345'
)
```

---

## ✅ Best Practices

### 1. Use Descriptive Titles

```python
# ❌ Bad
publish_notification(user_id, 'Done', 'Update')

# ✅ Good
publish_notification(user_id, 'Your vehicle service has been completed', 'Service Complete')
```

### 2. Include Relevant Metadata

```python
# Store additional context for frontend to use
publish_notification(
    recipient_user_id=customer_id,
    message='Your appointment has been confirmed',
    title='Appointment Confirmed',
    metadata={
        'appointment_id': str(appointment.id),
        'date': str(appointment.date),
        'time': appointment.time,
        'can_reschedule': True
    }
)
```

### 3. Use Appropriate Priority

```python
# Low priority for promotions
publish_notification(user_id, 'Special offer!', 'Promotion', priority='low')

# High priority for confirmations
publish_notification(user_id, 'Appointment confirmed', 'Confirmation', priority='high')

# Urgent for critical alerts
publish_notification(user_id, 'Security alert', 'Security', priority='urgent')
```

### 4. Choose Correct Notification Type

```python
# Use specific types for better filtering and organization
publish_notification(
    user_id,
    'Payment processed',
    'Payment Success',
    notification_type='PAYMENT'  # Not 'OTHER'
)
```

### 5. Handle Errors Gracefully

```python
try:
    success = publish_notification(
        recipient_user_id=customer_id,
        message='Your appointment is confirmed',
        title='Appointment'
    )
    if not success:
        logger.error(f"Failed to send notification to {customer_id}")
except Exception as e:
    logger.exception(f"Error sending notification: {e}")
    # Don't let notification failures break your business logic
```

---

## 🚨 Error Handling

### Connection Errors

If RabbitMQ is unavailable, the publisher will log an error and return `False`:

```python
success = publish_notification(user_id, message, title)
if not success:
    # Handle failure - maybe retry or log for manual follow-up
    logger.warning(f"Failed to send notification to {user_id}")
```

### Retry Logic

For critical notifications, implement retry logic:

```python
def send_notification_with_retry(user_id, message, title, max_retries=3):
    """Send notification with automatic retry"""
    for attempt in range(max_retries):
        success = publish_notification(user_id, message, title)
        if success:
            return True

        # Wait before retry (exponential backoff)
        time.sleep(2 ** attempt)

    logger.error(f"Failed to send notification after {max_retries} attempts")
    return False
```

### Validation

The publisher validates inputs before sending:

```python
# ❌ This will fail validation
publish_notification(
    recipient_user_id='invalid-id',  # Not a valid UUID
    message='',  # Empty message
    title=None  # None title
)
# Returns: False

# ✅ This is valid
publish_notification(
    recipient_user_id='bcee5755-2c9f-4c0a-8720-1592b75edf96',
    message='Your appointment is confirmed',
    title='Appointment Confirmed'
)
# Returns: True
```

---

## 🔍 Testing

### Test Notification Publisher

Create a test script to verify integration:

```python
# test_notifications.py
from notification_publisher import publish_notification

def test_send_notification():
    """Test sending a notification"""
    success = publish_notification(
        recipient_user_id='bcee5755-2c9f-4c0a-8720-1592b75edf96',
        message='Test notification from service',
        title='Test',
        notification_type='SYSTEM'
    )

    assert success, "Notification should be sent successfully"
    print("✓ Test notification sent successfully")

if __name__ == '__main__':
    test_send_notification()
```

Run the test:

```bash
python test_notifications.py
```

### Test with Docker

If your service runs in Docker, test from inside the container:

```bash
docker exec your-service-container python -c "
from notification_publisher import publish_notification
publish_notification(
    'bcee5755-2c9f-4c0a-8720-1592b75edf96',
    'Test from Docker',
    'Test'
)
"
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────┐
│  Your Microservice  │
│                     │
│  - Appointment      │
│  - Vehicle          │
│  - Employee         │
│  - Customer         │
└──────────┬──────────┘
           │
           │ publish_notification()
           ▼
┌─────────────────────┐
│     RabbitMQ        │
│ notification_events │
│      queue          │
└──────────┬──────────┘
           │
           │ consume
           ▼
┌─────────────────────┐
│ Notification Service│
│  - Save to DB       │
│  - Send via WebSocket│
└──────────┬──────────┘
           │
           │ real-time
           ▼
┌─────────────────────┐
│   Frontend React    │
│  - Notification Bell│
│  - Toast Messages   │
└─────────────────────┘
```

---

## 📚 Additional Resources

- **RabbitMQ Documentation**: See `RABBITMQ_IMPLEMENTATION.md`
- **Integration Guide**: See `INTEGRATION_GUIDE.md`
- **Quick Start**: See `QUICK_START_RABBITMQ.md`
- **WebSocket Authentication**: See `WEBSOCKET_AUTHENTICATION.md`

---

## ❓ FAQ

### Q: Do I need to install the notification service in my service?

**A:** No! Just copy the `notification_publisher.py` file and install `pika`. The publisher is standalone.

### Q: What happens if RabbitMQ is down?

**A:** The publisher will fail gracefully and return `False`. Your service logic continues normally.

### Q: Can I send notifications to multiple users at once?

**A:** Yes! Use `publish_bulk_notifications()` for better performance.

### Q: How do I know if a notification was delivered?

**A:** The publisher returns `True` if sent to RabbitMQ successfully. The notification service handles delivery to users.

### Q: Can I customize notification appearance in the frontend?

**A:** Yes! Use the `metadata` field to pass custom data that the frontend can use for rendering.

### Q: What's the UUID format for user IDs?

**A:** Standard UUID v4 format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (e.g., `bcee5755-2c9f-4c0a-8720-1592b75edf96`)

---

## 🆘 Support

If you encounter issues:

1. Check RabbitMQ is running: `docker ps | grep rabbitmq`
2. Check environment variables are set correctly
3. Verify user IDs are valid UUIDs
4. Check notification service logs: `docker logs backend-notification-service-1`
5. Check RabbitMQ management UI: `http://localhost:15672` (admin/admin123)

---

**Happy Notifying! 🎉**
