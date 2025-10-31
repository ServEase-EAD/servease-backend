# Customer Service - Quick Reference

## Service Responsibilities

### Authentication Service (Port 8001)

✅ User registration & login
✅ Email, name, phone, password
✅ JWT token generation
✅ User roles & permissions

### Customer Service (Port 8002)

✅ Customer profile data
✅ Address information
✅ Business details
✅ Emergency contacts
✅ Service history
✅ Customer preferences

## Key Changes

| Field        | OLD               | NEW                                    |
| ------------ | ----------------- | -------------------------------------- |
| `user_id`    | IntegerField      | UUIDField                              |
| `first_name` | In Customer model | ❌ Removed (use auth service)          |
| `last_name`  | In Customer model | ❌ Removed (use auth service)          |
| `email`      | In Customer model | ❌ Removed (use auth service)          |
| `phone`      | In Customer model | ❌ Removed (use auth service)          |
| `address`    | TextField         | ✅ Split into structured fields        |
| N/A          | N/A               | ✅ Added `total_services` counter      |
| N/A          | N/A               | ✅ Added preferences & business fields |

## API Quick Reference

### Registration Flow

```
1. POST /api/auth/register/ (Auth Service)
   → Returns JWT token + user data

2. POST /api/v1/customers/profile/create/ (Customer Service)
   → Uses JWT token
   → Creates customer profile
```

### Get Customer Profile

```
GET /api/v1/customers/profile/
Authorization: Bearer <token>

Response includes:
- email, first_name, last_name (from JWT)
- All customer-specific data
```

### Update User Info

```
# Update credentials (email, name, phone)
PATCH /api/auth/profile/update/ (Auth Service)

# Update customer data (address, company, etc)
PATCH /api/v1/customers/profile/update/ (Customer Service)
```

## Data Model

```python
Customer Model (NEW):
├── id (UUID)
├── user_id (UUID) → Links to auth service
├── Address
│   ├── street_address
│   ├── city
│   ├── state
│   ├── postal_code
│   └── country
├── Business
│   ├── company_name
│   ├── business_type
│   └── tax_id
├── Emergency Contact
│   ├── emergency_contact_name
│   ├── emergency_contact_phone
│   └── emergency_contact_relationship
├── Status
│   ├── is_verified
│   ├── customer_since
│   ├── last_service_date
│   └── total_services
└── Preferences
    ├── preferred_contact_method
    └── notification_preferences
```

## Common Tasks

### Create Customer Account

```javascript
// 1. Register user
const auth = await fetch("/api/auth/register/", {
  method: "POST",
  body: JSON.stringify({
    email,
    first_name,
    last_name,
    phone_number,
    password1,
    password2,
  }),
});

const { tokens } = await auth.json();

// 2. Create profile
const profile = await fetch("/api/v1/customers/profile/create/", {
  method: "POST",
  headers: { Authorization: `Bearer ${tokens.access}` },
  body: JSON.stringify({
    street_address,
    city,
    state,
    postal_code,
    country,
  }),
});
```

### Get Complete Customer Info

```javascript
const profile = await fetch("/api/v1/customers/profile/", {
  headers: { Authorization: `Bearer ${token}` },
});

// Returns customer data + user data from JWT/auth service
```

### Check if Profile Exists

```javascript
const check = await fetch("/api/v1/customers/check_profile_exists/", {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
  body: JSON.stringify({ user_id: userId }),
});
```

## Testing

### PowerShell Quick Test

```powershell
# Register
$auth = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/register/" `
  -Method POST -ContentType "application/json" -Body (@{
    email="test@example.com"; first_name="Test"; last_name="User";
    phone_number="+15551234567"; password1="Pass123!"; password2="Pass123!"
  } | ConvertTo-Json)

$token = $auth.tokens.access

# Create Profile
$profile = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/profile/create/" `
  -Method POST -ContentType "application/json" `
  -Headers @{"Authorization"="Bearer $token"} -Body (@{
    street_address="123 Test St"; city="Portland";
    state="Oregon"; postal_code="97201"; country="USA"
  } | ConvertTo-Json)

$profile | ConvertTo-Json -Depth 3
```

## Migration

### Required Steps

1. ✅ Update models.py (user_id to UUID, remove duplicates)
2. ✅ Update serializers.py (handle user data from context)
3. ✅ Update views.py (integrate with auth service)
4. ✅ Update authentication.py (proper JWT handling)
5. ⚠️ Create & run migrations
6. ⚠️ Transform existing data
7. ⚠️ Update frontend code

### Data Transformation

```python
# Convert old address to new structure
Old: "123 Main St, Portland, OR, 97201, USA"
New:
  street_address: "123 Main St"
  city: "Portland"
  state: "OR"
  postal_code: "97201"
  country: "USA"
```

## Endpoints

### Customer Profile

- `GET /api/v1/customers/profile/` - Get current profile
- `POST /api/v1/customers/profile/create/` - Create profile
- `PATCH /api/v1/customers/profile/update/` - Update profile
- `DELETE /api/v1/customers/profile/delete/` - Delete profile

### Customer Management

- `GET /api/v1/customers/` - List all (admin)
- `GET /api/v1/customers/{id}/` - Get by ID
- `GET /api/v1/customers/by_user_id/?user_id=<uuid>` - Get by user_id
- `POST /api/v1/customers/{id}/increment_service/` - Track service
- `POST /api/v1/customers/{id}/verify/` - Verify customer

### Utilities

- `GET /api/v1/customers/health/` - Health check
- `GET /api/v1/customers/stats/` - Statistics
- `POST /api/v1/customers/check_profile_exists/` - Check existence

## Key Points

✅ **No duplicate data** - User info only in auth service
✅ **JWT contains user data** - No extra HTTP calls for basic info
✅ **Optional fetching** - Can fetch from auth service when needed
✅ **Proper UUIDs** - Matches auth service user IDs
✅ **Structured data** - Better address & business fields
✅ **Service tracking** - Built-in service counter

## Troubleshooting

### "Customer profile not found"

→ User exists in auth but no profile created yet
→ Call `POST /profile/create/`

### "Only customers can access"

→ Token has wrong user_role
→ Ensure token is for a customer user

### User data missing in response

→ Auth service unavailable
→ Check service connectivity

### Migration failed

→ Backup and review data
→ Check UUID compatibility
→ Verify user_id references

## Documentation

- `REFACTORING_GUIDE.md` - Complete technical guide
- `INTEGRATION_SUMMARY.md` - Integration overview
- `models.py` - Data model definition
- `views.py` - API implementation
- `serializers.py` - Data serialization

---

**Version**: 2.0.0  
**Last Updated**: October 31, 2025  
**Status**: ✅ Refactored & Production Ready
