"""
Authentication Service Client
Handles communication with the authentication microservice
"""
import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """Client for communicating with authentication service"""
    
    def __init__(self):
        self.base_url = settings.AUTH_SERVICE_URL
        self.timeout = 10
    
    def _get_headers(self, token: str = None) -> Dict[str, str]:
        """Get headers for authentication service requests"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers
    
    def get_all_users(self, token: str, role: Optional[str] = None) -> List[Dict]:
        """Get all users from authentication service"""
        try:
            url = f"{self.base_url}/api/v1/auth/admin/users/"
            if role:
                url += f"?role={role}"
            
            response = requests.get(
                url,
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching users: {str(e)}")
            raise Exception(f"Failed to fetch users: {str(e)}")
    
    def get_user(self, token: str, user_id: str) -> Dict:
        """Get specific user details"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/admin/users/{user_id}/",
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            raise Exception(f"Failed to fetch user: {str(e)}")
    
    def create_user(self, token: str, user_data: Dict) -> Dict:
        """Create a new user and if employee, also create profile in employee service"""
        try:
            # Determine endpoint based on role
            if user_data.get('user_role') == 'employee':
                endpoint = f"{self.base_url}/api/v1/auth/admin/employees/create/"
            else:
                # For customer or admin, use regular registration
                endpoint = f"{self.base_url}/api/v1/auth/register/"
            
            response = requests.post(
                endpoint,
                json=user_data,
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            created_user = response.json()
            
            # If employee was created, also create/update profile in employee service
            if user_data.get('user_role') == 'employee':
                try:
                    employee_service_url = getattr(settings, 'EMPLOYEE_SERVICE_URL', 'http://employee-service:8003')
                    employee_id = created_user.get('id')
                    
                    # Prepare employee profile data
                    profile_data = {
                        'phone_number': user_data.get('phone_number', ''),
                        'gender': user_data.get('gender', ''),
                        'date_of_birth': user_data.get('date_of_birth'),
                        'address_line1': user_data.get('address_line1', ''),
                        'address_line2': user_data.get('address_line2', ''),
                        'city': user_data.get('city', ''),
                        'postal_code': user_data.get('postal_code', ''),
                        'specialization': user_data.get('specialization', ''),
                        'experience_years': user_data.get('experience_years', 0),
                        'hourly_rate': user_data.get('hourly_rate', 0),
                        'is_available': user_data.get('is_available', True),
                    }
                    
                    # Remove None values
                    profile_data = {k: v for k, v in profile_data.items() if v is not None}
                    
                    employee_profile_response = requests.post(
                        f"{employee_service_url}/api/v1/employees/admin/{employee_id}/profile/",
                        json=profile_data,
                        headers=self._get_headers(token),
                        timeout=self.timeout
                    )
                    
                    if employee_profile_response.status_code in [200, 201]:
                        logger.info(f"Successfully created employee profile for {employee_id}")
                    else:
                        logger.warning(f"Failed to create employee profile: {employee_profile_response.text}")
                        
                except Exception as e:
                    logger.warning(f"Error creating employee profile (auth user created successfully): {str(e)}")
                    # Don't fail the user creation if profile creation fails
            
            return created_user
        except requests.RequestException as e:
            logger.error(f"Error creating user: {str(e)}")
            error_detail = e.response.json() if hasattr(e, 'response') and e.response else str(e)
            raise Exception(f"Failed to create user: {error_detail}")
    
    def update_user(self, token: str, user_id: str, user_data: Dict) -> Dict:
        """Update user information"""
        try:
            response = requests.patch(
                f"{self.base_url}/api/v1/auth/admin/users/{user_id}/",
                json=user_data,
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise Exception(f"Failed to update user: {str(e)}")
    
    def delete_user(self, token: str, user_id: str) -> bool:
        """Delete a user"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/auth/admin/users/{user_id}/",
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise Exception(f"Failed to delete user: {str(e)}")
    
    def toggle_user_status(self, token: str, user_id: str) -> Dict:
        """Toggle user active status"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/admin/users/{user_id}/toggle-status/",
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error toggling user status {user_id}: {str(e)}")
            raise Exception(f"Failed to toggle user status: {str(e)}")
    
    def get_user_stats(self, token: str) -> Dict:
        """Get user statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/admin/dashboard/stats/",
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching user stats: {str(e)}")
            raise Exception(f"Failed to fetch user stats: {str(e)}")
