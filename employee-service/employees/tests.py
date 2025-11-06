from django.test import TestCase
from .models import Employee
from rest_framework.test import APITestCase
from rest_framework import status
import uuid

class EmployeeModelTests(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            address="123 Test St",
            specialization="Plumbing",
            experience_years=5,
            hourly_rate=25.00
        )

    def test_employee_creation(self):
        self.assertTrue(isinstance(self.employee, Employee))
        self.assertEqual(self.employee.__str__(), "John Doe")

class EmployeeAPITests(APITestCase):
    def setUp(self):
        self.employee_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "0987654321",
            "address": "456 Test Ave",
            "specialization": "Electrical",
            "experience_years": 3,
            "hourly_rate": 30.00,
            "is_available": True
        }

    def test_create_employee(self):
        response = self.client.post('/api/employees/', self.employee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.get().email, 'jane.smith@example.com')