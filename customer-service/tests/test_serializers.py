"""
Unit tests for customer service serializers.
"""
import pytest
import uuid
from customers.serializers import (
    CustomerSerializer,
    CustomerBasicSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
    CustomerDashboardSerializer,
    CustomerWithUserDataSerializer
)
from customers.models import Customer


@pytest.mark.django_db
class TestCustomerSerializer:
    """Tests for CustomerSerializer."""
    
    def test_serialize_customer(self, sample_customer):
        """Test serializing a customer object."""
        serializer = CustomerSerializer(sample_customer)
        data = serializer.data
        
        assert data['id'] == str(sample_customer.user_id)
        assert data['street_address'] == sample_customer.street_address
        assert data['city'] == sample_customer.city
        assert data['state'] == sample_customer.state
        assert data['postal_code'] == sample_customer.postal_code
        assert 'full_address' in data
        assert 'is_business_customer' in data
    
    def test_get_id_returns_user_id(self, sample_customer):
        """Test that id field returns user_id."""
        serializer = CustomerSerializer(sample_customer)
        assert serializer.data['id'] == str(sample_customer.user_id)
    
    def test_get_full_name_with_context(self, sample_customer):
        """Test getting full name from context."""
        context = {
            'user_data': {
                'first_name': 'John',
                'last_name': 'Doe'
            }
        }
        serializer = CustomerSerializer(sample_customer, context=context)
        assert serializer.data['full_name'] == 'John Doe'
    
    def test_get_full_name_without_context(self, sample_customer):
        """Test getting full name without context returns N/A."""
        serializer = CustomerSerializer(sample_customer)
        assert serializer.data['full_name'] == 'N/A'
    
    def test_read_only_fields(self, sample_customer):
        """Test that certain fields are read-only."""
        serializer = CustomerSerializer(sample_customer)
        read_only_fields = serializer.Meta.read_only_fields
        
        assert 'id' in read_only_fields
        assert 'customer_since' in read_only_fields
        assert 'created_at' in read_only_fields
        assert 'updated_at' in read_only_fields
        assert 'total_services' in read_only_fields


@pytest.mark.django_db
class TestCustomerBasicSerializer:
    """Tests for CustomerBasicSerializer."""
    
    def test_serialize_basic_customer_info(self, sample_customer):
        """Test serializing basic customer information."""
        serializer = CustomerBasicSerializer(sample_customer)
        data = serializer.data
        
        assert 'id' in data
        assert 'user_id' in data
        assert 'street_address' in data
        assert 'city' in data
        assert 'state' in data
        assert 'full_address' in data
        assert 'company_name' in data
        assert 'is_business_customer' in data
        assert 'customer_since' in data
        assert 'total_services' in data
    
    def test_minimal_fields_for_performance(self, business_customer):
        """Test that only essential fields are included."""
        serializer = CustomerBasicSerializer(business_customer)
        data = serializer.data
        
        # Should not include detailed fields like emergency contacts
        assert 'emergency_contact_name' not in data
        assert 'notification_preferences' not in data
        assert 'preferred_contact_method' not in data


@pytest.mark.django_db
class TestCustomerCreateSerializer:
    """Tests for CustomerCreateSerializer."""
    
    def test_validate_unique_user_id(self, customer_data):
        """Test creating customer with unique user_id."""
        serializer = CustomerCreateSerializer(data=customer_data)
        assert serializer.is_valid()
    
    def test_reject_duplicate_user_id(self, sample_customer, customer_data):
        """Test that duplicate user_id is rejected."""
        customer_data['user_id'] = str(sample_customer.user_id)
        serializer = CustomerCreateSerializer(data=customer_data)
        
        assert not serializer.is_valid()
        assert 'user_id' in serializer.errors
    
    def test_create_customer_with_all_fields(self, customer_data):
        """Test creating customer with all provided fields."""
        serializer = CustomerCreateSerializer(data=customer_data)
        assert serializer.is_valid()
        
        customer = serializer.save()
        assert customer.user_id == uuid.UUID(customer_data['user_id'])
        assert customer.street_address == customer_data['street_address']
        assert customer.city == customer_data['city']
        assert customer.emergency_contact_name == customer_data['emergency_contact_name']
    
    def test_create_business_customer(self, business_customer_data):
        """Test creating a business customer."""
        serializer = CustomerCreateSerializer(data=business_customer_data)
        assert serializer.is_valid()
        
        customer = serializer.save()
        assert customer.company_name == business_customer_data['company_name']
        assert customer.business_type == business_customer_data['business_type']
        assert customer.tax_id == business_customer_data['tax_id']
    
    def test_required_field_user_id(self):
        """Test that user_id is required."""
        data = {
            'street_address': '123 Main St',
            'city': 'Springfield'
        }
        serializer = CustomerCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'user_id' in serializer.errors


