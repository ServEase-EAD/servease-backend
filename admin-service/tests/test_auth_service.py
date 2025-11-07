import pytest
import responses
from admin_api.services.auth_service import AuthServiceClient
import json


@pytest.mark.unit
class TestAuthServiceClient:
    """Test suite for AuthServiceClient."""

    def setup_method(self, mock_auth_service_url=None):
        """Set up test client."""
        self.token = 'test-token-12345'
        self.base_url = 'http://localhost:8001'

    @responses.activate
    def test_get_all_users_success(self, sample_user_list, mock_auth_service_url):
        """Test successfully fetching all users."""
        client = AuthServiceClient()
        responses.add(
            responses.GET,
            f'{self.base_url}/api/v1/auth/admin/users/',
            json=sample_user_list,
            status=200
        )
        
        result = client.get_all_users(self.token)
        assert len(result) == 2
        assert result[0]['email'] == 'user1@test.com'

    @responses.activate
    def test_get_all_users_with_role_filter(self, sample_user_list, mock_auth_service_url):
        """Test fetching users with role filter."""
        client = AuthServiceClient()
        filtered_users = [u for u in sample_user_list if u['user_role'] == 'customer']
        responses.add(
            responses.GET,
            f'{self.base_url}/api/v1/auth/admin/users/?role=customer',
            json=filtered_users,
            status=200
        )
        
        result = client.get_all_users(self.token, role='customer')
        assert len(result) == 1
        assert result[0]['user_role'] == 'customer'

    @responses.activate
    def test_get_all_users_failure(self, mock_auth_service_url):
        """Test handling error when fetching users fails."""
        client = AuthServiceClient()
        responses.add(
            responses.GET,
            f'{self.base_url}/api/v1/auth/admin/users/',
            json={'error': 'Internal server error'},
            status=500
        )
        
        with pytest.raises(Exception, match='Failed to fetch users'):
            client.get_all_users(self.token)

    @responses.activate
    def test_get_user_success(self, sample_user_data, mock_auth_service_url):
        """Test successfully fetching a specific user."""
        client = AuthServiceClient()
        user_id = sample_user_data['id']
        responses.add(
            responses.GET,
            f'{self.base_url}/api/v1/auth/admin/users/{user_id}/',
            json=sample_user_data,
            status=200
        )
        
        result = client.get_user(self.token, user_id)
        assert result['email'] == 'newuser@test.com'

    @responses.activate
    def test_get_user_not_found(self, mock_auth_service_url):
        """Test handling user not found error."""
        client = AuthServiceClient()
        user_id = 'nonexistent-id'
        responses.add(
            responses.GET,
            f'{self.base_url}/api/v1/auth/admin/users/{user_id}/',
            json={'error': 'User not found'},
            status=404
        )
        
        with pytest.raises(Exception, match='Failed to fetch user'):
            client.get_user(self.token, user_id)

    @responses.activate
    def test_create_employee_success(self, create_user_data, mock_auth_service_url):
        """Test creating an employee user."""
        client = AuthServiceClient()
        create_user_data['user_role'] = 'employee'
        response_data = {**create_user_data, 'id': 'new-user-id'}
        
        responses.add(
            responses.POST,
            f'{self.base_url}/api/v1/auth/admin/employees/create/',
            json=response_data,
            status=201
        )
        
        result = client.create_user(self.token, create_user_data)
        assert result['email'] == create_user_data['email']

    @responses.activate
    def test_create_customer_success(self, create_user_data, mock_auth_service_url):
        """Test creating a customer user."""
        client = AuthServiceClient()
        create_user_data['user_role'] = 'customer'
        response_data = {**create_user_data, 'id': 'new-user-id'}
        
        responses.add(
            responses.POST,
            f'{self.base_url}/api/v1/auth/register/',
            json=response_data,
            status=201
        )
        
        result = client.create_user(self.token, create_user_data)
        assert result['email'] == create_user_data['email']

    @responses.activate
    def test_create_user_failure(self, create_user_data, mock_auth_service_url):
        """Test handling error when creating user fails."""
        client = AuthServiceClient()
        responses.add(
            responses.POST,
            f'{self.base_url}/api/v1/auth/register/',
            json={'error': 'Email already exists'},
            status=400
        )
        
        with pytest.raises(Exception, match='Failed to create user'):
            client.create_user(self.token, create_user_data)

    @responses.activate
    def test_update_user_success(self, update_user_data, mock_auth_service_url):
        """Test successfully updating a user."""
        client = AuthServiceClient()
        user_id = 'test-user-id'
        response_data = {**update_user_data, 'id': user_id, 'email': 'user@test.com'}
        
        responses.add(
            responses.PATCH,
            f'{self.base_url}/api/v1/auth/admin/users/{user_id}/',
            json=response_data,
            status=200
        )
        
        result = client.update_user(self.token, user_id, update_user_data)
        assert result['first_name'] == 'Updated'

    @responses.activate
    def test_update_user_failure(self, update_user_data, mock_auth_service_url):
        """Test handling error when updating user fails."""
        client = AuthServiceClient()
        user_id = 'test-user-id'
        responses.add(
            responses.PATCH,
            f'{self.base_url}/api/v1/auth/admin/users/{user_id}/',
            json={'error': 'User not found'},
            status=404
        )
        
        with pytest.raises(Exception, match='Failed to update user'):
            client.update_user(self.token, user_id, update_user_data)

    @responses.activate
    def test_delete_user_success(self, mock_auth_service_url):
        """Test successfully deleting a user."""
        client = AuthServiceClient()
        user_id = 'test-user-id'
        responses.add(
            responses.DELETE,
            f'{self.base_url}/api/v1/auth/admin/users/{user_id}/',
            status=204
        )
        
        result = client.delete_user(self.token, user_id)
        assert result is True

    @responses.activate
    def test_delete_user_failure(self, mock_auth_service_url):
        """Test handling error when deleting user fails."""
        client = AuthServiceClient()
        user_id = 'test-user-id'
        responses.add(
            responses.DELETE,
            f'{self.base_url}/api/v1/auth/admin/users/{user_id}/',
            json={'error': 'Cannot delete user'},
            status=400
        )
        
        with pytest.raises(Exception, match='Failed to delete user'):
            client.delete_user(self.token, user_id)

    @responses.activate
    def test_toggle_user_status_success(self, mock_auth_service_url):
        """Test successfully toggling user status."""
        client = AuthServiceClient()
        user_id = 'test-user-id'
        response_data = {'message': 'User activated', 'is_active': True}
        
        responses.add(
            responses.POST,
            f'{self.base_url}/api/v1/auth/admin/users/{user_id}/toggle-status/',
            json=response_data,
            status=200
        )
        
        result = client.toggle_user_status(self.token, user_id)
        assert result['is_active'] is True

    @responses.activate
    def test_toggle_user_status_failure(self, mock_auth_service_url):
        """Test handling error when toggling status fails."""
        client = AuthServiceClient()
        user_id = 'test-user-id'
        responses.add(
            responses.POST,
            f'{self.base_url}/api/v1/auth/admin/users/{user_id}/toggle-status/',
            json={'error': 'User not found'},
            status=404
        )
        
        with pytest.raises(Exception, match='Failed to toggle user status'):
            client.toggle_user_status(self.token, user_id)

    @responses.activate
    def test_get_user_stats_success(self, sample_user_stats, mock_auth_service_url):
        """Test successfully fetching user statistics."""
        client = AuthServiceClient()
        responses.add(
            responses.GET,
            f'{self.base_url}/api/v1/auth/admin/dashboard/stats/',
            json=sample_user_stats,
            status=200
        )
        
        result = client.get_user_stats(self.token)
        assert result['total_users'] == 100
        assert result['total_customers'] == 70

    @responses.activate
    def test_get_user_stats_failure(self, mock_auth_service_url):
        """Test handling error when fetching stats fails."""
        client = AuthServiceClient()
        responses.add(
            responses.GET,
            f'{self.base_url}/api/v1/auth/admin/dashboard/stats/',
            json={'error': 'Server error'},
            status=500
        )
        
        with pytest.raises(Exception, match='Failed to fetch user stats'):
            client.get_user_stats(self.token)
