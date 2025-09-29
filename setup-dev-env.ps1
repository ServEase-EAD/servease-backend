# ServEase Development Environment Setup Script
# This script sets up the development environment for testing

param(
    [switch]$InstallDependencies,
    [switch]$SetupDatabase,
    [switch]$StartServices,
    [switch]$RunTests,
    [switch]$All
)

$ErrorActionPreference = "Stop"

# Colors
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor $Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Test-Docker {
    Write-Step "Checking Docker installation..."
    
    try {
        $DockerVersion = docker --version
        Write-Success "Docker is installed: $DockerVersion"
        return $true
    }
    catch {
        Write-Error "Docker is not installed or not in PATH"
        Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor $Yellow
        return $false
    }
}

function Test-DockerCompose {
    Write-Step "Checking Docker Compose..."
    
    try {
        $ComposeVersion = docker-compose --version
        Write-Success "Docker Compose is available: $ComposeVersion"
        return $true
    }
    catch {
        Write-Error "Docker Compose is not available"
        return $false
    }
}

function Install-PythonDependencies {
    Write-Step "Installing Python dependencies..."
    
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Warning "Python is not installed or not in PATH"
        Write-Host "Please install Python 3.8+ from: https://www.python.org/downloads/" -ForegroundColor $Yellow
        return $false
    }
    
    try {
        # Install requests for testing script
        python -m pip install requests
        Write-Success "Python dependencies installed"
        return $true
    }
    catch {
        Write-Error "Failed to install Python dependencies: $($_.Exception.Message)"
        return $false
    }
}

function Setup-Environment {
    Write-Step "Setting up environment file..."
    
    $EnvFile = ".env"
    
    if (-not (Test-Path $EnvFile)) {
        Write-Step "Creating .env file..."
        
        $EnvContent = @"
# Database Configuration
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=postgres123
DB_PORT=5432

# Service-specific Database Names
AUTH_DB_NAME=servease_authentication
CUSTOMER_DB_NAME=servease_customers
EMPLOYEE_DB_NAME=servease_employees
VEHICLE_DB_NAME=servease_vehicles
APPOINTMENT_DB_NAME=servease_appointments
NOTIFICATION_DB_NAME=servease_notifications
CHATBOT_DB_NAME=servease_chatbot

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Django Configuration
SECRET_KEY=django-insecure-dev-key-change-in-production-12345
DEBUG=True
ALLOWED_HOSTS=*

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Service URLs
AUTH_SERVICE_URL=http://authentication-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8002
EMPLOYEE_SERVICE_URL=http://employee-service:8003
VEHICLE_SERVICE_URL=http://vehicleandproject-service:8004
APPOINTMENT_SERVICE_URL=http://appointment-service:8005
NOTIFICATION_SERVICE_URL=http://notification-service:8006
CHATBOT_SERVICE_URL=http://chatbot-service:8008

# PgAdmin Configuration
PGADMIN_DEFAULT_EMAIL=admin@servease.local
PGADMIN_DEFAULT_PASSWORD=admin123
PGADMIN_PORT=5050

# Logging
LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=INFO
"@
        
        $EnvContent | Out-File -FilePath $EnvFile -Encoding UTF8
        Write-Success "Created .env file with default configuration"
    }
    else {
        Write-Success ".env file already exists"
    }
}

function Setup-Database {
    Write-Step "Setting up database..."
    
    try {
        # Start database services first
        docker-compose up -d redis
        Start-Sleep -Seconds 5
        
        # Run migrations for all services
        Write-Step "Running authentication service migrations..."
        docker-compose run --rm authentication-service python manage.py migrate
        
        Write-Step "Running customer service migrations..."
        docker-compose run --rm customer-service python manage.py migrate
        
        Write-Success "Database setup completed"
        return $true
    }
    catch {
        Write-Error "Database setup failed: $($_.Exception.Message)"
        return $false
    }
}

function Start-Services {
    Write-Step "Starting all services..."
    
    try {
        # Build and start all services
        docker-compose up --build -d
        
        # Wait for services to be ready
        Write-Step "Waiting for services to start..."
        Start-Sleep -Seconds 30
        
        # Check service health
        $Services = @(
            @{ Name = "Nginx"; Url = "http://localhost/health" },
            @{ Name = "Authentication"; Url = "http://localhost:8001" },
            @{ Name = "Customer"; Url = "http://localhost:8002" }
        )
        
        foreach ($Service in $Services) {
            try {
                $Response = Invoke-WebRequest -Uri $Service.Url -Method GET -TimeoutSec 5 -ErrorAction Stop
                Write-Success "$($Service.Name) service is running"
            }
            catch {
                Write-Warning "$($Service.Name) service may not be ready yet"
            }
        }
        
        Write-Success "Services started successfully"
        return $true
    }
    catch {
        Write-Error "Failed to start services: $($_.Exception.Message)"
        return $false
    }
}

