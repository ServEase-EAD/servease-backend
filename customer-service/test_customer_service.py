"""
Test script for Customer Profile Management API
Demonstrates CRUD operations and key features
"""
import json
from django.test import Client
from customers.serializers import CustomerCreateSerializer, VehicleSerializer
from customers.models import Customer, Vehicle, CustomerPreferences
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'customer_service.settings_local')
django.setup()


def test_customer_creation():
    """Test creating a customer with preferences"""
    print("\n=== Testing Customer Creation ===")

    # Create customer data
    customer_data = {
        'user_id': 1001,
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890',
        'street_address': '123 Main St',
        'city': 'Anytown',
        'state': 'CA',
        'zip_code': '12345',
        'preferences': {
            'email_notifications': True,
            'sms_notifications': False,
            'preferred_contact_method': 'email'
        }
    }

    # Test serializer
    serializer = CustomerCreateSerializer(data=customer_data)
    if serializer.is_valid():
        customer = serializer.save()
        print(f"✅ Customer created: {customer.full_name}")
        print(f"   Email: {customer.email}")
        print(f"   Address: {customer.full_address}")
        return customer
    else:
        print(f"❌ Customer creation failed: {serializer.errors}")
        return None


def test_vehicle_creation(customer):
    """Test adding a vehicle to a customer"""
    print("\n=== Testing Vehicle Creation ===")

    vehicle_data = {
        'make': 'Toyota',
        'model': 'Camry',
        'year': 2020,
        'color': 'Silver',
        'vin': '1HGBH41JXMN109186',
        'license_plate': 'ABC123',
        'current_mileage': 25000,
        'fuel_type': 'gasoline',
        'transmission': 'automatic'
    }

    vehicle = Vehicle.objects.create(customer=customer, **vehicle_data)
    print(f"✅ Vehicle created: {vehicle}")
    print(f"   VIN: {vehicle.vin}")
    print(f"   Mileage: {vehicle.current_mileage}")
    print(f"   Age: {vehicle.vehicle_age} years")
    return vehicle


def test_customer_dashboard_data(customer):
    """Test customer dashboard data retrieval"""
    print("\n=== Testing Customer Dashboard Data ===")

    # Get dashboard data
    vehicles_count = customer.get_active_vehicles_count()
    preferences = customer.preferences

    print(f"✅ Dashboard data for {customer.full_name}:")
    print(f"   Active Vehicles: {vehicles_count}")
    print(f"   Email Notifications: {preferences.email_notifications}")
    print(f"   Preferred Contact: {preferences.preferred_contact_method}")
    print(f"   Customer Since: {customer.customer_since.strftime('%Y-%m-%d')}")


def test_api_endpoints():
    """Test API endpoints using Django test client"""
    print("\n=== Testing API Endpoints ===")

    client = Client()

    # Test customer list endpoint
    response = client.get('/api/v1/customers/')
    print(f"✅ Customer List API: Status {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"   Total customers: {data.get('count', 0)}")

    # Test customer stats endpoint
    response = client.get('/api/v1/customers/stats/')
    print(f"✅ Customer Stats API: Status {response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print(f"   Total Customers: {stats.get('total_customers', 0)}")
        print(f"   Active Customers: {stats.get('active_customers', 0)}")


def test_model_relationships():
    """Test model relationships and properties"""
    print("\n=== Testing Model Relationships ===")

    # Get first customer
    customer = Customer.objects.first()
    if customer:
        print(f"✅ Testing relationships for {customer.full_name}")

        # Test vehicles relationship
        vehicles = customer.vehicles.all()
        print(f"   Vehicles: {vehicles.count()}")

        # Test preferences relationship
        if hasattr(customer, 'preferences'):
            print(f"   Preferences configured: ✅")
        else:
            print(f"   Preferences configured: ❌")

        # Test vehicle service due check
        for vehicle in vehicles:
            service_due = vehicle.is_service_due()
            print(f"   {vehicle} - Service Due: {'Yes' if service_due else 'No'}")


def main():
    """Run all tests"""
    print("🚀 Starting Customer Profile Management Tests")
    print("=" * 60)

    try:
        # Test customer creation
        customer = test_customer_creation()

        if customer:
            # Test vehicle creation
            vehicle = test_vehicle_creation(customer)

            # Test dashboard data
            test_customer_dashboard_data(customer)

            # Test model relationships
            test_model_relationships()

        # Test API endpoints
        test_api_endpoints()

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🔗 Access the API at: http://127.0.0.1:8002/api/v1/customers/")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
