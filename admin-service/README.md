# Admin Service - User Management

## Overview

The Admin Service is a dedicated microservice for managing users in the ServEase application. It provides comprehensive user management capabilities including adding, editing, removing users, and managing user roles.

## Architecture

### Backend (Django REST Framework)

- **Port**: 8007
- **Framework**: Django 5.2.6 with Django REST Framework
- **Database**: PostgreSQL (separate `admin_db`)
- **Authentication**: JWT tokens via djangorestframework-simplejwt

### Service Structure

```
admin-service/
├── admin_service/          # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI application
├── admin_api/             # Main API app
│   ├── views.py           # API endpoints
│   ├── serializers.py     # Data serializers
│   ├── permissions.py     # Custom permissions
│   ├── urls.py            # API URL routing
│   └── services/          # External service clients
│       └── auth_service.py # Auth service integration
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── manage.py              # Django management script
```

## API Endpoints

All endpoints require admin authentication (JWT token with admin role).

### User Management

#### 1. List All Users

```
GET /api/v1/admin/users/
Query Parameters:
  - role (optional): Filter by role (customer, employee, admin)

Response: Array of user objects
```

#### 2. Get User Details

```
GET /api/v1/admin/users/{user_id}/

Response: User object with full details
```

#### 3. Create New User

```
POST /api/v1/admin/users/create/
Body:
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password1": "password123",
  "password2": "password123",
  "user_role": "customer|employee|admin",
  "phone_number": "1234567890" (optional)
}

Response: Created user object
```

#### 4. Update User Information

```
PATCH /api/v1/admin/users/{user_id}/update/
Body:
{
  "first_name": "John" (optional),
  "last_name": "Doe" (optional),
  "phone_number": "1234567890" (optional),
  "is_active": true (optional)
}

Response: Updated user object
```

#### 5. Change User Role

```
PATCH /api/v1/admin/users/{user_id}/change-role/
Body:
{
  "user_role": "customer|employee|admin"
}

Response:
{
  "message": "User role updated to {role}",
  "user": {...}
}
```

#### 6. Delete User

```
DELETE /api/v1/admin/users/{user_id}/delete/

Response: 204 No Content
```

#### 7. Toggle User Status

```
POST /api/v1/admin/users/{user_id}/toggle-status/

Response:
{
  "message": "User {email} has been activated/deactivated",
  "is_active": true/false
}
```

#### 8. Get User Statistics

```
GET /api/v1/admin/statistics/

Response:
{
  "total_users": 100,
  "total_customers": 80,
  "total_employees": 15,
  "total_admins": 5,
  "active_users": 90,
  "inactive_users": 10
}
```

#### 9. Health Check

```
GET /api/v1/admin/health/

Response:
{
  "status": "healthy",
  "service": "admin-service"
}
```

## Frontend Integration

### Admin Dashboard Features

1. **User Statistics Dashboard**

   - Total users count
   - Role-based user counts (customers, employees, admins)
   - Active/inactive user counts
   - Visual statistics cards

2. **User Management Table**

   - Filterable by role (All, Customers, Employees, Admins)
   - Sortable columns
   - User details display (email, name, role, phone, status, created date)
   - Action buttons for each user

3. **User Operations**

   - **Add User**: Dialog form to create new users with any role
   - **Edit User**: Update user information (name, phone)
   - **Change Role**: Modify user role (customer ↔ employee ↔ admin)
   - **Toggle Status**: Activate/deactivate users
   - **Delete User**: Remove users from the system

4. **Real-time Feedback**
   - Success/error alerts for all operations
   - Loading indicators during API calls
   - Confirmation dialogs for destructive actions

### Frontend Files

```
frontend/src/
├── pages/
│   └── AdminDashboard.tsx    # Main admin dashboard component
├── services/
│   └── adminService.ts        # Admin API client functions
└── App.tsx                    # Updated with admin routes
```

## Security

### Authentication & Authorization

- All endpoints require valid JWT token
- Token must have `user_role: "admin"` claim
- Custom `IsAdminUser` permission class enforces admin-only access

### Inter-Service Communication

- Admin service communicates with Authentication service
- JWT tokens passed through for user operations
- No direct database access to auth service data

## Setup & Deployment

### Environment Variables

```bash
DB_HOST=localhost
DB_NAME=admin_db
DB_USER=servease_user
DB_PASSWORD=servease_pass
REDIS_HOST=redis
AUTH_SERVICE_URL=http://authentication-service:8001
SECRET_KEY=your-secret-key
DEBUG=False
```

### Docker Compose Integration

The admin service is included in the main `docker-compose.yml`:

- Depends on: redis, authentication-service
- Exposed port: 8007
- Network: servease_network

### Nginx Gateway Routing

```
/api/v1/admin/* → admin-service:8007
```

## Usage

### Creating an Admin User

First, create a superuser through Django:

```bash
cd backend/admin-service
python manage.py createsuperuser
```

Or use the authentication service to create an admin user:

```bash
# Through authentication service API
POST /api/v1/auth/register/
# Then manually change user_role to 'admin' in database
```

### Accessing Admin Dashboard

1. Login with admin credentials
2. Navigate to `/admin-dashboard`
3. The dashboard will load automatically for admin users

## Development

### Running Locally

```bash
# Navigate to admin-service
cd backend/admin-service

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver 8007
```

### Running with Docker

```bash
# From backend directory
docker-compose up admin-service
```

## Features Summary

✅ **User Management**

- Add users with any role (customer, employee, admin)
- Edit user information
- Change user roles dynamically
- Delete users
- Activate/deactivate users

✅ **Dashboard Analytics**

- Real-time user statistics
- Role-based filtering
- Visual data representation

✅ **Security**

- JWT-based authentication
- Admin-only access control
- Secure inter-service communication

✅ **User Experience**

- Intuitive Material-UI interface
- Real-time feedback
- Responsive design
- Confirmation dialogs for critical actions

## API Integration Example

### TypeScript/React

```typescript
import {
  getAllUsers,
  createUser,
  changeUserRole,
} from "../services/adminService";

// Get all users
const users = await getAllUsers();

// Create new employee
const newUser = await createUser({
  email: "employee@example.com",
  first_name: "John",
  last_name: "Doe",
  password1: "secure123",
  password2: "secure123",
  user_role: "employee",
  phone_number: "1234567890",
});

// Change user to admin
await changeUserRole(userId, { user_role: "admin" });
```

## Troubleshooting

### Common Issues

1. **Permission Denied**

   - Ensure user has admin role in JWT token
   - Check token expiration

2. **Cannot Connect to Auth Service**

   - Verify AUTH_SERVICE_URL environment variable
   - Check if authentication-service is running
   - Ensure services are on same Docker network

3. **Database Connection Error**
   - Verify database credentials
   - Check if PostgreSQL is running
   - Run migrations: `python manage.py migrate`

## Future Enhancements

- Bulk user operations
- User import/export functionality
- Advanced search and filtering
- User activity logs
- Role permissions customization
- Email notifications for user actions
