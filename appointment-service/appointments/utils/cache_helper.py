"""
Caching utilities for service data
"""
import json
from django.core.cache import cache
from ..services.service_clients import CustomerServiceClient, VehicleServiceClient, EmployeeServiceClient


# Cache timeout in seconds (5 minutes)
CACHE_TIMEOUT = 300


def get_customer_cached(customer_id, auth_token=None):
    """
    Get customer data with caching
    """
    cache_key = f"customer_{customer_id}"
    customer_data = cache.get(cache_key)
    
    # Check if we've already cached a 404 for this customer
    not_found_key = f"customer_404_{customer_id}"
    if cache.get(not_found_key):
        return {'full_name': 'Unknown Customer', 'email': ''}
    
    if customer_data is None:
        try:
            customer_data = CustomerServiceClient.validate_customer(customer_id, auth_token)
            cache.set(cache_key, customer_data, CACHE_TIMEOUT)
        except Exception as e:
            error_msg = str(e)
            print(f"Failed to fetch customer: {error_msg}")
            
            # If customer not found, cache the 404 to avoid repeated requests
            if 'Customer not found' in error_msg or '404' in error_msg:
                cache.set(not_found_key, True, CACHE_TIMEOUT * 2)  # Cache 404s longer
            
            return {'full_name': 'Unknown Customer', 'email': ''}
    
    return customer_data


def get_vehicle_cached(vehicle_id, auth_token=None):
    """
    Get vehicle data with caching
    """
    cache_key = f"vehicle_{vehicle_id}"
    vehicle_data = cache.get(cache_key)
    
    if vehicle_data is None:
        try:
            vehicle_data = VehicleServiceClient.get_vehicle(vehicle_id, auth_token)
            if vehicle_data:
                cache.set(cache_key, vehicle_data, CACHE_TIMEOUT)
        except Exception as e:
            print(f"Failed to fetch vehicle: {e}")
            return {'year': '', 'make': 'Unknown', 'model': 'Vehicle'}
    
    return vehicle_data or {'year': '', 'make': 'Unknown', 'model': 'Vehicle'}


def get_employee_cached(employee_id, auth_token=None):
    """
    Get employee data with caching
    """
    cache_key = f"employee_{employee_id}"
    employee_data = cache.get(cache_key)
    
    if employee_data is None:
        try:
            employee_data = EmployeeServiceClient.get_employee(employee_id, auth_token)
            if employee_data:
                cache.set(cache_key, employee_data, CACHE_TIMEOUT)
        except Exception as e:
            print(f"Failed to fetch employee: {e}")
            return {'full_name': 'Unassigned'}
    
    return employee_data or {'full_name': 'Unassigned'}


def invalidate_customer_cache(customer_id):
    """Invalidate customer cache"""
    cache_key = f"customer_{customer_id}"
    cache.delete(cache_key)


def invalidate_vehicle_cache(vehicle_id):
    """Invalidate vehicle cache"""
    cache_key = f"vehicle_{vehicle_id}"
    cache.delete(cache_key)


def invalidate_employee_cache(employee_id):
    """Invalidate employee cache"""
    cache_key = f"employee_{employee_id}"
    cache.delete(cache_key)