@pytest.mark.django_db
class TestCustomerUpdateSerializer:
    """Tests for CustomerUpdateSerializer."""
    
    def test_update_customer_fields(self, sample_customer, update_customer_data):
        """Test updating customer fields."""
        serializer = CustomerUpdateSerializer(sample_customer, data=update_customer_data, partial=True)
        assert serializer.is_valid()
        
        updated_customer = serializer.save()
        assert updated_customer.street_address == update_customer_data['street_address']
        assert updated_customer.city == update_customer_data['city']
        assert updated_customer.state == update_customer_data['state']
    
    def test_partial_update(self, sample_customer):
        """Test partial update of customer."""
        data = {'city': 'New York'}
        serializer = CustomerUpdateSerializer(sample_customer, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_customer = serializer.save()
        assert updated_customer.city == 'New York'
        # Other fields should remain unchanged
        assert updated_customer.street_address == sample_customer.street_address
    
    def test_user_id_not_in_update_fields(self, sample_customer):
        """Test that user_id cannot be updated."""
        data = {'user_id': str(uuid.uuid4())}
        serializer = CustomerUpdateSerializer(sample_customer, data=data, partial=True)
        
        # user_id should not be in the serializer fields
        assert 'user_id' not in serializer.Meta.fields


@pytest.mark.django_db
class TestCustomerDashboardSerializer:
    """Tests for CustomerDashboardSerializer."""
    
    def test_serialize_dashboard_data(self, verified_customer):
        """Test serializing customer dashboard data."""
        serializer = CustomerDashboardSerializer(verified_customer)
        data = serializer.data
        
        assert 'id' in data
        assert 'user_id' in data
        assert 'full_address' in data
        assert 'last_service_date' in data
        assert 'total_services' in data
        assert 'customer_since' in data
        assert 'is_verified' in data
        assert 'preferred_contact_method' in data
    
    def test_get_full_name_from_context(self, sample_customer):
        """Test getting full name from context for dashboard."""
        context = {
            'user_data': {
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        }
        serializer = CustomerDashboardSerializer(sample_customer, context=context)
        assert serializer.data['full_name'] == 'Jane Smith'
    
    def test_includes_verification_status(self, verified_customer):
        """Test that verification status is included."""
        serializer = CustomerDashboardSerializer(verified_customer)
        assert serializer.data['is_verified'] is True
        assert serializer.data['total_services'] == 5


@pytest.mark.django_db
class TestCustomerWithUserDataSerializer:
    """Tests for CustomerWithUserDataSerializer."""
    
    def test_serialize_with_user_data(self, sample_customer):
        """Test serializing customer with user data attached."""
        # Simulate user data being attached to the object
        sample_customer.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+11234567890',
            'user_role': 'customer',
            'is_active': True
        }
        
        serializer = CustomerWithUserDataSerializer(sample_customer)
        data = serializer.data
        
        assert data['user_email'] == 'test@example.com'
        assert data['user_first_name'] == 'Test'
        assert data['user_last_name'] == 'User'
        assert data['user_phone'] == '+11234567890'
        assert data['user_role'] == 'customer'
        assert data['user_is_active'] is True
    
    def test_get_full_name_from_user_data(self, sample_customer):
        """Test getting full name from attached user data."""
        sample_customer.user_data = {
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        serializer = CustomerWithUserDataSerializer(sample_customer)
        assert serializer.data['full_name'] == 'John Doe'
    
    def test_get_full_name_without_user_data(self, sample_customer):
        """Test getting full name without user data returns Unknown Customer."""
        serializer = CustomerWithUserDataSerializer(sample_customer)
        assert serializer.data['full_name'] == 'Unknown Customer'
    
    def test_includes_all_customer_and_user_fields(self, sample_customer):
        """Test that all customer and user fields are included."""
        sample_customer.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+11234567890',
            'user_role': 'customer',
            'is_active': True
        }
        
        serializer = CustomerWithUserDataSerializer(sample_customer)
        data = serializer.data
        
        # Check customer fields
        assert 'street_address' in data
        assert 'city' in data
        assert 'company_name' in data
        assert 'full_address' in data
        assert 'is_business_customer' in data
        
        # Check user fields
        assert 'user_email' in data
        assert 'user_first_name' in data
        assert 'user_last_name' in data
        assert 'user_phone' in data
        assert 'user_role' in data
        assert 'user_is_active' in data
        assert 'full_name' in data
