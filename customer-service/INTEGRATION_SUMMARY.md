# Customer Service Integration Summary

## Executive Summary

The customer-service has been refactored to properly integrate with the authentication-service, eliminating data duplication and establishing clear microservice boundaries.

## Key Changes

### 1. **Data Model** (`customers/models.py`)

**Removed Fields** (now managed by auth service):

- `first_name`, `last_name` - Use auth service
- `email` - Use auth service
- `phone` - Use auth service
- `address` (TextField) - Replaced with structured fields

**Changed Fields**:

- `user_id`: Changed from `IntegerField` to `UUIDField` to match auth service

**New Fields**:

- `street_address`, `city`, `state`, `postal_code`, `country` - Structured address
- `business_type`, `tax_id` - Enhanced business customer support
- `total_services` - Service counter (auto-incremented)
- `preferred_contact_method` - Customer preferences
- `notification_preferences` - JSON field for settings

### 2. **Serializers** (`customers/serializers.py`)

**New Serializers**:

- `CustomerWithUserDataSerializer` - Combines customer + auth user data
- Enhanced serializers to handle user data from context

**Key Features**:

- Read-only fields for auth service data (email, name, phone)
- Serializers fetch user data from JWT token payload
- Optional fetching from auth service for complete data

### 3. **Authentication** (`customers/authentication.py`)

**Improved**:

- `CustomerUser` class now includes first_name, last_name
- Better JWT token decoding with validation
- Helper function `get_user_data_from_auth_service()` for fetching complete user info
- Clear error messages for authentication failures

### 4. **Views** (`customers/views.py`)

**New Endpoints**:

- `POST /profile/create/` - Create profile (auto-uses authenticated user)
- `DELETE /profile/delete/` - Delete profile
- `POST /<id>/increment_service/` - Service counter
- `POST /check_profile_exists/` - Check if profile exists

**Improved**:

- All endpoints properly integrate with auth service
- User data fetched when needed for display
- Better error handling and messages

### 5. **Permissions** (`customers/permissions.py`)

No changes needed - existing permissions work correctly.

## Architecture

```
┌──────────────────────────────────────────────┐
│         Authentication Service               │
│                 (Port 8001)                  │
│                                              │
│  CustomUser Model:                           │
│  - id (UUID, PK)                            │
│  - email (unique)                           │
│  - first_name                               │
│  - last_name                                │
│  - phone_number                             │
│  - user_role (customer/employee/admin)      │
│  - password (hashed)                        │
│                                              │
│  Responsibilities:                           │
│  - User registration                         │
│  - Login/logout                             │
│  - JWT token generation                     │
│  - User credential management               │
└─────────────────┬────────────────────────────┘
                  │
                  │ JWT Token Contains:
                  │ {user_id, email, first_name,
                  │  last_name, user_role}
                  │
                  ▼
┌──────────────────────────────────────────────┐
│         Customer Service                     │
│              (Port 8002)                     │
│                                              │
│  Customer Model:                             │
│  - id (UUID, PK)                            │
│  - user_id (UUID, FK to auth service)       │
│  - street_address                            │
│  - city, state, postal_code, country        │
│  - company_name, business_type, tax_id      │
│  - emergency contacts                        │
│  - is_verified, customer_since              │
│  - total_services, last_service_date        │
│  - preferences                               │
│                                              │
│  Responsibilities:                           │
│  - Customer profile management              │
│  - Address information                       │
│  - Business customer data                    │
│  - Emergency contacts                        │
│  - Service history tracking                  │
│  - Customer preferences                      │
└──────────────────────────────────────────────┘
```

## Registration & Profile Creation Flow

### Step-by-Step Process

```
1. User Registration (Frontend → Auth Service)
   POST /api/auth/register/
   Body: {
     email, first_name, last_name,
     phone_number, password1, password2
   }
   Response: {
     user data + JWT tokens
   }

2. Customer Profile Creation (Frontend → Customer Service)
   POST /api/v1/customers/profile/create/
   Headers: Authorization: Bearer <access_token>
   Body: {
     street_address, city, state,
     postal_code, country, company_name, ...
   }
   Response: {
     Complete customer profile including user data
   }
```

### Example Frontend Code

```javascript
// Complete registration flow
async function registerCustomer(userData, addressData) {
  try {
    // Step 1: Register user in auth service
    const authResponse = await fetch(
      "http://localhost:8001/api/auth/register/",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: userData.email,
          first_name: userData.firstName,
          last_name: userData.lastName,
          phone_number: userData.phone,
          password1: userData.password,
          password2: userData.password,
        }),
      }
    );

    if (!authResponse.ok) {
      throw new Error("User registration failed");
    }

    const authData = await authResponse.json();
    const accessToken = authData.tokens.access;

    // Step 2: Create customer profile
    const profileResponse = await fetch(
      "http://localhost:8002/api/v1/customers/profile/create/",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          street_address: addressData.street,
          city: addressData.city,
          state: addressData.state,
          postal_code: addressData.postalCode,
          country: addressData.country || "USA",
          company_name: addressData.companyName || "",
          emergency_contact_name: addressData.emergencyName || "",
          emergency_contact_phone: addressData.emergencyPhone || "",
          emergency_contact_relationship: addressData.emergencyRelation || "",
        }),
      }
    );

    if (!profileResponse.ok) {
      throw new Error("Customer profile creation failed");
    }

    const customerProfile = await profileResponse.json();

    return {
      success: true,
      tokens: authData.tokens,
      user: authData,
      profile: customerProfile,
    };
  } catch (error) {
    console.error("Registration error:", error);
    return { success: false, error: error.message };
  }
}
```

