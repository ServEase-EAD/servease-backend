import pytest
import responses
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch, Mock
import uuid


@pytest.mark.integration
class TestHealthCheck:
    """Test suite for health check endpoint."""

    def test_health_check_success(self, api_client):
        """Test health check endpoint returns success."""
        url = reverse('admin-health-check')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert response.data['service'] == 'admin-service'


@pytest.mark.integration
class TestUserManagement:
    """Test suite for user management endpoints."""

    @patch('admin_api.views.AuthServiceClient')
    def test_list_users_success(self, mock_auth_client, authenticated_admin_client, sample_user_list):
        """Test successfully listing all users."""
        mock_instance = mock_auth_client.return_value
        mock_instance.get_all_users.return_value = sample_user_list
        
        url = reverse('list-users')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    @patch('admin_api.views.AuthServiceClient')
    def test_list_users_with_role_filter(self, mock_auth_client, authenticated_admin_client, sample_user_list):
        """Test listing users with role filter."""
        filtered_users = [u for u in sample_user_list if u['user_role'] == 'customer']
        mock_instance = mock_auth_client.return_value
        mock_instance.get_all_users.return_value = filtered_users
        
        url = reverse('list-users') + '?role=customer'
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    @patch('admin_api.views.AuthServiceClient')
    def test_list_users_paginated_response(self, mock_auth_client, authenticated_admin_client, sample_user_list):
        """Test listing users with paginated response."""
        paginated_response = {
            'count': 2,
            'next': None,
            'previous': None,
            'results': sample_user_list
        }
        mock_instance = mock_auth_client.return_value
        mock_instance.get_all_users.return_value = paginated_response
        
        url = reverse('list-users')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_users_unauthorized(self, authenticated_customer_client):
        """Test listing users fails for non-admin."""
        url = reverse('list-users')
        response = authenticated_customer_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_unauthenticated(self, api_client):
        """Test listing users fails for unauthenticated user."""
        url = reverse('list-users')
        response = api_client.get(url)
        
        # Accept either 401 or 403 depending on middleware configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch('admin_api.views.AuthServiceClient')
    def test_get_user_detail_success(self, mock_auth_client, authenticated_admin_client, sample_user_data):
        """Test successfully getting user details."""
        user_id = sample_user_data['id']
        mock_instance = mock_auth_client.return_value
        mock_instance.get_user.return_value = sample_user_data
        
        url = reverse('user-detail', kwargs={'user_id': user_id})
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'newuser@test.com'

    @patch('admin_api.views.AuthServiceClient')
    def test_get_user_detail_not_found(self, mock_auth_client, authenticated_admin_client):
        """Test getting user details returns 404 for nonexistent user."""
        user_id = str(uuid.uuid4())
        mock_instance = mock_auth_client.return_value
        mock_instance.get_user.side_effect = Exception('404: User not found')
        
        url = reverse('user-detail', kwargs={'user_id': user_id})
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('admin_api.views.AuthServiceClient')
    def test_create_user_success(self, mock_auth_client, authenticated_admin_client, create_user_data, sample_user_data):
        """Test successfully creating a new user."""
        mock_instance = mock_auth_client.return_value
        mock_instance.create_user.return_value = sample_user_data
        
        url = reverse('create-user')
        response = authenticated_admin_client.post(url, create_user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'newuser@test.com'

    def test_create_user_invalid_data(self, authenticated_admin_client):
        """Test creating user fails with invalid data."""
        invalid_data = {'email': 'invalid'}
        
        url = reverse('create-user')
        response = authenticated_admin_client.post(url, invalid_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_password_mismatch(self, authenticated_admin_client, create_user_data):
        """Test creating user fails with password mismatch."""
        create_user_data['password2'] = 'differentpass'
        
        url = reverse('create-user')
        response = authenticated_admin_client.post(url, create_user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('admin_api.views.AuthServiceClient')
    def test_update_user_success(self, mock_auth_client, authenticated_admin_client, update_user_data, sample_user_data):
        """Test successfully updating a user."""
        user_id = sample_user_data['id']
        updated_user = {**sample_user_data, **update_user_data}
        mock_instance = mock_auth_client.return_value
        mock_instance.update_user.return_value = updated_user
        
        url = reverse('update-user', kwargs={'user_id': user_id})
        response = authenticated_admin_client.put(url, update_user_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'

    @patch('admin_api.views.AuthServiceClient')
    def test_update_user_partial(self, mock_auth_client, authenticated_admin_client, sample_user_data):
        """Test partial update of user."""
        user_id = sample_user_data['id']
        partial_data = {'first_name': 'NewName'}
        updated_user = {**sample_user_data, **partial_data}
        mock_instance = mock_auth_client.return_value
        mock_instance.update_user.return_value = updated_user
        
        url = reverse('update-user', kwargs={'user_id': user_id})
        response = authenticated_admin_client.patch(url, partial_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK

    @patch('admin_api.views.AuthServiceClient')
    def test_change_user_role_success(self, mock_auth_client, authenticated_admin_client, sample_user_data):
        """Test successfully changing user role."""
        user_id = sample_user_data['id']
        role_data = {'user_role': 'employee'}
        updated_user = {**sample_user_data, 'user_role': 'employee'}
        mock_instance = mock_auth_client.return_value
        mock_instance.update_user.return_value = updated_user
        
        url = reverse('change-user-role', kwargs={'user_id': user_id})
        response = authenticated_admin_client.patch(url, role_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert response.data['user']['user_role'] == 'employee'

    def test_change_user_role_invalid(self, authenticated_admin_client):
        """Test changing user role fails with invalid role."""
        user_id = str(uuid.uuid4())
        role_data = {'user_role': 'invalid_role'}
        
        url = reverse('change-user-role', kwargs={'user_id': user_id})
        response = authenticated_admin_client.patch(url, role_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('admin_api.views.AuthServiceClient')
    def test_delete_user_success(self, mock_auth_client, authenticated_admin_client):
        """Test successfully deleting a user."""
        user_id = str(uuid.uuid4())
        mock_instance = mock_auth_client.return_value
        mock_instance.delete_user.return_value = True
        
        url = reverse('delete-user', kwargs={'user_id': user_id})
        response = authenticated_admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch('admin_api.views.AuthServiceClient')
    def test_toggle_user_status_success(self, mock_auth_client, authenticated_admin_client):
        """Test successfully toggling user status."""
        user_id = str(uuid.uuid4())
        toggle_result = {'message': 'User activated', 'is_active': True}
        mock_instance = mock_auth_client.return_value
        mock_instance.toggle_user_status.return_value = toggle_result
        
        url = reverse('toggle-user-status', kwargs={'user_id': user_id})
        response = authenticated_admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] is True

    @patch('admin_api.views.AuthServiceClient')
    def test_get_user_statistics_success(self, mock_auth_client, authenticated_admin_client, sample_user_stats):
        """Test successfully getting user statistics."""
        mock_instance = mock_auth_client.return_value
        mock_instance.get_user_stats.return_value = sample_user_stats
        
        url = reverse('user-statistics')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_users'] == 100
        assert response.data['total_customers'] == 70

    def test_get_user_statistics_unauthorized(self, authenticated_employee_client):
        """Test getting statistics fails for non-admin."""
        url = reverse('user-statistics')
        response = authenticated_employee_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
class TestTokenHandling:
    """Test suite for JWT token handling in views."""

    @patch('admin_api.views.get_auth_token')
    @patch('admin_api.views.AuthServiceClient')
    def test_missing_token_returns_401(self, mock_auth_client, mock_get_token, authenticated_admin_client):
        """Test that missing token returns 401."""
        mock_get_token.return_value = None
        
        url = reverse('list-users')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    @patch('admin_api.views.AuthServiceClient')
    def test_service_exception_returns_500(self, mock_auth_client, authenticated_admin_client):
        """Test that service exceptions return 500."""
        mock_instance = mock_auth_client.return_value
        mock_instance.get_all_users.side_effect = Exception('Service unavailable')
        
        url = reverse('list-users')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data
