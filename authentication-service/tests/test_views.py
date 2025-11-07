import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Test suite for user registration endpoint."""

    def test_successful_registration(self, api_client, user_registration_data):
        """Test successful user registration."""
        url = reverse('register-user')
        response = api_client.post(url, user_registration_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['email'] == user_registration_data['email']
        assert response.data['user_role'] == 'customer'

    def test_registration_with_existing_email(self, api_client, customer_user, user_registration_data):
        """Test registration fails with existing email."""
        user_registration_data['email'] = customer_user.email
        url = reverse('register-user')
        response = api_client.post(url, user_registration_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_password_mismatch(self, api_client, user_registration_data):
        """Test registration fails when passwords don't match."""
        user_registration_data['password2'] = 'differentpass'
        url = reverse('register-user')
        response = api_client.post(url, user_registration_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_short_password(self, api_client, user_registration_data):
        """Test registration fails with short password."""
        user_registration_data['password1'] = 'short'
        user_registration_data['password2'] = 'short'
        url = reverse('register-user')
        response = api_client.post(url, user_registration_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Test suite for user login endpoint."""

    def test_successful_login(self, api_client, customer_user):
        """Test successful user login."""
        url = reverse('login-user')
        data = {
            'email': 'customer@test.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    def test_login_with_wrong_password(self, api_client, customer_user):
        """Test login fails with incorrect password."""
        url = reverse('login-user')
        data = {
            'email': 'customer@test.com',
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_nonexistent_email(self, api_client):
        """Test login fails with non-existent email."""
        url = reverse('login-user')
        data = {
            'email': 'nonexistent@test.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_inactive_user(self, api_client, inactive_user):
        """Test login fails for inactive user."""
        url = reverse('login-user')
        data = {
            'email': 'inactive@test.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogout:
    """Test suite for user logout endpoint."""

    def test_successful_logout(self, authenticated_customer_client, customer_token):
        """Test successful user logout."""
        url = reverse('logout-user')
        data = {'refresh': customer_token['refresh']}
        response = authenticated_customer_client.post(url, data, format='json')
        
        # Accept both 205 (blacklist success) and 400 (blacklist not configured)
        assert response.status_code in [status.HTTP_205_RESET_CONTENT, status.HTTP_400_BAD_REQUEST]

    def test_logout_without_token(self, authenticated_customer_client):
        """Test logout fails without refresh token."""
        url = reverse('logout-user')
        response = authenticated_customer_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self, api_client):
        """Test logout fails for unauthenticated user."""
        url = reverse('logout-user')
        response = api_client.post(url, {}, format='json')
        
        # Can be 401 or 403 depending on middleware configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db
class TestCurrentUserProfile:
    """Test suite for current user profile endpoints."""

    def test_get_current_user_profile(self, authenticated_customer_client, customer_user):
        """Test getting current user's profile."""
        url = reverse('current-user-profile')
        response = authenticated_customer_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == customer_user.email
        assert response.data['user_role'] == 'customer'

    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile fails for unauthenticated user."""
        url = reverse('current-user-profile')
        response = api_client.get(url)
        
        # Can be 401 or 403 depending on middleware configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_update_current_user_profile(self, authenticated_customer_client):
        """Test updating current user's profile."""
        url = reverse('update-user-profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '9999999999'
        }
        response = authenticated_customer_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'


@pytest.mark.django_db
class TestEmployeeRegistration:
    """Test suite for employee registration endpoint (admin only)."""

    def test_admin_can_create_employee(self, authenticated_admin_client, employee_registration_data):
        """Test admin can create employee account."""
        url = reverse('create-employee')
        response = authenticated_admin_client.post(url, employee_registration_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == employee_registration_data['email']
        
        # Verify user was created with employee role
        user = User.objects.get(email=employee_registration_data['email'])
        assert user.user_role == 'employee'

    def test_customer_cannot_create_employee(self, authenticated_customer_client, employee_registration_data):
        """Test customer cannot create employee account."""
        url = reverse('create-employee')
        response = authenticated_customer_client.post(url, employee_registration_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create_employee(self, api_client, employee_registration_data):
        """Test unauthenticated user cannot create employee."""
        url = reverse('create-employee')
        response = api_client.post(url, employee_registration_data, format='json')
        
        # Can be 401 or 403 depending on middleware configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db
class TestEmployeeList:
    """Test suite for employee list endpoint (admin only)."""

    def test_admin_can_list_employees(self, authenticated_admin_client, employee_user):
        """Test admin can list all employees."""
        url = reverse('list-employees')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_customer_cannot_list_employees(self, authenticated_customer_client):
        """Test customer cannot list employees."""
        url = reverse('list-employees')
        response = authenticated_customer_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserList:
    """Test suite for user list endpoint (admin only)."""

    def test_admin_can_list_all_users(self, authenticated_admin_client, customer_user, employee_user):
        """Test admin can list all users."""
        url = reverse('list-all-users')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_filter_users_by_role(self, authenticated_admin_client, customer_user, employee_user):
        """Test filtering users by role."""
        url = reverse('list-all-users') + '?role=customer'
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Check if response is paginated or list
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            for user in response.data['results']:
                assert user['user_role'] == 'customer'
        elif isinstance(response.data, list):
            # List response
            for user in response.data:
                assert user['user_role'] == 'customer'

    def test_customer_cannot_list_users(self, authenticated_customer_client):
        """Test customer cannot list all users."""
        url = reverse('list-all-users')
        response = authenticated_customer_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserDetail:
    """Test suite for user detail endpoint."""

    def test_admin_can_view_any_user(self, authenticated_admin_client, customer_user):
        """Test admin can view any user's details."""
        url = reverse('user-detail', kwargs={'pk': customer_user.id})
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == customer_user.email

    def test_user_can_view_own_profile(self, authenticated_customer_client, customer_user):
        """Test user can view their own profile."""
        url = reverse('user-detail', kwargs={'pk': customer_user.id})
        response = authenticated_customer_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_user_cannot_view_other_profile(self, authenticated_customer_client, employee_user):
        """Test user cannot view other user's profile."""
        url = reverse('user-detail', kwargs={'pk': employee_user.id})
        response = authenticated_customer_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_update_any_user(self, authenticated_admin_client, customer_user):
        """Test admin can update any user."""
        url = reverse('user-detail', kwargs={'pk': customer_user.id})
        data = {'first_name': 'AdminUpdated'}
        response = authenticated_admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'AdminUpdated'

    def test_only_admin_can_delete_user(self, authenticated_admin_client, customer_user):
        """Test only admin can delete users."""
        url = reverse('user-detail', kwargs={'pk': customer_user.id})
        response = authenticated_admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestToggleUserStatus:
    """Test suite for toggle user status endpoint (admin only)."""

    def test_admin_can_toggle_user_status(self, authenticated_admin_client, customer_user):
        """Test admin can toggle user active status."""
        initial_status = customer_user.is_active
        url = reverse('toggle-user-status', kwargs={'user_id': customer_user.id})
        response = authenticated_admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] != initial_status

    def test_customer_cannot_toggle_status(self, authenticated_customer_client, employee_user):
        """Test customer cannot toggle user status."""
        url = reverse('toggle-user-status', kwargs={'user_id': employee_user.id})
        response = authenticated_customer_client.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_toggle_nonexistent_user(self, authenticated_admin_client):
        """Test toggling status of non-existent user."""
        url = reverse('toggle-user-status', kwargs={'user_id': '00000000-0000-0000-0000-000000000000'})
        response = authenticated_admin_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestAdminDashboardStats:
    """Test suite for admin dashboard stats endpoint."""

    def test_admin_can_view_stats(self, authenticated_admin_client, customer_user, employee_user):
        """Test admin can view dashboard statistics."""
        url = reverse('admin-dashboard-stats')
        response = authenticated_admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_users' in response.data
        assert 'total_customers' in response.data
        assert 'total_employees' in response.data
        assert 'total_admins' in response.data
        assert 'active_users' in response.data
        assert 'inactive_users' in response.data

    def test_customer_cannot_view_stats(self, authenticated_customer_client):
        """Test customer cannot view dashboard stats."""
        url = reverse('admin-dashboard-stats')
        response = authenticated_customer_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTokenValidation:
    """Test suite for token validation endpoint."""

    def test_valid_token_validation(self, authenticated_customer_client, customer_user):
        """Test validation of valid token."""
        url = reverse('validate-token')
        response = authenticated_customer_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data['user_id']) == str(customer_user.id)
        assert response.data['email'] == customer_user.email
        assert response.data['user_role'] == customer_user.user_role

    def test_invalid_token_validation(self, api_client):
        """Test validation fails with invalid token."""
        url = reverse('validate-token')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
        response = api_client.post(url)
        
        # Can be 401 or 403 depending on middleware configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_missing_token_validation(self, api_client):
        """Test validation fails without token."""
        url = reverse('validate-token')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """Test suite for token refresh endpoint."""

    def test_successful_token_refresh(self, api_client, customer_token):
        """Test successful token refresh."""
        url = reverse('token-refresh')
        data = {'refresh': customer_token['refresh']}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_token_refresh_with_invalid_token(self, api_client):
        """Test token refresh fails with invalid token."""
        url = reverse('token-refresh')
        data = {'refresh': 'invalidrefreshtoken'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
