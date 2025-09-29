# ServEase Customer Authentication API Documentation

## Overview

This document describes the token-based authentication system for ServEase customers. The system uses JWT (JSON Web Tokens) for secure authentication and authorization.

## Authentication Flow

1. **Customer Registration/Login** → Authentication Service generates JWT tokens
2. **Token Storage** → Frontend stores tokens in localStorage
3. **API Requests** → Frontend includes JWT token in Authorization header
4. **Token Validation** → Services validate token and extract user information
5. **Automatic Refresh** → Frontend automatically refreshes expired tokens

## API Endpoints

### Authentication Service (`/api/v1/auth/`)

#### Customer Registration

```http
POST /api/v1/auth/register/
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "securepassword123",
    "phone_number": "+1234567890"
}
```

**Response:**

```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_role": "customer",
  "phone_number": "+1234567890",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "created_at": "2025-09-29T10:30:00Z"
}
```

#### Customer Login

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "john.doe@example.com",
    "password": "securepassword123"
}
```

**Response:**

```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_role": "customer",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Token Refresh

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Customer Logout

```http
POST /api/v1/auth/logout/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Get Current User Profile

```http
GET /api/v1/auth/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Customer Service (`/api/v1/customers/`)

All customer service endpoints require JWT authentication with `Authorization: Bearer <token>` header.

#### Get Customer Profile

```http
GET /api/v1/customers/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State 12345",
  "company_name": "Acme Corp",
  "is_verified": true,
  "customer_since": "2025-01-15T08:00:00Z",
  "last_service_date": "2025-09-15T14:30:00Z",
  "created_at": "2025-01-15T08:00:00Z",
  "updated_at": "2025-09-29T10:30:00Z"
}
```

#### Create Customer Profile

```http
POST /api/v1/customers/profile/create/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St, City, State 12345",
    "company_name": "Acme Corp",
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_phone": "+1234567891",
    "emergency_contact_relationship": "Spouse"
}
```

#### Update Customer Profile

```http
PATCH /api/v1/customers/profile/update/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "phone": "+1234567890",
    "address": "456 New St, City, State 12345",
    "company_name": "New Company Ltd"
}
```

## Frontend Integration

### Token Storage

Tokens are stored in browser's localStorage:

- `servease_access_token`: JWT access token (short-lived, 5 minutes)
- `servease_refresh_token`: JWT refresh token (long-lived, 1 day)
- `servease_user_data`: User profile information

### Making Authenticated Requests

```javascript
// Using the TokenManager utility
import tokenManager from "./TokenManager";

// Login
const loginResult = await tokenManager.login(email, password);

// Make authenticated request
const response = await tokenManager.authenticatedFetch(
  "/api/v1/customers/profile/"
);

// Get customer profile
const profileResult = await tokenManager.getCustomerProfile();

// Update customer profile
const updateResult = await tokenManager.updateCustomerProfile(data);
```

### Using React Authentication Context

```javascript
import { useAuth } from "./AuthContext";

function MyComponent() {
  const {
    user,
    isAuthenticated,
    login,
    logout,
    getCustomerProfile,
    updateCustomerProfile,
  } = useAuth();

  // Component logic
}
```

## Security Features

### JWT Token Configuration

- **Access Token Lifetime**: 5 minutes
- **Refresh Token Lifetime**: 1 day
- **Token Rotation**: Enabled (new refresh token on each refresh)
- **Blacklisting**: Tokens are blacklisted on logout
- **Algorithm**: HS256

### Request Headers

All authenticated requests must include:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Nginx Configuration

- Authorization headers are properly forwarded to backend services
- Rate limiting: 10 requests per second per IP
- Security headers included in responses

## Error Handling

### Authentication Errors

| Status Code | Error          | Description               |
| ----------- | -------------- | ------------------------- |
| 401         | `UNAUTHORIZED` | Invalid or expired token  |
| 403         | `FORBIDDEN`    | Insufficient permissions  |
| 400         | `BAD_REQUEST`  | Invalid login credentials |

### Example Error Response

```json
{
  "error": "Invalid token",
  "detail": "Given token not valid for any token type"
}
```

## Customer-Specific Features

### Permissions

- Customers can only access their own profile data
- User ID is extracted from JWT token for data filtering
- Cross-user access is automatically prevented

### Profile Management

- Automatic profile creation after registration
- Profile updates maintain data integrity
- Emergency contact information support

## Development Setup

### Environment Variables

```env
# Authentication Service
SECRET_KEY=your-secret-key
AUTH_SERVICE_URL=http://localhost:8001

# Customer Service
CUSTOMER_SERVICE_URL=http://localhost:8002
AUTH_SERVICE_URL=http://localhost:8001
```

### Required Dependencies

```python
# Customer Service requirements.txt
djangorestframework-simplejwt==5.3.0
requests==2.32.3
```

## Testing

### Test Customer Login

```bash
curl -X POST http://localhost/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'
```

### Test Authenticated Request

```bash
curl -X GET http://localhost/api/v1/customers/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Best Practices

### Frontend

1. Always store tokens securely in localStorage
2. Implement automatic token refresh
3. Handle authentication errors gracefully
4. Clear tokens on logout
5. Validate token expiration before requests

### Backend

1. Use short-lived access tokens
2. Implement token blacklisting
3. Validate user permissions on each request
4. Log authentication events
5. Use HTTPS in production

### Security

1. Never expose tokens in URLs or logs
2. Implement proper CORS configuration
3. Use secure, httpOnly cookies for sensitive data
4. Regularly rotate JWT signing keys
5. Monitor for suspicious authentication patterns
