# Customer Service Refactoring Guide

## Overview

The customer service has been refactored to properly integrate with the authentication service, following microservice best practices and eliminating data duplication.

## What Changed?

### 1. **Data Model Restructuring**

#### Before:

```python
class Customer(models.Model):
    user_id = models.IntegerField(unique=True)  # Integer ID
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=17)
    address = models.TextField()
    # ... other fields
```

#### After:

```python
class Customer(models.Model):
    user_id = models.UUIDField(unique=True)  # UUID linking to auth service
    # Removed: first_name, last_name, email, phone
    # These are managed by authentication service

    # Customer-specific fields:
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=100)
    # ... other customer-specific fields
```

### 2. **Key Improvements**

#### ✅ Single Source of Truth

- **User credentials** (email, name, phone, password) → Authentication Service
- **Customer-specific data** (address, company, preferences) → Customer Service

#### ✅ Proper UUID Linking

- Changed from `IntegerField` to `UUIDField` for `user_id`
- Matches the `CustomUser.id` field in authentication service

#### ✅ Enhanced Customer Data

- Separated address into structured fields (street, city, state, postal_code, country)
- Added business-specific fields (business_type, tax_id)
- Added service tracking (total_services counter, last_service_date)
- Added preferences (preferred_contact_method, notification_preferences)

#### ✅ Proper Authentication Integration

- JWT tokens are decoded locally (faster, no extra HTTP call)
- Optional user data fetching from auth service for display purposes
- Clear separation of concerns

## Architecture

```
┌─────────────────────────────┐
│  Authentication Service     │
│  Port: 8001                 │
│                             │
│  - User Registration        │
│  - Login/Logout             │
│  - JWT Token Generation     │
│  - User Credentials         │
│    (email, name, phone)     │
│  - User Roles               │
└──────────┬──────────────────┘
           │
           │ JWT Token (with user_id, email, role)
           │
           ▼
┌─────────────────────────────┐
│  Customer Service           │
│  Port: 8002                 │
│                             │
│  - Customer Profile CRUD    │
│  - Address Management       │
│  - Company Information      │
│  - Emergency Contacts       │
│  - Service History          │
│  - Preferences              │
│                             │
│  References user via UUID   │
└─────────────────────────────┘
```

## API Changes

### Removed Endpoints

- ❌ `DELETE /api/v1/customers/delete_by_user_id/` - Use delete profile endpoint instead

### New Endpoints

- ✅ `POST /api/v1/customers/profile/create/` - Create customer profile (auto-uses authenticated user_id)
- ✅ `DELETE /api/v1/customers/profile/delete/` - Delete customer profile
- ✅ `POST /api/v1/customers/<id>/increment_service/` - Increment service counter
- ✅ `POST /api/v1/customers/check_profile_exists/` - Check if profile exists for user_id

### Modified Endpoints

#### Customer Profile Response

**Before:**

```json
{
  "id": "uuid",
  "user_id": 12345,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State, 12345",
  "company_name": "Tech Inc"
}
```

**After:**

```json
{
  "id": "uuid",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",

  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "full_name": "John Doe",

  "street_address": "123 Main St, Apt 4B",
  "city": "Portland",
  "state": "Oregon",
  "postal_code": "97201",
  "country": "USA",
  "full_address": "123 Main St, Apt 4B, Portland, Oregon, 97201, USA",

  "company_name": "Tech Inc",
  "business_type": "Software Development",
  "tax_id": "12-3456789",
  "is_business_customer": true,

  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1987654321",
  "emergency_contact_relationship": "Spouse",

  "is_verified": true,
  "customer_since": "2025-01-15T10:30:00Z",
  "last_service_date": "2025-10-25T14:20:00Z",
  "total_services": 5,

  "preferred_contact_method": "email",
  "notification_preferences": {},

  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-10-30T09:15:00Z"
}
```

## Migration Steps

### 1. Database Migration

You'll need to create and run migrations to update the database schema:

