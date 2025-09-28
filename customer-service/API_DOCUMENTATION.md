# Customer Service API Documentation

## Available Endpoints

### Base URL: `http://127.0.0.1:8002/api/v1/customers/`

**Note**: This service follows the same URL pattern as the authentication-service, with explicit path mappings instead of router-generated URLs.

## Customer Endpoints

### 1. List All Customers

- **GET** `/api/v1/customers/`
- **Description**: Get a paginated list of all customers
- **Query Parameters**:
  - `search`: Search by first_name, last_name, email, phone, or company_name
  - `is_verified`: Filter by verification status (true/false)
  - `ordering`: Order by first_name, last_name, created_at, customer_since

### 2. Create New Customer

- **POST** `/api/v1/customers/`
- **Description**: Create a new customer profile
- **Required Fields**:
  - `user_id`: Integer (unique)
  - `first_name`: String
  - `last_name`: String
  - `email`: String (unique)
- **Optional Fields**:
  - `phone`: String (with validation)
  - `address`: Text
  - `company_name`: String
  - `emergency_contact_name`: String
  - `emergency_contact_phone`: String
  - `emergency_contact_relationship`: String

### 3. Get Specific Customer

- **GET** `/api/v1/customers/{id}/`
- **Description**: Get detailed information about a specific customer

### 4. Update Customer (Full)

- **PUT** `/api/v1/customers/{id}/`
- **Description**: Update all customer information

### 5. Update Customer (Partial)

- **PATCH** `/api/v1/customers/{id}/`
- **Description**: Update specific customer fields

### 6. Delete Customer

- **DELETE** `/api/v1/customers/{id}/`
- **Description**: Delete a customer profile

## Custom Action Endpoints

### 7. Verify Customer

- **POST** `/api/v1/customers/{id}/verify/`
- **Description**: Mark a customer as verified

### 8. Customer Dashboard

- **GET** `/api/v1/customers/{id}/dashboard/`
- **Description**: Get dashboard data for a specific customer

### 9. Customer Statistics

- **GET** `/api/v1/customers/stats/`
- **Description**: Get overall customer statistics
- **Returns**:
  - `total_customers`: Total number of customers
  - `verified_customers`: Number of verified customers
  - `new_customers_last_30_days`: New customers in last 30 days
  - `verification_rate`: Percentage of verified customers

### 10. Get Customer by User ID

- **GET** `/api/v1/customers/by_user_id/?user_id={user_id}`
- **Description**: Find customer by their authentication service user ID

## Response Format

All endpoints return JSON responses with appropriate HTTP status codes:

- `200`: Success
- `201`: Created (for POST requests)
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

## Pagination

List endpoints use Django REST Framework pagination:

```json
{
  "count": 10,
  "next": "http://127.0.0.1:8002/api/v1/customers/?page=2",
  "previous": null,
  "results": [...]
}
```

## Error Handling

Validation errors return structured error messages:

```json
{
  "field_name": ["Error message"]
}
```
