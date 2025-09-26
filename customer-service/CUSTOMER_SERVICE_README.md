# Customer Profile Management Service

This service handles comprehensive customer profile management for the ServEase automobile service platform.

## Features Implemented

### 1. Customer Model

- **Personal Information**: Name, email, phone, address details
- **Vehicle Ownership**: Related vehicles with full tracking
- **Service History**: Integration points for service tracking
- **Preferences**: Communication and service preferences
- **Business Support**: Business customer features
- **Emergency Contacts**: Safety and emergency contact information

### 2. Vehicle Management

- **Complete Vehicle Profiles**: Make, model, year, VIN, etc.
- **Service Tracking**: Mileage-based and date-based service scheduling
- **Insurance & Registration**: Document expiry tracking
- **Warranty Management**: Warranty status and expiration
- **Service Due Calculations**: Automatic service due notifications

### 3. Customer Preferences

- **Communication Preferences**: Email, SMS, push notifications
- **Service Preferences**: Preferred times and days
- **Language & Localization**: Multi-language support
- **Marketing Preferences**: Opt-in/out for marketing communications
- **Privacy Settings**: Data sharing and analytics consent

### 4. Document Management

- **File Storage**: Customer and vehicle document storage
- **Document Types**: Insurance, registration, service history, etc.
- **Expiry Tracking**: Automatic expiration notifications
- **Security**: Sensitive document handling

### 5. Customer Notes

- **Internal Notes**: Service team notes about customers
- **Note Types**: General, service, billing, complaints, etc.
- **Privacy Controls**: Private notes and importance flagging

## API Endpoints

### Customer Management

```
GET    /api/v1/customers/                    - List all customers
POST   /api/v1/customers/                    - Create new customer
GET    /api/v1/customers/{id}/               - Get customer details
PUT    /api/v1/customers/{id}/               - Update customer
PATCH  /api/v1/customers/{id}/               - Partial update customer
DELETE /api/v1/customers/{id}/               - Delete customer
```

### Customer Dashboard & Actions

```
GET    /api/v1/customers/{id}/dashboard/     - Customer dashboard data
GET    /api/v1/customers/{id}/preferences/   - Get customer preferences
PUT    /api/v1/customers/{id}/preferences/   - Update preferences
GET    /api/v1/customers/{id}/vehicles/      - Get customer vehicles
GET    /api/v1/customers/{id}/service-history/ - Get service history
GET    /api/v1/customers/{id}/documents/     - Get customer documents
POST   /api/v1/customers/{id}/verify/        - Verify customer
POST   /api/v1/customers/{id}/deactivate/    - Deactivate customer
GET    /api/v1/customers/stats/              - Customer statistics
```

### Vehicle Management

```
GET    /api/v1/vehicles/                     - List vehicles
POST   /api/v1/vehicles/                     - Create new vehicle
GET    /api/v1/vehicles/{id}/                - Get vehicle details
PUT    /api/v1/vehicles/{id}/                - Update vehicle
POST   /api/v1/vehicles/{id}/update-mileage/ - Update vehicle mileage
GET    /api/v1/vehicles/{id}/service-status/ - Get service status
```

### Document & Notes Management

```
GET    /api/v1/documents/                    - List documents
POST   /api/v1/documents/                    - Upload new document
GET    /api/v1/documents/expiring-soon/     - Get expiring documents
GET    /api/v1/notes/                        - List notes
POST   /api/v1/notes/                        - Create new note
```

## Database Models

### Customer

- Personal and contact information
- Business customer support
- Emergency contact details
- Status and verification tracking

### Vehicle

- Complete vehicle specifications
- Service tracking and scheduling
- Insurance and registration tracking
- Warranty management

### CustomerPreferences

- Communication preferences
- Service preferences
- Localization settings
- Privacy and marketing preferences

### CustomerDocument

- File storage and management
- Document categorization
- Expiry tracking
- Security features

### CustomerNote

- Internal notes system
- Note categorization
- Privacy controls
- Employee tracking

## Key Features

### 1. CRUD Operations

- Full Create, Read, Update, Delete operations for all models
- Comprehensive validation and error handling
- Optimized database queries with prefetch_related

### 2. Profile Dashboard

- Real-time customer dashboard with key information
- Vehicle status and service due notifications
- Recent documents and important notes
- Comprehensive customer overview

### 3. API Features

- RESTful API design
- Pagination, filtering, and searching
- Authentication and permission controls
- Comprehensive error handling
- API documentation and browsable interface

### 4. Data Validation

- Email and phone number validation
- VIN format validation
- Date and mileage validation
- Unique constraint handling

### 5. Integration Points

- Authentication service integration via user_id
- Vehicle service integration endpoints
- Notification service integration
- Employee service integration

## Installation & Setup

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**

   - Copy `.env` file and configure database settings
   - Set up PostgreSQL database: `servease_customers`

3. **Run Migrations**

   ```bash
   python manage.py makemigrations customers
   python manage.py migrate
   ```

4. **Create Superuser**

   ```bash
   python manage.py createsuperuser
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver 8002
   ```

## Configuration

### Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_ENGINE`: Database engine (postgresql)
- `CUSTOMER_DB_NAME`: Database name (servease_customers)
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`: Database connection
- CORS settings for frontend integration

### Django Settings

- REST Framework configuration
- CORS middleware setup
- File upload settings for documents
- Logging configuration
- Media file handling

## Testing

The service includes comprehensive tests:

- Model tests for all functionality
- API endpoint tests
- Data validation tests
- Integration tests

Run tests with:

```bash
python manage.py test customers
```

## Integration with Other Services

### Authentication Service

- Links customers to authentication via `user_id`
- Handles user authentication and authorization

### Vehicle & Project Service

- Service history integration
- Project tracking integration
- Service scheduling coordination

### Appointment Service

- Customer appointment booking
- Service scheduling integration

### Notification Service

- Customer communication preferences
- Service due notifications
- Document expiry alerts

### Employee Service

- Note creation tracking
- Service assignment integration

## Security Features

- Authentication required for all endpoints
- Data validation and sanitization
- Sensitive document handling
- Privacy preference enforcement
- Secure file upload handling

## Performance Optimizations

- Database query optimization
- Prefetch related data
- Efficient pagination
- Indexed database fields
- Optimized API responses

This customer service provides a solid foundation for customer profile management with comprehensive features, API endpoints, and integration capabilities for the ServEase automobile service platform.
