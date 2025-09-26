# Customer Service Development Guide

## Quick Start

### 1. Run Migrations

```bash
cd customer-service
python manage.py migrate --settings=customer_service.settings_local
```

### 2. Start Development Server

```bash
python manage.py runserver 8002 --settings=customer_service.settings_local
```

### 3. Test API Endpoints

Open: http://127.0.0.1:8002/api/v1/customers/
(Note: API requires authentication)

## Development Commands

### Run Tests

```bash
python manage.py test customers --settings=customer_service.settings_local
```

### Run Custom Test Script

```bash
python test_customer_service.py
```

### Create New Migrations

```bash
python manage.py makemigrations customers --settings=customer_service.settings_local
```

## API Endpoints Available

- **GET** `/api/v1/customers/` - List customers
- **POST** `/api/v1/customers/` - Create customer
- **GET** `/api/v1/customers/{id}/` - Get customer details
- **PUT/PATCH** `/api/v1/customers/{id}/` - Update customer
- **GET** `/api/v1/customers/{id}/dashboard/` - Dashboard data
- **GET** `/api/v1/customers/{id}/preferences/` - Get preferences
- **PUT** `/api/v1/customers/{id}/preferences/` - Update preferences
- **GET** `/api/v1/customers/stats/` - Customer statistics
- **GET** `/api/v1/vehicles/` - List vehicles
- **POST** `/api/v1/vehicles/` - Create vehicle

## Database Info

- **Development**: SQLite (db.sqlite3)
- **Production**: PostgreSQL (via Docker)
- **Local Settings**: `customer_service.settings_local`
- **Production Settings**: `customer_service.settings`

## Features Implemented

✅ Customer Profile Management  
✅ Vehicle Management  
✅ Preferences System  
✅ Document Storage  
✅ Customer Notes  
✅ Dashboard APIs  
✅ Authentication Integration  
✅ Comprehensive Testing
