from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Customer
import uuid


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer_data = {
            'user_id': 12345,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'address': '123 Test St, Test City'
        }

    def test_customer_creation(self):
        """Test creating a customer"""
        customer = Customer.objects.create(**self.customer_data)
        self.assertEqual(customer.full_name, 'John Doe')
        self.assertEqual(str(customer), 'John Doe (john.doe@example.com)')
        self.assertFalse(customer.is_verified)
        self.assertIsInstance(customer.id, uuid.UUID)

    def test_customer_unique_constraints(self):
        """Test unique constraints on email and user_id"""
        Customer.objects.create(**self.customer_data)

        # Test duplicate email
        with self.assertRaises(Exception):
            Customer.objects.create(**{**self.customer_data, 'user_id': 54321})

        # Test duplicate user_id
        with self.assertRaises(Exception):
            Customer.objects.create(
                **{**self.customer_data, 'email': 'different@example.com'})
