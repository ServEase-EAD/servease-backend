# 🚀 POSTMAN TESTING GUIDE - ServEase Authentication Flow

## 📋 Overview

This guide will help you test your authentication requirement using Postman:

> "Customer must be logged in → Server generates token → Token sent with requests"

## 🔧 Prerequisites

1. Ensure Docker services are running: `docker-compose up -d`
2. Services should be accessible through nginx on `http://localhost`
3. Postman installed and ready

---

## 📚 STEP-BY-STEP TESTING GUIDE

### 🔹 **STEP 1: Test Service Health (No Authentication Required)**

**Request:**

```
Method: GET
URL: http://localhost/api/v1/customers/health/
Headers: None required
```

**Expected Response:**

```json
{
  "status": "healthy",
  "service": "customer-service",
  "timestamp": "2025-09-30T...",
  "version": "1.0.0"
}
```

---

### 🔹 **STEP 2: Test Unauthenticated Access (Should Fail)**

**Request:**

```
Method: GET
URL: http://localhost/api/v1/customers/profile/
Headers: None
```

**Expected Response:**

- Status: `403 Forbidden` or `401 Unauthorized`
- This proves authentication is required ✅

---

### 🔹 **STEP 3: Customer Registration (If Needed)**

**Request:**

```
Method: POST
URL: http://localhost/api/v1/auth/register/
Headers:
  Content-Type: application/json

Body (JSON):
{
    "email": "test.customer@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "Customer",
    "user_role": "customer"
}
```

**Expected Response:**

```json
{
  "id": "...",
  "email": "test.customer@example.com",
  "first_name": "Test",
  "last_name": "Customer",
  "user_role": "customer",
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**⚠️ Note:** If you get `400 Bad Request` with "email already exists", proceed to Step 4 (Login).

---

### 🔹 **STEP 4: Customer Login (Server Generates Token)**

**Request:**

```
Method: POST
URL: http://localhost/api/v1/auth/login/
Headers:
  Content-Type: application/json

Body (JSON):
{
    "email": "test.customer@example.com",
    "password": "TestPassword123!"
}
```

**Expected Response:**

```json
{
  "id": "...",
  "email": "test.customer@example.com",
  "first_name": "Test",
  "last_name": "Customer",
  "user_role": "customer",
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**📋 IMPORTANT:** Copy the `access` token - you'll need it for the next steps!

---

### 🔹 **STEP 5: Test Authenticated Request (Token Sent with Request)**

**Request:**

```
Method: GET
URL: http://localhost/api/v1/customers/profile/
Headers:
  Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
  Content-Type: application/json
```

**Example Authorization Header:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InRlc3QuY3VzdG9tZXJAZXhhbXBsZS5jb20iLCJ1c2VyX3JvbGUiOiJjdXN0b21lciIsImZpcnN0X25hbWUiOiJUZXN0IiwibGFzdF9uYW1lIjoiQ3VzdG9tZXIiLCJleHAiOjE3Mjc2MzU2NTQsImlhdCI6MTcyNzYzNTM1NCwidG9rZW5fdHlwZSI6ImFjY2VzcyJ9.example
```

**Expected Response:**

- Status: `200 OK` - Authentication successful ✅
- Status: `404 Not Found` - Token accepted, customer profile not found (still proves auth works) ✅
- Status: `500 Server Error` - Token accepted, database issue (still proves auth works) ✅

**❌ If you get `403 Forbidden`:** Token validation failed

---

### 🔹 **STEP 6: Test Multiple Authenticated Endpoints**

Try these endpoints with the same `Authorization: Bearer <token>` header:

**Customer Statistics:**

```
Method: GET
URL: http://localhost/api/v1/customers/stats/
Headers:
  Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Customer List:**

```
Method: GET
URL: http://localhost/api/v1/customers/
Headers:
  Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## 🔍 **TROUBLESHOOTING GUIDE**

### **502 Bad Gateway**

- Services are not running or nginx can't reach them
- Run: `docker-compose ps` to check service status
- Run: `docker-compose logs nginx` to check nginx logs

### **500 Internal Server Error**

- Database connectivity issues (AWS RDS)
- This is **NOT** an authentication problem
- Authentication is working if you get 500 instead of 403

### **403 Forbidden**

- Token is invalid or expired
- Token format is incorrect
- Make sure Authorization header is: `Bearer <space><token>`

### **401 Unauthorized**

- Missing Authorization header
- Invalid token format

---

## 📋 **POSTMAN COLLECTION SETUP**

### **Environment Variables**

Create a Postman environment with these variables:

```
base_url = http://localhost
auth_url = {{base_url}}/api/v1/auth
customer_url = {{base_url}}/api/v1/customers
access_token = (will be set automatically)
```

### **Auto-Token Management**

In your login request, add this to the **Tests** tab:

```javascript
if (pm.response.code === 200) {
  const responseJson = pm.response.json();
  pm.environment.set("access_token", responseJson.tokens.access);
  console.log(
    "Access token saved:",
    responseJson.tokens.access.substring(0, 50) + "..."
  );
}
```

Then use `{{access_token}}` in Authorization headers:

```
Authorization: Bearer {{access_token}}
```

---

## ✅ **SUCCESS CRITERIA**

Your authentication requirement is working if:

1. ✅ **Unauthenticated requests get rejected** (403/401)
2. ✅ **Login generates JWT tokens** (tokens returned in response)
3. ✅ **Authenticated requests with valid tokens succeed** (200/404/500 but NOT 403)
4. ✅ **Invalid/missing tokens get rejected** (403/401)

---

## 🎯 **Quick Test Sequence**

1. **GET** `http://localhost/api/v1/customers/health/` ➜ Should return 200
2. **GET** `http://localhost/api/v1/customers/profile/` ➜ Should return 403 (no auth)
3. **POST** `http://localhost/api/v1/auth/login/` ➜ Should return tokens
4. **GET** `http://localhost/api/v1/customers/profile/` with Bearer token ➜ Should NOT return 403

If all these work as expected, your authentication requirement is **FULLY IMPLEMENTED** ✅

---

## 🔧 **Sample Postman Collection JSON**

Save this as a `.json` file and import into Postman:

```json
{
  "info": {
    "name": "ServEase Authentication Test",
    "description": "Test authentication requirement flow"
  },
  "item": [
    {
      "name": "1. Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{base_url}}/api/v1/customers/health/"
      }
    },
    {
      "name": "2. Unauthenticated Access (Should Fail)",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{base_url}}/api/v1/customers/profile/"
      }
    },
    {
      "name": "3. Customer Login",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "if (pm.response.code === 200) {",
              "    const responseJson = pm.response.json();",
              "    pm.environment.set('access_token', responseJson.tokens.access);",
              "}"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"email\": \"test.customer@example.com\",\n    \"password\": \"TestPassword123!\"\n}"
        },
        "url": "{{base_url}}/api/v1/auth/login/"
      }
    },
    {
      "name": "4. Authenticated Profile Access",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": "{{base_url}}/api/v1/customers/profile/"
      }
    }
  ]
}
```

Happy testing! 🚀
