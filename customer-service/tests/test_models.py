"""
Unit tests for Customer model.
"""
import pytest
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from customers.models import Customer


@pytest.mark.django_db
class TestCustomerModel:
    """Tests for the Customer model."""
    
    def test_create_customer(self, customer_factory):
        """Test creating a customer with minimal required fields."""
        user_id = uuid.uuid4()
        customer = customer_factory(user_id=user_id)
        
        assert customer.id is not None
        assert customer.user_id == user_id
        assert customer.total_services == 0
        assert customer.is_verified is False
        assert customer.customer_since is not None
    
    def test_customer_str_representation(self, sample_customer):
        """Test string representation of customer."""
        assert str(sample_customer) == f"Customer Profile (user_id: {sample_customer.user_id})"
    
    def test_unique_user_id_constraint(self, customer_factory):
        """Test that user_id must be unique."""
        user_id = uuid.uuid4()
        customer_factory(user_id=user_id)
        
        # Attempting to create another customer with same user_id should fail
        with pytest.raises(Exception):  # Django will raise IntegrityError
            customer_factory(user_id=user_id)
    
    def test_full_address_property(self, customer_factory):
        """Test full_address property returns formatted address."""
        customer = customer_factory(
            street_address='123 Main St',
            city='Springfield',
            state='IL',
            postal_code='62701',
            country='USA'
        )
        
        expected = '123 Main St, Springfield, IL, 62701, USA'
        assert customer.full_address == expected
    
    def test_full_address_with_missing_fields(self, customer_factory):
        """Test full_address handles missing fields gracefully."""
        customer = customer_factory(
            street_address='123 Main St',
            city='Springfield',
            state='',
            postal_code='',
            country='USA'
        )
        
        assert '123 Main St' in customer.full_address
        assert 'Springfield' in customer.full_address
        assert 'USA' in customer.full_address
    
    def test_is_business_customer_property_true(self, business_customer):
        """Test is_business_customer returns True for business customers."""
        assert business_customer.is_business_customer is True
    
    def test_is_business_customer_property_false(self, customer_factory):
        """Test is_business_customer returns False for individual customers."""
        customer = customer_factory(company_name='')
        assert customer.is_business_customer is False
    
    def test_increment_service_count(self, sample_customer):
        """Test incrementing service count updates fields correctly."""
        initial_count = sample_customer.total_services
        initial_date = sample_customer.last_service_date
        
        sample_customer.increment_service_count()
        sample_customer.refresh_from_db()
        
        assert sample_customer.total_services == initial_count + 1
        assert sample_customer.last_service_date is not None
        assert sample_customer.last_service_date > (initial_date or timezone.now() - timedelta(seconds=1))
    
    def test_emergency_contact_fields(self, customer_factory):
        """Test storing emergency contact information."""
        customer = customer_factory(
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='+11234567890',
            emergency_contact_relationship='Spouse'
        )
        
        assert customer.emergency_contact_name == 'Jane Doe'
        assert customer.emergency_contact_phone == '+11234567890'
        assert customer.emergency_contact_relationship == 'Spouse'
    
    def test_business_information_fields(self, business_customer):
        """Test storing business customer information."""
        assert business_customer.company_name == 'Acme Corp'
        assert business_customer.business_type == 'Auto Repair'
        assert business_customer.tax_id == '12-3456789'
    
    def test_notification_preferences_json(self, customer_factory):
        """Test storing notification preferences as JSON."""
        preferences = {
            'email_notifications': True,
            'sms_notifications': False,
            'appointment_reminders': True
        }
        customer = customer_factory(notification_preferences=preferences)
        
        assert customer.notification_preferences == preferences
        assert customer.notification_preferences['email_notifications'] is True
    
    def test_preferred_contact_method_choices(self, customer_factory):
        """Test different contact method preferences."""
        customer_email = customer_factory(preferred_contact_method='email')
        customer_phone = customer_factory(preferred_contact_method='phone')
        customer_sms = customer_factory(preferred_contact_method='sms')
        
        assert customer_email.preferred_contact_method == 'email'
        assert customer_phone.preferred_contact_method == 'phone'
        assert customer_sms.preferred_contact_method == 'sms'
    
    def test_customer_timestamps(self, sample_customer):
        """Test that timestamps are automatically set."""
        assert sample_customer.created_at is not None
        assert sample_customer.updated_at is not None
        assert sample_customer.customer_since is not None
    
    def test_customer_ordering(self, customer_factory):
        """Test that customers are ordered by creation date descending."""
        customer1 = customer_factory()
        customer2 = customer_factory()
        customer3 = customer_factory()
        
        customers = list(Customer.objects.all())
        assert customers[0].created_at >= customers[1].created_at
        assert customers[1].created_at >= customers[2].created_at
    
    def test_verified_customer(self, verified_customer):
        """Test verified customer has expected attributes."""
        assert verified_customer.is_verified is True
        assert verified_customer.total_services == 5
        assert verified_customer.last_service_date is not None
    
    def test_default_country(self, customer_factory):
        """Test default country is USA."""
        customer = customer_factory()
        assert customer.country == 'USA'
    
    def test_default_notification_preferences(self, customer_factory):
        """Test default notification preferences is empty dict."""
        customer = customer_factory()
        assert customer.notification_preferences == {}