## API Comparison

### Creating a Customer

**OLD WAY** (❌ Duplicated data):

```json
POST /api/v1/customers/
{
  "user_id": 123,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, Portland, OR, 97201",
  "company_name": "Tech Corp"
}
```

**NEW WAY** (✅ Clean separation):

```json
// 1. Create user in auth service
POST /api/auth/register/
{
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "password1": "SecurePass123!",
  "password2": "SecurePass123!"
}

// 2. Create customer profile (with JWT token)
POST /api/v1/customers/profile/create/
Authorization: Bearer <token>
{
  "street_address": "123 Main St",
  "city": "Portland",
  "state": "Oregon",
  "postal_code": "97201",
  "country": "USA",
  "company_name": "Tech Corp"
}
```

### Updating Information

**Update User Credentials** → Auth Service:

```json
PATCH /api/auth/profile/update/
Authorization: Bearer <token>
{
  "first_name": "Jane",
  "email": "jane@example.com",
  "phone_number": "+1987654321"
}
```

**Update Customer Data** → Customer Service:

```json
PATCH /api/v1/customers/profile/update/
Authorization: Bearer <token>
{
  "street_address": "456 New Ave",
  "city": "Seattle",
  "company_name": "New Company LLC"
}
```

## Migration Checklist

### Before Migration

- [ ] Backup all databases
- [ ] Document current customer data structure
- [ ] Map old address fields to new structured fields
- [ ] Verify all user_ids have corresponding users in auth service
- [ ] Test migration scripts in development environment

### During Migration

- [ ] Stop both services
- [ ] Run database migrations for customer service
- [ ] Run data transformation script
- [ ] Verify data integrity
- [ ] Start services
- [ ] Test all endpoints

### After Migration

- [ ] Update frontend to use new API flow
- [ ] Update any scripts or integrations
- [ ] Monitor for errors
- [ ] Update documentation
- [ ] Train team on new architecture

## Testing Commands

```powershell
# 1. Register a new user
$userData = @{
    email = "newuser@test.com"
    first_name = "Test"
    last_name = "User"
    phone_number = "+15551234567"
    password1 = "TestPass123!"
    password2 = "TestPass123!"
} | ConvertTo-Json

$auth = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/register/" `
    -Method POST -Body $userData -ContentType "application/json"

$token = $auth.tokens.access

# 2. Create customer profile
$profileData = @{
    street_address = "123 Test Lane"
    city = "Portland"
    state = "Oregon"
    postal_code = "97201"
    country = "USA"
    company_name = "Test Company"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
}

$profile = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/profile/create/" `
    -Method POST -Body $profileData -Headers $headers -ContentType "application/json"

Write-Host "Profile Created:" -ForegroundColor Green
$profile | ConvertTo-Json -Depth 3

# 3. Get customer profile
$currentProfile = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/profile/" `
    -Method GET -Headers $headers

Write-Host "`nCurrent Profile:" -ForegroundColor Green
$currentProfile | ConvertTo-Json -Depth 3

# 4. Update customer profile
$updateData = @{
    street_address = "456 Updated Street"
    city = "Seattle"
} | ConvertTo-Json

$updated = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/profile/update/" `
    -Method PATCH -Body $updateData -Headers $headers -ContentType "application/json"

Write-Host "`nUpdated Profile:" -ForegroundColor Green
$updated | ConvertTo-Json -Depth 3

# 5. Check stats
$stats = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/stats/" `
    -Method GET -Headers $headers

Write-Host "`nCustomer Stats:" -ForegroundColor Green
$stats | ConvertTo-Json -Depth 3
```

## Benefits

### ✅ Single Source of Truth

- User credentials only in auth service
- No email/name/phone duplication

### ✅ Proper Microservice Architecture

- Clear service boundaries
- Independent scaling
- Focused responsibilities

### ✅ Better Data Structure

- Structured address fields
- Enhanced business customer support
- Service history tracking

### ✅ Improved Security

- Centralized authentication
- JWT-based authorization
- No password handling in customer service

### ✅ Easier Maintenance

- Changes in one place
- Reduced synchronization complexity
- Clear integration points

## Next Steps

1. **Review the changes** in each modified file
2. **Run migrations** in development environment
3. **Test thoroughly** with the provided test commands
4. **Update frontend** integration code
5. **Deploy** when confident

## Questions?

Refer to:

- `REFACTORING_GUIDE.md` - Detailed technical guide
- `models.py` - New data model
- `views.py` - API implementation
- `authentication.py` - JWT integration

The customer service is now properly architected as a microservice that focuses on customer-specific data while delegating user credential management to the authentication service.
