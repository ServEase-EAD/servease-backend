py# Chatbot Service - Authentication & Authorization Guide

## 🔐 Overview

The Chatbot Service uses **JWT (JSON Web Token)** authentication with **stateless validation**. This means:

- ✅ No database lookups for authentication
- ✅ Tokens are validated using the shared secret key
- ✅ All authenticated users (customer, employee, admin) can use the chatbot
- ✅ Users can **only** access their own chat sessions

---

## 🎯 Access Control Rules

### Who Can Access the Chatbot?

**✅ ALL authenticated users** regardless of role:

- Customers
- Employees
- Admins

### Resource Ownership Rules

**🔒 Strict Ownership Enforcement:**

- Users can **ONLY** create sessions for themselves
- Users can **ONLY** view their own sessions
- Users can **ONLY** clear their own sessions
- Users can **ONLY** delete their own sessions
- Attempting to access another user's session returns **404 Not Found**

---

## 📡 API Endpoints & Usage

### 1. **POST `/api/v1/chatbot/chat/` - Send Chat Message**

**Purpose:** Send a message and get AI response

**Authentication:** ✅ Required

**Request:**

```bash
curl -X POST http://localhost/api/v1/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "message": "How do I book a service appointment?",
    "model": "gemini-1.5-flash"
  }'
```

**Response (Success - 200):**

```json
{
  "session_id": "abc-123-456-...",
  "message": "To book a service appointment, you can...",
  "role": "assistant",
  "timestamp": "2024-11-06T10:30:00Z"
}
```

**Response (Unauthorized - 401):**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Response (Invalid Token - 401):**

```json
{
  "detail": "Invalid token"
}
```

---

### 2. **POST `/api/v1/chatbot/chat/` - Continue Conversation**

**Purpose:** Continue an existing conversation

**Authentication:** ✅ Required

**Request:**

```bash
curl -X POST http://localhost/api/v1/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "message": "What documents do I need?",
    "session_id": "abc-123-456-..."
  }'
```

**Response (Success - 200):**

```json
{
  "session_id": "abc-123-456-...",
  "message": "You'll need your vehicle registration...",
  "role": "assistant",
  "timestamp": "2024-11-06T10:31:00Z"
}
```

**Response (Access Denied - 404):**

```json
{
  "error": "Session not found or access denied",
  "message": "You can only access your own chat sessions"
}
```

---

### 3. **GET `/api/v1/chatbot/sessions/` - List My Sessions**

**Purpose:** Get all chat sessions for the authenticated user

**Authentication:** ✅ Required

**Request:**

```bash
curl -X GET http://localhost/api/v1/chatbot/sessions/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response (Success - 200):**

```json
{
  "count": 3,
  "results": [
    {
      "session_id": "abc-123-...",
      "user_id": 42,
      "created_at": "2024-11-06T10:00:00Z",
      "updated_at": "2024-11-06T10:30:00Z",
      "is_active": true,
      "message_count": 8,
      "messages": [...]
    },
    {
      "session_id": "def-456-...",
      "user_id": 42,
      "created_at": "2024-11-05T14:00:00Z",
      "updated_at": "2024-11-05T15:00:00Z",
      "is_active": true,
      "message_count": 12,
      "messages": [...]
    }
  ]
}
```

**Key Point:** Only returns sessions owned by the authenticated user.

---

### 4. **GET `/api/v1/chatbot/session/{session_id}/` - Get Session Details**

**Purpose:** Get full conversation history for a specific session

**Authentication:** ✅ Required

**Request:**

```bash
curl -X GET http://localhost/api/v1/chatbot/session/abc-123-456-.../ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response (Success - 200):**

```json
{
  "session_id": "abc-123-456-...",
  "user_id": 42,
  "created_at": "2024-11-06T10:00:00Z",
  "updated_at": "2024-11-06T10:30:00Z",
  "is_active": true,
  "messages": [
    {
      "role": "user",
      "content": "How do I book a service appointment?",
      "timestamp": "2024-11-06T10:00:15Z"
    },
    {
      "role": "assistant",
      "content": "To book a service appointment...",
      "timestamp": "2024-11-06T10:00:18Z"
    }
  ]
}
```

**Response (Access Denied - 404):**

```json
{
  "error": "Session not found or access denied",
  "message": "You can only access your own chat sessions"
}
```

---

### 5. **POST `/api/v1/chatbot/session/{session_id}/clear/` - Clear Messages**

**Purpose:** Delete all messages in a session (keeps session)

**Authentication:** ✅ Required

**Request:**

```bash
curl -X POST http://localhost/api/v1/chatbot/session/abc-123-456-.../clear/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response (Success - 200):**

```json
{
  "message": "Session cleared successfully",
  "session_id": "abc-123-456-..."
}
```

**Response (Access Denied - 404):**

```json
{
  "error": "Session not found or access denied",
  "message": "You can only clear your own chat sessions"
}
```

---

### 6. **DELETE `/api/v1/chatbot/session/{session_id}/delete/` - Delete Session**

**Purpose:** Soft-delete a session (marks as inactive)

**Authentication:** ✅ Required

**Request:**

```bash
curl -X DELETE http://localhost/api/v1/chatbot/session/abc-123-456-.../delete/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response (Success - 200):**

```json
{
  "message": "Session deleted successfully",
  "session_id": "abc-123-456-..."
}
```

**Response (Access Denied - 404):**

```json
{
  "error": "Session not found or access denied",
  "message": "You can only delete your own chat sessions"
}
```

---

## 🔒 JWT Token Structure

### Token Payload Example:

```json
{
  "user_id": 42,
  "email": "john.doe@example.com",
  "user_role": "customer",
  "exp": 1699876543,
  "iat": 1699872943
}
```

