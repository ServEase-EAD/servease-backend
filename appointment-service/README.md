# Appointment Service

The Appointment Service manages all appointment scheduling for the ServEase platform, including service appointments for customer vehicles, time slot management, and appointment lifecycle tracking.

## Features

- **Appointment Management**: Create, update, cancel, and reschedule appointments
- **Time Slot Management**: Manage available appointment slots with concurrent booking support
- **Status Tracking**: Track appointment lifecycle through various states (pending, confirmed, in-progress, completed, cancelled)
- **History Tracking**: Maintain complete audit trail of all appointment changes
- **Inter-Service Communication**: Validates customers, vehicles, and employees via other microservices
- **Notification Integration**: Sends notifications for appointment events
- **Caching**: Redis-based caching for improved performance

## API Endpoints

### Appointments

- `GET /api/v1/appointments/` - List all appointments (with filters)
- `POST /api/v1/appointments/` - Create new appointment
- `GET /api/v1/appointments/{id}/` - Get appointment details
- `PUT /api/v1/appointments/{id}/` - Update appointment
- `PATCH /api/v1/appointments/{id}/` - Partial update
- `DELETE /api/v1/appointments/{id}/` - Delete appointment

### Appointment Actions

- `POST /api/v1/appointments/{id}/confirm/` - Confirm appointment
- `POST /api/v1/appointments/{id}/start/` - Start appointment (in-progress)
- `POST /api/v1/appointments/{id}/complete/` - Complete appointment
- `POST /api/v1/appointments/{id}/cancel/` - Cancel appointment
- `POST /api/v1/appointments/{id}/reschedule/` - Reschedule appointment
- `POST /api/v1/appointments/{id}/assign/` - Assign employee

### Query Endpoints

- `GET /api/v1/appointments/customer_appointments/?customer_id={id}` - Customer's appointments
- `GET /api/v1/appointments/employee_schedule/?employee_id={id}` - Employee's schedule
- `GET /api/v1/appointments/vehicle_history/?vehicle_id={id}` - Vehicle service history
- `GET /api/v1/appointments/available_slots/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Available time slots
- `GET /api/v1/appointments/stats/` - Dashboard statistics
- `GET /api/v1/appointments/{id}/history/` - Appointment change history

### Time Slots

- `GET /api/v1/time-slots/` - List time slots
- `POST /api/v1/time-slots/` - Create time slot
- `GET /api/v1/time-slots/{id}/` - Get time slot details
- `PUT /api/v1/time-slots/{id}/` - Update time slot
- `DELETE /api/v1/time-slots/{id}/` - Delete time slot
- `POST /api/v1/time-slots/bulk_create/` - Bulk create time slots

### History

- `GET /api/v1/history/` - List appointment history
- `GET /api/v1/history/?appointment_id={id}` - History for specific appointment

## Models

### Appointment

Main appointment model with fields:
- `id` (UUID primary key)
- `customer_id`, `vehicle_id`, `assigned_employee_id`, `created_by_user_id` (all UUIDs)
- `appointment_type` (maintenance, repair, inspection, diagnostic, emergency)
- `scheduled_date`, `scheduled_time`, `duration_minutes`
- `status` (pending, confirmed, in_progress, completed, cancelled, no_show)
- `service_description`, `customer_notes`, `internal_notes`
- `estimated_cost`
- Timestamps: `created_at`, `updated_at`, `cancelled_at`, `completed_at`

### TimeSlot

Time slot availability management:
- `date`, `start_time`, `end_time`
- `is_available`
- `max_concurrent_appointments`

### AppointmentHistory

Audit trail for appointment changes:
- `appointment_id`, `changed_by_user_id` (UUIDs)
- `previous_status`, `new_status`
- `change_reason`, `changed_at`

## Setup and Installation

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- JWT authentication via Authentication Service

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create `.env` file):
```env
DB_HOST=localhost
DB_NAME=servease_appointments
DB_USER=postgres
DB_PASSWORD=your_password
REDIS_HOST=localhost
REDIS_PORT=6379

# Service URLs
CUSTOMER_SERVICE_URL=http://customer-service:8002
EMPLOYEE_SERVICE_URL=http://employee-service:8003
VEHICLE_SERVICE_URL=http://vehicleandproject-service:8004
NOTIFICATION_SERVICE_URL=http://notification-service:8006
AUTH_SERVICE_URL=http://authentication-service:8001
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Seed time slots (optional):
```bash
python manage.py seed_timeslots --days=30
```

