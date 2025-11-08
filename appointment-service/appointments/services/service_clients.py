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
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.Timeout as e:
            raise ValidationError(f"Service timeout error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Service communication error: {str(e)}")


class CustomerServiceClient(ServiceClient):
    """Client for Customer Service interactions"""
    
    @staticmethod
    def validate_customer(customer_id, auth_token=None):
        """
        Validates customer exists and is active
        Returns: customer_data or raises ValidationError
        
        Note: customer_id can be either the database ID or the user_id (logical ID)
        We try the logical ID endpoint first as appointments store user_id
        """
        # Try logical ID endpoint first (using user_id from auth service)
        url = f"{settings.SERVICE_URLS['CUSTOMER_SERVICE']}/api/v1/customers/logical/{customer_id}/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            response = CustomerServiceClient._make_request(url, headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                # If not found by logical ID, try database ID (legacy support)
                legacy_url = f"{settings.SERVICE_URLS['CUSTOMER_SERVICE']}/api/v1/customers/{customer_id}/"
                legacy_response = CustomerServiceClient._make_request(legacy_url, headers)
                
                if legacy_response.status_code == 404:
                    raise ValidationError("Customer not found")
                elif legacy_response.status_code != 200:
                    raise ValidationError(f"Customer validation failed: {legacy_response.status_code}")
                
                return legacy_response.json()
            else:
                raise ValidationError(f"Customer validation failed: {response.status_code}")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Customer service error: {str(e)}")


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
        """Get employee details using the basic info endpoint for better permissions"""
        url = f"{settings.SERVICE_URLS['EMPLOYEE_SERVICE']}/api/v1/employees/{employee_id}/basic/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        print(f"[EMPLOYEE SERVICE] Request URL: {url}")
        print(f"[EMPLOYEE SERVICE] Headers: {headers}")
        
        response = EmployeeServiceClient._make_request(url, headers)
        
        print(f"[EMPLOYEE SERVICE] Response status: {response.status_code}")
        print(f"[EMPLOYEE SERVICE] Response body: {response.text[:500]}")
        
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


class AuthServiceClient(ServiceClient):
    """Client for Authentication Service interactions"""
    
    @staticmethod
    def get_admin_users(auth_token=None):
        """
        Get all admin users from authentication service
        Returns: List of admin user objects
        """
        url = f"{settings.SERVICE_URLS['USER_SERVICE']}/api/v1/auth/admin/users/"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Add role filter for admin users
        params = {'role': 'admin'}
        
        try:
            response = AuthServiceClient._make_request(url, headers, method='GET')
            if response.status_code == 200:
                users_data = response.json()
                # Handle both list and paginated response formats
                if isinstance(users_data, dict) and 'results' in users_data:
                    return users_data['results']
                elif isinstance(users_data, list):
                    return users_data
                else:
                    return []
            else:
                print(f"Failed to get admin users: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error fetching admin users: {e}")
            return []

