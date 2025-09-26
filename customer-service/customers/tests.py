"""
Customer Service Tests
Comprehensive test suite for customer management functionality
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from datetime import date, timedelta

from .models import Customer, Vehicle, CustomerPreferences, CustomerDocument, CustomerNote


class CustomerModelTest(TestCase):
    """Test Customer model functionality"""

    def setUp(self):
        """Set up test data"""
        self.customer_data = {
            'user_id': 1,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'street_address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345'
        }

    def test_customer_creation(self):
        """Test customer creation with valid data"""
        customer = Customer.objects.create(**self.customer_data)
        self.assertEqual(customer.full_name, 'John Doe')
        self.assertEqual(customer.email, 'john.doe@example.com')
        self.assertTrue(customer.is_active)
        self.assertFalse(customer.is_verified)

    def test_customer_full_address_property(self):
        """Test full address property"""
        customer = Customer.objects.create(**self.customer_data)
        expected_address = '123 Main St, Anytown, CA, 12345'
        self.assertEqual(customer.full_address, expected_address)

    def test_customer_with_apartment_unit(self):
        """Test customer with apartment unit in address"""
        self.customer_data['apartment_unit'] = 'Apt 2B'
        customer = Customer.objects.create(**self.customer_data)
        expected_address = '123 Main St, Apt 2B, Anytown, CA, 12345'
        self.assertEqual(customer.full_address, expected_address)

    def test_unique_user_id(self):
        """Test that user_id must be unique"""
        Customer.objects.create(**self.customer_data)
        with self.assertRaises(Exception):
            Customer.objects.create(**self.customer_data)

    def test_unique_email(self):
        """Test that email must be unique"""
        Customer.objects.create(**self.customer_data)
        customer_data_2 = self.customer_data.copy()
        customer_data_2['user_id'] = 2
        with self.assertRaises(Exception):
            Customer.objects.create(**customer_data_2)


class VehicleModelTest(TestCase):
    """Test Vehicle model functionality"""

    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            user_id=1,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            street_address='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345'
        )

        self.vehicle_data = {
            'customer': self.customer,
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'color': 'Silver',
            'vin': '1HGBH41JXMN109186',
            'license_plate': 'ABC123',
            'current_mileage': 25000
        }

    def test_vehicle_creation(self):
        """Test vehicle creation with valid data"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        self.assertEqual(str(vehicle), '2020 Toyota Camry - ABC123')
        self.assertEqual(vehicle.customer, self.customer)
        self.assertTrue(vehicle.is_active)

    def test_vehicle_age_property(self):
        """Test vehicle age calculation"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        expected_age = timezone.now().year - 2020
        self.assertEqual(vehicle.vehicle_age, expected_age)

    def test_service_due_by_date(self):
        """Test service due calculation by date"""
        self.vehicle_data['next_service_due_date'] = date.today() - \
            timedelta(days=1)
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        self.assertTrue(vehicle.is_service_due())

    def test_service_due_by_mileage(self):
        """Test service due calculation by mileage"""
        self.vehicle_data['next_service_due_mileage'] = 24000
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        self.assertTrue(vehicle.is_service_due())

    def test_service_not_due(self):
        """Test when service is not due"""
        self.vehicle_data['next_service_due_date'] = date.today() + \
            timedelta(days=30)
        self.vehicle_data['next_service_due_mileage'] = 30000
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        self.assertFalse(vehicle.is_service_due())


class CustomerPreferencesModelTest(TestCase):
    """Test CustomerPreferences model"""

    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            user_id=1,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            street_address='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345'
        )

    def test_preferences_creation(self):
        """Test preferences creation with defaults"""
        preferences = CustomerPreferences.objects.create(
            customer=self.customer)
        self.assertTrue(preferences.email_notifications)
        self.assertTrue(preferences.sms_notifications)
        self.assertEqual(preferences.preferred_contact_method, 'email')
        self.assertEqual(preferences.preferred_language, 'en')


class CustomerAPITest(APITestCase):
    """Test Customer API endpoints"""

    def setUp(self):
        """Set up test data and authentication"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.customer_data = {
            'user_id': 1,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'street_address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345'
        }

    def test_create_customer(self):
        """Test creating a customer via API"""
        response = self.client.post('/api/v1/customers/', self.customer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)

        customer = Customer.objects.first()
        self.assertEqual(customer.email, 'john.doe@example.com')
        self.assertTrue(hasattr(customer, 'preferences'))

    def test_get_customer_list(self):
        """Test getting customer list"""
        Customer.objects.create(**self.customer_data)
        response = self.client.get('/api/v1/customers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_customer_detail(self):
        """Test getting customer details"""
        customer = Customer.objects.create(**self.customer_data)
        response = self.client.get(f'/api/v1/customers/{customer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'john.doe@example.com')

    def test_update_customer(self):
        """Test updating customer information"""
        customer = Customer.objects.create(**self.customer_data)
        update_data = {'first_name': 'Jane'}
        response = self.client.patch(
            f'/api/v1/customers/{customer.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        customer.refresh_from_db()
        self.assertEqual(customer.first_name, 'Jane')

    def test_customer_dashboard(self):
        """Test customer dashboard endpoint"""
        customer = Customer.objects.create(**self.customer_data)
        response = self.client.get(
            f'/api/v1/customers/{customer.id}/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('full_name', response.data)
        self.assertIn('vehicles', response.data)
        self.assertIn('preferences', response.data)

    def test_customer_preferences(self):
        """Test customer preferences endpoint"""
        customer = Customer.objects.create(**self.customer_data)
        response = self.client.get(
            f'/api/v1/customers/{customer.id}/preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test updating preferences
        preferences_data = {'email_notifications': False}
        response = self.client.patch(
            f'/api/v1/customers/{customer.id}/preferences/',
            preferences_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['email_notifications'])

    def test_customer_verification(self):
        """Test customer verification endpoint"""
        customer = Customer.objects.create(**self.customer_data)
        response = self.client.post(f'/api/v1/customers/{customer.id}/verify/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        customer.refresh_from_db()
        self.assertTrue(customer.is_verified)

    def test_customer_stats(self):
        """Test customer statistics endpoint"""
        Customer.objects.create(**self.customer_data)
        response = self.client.get('/api/v1/customers/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('total_customers', response.data)
        self.assertIn('active_customers', response.data)
        self.assertEqual(response.data['total_customers'], 1)


class VehicleAPITest(APITestCase):
    """Test Vehicle API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.customer = Customer.objects.create(
            user_id=1,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            street_address='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345'
        )

        self.vehicle_data = {
            'customer_id': str(self.customer.id),
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'color': 'Silver',
            'vin': '1HGBH41JXMN109186',
            'license_plate': 'ABC123',
            'current_mileage': 25000
        }

    def test_create_vehicle(self):
        """Test creating a vehicle via API"""
        response = self.client.post('/api/v1/vehicles/', self.vehicle_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.count(), 1)

    def test_update_vehicle_mileage(self):
        """Test updating vehicle mileage"""
        vehicle = Vehicle.objects.create(
            customer=self.customer,
            make='Toyota',
            model='Camry',
            year=2020,
            color='Silver',
            vin='1HGBH41JXMN109186',
            license_plate='ABC123',
            current_mileage=25000
        )

        mileage_data = {'mileage': 26000}
        response = self.client.post(
            f'/api/v1/vehicles/{vehicle.id}/update-mileage/',
            mileage_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        vehicle.refresh_from_db()
        self.assertEqual(vehicle.current_mileage, 26000)

    def test_vehicle_service_status(self):
        """Test vehicle service status endpoint"""
        vehicle = Vehicle.objects.create(
            customer=self.customer,
            make='Toyota',
            model='Camry',
            year=2020,
            color='Silver',
            vin='1HGBH41JXMN109186',
            license_plate='ABC123',
            current_mileage=25000
        )

        response = self.client.get(
            f'/api/v1/vehicles/{vehicle.id}/service-status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('is_service_due', response.data)
        self.assertIn('current_mileage', response.data)
        self.assertEqual(response.data['current_mileage'], 25000)
