"""
Service Clients for external API communication
"""
import requests
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# Service URLs from environment or defaults
AUTH_SERVICE_URL = getattr(settings, 'AUTH_SERVICE_URL', 'http://authentication-service:8001')


class AuthServiceClient:
    """Client for authentication service"""
    
    @staticmethod
    def get_admin_users() -> List[Dict[str, Any]]:
        """
        Get all users with admin role from authentication service
        Returns list of admin user data
        """
        try:
            url = f"{AUTH_SERVICE_URL}/api/v1/accounts/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                all_users = response.json()
                # Filter for admin users
                admin_users = [
                    user for user in all_users 
                    if user.get('role') == 'employee' and user.get('is_admin', False)
                ]
                logger.info(f"Retrieved {len(admin_users)} admin users")
                return admin_users
            else:
                logger.error(f"Failed to fetch users: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to auth service: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching admin users: {e}")
            return []
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user details by user ID
        """
        try:
            url = f"{AUTH_SERVICE_URL}/api/v1/accounts/{user_id}/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch user {user_id}: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to auth service: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching user: {e}")
            return None