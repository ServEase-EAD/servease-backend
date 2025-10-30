# Appointment Service - Complete API Guide

## Base URL
```
http://localhost:8005/api/v1/
```

## Authentication
All requests require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

**Token Duration:** Access tokens are valid for **1 hour**

---

## 📖 Table of Contents

1. [Role-Based Access Overview](#role-based-access-overview)
2. [Customer Endpoints](#customer-endpoints)
3. [Employee/Admin Endpoints](#employeeadmin-endpoints)
4. [All Users Endpoints](#all-users-endpoints)
5. [Common Error Responses](#common-error-responses)

---

## 🔐 Role-Based Access Overview

| Icon | Role | Description |
|------|------|-------------|
| 👤 | **Customer** | Can manage their own appointments |
| 👨‍💼 | **Employee** | Can manage all appointments and workflows |
| 👑 | **Admin** | Full access to all features |
| 🌐 | **All** | Any authenticated user |

---

## 👤 Customer Endpoints

### 1. Get Available Time Slots 🌐
Check available appointment times before booking.

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/appointments/available_slots/`

**Query Parameters:**
- `start_date` (required): YYYY-MM-DD
- `end_date` (required): YYYY-MM-DD
- `duration_minutes` (optional): default 60

**Example:**
```
GET http://localhost:8005/api/v1/appointments/available_slots/?start_date=2025-11-01&end_date=2025-11-07&duration_minutes=60
```

**Response:** `200 OK`
```json
{
  "count": 45,
  "slots": [
    {
      "date": "2025-11-03",
      "start_time": "09:00:00",
      "end_time": "10:00:00",
      "available_capacity": 3
    }
  ]
}
```

---

### 2. Create New Appointment 👤
Book a new service appointment.

**Access:** Customers (for themselves)  
**Endpoint:** `POST /api/v1/appointments/`

**JSON Body:**
```json
{
  "customer_id": "bcee5755-2c9f-4c0a-8720-1592b75edf96",
  "vehicle_id": "d540f435-b72e-41a3-8ddd-88a58f625244",
  "appointment_type": "maintenance",
  "scheduled_date": "2025-11-05",
  "scheduled_time": "10:00:00",
  "duration_minutes": 60,
  "service_description": "Regular oil change and tire rotation",
  "customer_notes": "Please check the brake pads as well",
  "estimated_cost": "150.00",
  "created_by_user_id": "bcee5755-2c9f-4c0a-8720-1592b75edf96"
}
```

**Appointment Types:**
- `maintenance` - Regular Maintenance
- `repair` - Repair
- `inspection` - Inspection
- `diagnostic` - Diagnostic
- `emergency` - Emergency Service

**Response:** `201 Created`

---

### 3. List All Appointments 🌐
View appointments (filtered by role).

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/appointments/`

**Query Parameters (all optional):**
- `status` - Filter by: pending, confirmed, in_progress, completed, cancelled
- `start_date` - From date (YYYY-MM-DD)
- `end_date` - To date (YYYY-MM-DD)
- `appointment_type` - Filter by type
- `customer_id` - Filter by customer
- `employee_id` - Filter by employee

**Examples:**
```
GET http://localhost:8005/api/v1/appointments/
GET http://localhost:8005/api/v1/appointments/?status=pending
GET http://localhost:8005/api/v1/appointments/?customer_id=bcee5755-2c9f-4c0a-8720-1592b75edf96
GET http://localhost:8005/api/v1/appointments/?start_date=2025-11-01&end_date=2025-11-30
```

**Note:** Customers only see their own appointments. Employees/Admins see all appointments.

---

### 4. Get Specific Appointment Details 🌐
View details of a specific appointment.

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/appointments/{appointment_id}/`

**Example:**
```
GET http://localhost:8005/api/v1/appointments/abc12345-6789-4def-0123-456789abcdef/
```

---

### 5. Get Customer Appointments 🌐
Get all appointments for a specific customer.

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/appointments/customer_appointments/`

**Query Parameter:**
- `customer_id` (required): Customer UUID

**Example:**
```
GET http://localhost:8005/api/v1/appointments/customer_appointments/?customer_id=bcee5755-2c9f-4c0a-8720-1592b75edf96
```

---

### 6. Reschedule Appointment 🌐
Change the date/time of an appointment.

**Access:** All authenticated users (customers can reschedule their own)  
**Endpoint:** `POST /api/v1/appointments/{appointment_id}/reschedule/`

**JSON Body:**
```json
{
  "new_date": "2025-11-10",
  "new_time": "14:00:00",
  "reason": "Need to change appointment time"
}
```

**Response:** `200 OK`
```json
{
  "status": "rescheduled",
  "message": "Appointment rescheduled successfully",
  "appointment": {
    "id": "abc12345-6789-4def-0123-456789abcdef",
    "scheduled_date": "2025-11-10",
    "scheduled_time": "14:00:00"
  }
}
```

---

### 7. Cancel Appointment 🌐
Cancel an appointment.

**Access:** All authenticated users (customers can cancel their own)  
**Endpoint:** `POST /api/v1/appointments/{appointment_id}/cancel/`

**JSON Body:**
```json
{
  "reason": "No longer need the service"
}
```

**Response:** `200 OK`
```json
{
  "status": "cancelled",
  "message": "Appointment cancelled successfully",
  "appointment": {
    "id": "abc12345-6789-4def-0123-456789abcdef",
    "status": "cancelled",
    "cancelled_at": "2025-10-30T10:00:00Z"
  }
}
```

---

### 8. Get Appointment History 🌐
View status change history for an appointment.

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/appointments/{appointment_id}/history/`

**Example:**
```
GET http://localhost:8005/api/v1/appointments/abc12345-6789-4def-0123-456789abcdef/history/
```

**Response:** `200 OK`
```json
[
  {
    "id": "hist-uuid-1",
    "appointment_id": "abc12345-6789-4def-0123-456789abcdef",
    "changed_by_user_id": "bcee5755-2c9f-4c0a-8720-1592b75edf96",
    "previous_status": "pending",
    "new_status": "confirmed",
    "change_reason": "Availability confirmed",
    "changed_at": "2025-10-30T09:00:00Z"
  }
]
```

---

### 9. Get Vehicle Service History 🌐
View all appointments for a specific vehicle.

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/appointments/vehicle_history/`

**Query Parameter:**
- `vehicle_id` (required): Vehicle UUID

**Example:**
```
GET http://localhost:8005/api/v1/appointments/vehicle_history/?vehicle_id=d540f435-b72e-41a3-8ddd-88a58f625244
```

**Response:** `200 OK`
```json
[
  {
    "id": "appointment-uuid-1",
    "appointment_type": "maintenance",
    "scheduled_date": "2025-10-15",
    "status": "completed",
    "service_description": "Oil change"
  },
  {
    "id": "appointment-uuid-2",
    "appointment_type": "inspection",
    "scheduled_date": "2025-11-05",
    "status": "pending"
  }
]
```

---

### 10. Get Appointment Statistics 🌐
View overall appointment statistics.

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/appointments/stats/`

**Example:**
```
GET http://localhost:8005/api/v1/appointments/stats/
```

**Response:** `200 OK`
```json
{
  "total_appointments": 250,
  "pending": 15,
  "confirmed": 30,
  "in_progress": 5,
  "completed": 180,
  "cancelled": 20,
  "today": 8,
  "completed_today": 3,
  "upcoming": 45,
  "by_type": {
    "maintenance": 120,
    "repair": 80,
    "inspection": 30,
    "diagnostic": 15,
    "emergency": 5
  }
}
```

---

## 👨‍💼👑 Employee/Admin Endpoints

### 11. Confirm Appointment 👨‍💼👑
Confirm a pending appointment.

**Access:** Employees and Admins ONLY  
**Endpoint:** `POST /api/v1/appointments/{appointment_id}/confirm/`

**JSON Body:**
```json
{
  "reason": "Availability confirmed with customer"
}
```

**Response:** `200 OK`
```json
{
  "status": "confirmed",
  "message": "Appointment confirmed successfully",
  "appointment": {
    "id": "abc12345-6789-4def-0123-456789abcdef",
    "status": "confirmed",
    "updated_at": "2025-10-30T10:00:00Z"
  }
}
```

---

### 12. Start Appointment 👨‍💼👑
Mark an appointment as in-progress.

**Access:** Employees and Admins ONLY  
**Endpoint:** `POST /api/v1/appointments/{appointment_id}/start/`

**JSON Body:**
```json
{
  "reason": "Service started"
}
```

**Response:** `200 OK`
```json
{
  "status": "in_progress",
  "message": "Appointment started",
  "appointment": {
    "id": "abc12345-6789-4def-0123-456789abcdef",
    "status": "in_progress"
  }
}
```

---

### 13. Complete Appointment 👨‍💼👑
Mark an appointment as completed.

**Access:** Employees and Admins ONLY  
**Endpoint:** `POST /api/v1/appointments/{appointment_id}/complete/`

**JSON Body:**
```json
{
  "reason": "All services completed successfully"
}
```

**Response:** `200 OK`
```json
{
  "status": "completed",
  "message": "Appointment completed successfully",
  "appointment": {
    "id": "abc12345-6789-4def-0123-456789abcdef",
    "status": "completed",
    "completed_at": "2025-10-30T15:00:00Z"
  }
}
```

---

### 14. Assign Employee to Appointment 👨‍💼👑
Assign an employee to handle an appointment.

**Access:** Employees and Admins ONLY  
**Endpoint:** `POST /api/v1/appointments/{appointment_id}/assign/`

**JSON Body:**
```json
{
  "employee_id": "bcee5755-2c9f-4c0a-8720-1592b75edf96"
}
```

**Response:** `200 OK`
```json
{
  "status": "assigned",
  "message": "Employee assigned successfully",
  "appointment": {
    "id": "abc12345-6789-4def-0123-456789abcdef",
    "assigned_employee_id": "bcee5755-2c9f-4c0a-8720-1592b75edf96",
    "employee_name": "John Smith"
  }
}
```

---

### 15. Get Employee Schedule 🌐
Get all appointments assigned to a specific employee.

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/appointments/employee_schedule/`

**Query Parameter:**
- `employee_id` (required): Employee ID (UUID)

**Example:**
```
GET http://localhost:8005/api/v1/appointments/employee_schedule/?employee_id=bcee5755-2c9f-4c0a-8720-1592b75edf96
```

**Response:** `200 OK`
```json
[
  {
    "id": "appointment-uuid-1",
    "appointment_type": "maintenance",
    "scheduled_date": "2025-11-05",
    "scheduled_time": "10:00:00",
    "status": "confirmed",
    "customer_name": "Sajith Mayadunna",
    "vehicle_details": "2020 Toyota Camry"
  }
]
```

---

## 🕐 Time Slot Management

### 16. List Time Slots 🌐
View available time slots.

**Access:** All authenticated users  
**Endpoint:** `GET /api/v1/time-slots/`

**Query Parameters (optional):**
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)

**Example:**
```
GET http://localhost:8005/api/v1/time-slots/?start_date=2025-11-01&end_date=2025-11-07
```

---

### 17. Bulk Create Time Slots 👨‍💼👑
Create time slots for a date range.

**Access:** Employees and Admins ONLY  
**Endpoint:** `POST /api/v1/time-slots/bulk_create/`

**JSON Body:**
```json
{
  "start_date": "2025-11-20",
  "end_date": "2025-11-30"
}
```

**Response:** `201 Created`
```json
{
  "message": "Created 88 time slots",
  "count": 88
}
```

---

## 📊 Quick Reference Table

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/appointments/available_slots/` | GET | 🌐 All | Get available time slots |
| `/appointments/` | POST | 👤 Customer | Create appointment |
| `/appointments/` | GET | 🌐 All | List appointments (role-filtered) |
| `/appointments/{id}/` | GET | 🌐 All | Get appointment details |
| `/appointments/{id}/confirm/` | POST | 👨‍💼👑 Employee/Admin | Confirm appointment |
| `/appointments/{id}/start/` | POST | 👨‍💼👑 Employee/Admin | Start appointment |
| `/appointments/{id}/complete/` | POST | 👨‍💼👑 Employee/Admin | Complete appointment |
| `/appointments/{id}/cancel/` | POST | 🌐 All | Cancel appointment |
| `/appointments/{id}/reschedule/` | POST | 🌐 All | Reschedule appointment |
| `/appointments/{id}/assign/` | POST | 👨‍💼👑 Employee/Admin | Assign employee |
| `/appointments/{id}/history/` | GET | 🌐 All | View appointment history |
| `/appointments/customer_appointments/` | GET | 🌐 All | Get customer appointments |
| `/appointments/employee_schedule/` | GET | 🌐 All | Get employee schedule |
| `/appointments/vehicle_history/` | GET | 🌐 All | Get vehicle service history |
| `/appointments/stats/` | GET | 🌐 All | Get statistics |
| `/time-slots/` | GET | 🌐 All | List time slots |
| `/time-slots/bulk_create/` | POST | 👨‍💼👑 Employee/Admin | Bulk create time slots |

---

## ⚠️ Common Error Responses

### 400 Bad Request
```json
{
  "detail": ["Appointment must be scheduled in the future"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🔄 Refreshing Your Token

When your access token expires (after 1 hour), use the refresh token to get a new one:

**Endpoint:** `POST http://localhost:8001/api/v1/auth/token/refresh/`

**JSON Body:**
```json
{
  "refresh": "your-refresh-token-here"
}
```

**Response:**
```json
{
  "access": "new-access-token-here",
  "refresh": "new-refresh-token-here"
}
```

---

## 📝 Postman Setup Instructions

1. **Create a new request**
2. **Set the Method** (GET/POST as needed)
3. **Enter the URL** (one from above)
4. **Add Authorization Header:**
   - Go to "Headers" tab
   - Add: `Authorization` with value: `Bearer <your-access-token>`
5. **For POST requests:**
   - Go to "Body" tab
   - Select "raw"
   - Select "JSON" from dropdown
   - Paste the JSON body

---

## 🧪 Testing Workflows

### Customer Workflow
1. ✅ Login and get token
2. ✅ Get available slots
3. ✅ Create appointment
4. ✅ View my appointments
5. ✅ Reschedule appointment (if needed)
6. ✅ Cancel appointment (if needed)

### Employee Workflow
1. ✅ Login and get token
2. ✅ View all appointments
3. ✅ Confirm pending appointments
4. ✅ Assign employee to appointments
5. ✅ Start appointment (when customer arrives)
6. ✅ Complete appointment (when done)
7. ✅ View employee schedule

### Admin Workflow
1. ✅ All Employee permissions
2. ✅ Create time slots
3. ✅ View statistics
4. ✅ Manage all appointments across the system

---

## 📞 Support

For issues or questions, contact your system administrator.

**Service URLs:**
- Authentication Service: `http://localhost:8001`
- Vehicle Service: `http://localhost:8004`
- Appointment Service: `http://localhost:8005`

---

**Last Updated:** October 30, 2025  
**Version:** 2.0