### Required Claims:

- `user_id` - Integer user ID (required)
- `email` - User email address (optional, for reference)
- `user_role` - Role: "customer", "employee", or "admin" (optional)
- `exp` - Token expiration timestamp
- `iat` - Token issued-at timestamp

---

## 🚀 Complete User Flow Example

### Step 1: User Logs In (via Authentication Service)

```bash
POST http://localhost/api/v1/auth/login/
Body: {
  "email": "customer@example.com",
  "password": "password123"
}

Response:
{
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 42,
    "email": "customer@example.com",
    "user_role": "customer"
  }
}
```

### Step 2: Frontend Stores Token

```javascript
localStorage.setItem("access_token", response.tokens.access);
```

### Step 3: User Starts Chat

```bash
POST http://localhost/api/v1/chatbot/chat/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Body: {
  "message": "Hello, I need help"
}

Response:
{
  "session_id": "abc-123-...",
  "message": "Hello! How can I assist you today?",
  "role": "assistant",
  "timestamp": "2024-11-06T10:00:00Z"
}
```

### Step 4: User Continues Conversation

```bash
POST http://localhost/api/v1/chatbot/chat/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Body: {
  "message": "I want to book a service",
  "session_id": "abc-123-..."
}

Response:
{
  "session_id": "abc-123-...",
  "message": "Great! Let me help you book a service...",
  "role": "assistant",
  "timestamp": "2024-11-06T10:01:00Z"
}
```

### Step 5: User Views Chat History

```bash
GET http://localhost/api/v1/chatbot/sessions/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response:
{
  "count": 1,
  "results": [
    {
      "session_id": "abc-123-...",
      "user_id": 42,
      "message_count": 4,
      "created_at": "2024-11-06T10:00:00Z",
      "is_active": true
    }
  ]
}
```

---

## 🛡️ Security Features

### ✅ Implemented Security Measures:

1. **JWT Token Validation**

   - Signature verification using shared secret
   - Expiration time checking
   - Algorithm validation (HS256)

2. **Stateless Authentication**

   - No database lookups
   - Fast validation
   - Scalable across multiple instances

3. **Resource Ownership Enforcement**

   - User ID extracted from JWT token
   - Database queries filtered by `user_id`
   - Prevents cross-user access

4. **CORS Protection**

   - Configured allowed origins
   - Credentials allowed for authenticated requests
   - Proper header handling

5. **Error Messages**
   - Generic "not found" for unauthorized access
   - Prevents information disclosure
   - No hints about existing resources

---

## ⚙️ Configuration

### Environment Variables Required:

```bash
# JWT Configuration (must match authentication service)
SECRET_KEY=your-super-secret-key-here
SIMPLE_JWT_SIGNING_KEY=your-super-secret-key-here

# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Database
CHATBOT_DB_NAME=servease_chatbot
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432
```

### Settings Configuration:

```python
# chatbot_service/settings.py

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'common.authentication.StatelessJWTAuthentication',
    ),
}

SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "USER_ID_FIELD": "user_id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

---

## 🧪 Testing Authentication

### Test 1: Without Token (Should Fail)

```bash
curl -X POST http://localhost/api/v1/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

Expected: 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

### Test 2: With Valid Token (Should Succeed)

```bash
curl -X POST http://localhost/api/v1/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <valid_token>" \
  -d '{"message": "Hello"}'

Expected: 200 OK
{
  "session_id": "...",
  "message": "...",
  "role": "assistant"
}
```

### Test 3: Access Another User's Session (Should Fail)

```bash
# User A's token trying to access User B's session
curl -X GET http://localhost/api/v1/chatbot/session/<user_b_session_id>/ \
  -H "Authorization: Bearer <user_a_token>"

Expected: 404 Not Found
{
  "error": "Session not found or access denied",
  "message": "You can only access your own chat sessions"
}
```

---

## 📊 Database Schema

### ChatSession Table:

```sql
CREATE TABLE chatbot_chatsession (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_user_active (user_id, is_active)
);
```

### ChatMessage Table:

```sql
CREATE TABLE chatbot_chatmessage (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES chatbot_chatsession(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    token_count INTEGER,
    INDEX idx_session_timestamp (session_id, timestamp)
);
```

---

## 🔧 Troubleshooting

### Issue: "Authentication credentials were not provided"

**Cause:** Token missing from request

**Solution:**

```bash
# Ensure Authorization header is present
Authorization: Bearer <your_token>
```

### Issue: "Invalid token"

**Causes:**

1. Token expired
2. Wrong secret key
3. Token format invalid

**Solutions:**

1. Get a new token (login again)
2. Verify `SECRET_KEY` matches authentication service
3. Check token format: `Bearer <token>`

### Issue: "Session not found or access denied"

**Cause:** Trying to access another user's session

**Solution:** Only use session IDs from your own sessions list

---

## 📈 Performance Considerations

### Optimizations Implemented:

1. **Database Indexes**

   - `user_id` + `created_at` for fast session listing
   - `user_id` + `is_active` for active session filtering
   - `session_id` + `timestamp` for message retrieval

2. **Stateless Authentication**

   - No DB lookup for user validation
   - JWT decoded and validated in memory
   - Fast authentication checks

3. **Efficient Queries**
   - Filtered by `user_id` at database level
   - Limited conversation history (last 10 messages)
   - Proper use of indexes

---

## 🎯 Summary

✅ **JWT-based stateless authentication**  
✅ **Role-agnostic access** (all authenticated users)  
✅ **Strict resource ownership** enforcement  
✅ **No cross-user access** possible  
✅ **Fast and scalable** authentication  
✅ **Secure token validation**

Your chatbot service is now fully secured with proper authentication and authorization! 🚀
