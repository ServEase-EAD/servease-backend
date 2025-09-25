# ServEase Backend (Microservices Architecture)

This repository contains the backend implementation of the **ServEase** platform using **Django** with a **full microservice architecture**. Each service runs independently in Docker containers and communicates via REST APIs through an Nginx API Gateway.

---

## 🏗️ Architecture Overview

### Microservices
- **Authentication Service** (Port 8001) - User authentication and authorization
- **Customer Service** (Port 8002) - Customer management
- **Employee Service** (Port 8003) - Employee management
- **Vehicle & Project Service** (Port 8004) - Vehicle and project management
- **Appointment Service** (Port 8005) - Appointment scheduling
- **Notification Service** (Port 8006) - Notifications and messaging
- **User Service** (Port 8007) - User profile management
- **Chatbot Service** (Port 8008) - AI chatbot functionality

### Infrastructure Components
- **PostgreSQL** - Single instance with separate databases per service
- **Redis** - Shared caching and message broker
- **Nginx** - API Gateway and load balancer
- **Docker** - Containerization platform

### Database Architecture
Each microservice has its own isolated database:
- `authentication_service_db` - Authentication data
- `customer_service_db` - Customer data
- `employee_service_db` - Employee data  
- `vehicleandproject_service_db` - Vehicles and projects
- `appointment_service_db` - Appointment data
- `notification_service_db` - Notification data
- `user_service_db` - User profile data
- `chatbot_service_db` - Chat history and AI data

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed

### Start All Services
```bash
# Start all microservices
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f [service-name]
```

### Verify Installation
```bash
# Check API Gateway health
curl http://localhost/health

# Check individual service
curl http://localhost:8001/health/
```

---

## 🌐 API Endpoints

All services are accessible through the API Gateway at `http://localhost` with proper versioning:

### API v1 Endpoints
| Service | Endpoint | Description |
|---------|----------|-------------|
| Authentication | `/api/v1/auth/` | User login, logout, registration |
| Customer | `/api/v1/customers/` | Customer CRUD operations |
| Employee | `/api/v1/employees/` | Employee management |
| Vehicle | `/api/v1/vehicles/` | Vehicle management |
| Project | `/api/v1/projects/` | Project management |
| Appointment | `/api/v1/appointments/` | Appointment scheduling |
| Notification | `/api/v1/notifications/` | Push notifications |
| User | `/api/v1/users/` | User profile management |
| Chatbot | `/api/v1/chatbot/` | AI chatbot interactions |

### Direct Service Access (Development Only)
- Authentication: `http://localhost:8001`
- Customer: `http://localhost:8002`
- Employee: `http://localhost:8003`
- Vehicle & Project: `http://localhost:8004`
- Appointment: `http://localhost:8005`
- Notification: `http://localhost:8006`
- User: `http://localhost:8007`
- Chatbot: `http://localhost:8008`

---

## 🛠️ Development

### Project Structure
```
backend/
├── docker-compose.yml          # Service orchestration
├── .env.development           # Development environment
├── nginx/                     # API Gateway configuration
│   └── nginx.conf
├── URL_STRUCTURE_GUIDE.md     # API development guide
└── [service-name]/            # Individual microservices
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    └── [service-name]/
        ├── settings.py
        ├── urls.py
        └── ...
```

### Adding New Services
1. Create service directory with Django project
2. Add Dockerfile and requirements.txt
3. Update docker-compose.yml
4. Update nginx configuration
5. Add service routes to API Gateway
6. **Follow URL structure guide** in `URL_STRUCTURE_GUIDE.md`

### URL Structure
- All APIs use versioning: `/api/v1/`
- Follow REST conventions
- Consistent response formats
- See `URL_STRUCTURE_GUIDE.md` for detailed patterns and examples

### Environment Configuration
- Development: `.env.development`
- Copy to `.env` or set environment variables directly

---

## 🔧 Configuration