5. Run the server:
```bash
python manage.py runserver 0.0.0.0:8005
```

## Docker Deployment

Build and run with Docker:

```bash
docker build -t appointment-service .
docker run -p 8005:8005 appointment-service
```

Or use with docker-compose (from project root):

```bash
docker-compose up appointment-service
```

## Query Parameters

### List Appointments

- `?status=pending` - Filter by status
- `?start_date=2024-01-01&end_date=2024-01-31` - Filter by date range
- `?appointment_type=maintenance` - Filter by type
- `?customer_id={uuid}` - Filter by customer
- `?employee_id={uuid}` - Filter by employee

## Request Examples

### Create Appointment

```json
POST /api/v1/appointments/
Authorization: Bearer <your-jwt-token>

{
  "customer_id": "123e4567-e89b-12d3-a456-426614174000",
  "vehicle_id": "123e4567-e89b-12d3-a456-426614174001",
  "appointment_type": "maintenance",
  "scheduled_date": "2024-12-15",
  "scheduled_time": "10:00:00",
  "duration_minutes": 60,
  "service_description": "Regular maintenance checkup",
  "customer_notes": "Check brake pads",
  "created_by_user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Reschedule Appointment

```json
POST /api/v1/appointments/{id}/reschedule/
{
  "new_date": "2024-12-20",
  "new_time": "14:00:00",
  "reason": "Customer requested change"
}
```

### Assign Employee

```json
POST /api/v1/appointments/{id}/assign/
Authorization: Bearer <your-jwt-token>

{
  "employee_id": "123e4567-e89b-12d3-a456-426614174002"
}
```

## Business Logic

### Appointment Creation Validation

- Customer must exist (validated via Customer Service)
- Vehicle must exist and belong to customer (validated via Vehicle Service)
- Date must be in the future
- Time slot must be available
- Employee must be available (if assigned)
- Customer cannot have conflicting appointments

### Status Transitions

Valid status transitions:
- `pending` → `confirmed`, `cancelled`
- `confirmed` → `in_progress`, `cancelled`, `no_show`
- `in_progress` → `completed`, `cancelled`
- `completed` → (terminal state)
- `cancelled` → (terminal state)

### Time Slot Management

- Supports concurrent appointments (configurable via `MAX_CONCURRENT_APPOINTMENTS`)
- Business hours: 9 AM - 5 PM (configurable)
- Automatically skips weekends
- Manual time slot creation for custom schedules

## Caching

The service uses Redis for caching:
- Customer data (5 minutes TTL)
- Vehicle data (5 minutes TTL)
- Employee data (5 minutes TTL)

Cache is automatically invalidated on updates.

## Authentication

All API requests require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <your-access-token>
```

**Token Details:**
- Access Token: Valid for **1 hour**
- Refresh Token: Valid for **7 days**
- Login endpoint: `http://localhost:8001/api/v1/auth/login/`
- Token refresh: `http://localhost:8001/api/v1/auth/token/refresh/`

## Permissions

- **IsAuthenticated**: All endpoints require JWT authentication
- **IsEmployeeOrAdmin**: Required for confirm, start, complete, assign actions
- **IsAppointmentOwnerOrAdmin**: Required for updating/deleting appointments
- **IsCustomerOrEmployee**: View appointments (customers see only theirs, employees see all)

## Management Commands

### Seed Time Slots

```bash
python manage.py seed_timeslots --days=30 --start-hour=9 --end-hour=17
```

Creates time slots for the next N business days.

## Testing

Run tests:
```bash
python manage.py test appointments
```

## Architecture

```
appointments/
├── models.py              # Database models
├── serializers.py         # DRF serializers
├── views.py              # ViewSets and views
├── urls.py               # URL routing
├── permissions.py        # Custom permissions
├── services/             # Business logic
│   ├── service_clients.py    # Inter-service communication
│   ├── validators.py          # Validation logic
│   ├── time_slot_manager.py  # Time slot management
│   └── status_handler.py      # Status transitions
├── utils/                # Utilities
│   ├── cache_helper.py       # Caching utilities
│   └── date_utils.py         # Date/time helpers
└── management/           # Management commands
    └── commands/
        └── seed_timeslots.py
```

## Contributing

1. Follow Django and DRF best practices
2. Add tests for new features
3. Update documentation
4. Use type hints where applicable
5. Follow PEP 8 style guide

## License

Proprietary - ServEase Platform

