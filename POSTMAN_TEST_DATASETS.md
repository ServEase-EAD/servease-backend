# ServEase JWT Authentication - Postman Test Datasets
# ===================================================

## 1. USER REGISTRATION
### Endpoint: POST http://localhost:8001/api/v1/auth/register/

### Test Case 1: Valid Customer Registration
```json
{
  "email": "customer1@servease.com",
  "password1": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "1234567890"
}
```

### Test Case 2: Another Valid Customer
```json
{
  "email": "alice.smith@servease.com",
  "password1": "MyPassword456!",
  "password2": "MyPassword456!",
  "first_name": "Alice",
  "last_name": "Smith",
  "phone_number": "9876543210"
}
```

### Test Case 3: Password Mismatch (Should Fail)
```json
{
  "email": "test.fail@servease.com",
  "password1": "Password123!",
  "password2": "DifferentPass456!",
  "first_name": "Test",
  "last_name": "User",
  "phone_number": "1111111111"
}
```

### Test Case 4: Weak Password (Should Fail)
```json
{
  "email": "weak.password@servease.com",
  "password1": "123",
  "password2": "123",
  "first_name": "Weak",
  "last_name": "Password",
  "phone_number": "2222222222"
}
```

### Test Case 5: Invalid Email Format (Should Fail)
```json
{
  "email": "invalid-email-format",
  "password1": "ValidPass123!",
  "password2": "ValidPass123!",
  "first_name": "Invalid",
  "last_name": "Email",
  "phone_number": "3333333333"
}
```

---

## 2. USER LOGIN
### Endpoint: POST http://localhost:8001/api/v1/auth/login/

### Test Case 1: Valid Login (Use after Registration)
```json
{
  "email": "customer1@servease.com",
  "password": "SecurePass123!"
}
```

### Test Case 2: Valid Login - Second User
```json
{
  "email": "alice.smith@servease.com",
  "password": "MyPassword456!"
}
```

### Test Case 3: Invalid Password (Should Fail)
```json
{
  "email": "customer1@servease.com",
  "password": "WrongPassword123!"
}
```

### Test Case 4: Non-existent User (Should Fail)
```json
{
  "email": "nonexistent@servease.com",
  "password": "AnyPassword123!"
}
```

### Test Case 5: Empty Credentials (Should Fail)
```json
{
  "email": "",
  "password": ""
}
```

---

## 3. PROTECTED ENDPOINT WITHOUT TOKEN (Should Fail)
### Endpoint: GET http://localhost:8002/api/v1/customers/
### Headers: (No Authorization header)
### Body: (Empty)
### Expected Response: 403 Forbidden

---

## 4. PROTECTED ENDPOINT WITH TOKEN
### Endpoint: GET http://localhost:8002/api/v1/customers/
### Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```
### Body: (Empty)
### Expected Response: 200 OK

---

## 5. TOKEN VALIDATION
### Endpoint: POST http://localhost:8001/api/v1/auth/validate-token/

### Test Case 1: Valid Token
```json
{
  "token": "YOUR_ACCESS_TOKEN_HERE"
}
```

### Test Case 2: Invalid Token (Should Fail)
```json
{
  "token": "invalid.token.here"
}
```

### Test Case 3: Expired Token (Should Fail)
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### Test Case 4: Empty Token (Should Fail)
```json
{
  "token": ""
}
```

---

## 6. USER PROFILE
### Endpoint: GET http://localhost:8001/api/v1/auth/profile/
### Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```
### Body: (Empty)

---

## 7. TOKEN REFRESH
### Endpoint: POST http://localhost:8001/api/v1/auth/token/refresh/

### Test Case 1: Valid Refresh Token
```json
{
  "refresh": "YOUR_REFRESH_TOKEN_HERE"
}
```

### Test Case 2: Invalid Refresh Token (Should Fail)
```json
{
  "refresh": "invalid.refresh.token.here"
}
```

### Test Case 3: Empty Refresh Token (Should Fail)
```json
{
  "refresh": ""
}
```

---

## 8. USER LOGOUT
### Endpoint: POST http://localhost:8001/api/v1/auth/logout/
### Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

### Test Case 1: Valid Logout
```json
{
  "refresh": "YOUR_REFRESH_TOKEN_HERE"
}
```

---

## ADDITIONAL TEST SCENARIOS

### 9. CUSTOMER SERVICE ENDPOINTS
### Endpoint: GET http://localhost:8002/api/v1/customers/
### Various scenarios to test with valid tokens

---

## 10. ADMIN ENDPOINTS (If available)
### Endpoint: GET http://localhost:8001/api/v1/auth/admin/dashboard/stats/
### Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

---

# POSTMAN ENVIRONMENT VARIABLES
# =============================

Set up these environment variables in Postman:

- `base_auth_url`: http://localhost:8001/api/v1/auth
- `base_customer_url`: http://localhost:8002/api/v1/customers
- `access_token`: (will be set automatically after login)
- `refresh_token`: (will be set automatically after login)

# POSTMAN TESTS SCRIPTS
# ======================

## For Login Request - Add this to "Tests" tab:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has tokens", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.tokens).to.exist;
    pm.expect(jsonData.tokens.access).to.exist;
    pm.expect(jsonData.tokens.refresh).to.exist;
    
    // Save tokens to environment
    pm.environment.set("access_token", jsonData.tokens.access);
    pm.environment.set("refresh_token", jsonData.tokens.refresh);
});

pm.test("Response has user data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.email).to.exist;
    pm.expect(jsonData.first_name).to.exist;
    pm.expect(jsonData.last_name).to.exist;
});
```

## For Protected Endpoints - Add this to "Tests" tab:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Authentication successful", function () {
    pm.expect(pm.response.code).to.not.equal(403);
    pm.expect(pm.response.code).to.not.equal(401);
});
```

## For Token Refresh - Add this to "Tests" tab:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("New access token received", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.access).to.exist;
    
    // Update access token
    pm.environment.set("access_token", jsonData.access);
});
```

# TESTING WORKFLOW
# ================

1. **Setup Environment**: Create environment variables
2. **Register User**: Use valid registration data
3. **Login**: Use same credentials, save tokens automatically
4. **Test Protected Access**: Without token (should fail)
5. **Test Protected Access**: With token (should work)
6. **Validate Token**: Test token validation endpoint
7. **Get Profile**: Test profile endpoint
8. **Refresh Token**: Test token refresh
9. **Test Edge Cases**: Invalid tokens, expired tokens, etc.
10. **Logout**: Test logout functionality

# EXPECTED RESPONSES
# ==================

## Successful Registration (201):
```json
{
  "id": 1,
  "email": "customer1@servease.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "1234567890",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user_role": "customer"
}
```

## Successful Login (200):
```json
{
  "id": 1,
  "email": "customer1@servease.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_role": "customer",
  "phone_number": "1234567890",
  "created_at": "2025-09-30T01:00:00Z",
  "is_active": true,
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

## Authentication Error (403):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Invalid Credentials (400):
```json
{
  "non_field_errors": ["Incorrect Credentials"]
}
```