function Show-ServiceStatus {
    Write-Step "Checking service status..."
    
    try {
        docker-compose ps
        Write-Success "Service status displayed above"
    }
    catch {
        Write-Error "Failed to check service status"
    }
}

function Run-Tests {
    Write-Step "Running authentication tests..."
    
    try {
        if (Test-Path "test_authentication.py") {
            python test_authentication.py
        }
        else {
            Write-Warning "Python test script not found, running PowerShell tests..."
            if (Test-Path "test_authentication.ps1") {
                & .\test_authentication.ps1
            }
            else {
                Write-Error "No test scripts found"
                return $false
            }
        }
        
        Write-Success "Tests completed"
        return $true
    }
    catch {
        Write-Error "Tests failed: $($_.Exception.Message)"
        return $false
    }
}

function Show-URLs {
    Write-Host ""
    Write-Host "🌐 Service URLs:" -ForegroundColor $Cyan
    Write-Host "  Main API Gateway: http://localhost" -ForegroundColor $Yellow
    Write-Host "  Authentication:  http://localhost/api/v1/auth/" -ForegroundColor $Yellow
    Write-Host "  Customer:        http://localhost/api/v1/customers/" -ForegroundColor $Yellow
    Write-Host "  PgAdmin:         http://localhost:5050" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "🔧 Direct Service URLs:" -ForegroundColor $Cyan
    Write-Host "  Auth Service:    http://localhost:8001" -ForegroundColor $Yellow
    Write-Host "  Customer Service: http://localhost:8002" -ForegroundColor $Yellow
    Write-Host ""
}

function Show-TestingInstructions {
    Write-Host ""
    Write-Host "🧪 Testing Instructions:" -ForegroundColor $Cyan
    Write-Host "1. Run automated tests:" -ForegroundColor $Yellow
    Write-Host "   python test_authentication.py" -ForegroundColor $Green
    Write-Host "   OR" -ForegroundColor $Yellow
    Write-Host "   .\test_authentication.ps1" -ForegroundColor $Green
    Write-Host ""
    Write-Host "2. Manual testing with curl:" -ForegroundColor $Yellow
    Write-Host "   See TESTING_GUIDE.md for detailed instructions" -ForegroundColor $Green
    Write-Host ""
    Write-Host "3. Test with Postman/Insomnia:" -ForegroundColor $Yellow
    Write-Host "   Import the API documentation and test endpoints" -ForegroundColor $Green
    Write-Host ""
}

# Main execution
Write-Host "🚀 ServEase Development Environment Setup" -ForegroundColor $Cyan
Write-Host "=" * 50 -ForegroundColor $Cyan

# Check prerequisites
if (-not (Test-Docker) -or -not (Test-DockerCompose)) {
    Write-Error "Required dependencies are missing"
    exit 1
}

# Navigate to project directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if ($All -or $InstallDependencies) {
    Install-PythonDependencies
    Setup-Environment
}

if ($All -or $SetupDatabase) {
    Setup-Database
}

if ($All -or $StartServices) {
    Start-Services
    Show-ServiceStatus
}

if ($All -or $RunTests) {
    # Wait a bit more for services to be fully ready
    if ($StartServices -or $All) {
        Write-Step "Waiting for services to be fully ready..."
        Start-Sleep -Seconds 10
    }
    Run-Tests
}

if ($All) {
    Show-URLs
    Show-TestingInstructions
}

if (-not ($InstallDependencies -or $SetupDatabase -or $StartServices -or $RunTests -or $All)) {
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor $Yellow
    Write-Host "  .\setup-dev-env.ps1 -All                    # Run complete setup" -ForegroundColor $Green
    Write-Host "  .\setup-dev-env.ps1 -InstallDependencies   # Install Python deps" -ForegroundColor $Green
    Write-Host "  .\setup-dev-env.ps1 -SetupDatabase         # Setup database" -ForegroundColor $Green
    Write-Host "  .\setup-dev-env.ps1 -StartServices         # Start all services" -ForegroundColor $Green
    Write-Host "  .\setup-dev-env.ps1 -RunTests              # Run tests" -ForegroundColor $Green
    Write-Host ""
}

Write-Success "Setup script completed!"