### Environment Variables
Key environment variables for each service:

```bash
# Database (Each service uses its own database)
DB_HOST=postgres
DB_USER=postgres
DB_PASSWORD=postgres_password

# Service-specific database names:
# authentication_service_db, customer_service_db, 
# employee_service_db, vehicleandproject_service_db,
# appointment_service_db, notification_service_db,
# user_service_db, chatbot_service_db

# Redis
REDIS_HOST=redis

# Service URLs (for inter-service communication)
AUTH_SERVICE_URL=http://authentication-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8002
# ... other service URLs
```

### Inter-Service Communication
Services communicate using:
- HTTP REST APIs
- Service discovery via Docker networking
- Environment variables for service URLs
- **Separate databases per service** for data isolation
- Redis for caching and real-time features

---

## 🔒 Security Features

- API Gateway with rate limiting
- CORS configuration
- Security headers (HSTS, XSS protection, etc.)
- Token-based authentication
- Input validation
- SQL injection protection
- CSRF protection

---

## 🤝 Contributing

1. Follow microservice principles
2. Each service should be independent
3. Use proper environment configurations
4. Follow URL structure guide
5. Test with Docker containers

---

**Note**: This is a complete microservice architecture foundation ready for your team to implement the specific business logic and APIs needed for the ServEase platform.

## � Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd servease/backend

# Run development setup
./scripts/setup-dev.sh
```

### 2. Start All Services
```bash
# Start in development mode (default)
./scripts/start.sh

# Or start in production mode
./scripts/start.sh production
```

### 3. Verify Installation
```bash
# Check service status
./scripts/manage.sh status

# Check API Gateway health
curl http://localhost/health
```

---

## 📊 Service Management

### Basic Commands
```bash
# View all services status
./scripts/manage.sh status

# View logs for all services
./scripts/manage.sh logs

# View logs for specific service
./scripts/manage.sh logs authentication-service

# Restart all services
./scripts/manage.sh restart

# Restart specific service
./scripts/manage.sh restart customer-service

# Stop all services
./scripts/stop.sh
```

### Database Operations
```bash
# Run migrations for all services
./scripts/manage.sh migrate

# Open shell in a service
./scripts/manage.sh shell authentication-service

# Execute custom commands
./scripts/manage.sh exec authentication-service python manage.py createsuperuser
```

### Scaling Services
```bash
# Scale authentication service to 3 instances
./scripts/manage.sh scale authentication-service 3
```

---

## 🌐 API Endpoints

All services are accessible through the API Gateway at `http://localhost` with proper versioning:

### API v1 Endpoints
| Service | Endpoint | Description |
|---------|----------|-------------|
| Authentication | `/api/v1/auth/` | User login, logout, registration |
| Customer | `/api/v1/customers/` | Customer CRUD operations |
| Employee | `/api/v1/employees/` | Employee management |
| Vehicle | `/api/v1/vehicles/` | Vehicle management |
| Project | `/api/v1/projects/` | Project management |
| Appointment | `/api/v1/appointments/` | Appointment scheduling |
| Notification | `/api/v1/notifications/` | Push notifications |
| User | `/api/v1/users/` | User profile management |
| Chatbot | `/api/v1/chatbot/` | AI chatbot interactions |

### Legacy Support
- Legacy endpoints without version (e.g., `/api/auth/`) automatically redirect to `/api/v1/`
- This ensures backward compatibility during migration

### Future Versioning
- Add new versions like `/api/v2/` as needed
- Maintain multiple versions simultaneously
- Gradual deprecation of older versions

### Direct Service Access (Development Only)
- Authentication: `http://localhost:8001`
- Customer: `http://localhost:8002`
- Employee: `http://localhost:8003`
- Vehicle & Project: `http://localhost:8004`
- Appointment: `http://localhost:8005`
- Notification: `http://localhost:8006`
- User: `http://localhost:8007`
- Chatbot: `http://localhost:8008`

