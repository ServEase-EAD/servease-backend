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
        """Create a new user"""
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
            return response.json()
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
