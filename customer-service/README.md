# ServEase Customer Service

A Django REST API microservice for managing customer profiles and data in the ServEase platform.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Database Setup](#database-setup)
- [Running the Service](#running-the-service)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Development Workflow](#development-workflow)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

The Customer Service is part of the ServEase microservices architecture that handles:

- Customer profile management (CRUD operations)
- Customer verification system
- Dashboard analytics and statistics
- Integration with authentication service via `user_id`
- PostgreSQL database with proper indexing for performance

**Key Features:**

- RESTful API with Django REST Framework
- PostgreSQL database (no SQLite)
- UUID-based primary keys for security
- Comprehensive validation and error handling
- Docker containerization
- CORS enabled for frontend integration

## 🛠 Prerequisites

Before setting up the customer service, ensure you have:

### Required Software

- **Python 3.11+** (Check: `python --version`)
- **Docker & Docker Compose** (Check: `docker --version`)
- **Git** (Check: `git --version`)
- **PostgreSQL client** (optional, for direct DB access)

### System Requirements

- Windows 10/11 (PowerShell 5.1+)
- 4GB+ RAM
- 2GB+ free disk space

## 🚀 Project Setup

### Step 1: Clone the Repository

```powershell
git clone https://github.com/ServEase-EAD/servease-backend.git
cd servease-backend
git checkout Customer-Hashan  # Switch to customer service branch
```

### Step 2: Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DB_HOST=postgres
DB_USER=postgres
DB_PASSWORD=postgres_password
DB_PORT=5432

# Service-specific databases
AUTH_DB_NAME=servease_auth
CUSTOMER_DB_NAME=servease_customers
EMPLOYEE_DB_NAME=servease_employees
VEHICLE_DB_NAME=servease_vehicles
APPOINTMENT_DB_NAME=servease_appointments
NOTIFICATION_DB_NAME=servease_notifications
CHATBOT_DB_NAME=servease_chatbot

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# PgAdmin Configuration
PGADMIN_DEFAULT_EMAIL=admin@servease.com
PGADMIN_DEFAULT_PASSWORD=admin123
PGADMIN_PORT=5050

# Service URLs
AUTH_SERVICE_URL=http://authentication-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8002

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=True
```

### Step 3: Verify Docker Setup

```powershell
# Verify Docker and Docker Compose are working
docker --version
docker-compose --version

# Test Docker connection
docker run hello-world
```

## 🗄 Database Setup

### Step 1: Start All Services with Docker

```powershell
# From the root project directory
docker-compose up -d
```

This will start all services including PostgreSQL, Redis, PgAdmin, and all microservices.

### Step 2: Verify Database Connection

```powershell
# Check if PostgreSQL is running
docker ps | findstr postgres

# Access PgAdmin (optional)
# Navigate to http://localhost:5050
# Email: admin@servease.com
# Password: admin123
```

### Step 3: Run Database Migrations

```powershell
# All services should already be running from Step 1
# Check if customer service is ready
docker-compose logs customer-service

# Check for migration issues
docker-compose exec customer-service python manage.py check

# Create migrations (if needed)
docker-compose exec customer-service python manage.py makemigrations

# Apply migrations
docker-compose exec customer-service python manage.py migrate
```

Expected output:

```
Operations to perform:
  Apply all migrations: customer_service
Running migrations:
  Applying customer_service.0001_initial... OK
```

## 🏃 Running the Service

### Docker (Standard Development Environment)

```powershell
# Start all services (recommended)
docker-compose up -d

# View customer service logs
docker-compose logs -f customer-service

# Access service at: http://localhost:8002
```

**Note:** The `docker-compose up -d` command starts all services defined in docker-compose.yml including PostgreSQL, Redis, PgAdmin, and all microservices.

### Verify Service is Running

```powershell
# Test health endpoint
curl http://localhost:8002/api/v1/customers/stats/
```

Expected response:

```json
{
  "total_customers": 0,
  "verified_customers": 0,
  "new_customers_last_30_days": 0,
  "verification_rate": 0
}
```

## 📚 API Endpoints

### Base URL

- Local Development: `http://localhost:8002/api/v1/customers/`
- Docker: `http://localhost:8002/api/v1/customers/`

### Available Endpoints

| Method | Endpoint                   | Description                    | Auth Required |
| ------ | -------------------------- | ------------------------------ | ------------- |
| GET    | `/`                        | List all customers (paginated) | No\*          |
| POST   | `/`                        | Create new customer            | No\*          |
| GET    | `/{id}/`                   | Get customer by UUID           | No\*          |
| PUT    | `/{id}/`                   | Update customer (full)         | No\*          |
| PATCH  | `/{id}/`                   | Update customer (partial)      | No\*          |
| DELETE | `/{id}/`                   | Delete customer                | No\*          |
| GET    | `/{id}/dashboard/`         | Get customer dashboard data    | No\*          |
| POST   | `/{id}/verify/`            | Mark customer as verified      | No\*          |
| GET    | `/stats/`                  | Get customer statistics        | No\*          |
| GET    | `/by_user_id/?user_id=123` | Get customer by user_id        | No\*          |

\*Authentication is disabled for development. Enable `IsAuthenticated` in production.

### Query Parameters for Listing

- `?is_verified=true` - Filter by verification status
- `?search=john` - Search by name, email, phone
- `?ordering=first_name` - Order by field
- `?page=2` - Pagination

## 🧪 Testing

### Test Dataset for POST Operations

Use this dataset to test customer creation:

```json
{
  "user_id": 12345,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "address": "123 Main Street, Springfield, IL, 62701, USA",
  "company_name": "Tech Solutions Inc",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+0987654321",
  "emergency_contact_relationship": "Spouse"
}
```

```json
{
  "user_id": 12346,
  "first_name": "Sarah",
  "last_name": "Johnson",
  "email": "sarah.johnson@example.com",
  "phone": "+1555123456",
  "address": "456 Oak Avenue, Portland, OR, 97201, USA",
  "company_name": "",
  "emergency_contact_name": "Mike Johnson",
  "emergency_contact_phone": "+1555987654",
  "emergency_contact_relationship": "Brother"
}
```

```json
{
  "user_id": 12347,
  "first_name": "Carlos",
  "last_name": "Rodriguez",
  "email": "carlos.rodriguez@example.com",
  "phone": "+1777888999",
  "address": "789 Pine Road, Austin, TX, 73301, USA",
  "company_name": "Rodriguez Auto Repair",
  "emergency_contact_name": "Maria Rodriguez",
  "emergency_contact_phone": "+1777111222",
  "emergency_contact_relationship": "Wife"
}
```

### PowerShell Testing Commands

#### 1. Create Customer (POST)

```powershell
$customer = @{
  user_id = 12345
  first_name = "John"
  last_name = "Doe"
  email = "john.doe@example.com"
  phone = "+1234567890"
  address = "123 Main Street, Springfield, IL, 62701, USA"
  company_name = "Tech Solutions Inc"
  emergency_contact_name = "Jane Doe"
  emergency_contact_phone = "+0987654321"
  emergency_contact_relationship = "Spouse"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/" -Method POST -Body $customer -ContentType "application/json"
$result | ConvertTo-Json -Depth 3
```

#### 2. Get All Customers (GET)

```powershell
$result = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/" -Method GET -ContentType "application/json"
$result | ConvertTo-Json -Depth 3
```

#### 3. Get Customer by ID (GET)

```powershell
# Use the UUID from the previous POST response
$customerId = "your-uuid-here"
$result = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/$customerId/" -Method GET -ContentType "application/json"
$result | ConvertTo-Json -Depth 2
```

#### 4. Get Customer by User ID (GET)

```powershell
$result = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/by_user_id/?user_id=12345" -Method GET -ContentType "application/json"
$result | ConvertTo-Json -Depth 2
```

#### 5. Update Customer (PATCH)

```powershell
$update = @{
  phone = "+1999888777"
  address = "Updated Address, New City, CA, 90210, USA"
} | ConvertTo-Json

$customerId = "your-uuid-here"
$result = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/$customerId/" -Method PATCH -Body $update -ContentType "application/json"
$result | ConvertTo-Json -Depth 2
```

#### 6. Verify Customer (POST)

```powershell
$customerId = "your-uuid-here"
$result = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/$customerId/verify/" -Method POST -ContentType "application/json"
$result | ConvertTo-Json -Depth 2
```

#### 7. Get Statistics (GET)

```powershell
$result = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/stats/" -Method GET -ContentType "application/json"
$result | ConvertTo-Json -Depth 2
```

#### 8. Search Customers (GET)

```powershell
$result = Invoke-RestMethod -Uri "http://localhost:8002/api/v1/customers/?search=john" -Method GET -ContentType "application/json"
$result | ConvertTo-Json -Depth 3
```

## 🔄 Development Workflow

### Daily Development Process

1. **Start Services**

   ```powershell
   # Start all services at once (recommended)
   docker-compose up -d

   # Or if you need to restart just the customer service
   docker-compose restart customer-service
   ```

2. **Make Changes**

   - Edit models in `customer_service/models.py`
   - Update views in `customer_service/views.py`
   - Modify serializers in `customer_service/serializers.py`

3. **Update Database**

   ```powershell
   # Access container to run migrations
   docker-compose exec customer-service python manage.py makemigrations
   docker-compose exec customer-service python manage.py migrate
   ```

4. **Test Changes**

   ```powershell
   # Check for issues within container
   docker-compose exec customer-service python manage.py check

   # Run your PowerShell test commands against http://localhost:8002
   ```

5. **View Logs**

   ```powershell
   # Monitor service logs
   docker-compose logs -f customer-service

   # View all services logs
   docker-compose logs -f
   ```

### Code Quality Checks

```powershell
# Check for issues within container
docker-compose exec customer-service python manage.py check

# Validate migrations
docker-compose exec customer-service python manage.py showmigrations

# Test database connection
docker-compose exec customer-service python manage.py dbshell
```

## 🏗 Architecture

### Project Structure

```
customer-service/
├── customer_service/           # Main Django app
│   ├── __init__.py
│   ├── models.py              # Customer model
│   ├── views.py               # API viewsets
│   ├── serializers.py         # DRF serializers
│   ├── urls.py                # URL routing
│   ├── settings.py            # Production settings
│   ├── settings_local.py      # Development settings
│   ├── wsgi.py                # WSGI config
│   └── asgi.py                # ASGI config
├── migrations/                # Database migrations
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management
├── Dockerfile                 # Container config
└── README.md                  # This file
```

### Model Schema

```python
Customer:
- id (UUID, Primary Key)
- user_id (Integer, Unique, Links to Auth Service)
- first_name (CharField)
- last_name (CharField)
- email (EmailField, Unique)
- phone (CharField with validation)
- address (TextField)
- is_verified (BooleanField)
- customer_since (DateTimeField)
- company_name (CharField, Optional)
- emergency_contact_* (CharField fields)
- created_at/updated_at (DateTimeField)
- last_service_date (DateTimeField, Optional)
```

### Database Indexes

- `user_id` (unique index for fast lookups)
- `email` (unique index)
- `phone` (index for search)
- `last_name, first_name` (composite index for name searches)

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. PostgreSQL Connection Error

```
django.db.utils.OperationalError: could not connect to server
```

**Solution:**

```powershell
# Check if PostgreSQL is running
docker ps | findstr postgres

# Start PostgreSQL if not running
docker-compose up -d postgres

# Wait 30 seconds for startup, then retry
```

#### 2. Migration Conflicts

```
django.db.utils.IntegrityError: duplicate key value
```

**Solution:**

```powershell
# Reset migrations (development only!)
docker-compose exec customer-service python manage.py migrate customer_service zero
docker-compose exec customer-service python manage.py migrate
```

#### 3. Permission Denied on Windows

```
PermissionError: [WinError 5] Access is denied
```

**Solution:**

```powershell
# Run PowerShell as Administrator
# Or change directory permissions:
icacls "D:\Application files - Do not delete\github\servease-backend" /grant Users:F /t

# Restart Docker containers
docker-compose down
docker-compose up -d
```

#### 4. Port Already in Use

```
OSError: [WinError 10048] Only one usage of each socket address
```

**Solution:**

```powershell
# Find process using port 8002
netstat -ano | findstr :8002

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Restart the service
docker-compose restart customer-service
```

#### 5. Missing Dependencies

```
ModuleNotFoundError: No module named 'rest_framework'
```

**Solution:**

```powershell
# Rebuild the container with fresh dependencies
docker-compose build customer-service
docker-compose up -d customer-service
```

### Debugging Tips

1. **Enable Detailed Logging**

   ```powershell
   # View container logs with timestamps
   docker-compose logs -f --timestamps customer-service
   ```

2. **Check Database State**

   ```powershell
   # Access database through container
   docker-compose exec customer-service python manage.py dbshell
   \dt  # List tables
   SELECT * FROM customers LIMIT 5;
   ```

3. **Access Container Shell**

   ```powershell
   # Get shell access to container
   docker-compose exec customer-service /bin/bash

   # Or run commands directly
   docker-compose exec customer-service python manage.py shell
   ```

4. **Validate API Responses**
   ```powershell
   # Check API browser (service must be running)
   # Navigate to: http://localhost:8002/api/v1/customers/
   ```

### Environment Variables Reference

| Variable           | Description         | Default              | Required |
| ------------------ | ------------------- | -------------------- | -------- |
| `DB_HOST`          | PostgreSQL host     | `postgres`           | Yes      |
| `DB_USER`          | PostgreSQL user     | `postgres`           | Yes      |
| `DB_PASSWORD`      | PostgreSQL password | -                    | Yes      |
| `CUSTOMER_DB_NAME` | Database name       | `servease_customers` | Yes      |
| `DEBUG`            | Django debug mode   | `True`               | No       |
| `SECRET_KEY`       | Django secret key   | -                    | Yes      |
| `ALLOWED_HOSTS`    | Allowed hosts       | `*`                  | No       |

## 📞 Support

For development support:

- **Repository**: https://github.com/ServEase-EAD/servease-backend
- **Branch**: Customer-Hashan
- **Documentation**: Check this README and inline code comments
- **API Browser**: http://localhost:8002/api/v1/customers/ (when service is running)

## 📄 License

This project is part of the ServEase platform. Check the main repository for license information.

---

**Happy Coding! 🚀**

_Last Updated: September 27, 2025_