```powershell
# Access the container
docker-compose exec customer-service /bin/bash

# Create migrations
python manage.py makemigrations

# Review the migration file
# It will show:
# - Changing user_id from IntegerField to UUIDField
# - Removing fields: first_name, last_name, email, phone, address
# - Adding fields: street_address, city, state, postal_code, country, etc.

# Apply migrations
python manage.py migrate
```

⚠️ **IMPORTANT**: This migration will **lose data** for removed fields. Before migrating production:

1. **Backup your database**
2. **Export existing customer data**
3. **Map old address field to new structured fields**
4. **Verify all user_id values exist in authentication service**

### 2. Data Migration Script

Create a data migration to preserve existing data:

```python
# Create empty migration
python manage.py makemigrations --empty customers

# Edit the migration file to add data transformation
from django.db import migrations

def migrate_customer_data(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')

    for customer in Customer.objects.all():
        # Parse old address field into structured fields
        # This is simplified - adjust based on your data format
        address_parts = customer.address.split(',')
        if len(address_parts) >= 4:
            customer.street_address = address_parts[0].strip()
            customer.city = address_parts[1].strip()
            customer.state = address_parts[2].strip()
            customer.postal_code = address_parts[3].strip()

        customer.save()

class Migration(migrations.Migration):
    dependencies = [
        ('customers', 'XXXX_previous_migration'),
    ]

    operations = [
        migrations.RunPython(migrate_customer_data),
    ]
```

### 3. Update Frontend Integration

Update frontend code to work with new API structure:

#### Creating Customer Profile

**Before:**

```javascript
// After user registration
const response = await fetch("http://localhost:8002/api/v1/customers/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    user_id: userId,
    first_name: "John",
    last_name: "Doe",
    email: "john@example.com",
    phone: "+1234567890",
    address: "123 Main St, City, State, 12345",
  }),
});
```

**After:**

```javascript
// 1. Register user in auth service
const authResponse = await fetch("http://localhost:8001/api/auth/register/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "john@example.com",
    first_name: "John",
    last_name: "Doe",
    phone_number: "+1234567890",
    password1: "securepass123",
    password2: "securepass123",
  }),
});

const { tokens, id: userId } = await authResponse.json();

// 2. Create customer profile (automatically uses authenticated user)
const profileResponse = await fetch(
  "http://localhost:8002/api/v1/customers/profile/create/",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${tokens.access}`,
    },
    body: JSON.stringify({
      street_address: "123 Main St, Apt 4B",
      city: "Portland",
      state: "Oregon",
      postal_code: "97201",
      country: "USA",
      company_name: "Tech Inc", // Optional
      business_type: "Software", // Optional
      emergency_contact_name: "Jane Doe",
      emergency_contact_phone: "+1987654321",
      emergency_contact_relationship: "Spouse",
    }),
  }
);
```

#### Updating User Information

**Before:**

```javascript
// Update everything in customer service
await fetch(`http://localhost:8002/api/v1/customers/${customerId}/`, {
  method: "PATCH",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    first_name: "Jane",
    email: "jane@example.com",
    phone: "+1111111111",
    address: "456 New St",
  }),
});
```

**After:**

```javascript
// Update user credentials in auth service
await fetch(`http://localhost:8001/api/auth/profile/update/`, {
  method: "PATCH",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    first_name: "Jane",
    email: "jane@example.com",
    phone_number: "+1111111111",
  }),
});

// Update customer-specific data in customer service
await fetch(`http://localhost:8002/api/v1/customers/profile/update/`, {
  method: "PATCH",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    street_address: "456 New St",
    city: "Seattle",
    state: "Washington",
  }),
});
```

## Testing

### 1. Test Customer Profile Creation

```powershell
# 1. Register a user in auth service
$registerData = @{
    email = "testuser@example.com"
    first_name = "Test"
    last_name = "User"
    phone_number = "+1234567890"
    password1 = "TestPass123!"
    password2 = "TestPass123!"
} | ConvertTo-Json

$authResult = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/register/" -Method POST -Body $registerData -ContentType "application/json"
$token = $authResult.tokens.access
$userId = $authResult.id

