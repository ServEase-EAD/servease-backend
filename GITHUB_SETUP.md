# GitHub Setup Guide for ServEase Microservices

This guide helps you set up the ServEase microservices architecture from GitHub.

## 📋 Prerequisites

Before you begin, make sure you have:

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- [Git](https://git-scm.com/downloads) installed

## 🚀 Quick Setup (3 Steps)

### 1. Clone and Navigate

```bash
git clone <your-github-repo-url>
cd servease/backend
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Open .env in your preferred editor
# Update these required values:
# - SECRET_KEY=your-unique-django-secret-key-here
# - DB_PASSWORD=your-secure-database-password
```

**🔐 Important**: Never commit your actual `.env` file to Git! It's already in `.gitignore`.

### 3. Start All Services

```bash
# Build and start all microservices
docker-compose up -d

# Verify everything is running
docker-compose ps
```

## ✅ Verify Your Setup

### Test API Gateway

```bash
curl http://localhost/health
# Expected: "healthy"
```

### Test Authentication Service

```bash
curl http://localhost:8001/health/
# Expected: {"status": "healthy", "service": "authentication-service"}
```

### View All Services

```bash
docker-compose ps
# All services should show "Up" status
```

## 📁 What You Get

After setup, you'll have these services running:

| Service              | URL                   | Purpose                      |
| -------------------- | --------------------- | ---------------------------- |
| API Gateway          | http://localhost      | Routes all API requests      |
| Auth Service         | http://localhost:8001 | User authentication          |
| Customer Service     | http://localhost:8002 | Customer management          |
| Employee Service     | http://localhost:8003 | Employee management          |
| Vehicle Service      | http://localhost:8004 | Vehicle & project management |
| Appointment Service  | http://localhost:8005 | Appointment scheduling       |
| Notification Service | http://localhost:8006 | Notifications                |
| Chatbot Service      | http://localhost:8008 | AI chatbot functionality     |
| pgAdmin (DB GUI)     | http://localhost:5050 | Database management GUI      |

Plus infrastructure:

- **PostgreSQL** database (with separate databases per service)
- **Redis** for caching and messaging
- **Nginx** API Gateway with rate limiting
- **pgAdmin** for visual database management

## 🎯 API Endpoints

All APIs are accessed through the gateway with versioning:

```bash
# Health check
GET http://localhost/health

# Authentication APIs
POST http://localhost/api/v1/auth/login/
POST http://localhost/api/v1/auth/register/

# Customer APIs
GET http://localhost/api/v1/customers/
POST http://localhost/api/v1/customers/

# And so on for other services...
```

## 🛠️ Development Commands

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs authentication-service

# Follow logs in real-time
docker-compose logs -f authentication-service
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart authentication-service
```

### Stop Services

```bash
docker-compose down
```

### Clean Reset

```bash
# Stop and remove everything
docker-compose down --volumes --remove-orphans
docker system prune -f

# Start fresh
docker-compose up -d
```

## 🔧 Configuration Details

### Environment Variables (.env)

The `.env` file contains all configuration. Key sections:

```bash
# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=*

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_HOST=postgres
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_PORT=5432

# Individual Service Databases (automatically created)
AUTH_DB_NAME=authentication_service_db
CUSTOMER_DB_NAME=customer_service_db
EMPLOYEE_DB_NAME=employee_service_db
# ... etc

# Service URLs (for inter-service communication)
AUTH_SERVICE_URL=http://authentication-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8002
# ... etc
```

### Database Structure

Each microservice gets its own PostgreSQL database:

- `authentication_service_db` - Auth data
- `customer_service_db` - Customer data
- `employee_service_db` - Employee data
- `vehicleandproject_service_db` - Vehicle/project data
- `appointment_service_db` - Appointment data
- `notification_service_db` - Notification data
- `chatbot_service_db` - Chatbot data

## 📊 Database Management with pgAdmin

### Accessing pgAdmin

1. **Open pgAdmin:** http://localhost:5050
2. **Login with:**
   - Email: `admin@servease.com` (or your configured email)
   - Password: `admin123` (or your configured password)

### Setting Up Server Connection

1. Right-click **"Servers"** → **"Create"** → **"Server"**
2. **General Tab:**
   - Name: `ServEase PostgreSQL`
3. **Connection Tab:**
   - Host name/address: `postgres`
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres_password` (or your configured password)
4. Click **Save**

### Available Databases

Once connected, you'll see all microservice databases:
- `servease_authentication` - Authentication service tables
- `servease_customers` - Customer service tables
- `servease_employees` - Employee service tables
- `servease_vehicles_projects` - Vehicle & project service tables
- `servease_appointments` - Appointment service tables
- `servease_notifications` - Notification service tables
- `servease_chatbot` - Chatbot service tables

### Useful pgAdmin Features

- **Query Tool:** Write and execute SQL queries
- **Schema Browser:** Explore tables, columns, and relationships
- **Data Viewer:** Browse table data with filtering
- **Import/Export:** Manage data imports and exports
- **Database Statistics:** Monitor database performance

## 🚨 Troubleshooting

### Services Won't Start

```bash
# Check what's failing
docker-compose logs

# Try rebuilding
docker-compose build --no-cache
docker-compose up -d
```

### Port Already in Use

If you get port conflicts, you can change the external ports in `docker-compose.yml`:

```yaml
ports:
  - "9001:8001" # Changes external port to 9001
```

### Database Connection Issues

1. Make sure you updated `DB_PASSWORD` in `.env`
2. Check PostgreSQL is healthy: `docker-compose ps`
3. View postgres logs: `docker-compose logs postgres`

### "File Not Found" Errors

Make sure you're in the `backend/` directory when running Docker commands.

## 🔐 Security Notes

- The `.env` file is gitignored - never commit it!
- Change the default `SECRET_KEY` and `DB_PASSWORD`
- For production, set `DEBUG=False` and configure proper hosts
- The setup includes rate limiting and security headers

## 📚 Next Steps

Now that everything is running, you can:

1. **Add Business Logic**: Each service is a clean Django project ready for your code
2. **Create APIs**: Follow the `/api/v1/` versioning pattern
3. **Database Models**: Each service can define its own models
4. **Inter-service Communication**: Services can call each other using the configured URLs

## 🤝 Contributing

1. Never commit `.env` files
2. Follow the existing microservice structure
3. Update documentation for new services
4. Test locally with `docker-compose up -d`
5. Create pull requests for review

## 📞 Need Help?

- Check the main `README.md` for detailed documentation
- Review `docker-compose logs` for error messages
- Create GitHub issues for bugs or questions
- The setup includes health checks and monitoring

---

**🎉 You're Ready!** Your microservices architecture is now running and ready for development.
