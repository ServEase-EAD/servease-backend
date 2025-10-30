"""
Service clients for inter-service communication
"""
import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


class ServiceClient:
    """Base class for service communication"""
    
    @staticmethod
    def _make_request(url, headers, method='GET', data=None):
        """Helper method to make HTTP requests"""
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=5)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=5)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Service communication error: {str(e)}")


class CustomerServiceClient(ServiceClient):
    """Client for Customer Service interactions"""
    
    @staticmethod
    def validate_customer(customer_id, auth_token=None):
        """
        Validates customer exists and is active
        Returns: customer_data or raises ValidationError
        """
        url = f"{settings.SERVICE_URLS['CUSTOMER_SERVICE']}/api/v1/customers/{customer_id}/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        response = CustomerServiceClient._make_request(url, headers)
        
        if response.status_code == 404:
            raise ValidationError("Customer not found")
        elif response.status_code != 200:
            raise ValidationError(f"Customer validation failed: {response.status_code}")
        
        return response.json()


class VehicleServiceClient(ServiceClient):
    """Client for Vehicle Service interactions"""
    
    @staticmethod
    def validate_vehicle_ownership(vehicle_id, customer_id, auth_token=None):
        """
        Validates vehicle exists and belongs to customer
        Returns: vehicle_data or raises ValidationError
        """
        url = f"{settings.SERVICE_URLS['VEHICLE_SERVICE']}/api/v1/vehicles/{vehicle_id}/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        response = VehicleServiceClient._make_request(url, headers)
        
        if response.status_code == 404:
            raise ValidationError("Vehicle not found")
        elif response.status_code != 200:
            raise ValidationError(f"Vehicle validation failed: {response.status_code}")
        
        vehicle_data = response.json()
        
        # Check ownership
        if str(vehicle_data.get('customer_id')) != str(customer_id):
            raise ValidationError("Vehicle does not belong to this customer")
        
        return vehicle_data
    
    @staticmethod
    def get_vehicle(vehicle_id, auth_token=None):
        """Get vehicle details"""
        url = f"{settings.SERVICE_URLS['VEHICLE_SERVICE']}/api/v1/vehicles/{vehicle_id}/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        response = VehicleServiceClient._make_request(url, headers)
        
        if response.status_code == 200:
            return response.json()
        return None


class EmployeeServiceClient(ServiceClient):
    """Client for Employee Service interactions"""
    
    @staticmethod
    def validate_employee(employee_id, auth_token=None):
        """
        Validates employee exists and is available
        Returns: employee_data or raises ValidationError
        """
        url = f"{settings.SERVICE_URLS['EMPLOYEE_SERVICE']}/api/v1/employees/{employee_id}/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        response = EmployeeServiceClient._make_request(url, headers)
        
        if response.status_code == 404:
            raise ValidationError("Employee not found")
        elif response.status_code != 200:
            raise ValidationError(f"Employee validation failed: {response.status_code}")
        
        return response.json()
    
    @staticmethod
    def get_employee(employee_id, auth_token=None):
        """Get employee details"""
        url = f"{settings.SERVICE_URLS['EMPLOYEE_SERVICE']}/api/v1/employees/{employee_id}/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        response = EmployeeServiceClient._make_request(url, headers)
        
        if response.status_code == 200:
            return response.json()
        return None


class NotificationServiceClient(ServiceClient):
    """Client for Notification Service interactions"""
    
    @staticmethod
    def send_appointment_notification(appointment, notification_type, auth_token=None):
        """
        Triggers notification for appointment events
        Types: 'created', 'confirmed', 'reminder', 'cancelled', 'completed', 'rescheduled'
        """
        url = f"{settings.SERVICE_URLS['NOTIFICATION_SERVICE']}/api/v1/notifications/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Generate notification message
        message = NotificationServiceClient._generate_message(appointment, notification_type)
        
        payload = {
            "type": notification_type,
            "recipient_user_id": str(appointment.customer_id),
            "title": f"Appointment {notification_type.title()}",
            "message": message,
            "data": {
                "appointment_id": str(appointment.id),
                "scheduled_date": appointment.scheduled_date.isoformat(),
                "scheduled_time": appointment.scheduled_time.isoformat(),
                "appointment_type": appointment.appointment_type,
                "status": appointment.status,
            }
        }
        
        try:
            NotificationServiceClient._make_request(url, headers, method='POST', data=payload)
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Notification failed: {e}")
    
    @staticmethod
    def _generate_message(appointment, notification_type):
        """Generate notification message based on type"""
        messages = {
            'created': f"Your {appointment.appointment_type} appointment has been created for {appointment.scheduled_date} at {appointment.scheduled_time}.",
            'confirmed': f"Your {appointment.appointment_type} appointment on {appointment.scheduled_date} at {appointment.scheduled_time} has been confirmed.",
            'reminder': f"Reminder: You have a {appointment.appointment_type} appointment tomorrow at {appointment.scheduled_time}.",
            'cancelled': f"Your {appointment.appointment_type} appointment on {appointment.scheduled_date} has been cancelled.",
            'completed': f"Your {appointment.appointment_type} appointment has been completed. Thank you for your business!",
            'rescheduled': f"Your appointment has been rescheduled to {appointment.scheduled_date} at {appointment.scheduled_time}.",
        }
        return messages.get(notification_type, f"Appointment {notification_type}")