---

## �️ Development

### Project Structure
```
backend/
├── docker-compose.yml          # Service orchestration
├── .env.development           # Development environment
├── .env.production           # Production environment
├── nginx/                    # API Gateway configuration
│   └── nginx.conf
├── scripts/                  # Management scripts
│   ├── start.sh
│   ├── stop.sh
│   ├── manage.sh
│   └── setup-dev.sh
└── [service-name]/           # Individual microservices
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    └── [service-name]/
        ├── settings.py
        ├── urls.py
        └── ...
```

### Adding New Services
1. Create service directory with Django project
2. Add Dockerfile and requirements.txt
3. Update docker-compose.yml
4. Update nginx configuration
5. Add service routes to API Gateway
6. **Follow URL structure guide** in `URL_STRUCTURE_GUIDE.md`

### URL Structure
- All APIs use versioning: `/api/v1/`
- Follow REST conventions
- Consistent response formats
- See `URL_STRUCTURE_GUIDE.md` for detailed patterns and examples

### Environment Configuration
- Development: `.env.development`
- Production: `.env.production` 
- Copy appropriate file to `.env` or use start script with environment parameter

---

## 🔧 Configuration

### Environment Variables
Key environment variables for each service:

```bash
# Database
DB_HOST=postgres
DB_NAME=servease_db
DB_USER=servease_user
DB_PASSWORD=servease_password

# Redis
REDIS_HOST=redis

# Service URLs (for inter-service communication)
AUTH_SERVICE_URL=http://authentication-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8002
# ... other service URLs

# Security
SECRET_KEY=your-secret-key
DEBUG=True  # False for production
```

### Inter-Service Communication
Services communicate using:
- HTTP REST APIs
- Service discovery via Docker networking
- Environment variables for service URLs
- Shared database for data consistency
- Redis for caching and real-time features

---

## 🚢 Production Deployment

### Environment Setup
1. Copy `.env.production` to `.env`
2. Update all production values:
   - Database credentials
   - Secret keys
   - Allowed hosts
   - SSL configuration

### Start Production Services
```bash
./scripts/start.sh production
```

### Production Checklist
- [ ] Update all secret keys
- [ ] Configure SSL certificates
- [ ] Set up proper database (PostgreSQL)
- [ ] Configure external Redis
- [ ] Update CORS and security settings
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies

---

## 🔒 Security Features

- API Gateway with rate limiting
- CORS configuration
- Security headers (HSTS, XSS protection, etc.)
- Token-based authentication
- Input validation
- SQL injection protection
- CSRF protection

---

## 📈 Monitoring and Logging

### View Logs
```bash
# All services
./scripts/manage.sh logs

# Specific service
./scripts/manage.sh logs authentication-service

# Follow logs in real-time
docker-compose logs -f authentication-service
```

### Health Checks
- API Gateway health: `http://localhost/health`
- Individual service health: Built into Docker Compose
- Database connectivity: Automatic health checks

---

## 🧹 Maintenance

### Cleanup
```bash
# Remove unused containers, networks, volumes
./scripts/manage.sh cleanup

# Complete cleanup (removes data)
docker-compose down -v --rmi all
```

### Backup
```bash
# Database backup
docker-compose exec postgres pg_dump -U servease_user servease_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U servease_user servease_db < backup.sql
```

---

## 🤝 Contributing

1. Follow microservice principles
2. Each service should be independent
3. Use proper environment configurations
4. Update documentation for new features
5. Test with Docker containers

---

## 📞 Support

For issues or questions:
1. Check service logs: `./scripts/manage.sh logs [service]`
2. Verify service status: `./scripts/manage.sh status`
3. Check API Gateway health: `curl http://localhost/health`

---

**Note**: This is a complete microservice architecture foundation. Each service is ready for your team to implement the specific business logic and APIs needed for the ServEase platform.