# 2. Create customer profile
$profileData = @{
    street_address = "123 Test Street"
    city = "Portland"
    state = "Oregon"
    postal_code = "97201"
    country = "USA"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$customerResult = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/profile/create/" -Method POST -Body $profileData -Headers $headers -ContentType "application/json"
$customerResult | ConvertTo-Json -Depth 3
```

### 2. Test Profile Retrieval

```powershell
# Get current customer profile
$profile = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/profile/" -Method GET -Headers $headers
$profile | ConvertTo-Json -Depth 3
```

### 3. Test Profile Update

```powershell
# Update customer profile
$updateData = @{
    street_address = "456 Updated Avenue"
    city = "Seattle"
    company_name = "New Company LLC"
} | ConvertTo-Json

$updated = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/profile/update/" -Method PATCH -Body $updateData -Headers $headers -ContentType "application/json"
$updated | ConvertTo-Json -Depth 3
```

## Benefits of This Refactoring

### 1. **No Data Duplication**

- Email, name, phone are only stored in authentication service
- Reduces sync issues and data inconsistency

### 2. **Clear Separation of Concerns**

- Authentication service handles identity and credentials
- Customer service handles customer-specific business data

### 3. **Better Scalability**

- Each service can be scaled independently
- Reduced database load on customer service

### 4. **Improved Security**

- User credentials and authentication are centralized
- Easier to implement security policies

### 5. **Easier Maintenance**

- Changes to user credentials only need to be made in one place
- Customer service focuses on its core responsibility

### 6. **Better Data Structure**

- Structured address fields enable better queries and analytics
- Business customer tracking
- Service history tracking

## Inter-Service Communication

### How Customer Service Gets User Data

1. **During Authentication (Fast)**

   ```python
   # JWT token includes user data
   token_payload = {
       'user_id': '550e8400-e29b-41d4-a716-446655440000',
       'email': 'john@example.com',
       'first_name': 'John',
       'last_name': 'Doe',
       'user_role': 'customer'
   }
   ```

2. **For Display Purposes (When Needed)**
   ```python
   # Fetch complete user data from auth service
   user_data = get_user_data_from_auth_service(user_id)
   ```

### Integration Points

1. **Registration Flow**:

   - Frontend → Auth Service (create user)
   - Frontend → Customer Service (create profile)

2. **Authentication Flow**:

   - Frontend → Auth Service (login, get JWT)
   - Frontend → Customer Service (use JWT for requests)

3. **Profile Management**:
   - User credentials → Auth Service
   - Customer data → Customer Service

## Troubleshooting

### Issue: "Customer profile not found"

**Cause**: User exists in auth service but no customer profile created yet.

**Solution**: Call `POST /api/v1/customers/profile/create/` endpoint.

### Issue: "Only customers can access this service"

**Cause**: Token has `user_role` other than 'customer' (e.g., 'employee', 'admin').

**Solution**: Ensure only customer tokens are used with customer service.

### Issue: User data not showing in customer profile

**Cause**: Auth service is unavailable or user doesn't exist.

**Solution**:

1. Check auth service is running
2. Verify user_id exists in auth service
3. Check network connectivity between services

## Future Enhancements

1. **Event-Driven Updates**

   - When user updates email in auth service, emit event
   - Customer service can cache user data and update on event

2. **Service Mesh**

   - Implement service discovery
   - Add circuit breakers for resilience

3. **Async Communication**

   - Use message queue (RabbitMQ/Redis) for non-critical operations
   - Decouple services further

4. **Caching Layer**
   - Cache user data in customer service (with TTL)
   - Reduce calls to auth service

## Conclusion

This refactoring establishes a proper microservice architecture where:

- ✅ Each service has a clear, focused responsibility
- ✅ Data is not duplicated across services
- ✅ Services communicate properly via JWT and APIs
- ✅ The system is more maintainable and scalable

Follow this guide when integrating the refactored customer service with your frontend and other microservices.
