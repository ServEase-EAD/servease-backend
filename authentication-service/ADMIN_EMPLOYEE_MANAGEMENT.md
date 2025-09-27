# ServEase Authentication Service - Admin & Employee Management

## Overview

This implementation extends the ServEase authentication system to support role-based access control with admin dashboard functionality for employee account management. The system now supports three user roles: **Customer**, **Employee**, and **Admin**.

## Key Features Implemented

### 1. Role-Based User System
- **Customer**: Default role for public registration
- **Employee**: Created only by admin users
- **Admin**: System administrators with full access

### 2. Enhanced User Model
```python
class CustomUser(AbstractUser):
    USER_ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]
    
    user_role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 3. Permission Classes
- `IsAdmin`: Only admin users
- `IsEmployee`: Only employee users  
- `IsCustomer`: Only customer users
- `IsEmployeeOrAdmin`: Employee or admin users
- `IsOwnerOrAdmin`: Resource owner or admin

## API Endpoints

### Public Endpoints

#### Customer Registration
```http
POST /api/auth/register/
Content-Type: application/json

{
    "email": "customer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "password1": "SecurePass123!",
    "password2": "SecurePass123!"
}
```

#### User Login (All Roles)
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_role": "customer",
    "phone_number": "+1234567890",
    "created_at": "2025-09-27T18:20:00Z",
    "is_active": true,
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### User Logout
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "refresh": "refresh_token_here"
}
```

### User Profile Endpoints

#### Get Current User Profile
```http
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

#### Update Current User Profile
```http
PUT /api/auth/profile/update/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "first_name": "Updated Name",
    "phone_number": "+1987654321"
}
```

### Admin-Only Endpoints

#### Create Employee Account
**Only admins can create employee accounts**
```http
POST /api/auth/admin/employees/create/
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
    "email": "employee@servease.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+1987654321",
    "password1": "EmpPass123!",
    "password2": "EmpPass123!"
}
```

**Response:**
```json
{
    "id": 3,
    "email": "employee@servease.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "user_role": "employee",
    "phone_number": "+1987654321",
    "is_active": true,
    "created_at": "2025-09-27T18:25:00Z",
    "updated_at": "2025-09-27T18:25:00Z",
    "last_login": null,
    "message": "Employee account created successfully"
}
```

#### List All Employees
```http
GET /api/auth/admin/employees/
Authorization: Bearer <admin_access_token>
```

#### List All Users (with filtering)
```http
GET /api/auth/admin/users/?role=employee
Authorization: Bearer <admin_access_token>
```

#### Get User Details
```http
GET /api/auth/admin/users/3/
Authorization: Bearer <admin_access_token>
```

#### Update User Details
```http
PUT /api/auth/admin/users/3/
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
    "first_name": "Updated Name",
    "is_active": false
}
```

#### Delete User
```http
DELETE /api/auth/admin/users/3/
Authorization: Bearer <admin_access_token>
```

#### Toggle User Active Status
```http
POST /api/auth/admin/users/3/toggle-status/
Authorization: Bearer <admin_access_token>
```

#### Admin Dashboard Statistics
```http
GET /api/auth/admin/dashboard/stats/
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
    "total_users": 5,
    "total_customers": 3,
    "total_employees": 1,
    "total_admins": 1,
    "active_users": 5,
    "inactive_users": 0
}
```

## Database Schema Changes

### Added Fields to CustomUser:
- `user_role`: CharField with choices (customer, employee, admin)
- `phone_number`: CharField for contact information
- `created_at`: Auto-generated timestamp
- `updated_at`: Auto-updated timestamp

### Migration Applied:
```bash
python manage.py migrate
# Creates: accounts/migrations/0003_alter_customuser_options_customuser_created_at_and_more.py
```

## Security Features

### 1. Role-Based Access Control
- Endpoints are protected with appropriate permission classes
- Admin-only endpoints reject non-admin users with 403 Forbidden
- Token-based authentication using JWT

### 2. Password Validation
- Minimum 8 characters
- Password confirmation required
- Django's built-in password validators

### 3. Input Validation
- Email format validation
- Required field validation
- Custom business logic validation

## Testing Results

All implemented features have been successfully tested:

✅ **Admin Login**: Working  
✅ **Customer Registration**: Working (creates customer role)  
✅ **Employee Creation**: Working (admin-only)  
✅ **Employee Login**: Working  
✅ **Dashboard Stats**: Working  
✅ **Access Control**: Working (properly rejects unauthorized access)  

### Test Data Created:
- **Admin**: `admin@servease.com` / `AdminPass123!`
- **Customer**: `customer@test.com` / `TestPass123!`  
- **Employee**: `employee@servease.com` / `EmpPass123!`

## Django Admin Interface

The Django admin interface has been enhanced with:
- Role-based filtering
- Color-coded role badges
- Enhanced user listing with role information
- Proper field organization for user management

Access Django admin at: `http://localhost:8001/admin/`

## Environment Setup

### Database Configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'servease_authentication',
        'USER': 'postgres',
        'PASSWORD': 'postgres_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Required Dependencies:
- Django 5.2.6
- djangorestframework 3.15.2
- django-cors-headers 4.4.0
- python-decouple 3.8
- psycopg[binary] 3.2.3
- djangorestframework-simplejwt

## Usage Examples

### 1. Admin Creates Employee Account
```python
import requests

# Admin login
admin_login = requests.post("http://localhost:8001/api/auth/login/", json={
    "email": "admin@servease.com", 
    "password": "AdminPass123!"
})
admin_token = admin_login.json()["tokens"]["access"]

# Create employee
employee_data = {
    "email": "newemployee@servease.com",
    "first_name": "New",
    "last_name": "Employee",
    "phone_number": "+1111111111",
    "password1": "NewEmpPass123!",
    "password2": "NewEmpPass123!"
}

response = requests.post(
    "http://localhost:8001/api/auth/admin/employees/create/",
    json=employee_data,
    headers={"Authorization": f"Bearer {admin_token}"}
)

print(f"Employee created: {response.json()}")
```

### 2. Customer Self-Registration
```python
import requests

customer_data = {
    "email": "newcustomer@example.com",
    "first_name": "New",
    "last_name": "Customer", 
    "phone_number": "+2222222222",
    "password1": "CustomerPass123!",
    "password2": "CustomerPass123!"
}

response = requests.post(
    "http://localhost:8001/api/auth/register/",
    json=customer_data
)

print(f"Customer registered: {response.json()}")
```

## Future Enhancements

1. **Email Verification**: Add email verification for employee accounts
2. **Password Reset**: Implement secure password reset functionality  
3. **Audit Logging**: Track admin actions for security
4. **Bulk Operations**: Allow bulk employee creation/updates
5. **Role Permissions**: More granular permissions beyond basic roles
6. **Employee Profiles**: Extended profile fields for employees
7. **Department Management**: Organize employees by departments

## Conclusion

The ServEase authentication system now successfully implements:
- ✅ Role-based user management (Customer/Employee/Admin)
- ✅ Admin-only employee account creation
- ✅ Secure API endpoints with proper access control
- ✅ Comprehensive user management functionality
- ✅ Django admin interface integration
- ✅ PostgreSQL database integration
- ✅ Complete testing coverage

The system is ready for integration with other ServEase microservices and can be extended with additional features as needed.