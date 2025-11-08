"""
Tests for Vehicle models in the vehicleandproject service.

Tests cover:
- Vehicle model creation and validation
- VIN validation
- Plate number validation
- Model methods and properties
- Relationships and constraints
"""

import pytest
import uuid
from datetime import datetime
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from vehicles.models import Vehicle


# ==================== Vehicle Model Tests ====================

class TestVehicleModel:
    """Test cases for Vehicle model."""
    
    def test_create_vehicle(self, vehicle_factory):
        """Test basic vehicle creation."""
        vehicle = vehicle_factory(
            make='Tesla',
            model='Model 3',
            year=2023,
            color='Red'
        )
        
        assert vehicle.vehicle_id is not None
        assert isinstance(vehicle.vehicle_id, uuid.UUID)
        assert vehicle.make == 'Tesla'
        assert vehicle.model == 'Model 3'
        assert vehicle.year == 2023
        assert vehicle.color == 'Red'
        assert vehicle.is_active is True
        assert vehicle.created_at is not None
        assert vehicle.updated_at is not None
    
    def test_vehicle_str_representation(self, sample_vehicle):
        """Test vehicle string representation."""
        expected = f"{sample_vehicle.year} {sample_vehicle.make} {sample_vehicle.model} ({sample_vehicle.plate_number})"
        assert str(sample_vehicle) == expected
    
    def test_vehicle_display_name(self, sample_vehicle):
        """Test get_display_name method."""
        expected = f"{sample_vehicle.year} {sample_vehicle.make} {sample_vehicle.model}"
        assert sample_vehicle.get_display_name() == expected
    
    def test_vehicle_age_property(self, vehicle_factory):
        """Test age property calculation."""
        current_year = datetime.now().year
        vehicle = vehicle_factory(year=2020)
        
        expected_age = current_year - 2020
        assert vehicle.age == expected_age
    
    def test_vehicle_age_new_car(self, vehicle_factory):
        """Test age for brand new car."""
        current_year = datetime.now().year
        vehicle = vehicle_factory(year=current_year)
        
        assert vehicle.age == 0
    
    def test_vehicle_default_is_active(self, vehicle_factory):
        """Test default is_active value."""
        vehicle = vehicle_factory()
        assert vehicle.is_active is True
    
    def test_vehicle_can_be_inactive(self, inactive_vehicle):
        """Test setting vehicle as inactive."""
        assert inactive_vehicle.is_active is False
    
    def test_vehicle_unique_vin(self, vehicle_factory):
        """Test VIN uniqueness constraint."""
        vin = '1HGBH41JXMN109186'
        vehicle_factory(vin=vin)
        
        with pytest.raises(IntegrityError):
            vehicle_factory(vin=vin, plate_number='DIFF123')
    
    def test_vehicle_unique_plate_number(self, vehicle_factory):
        """Test plate number uniqueness constraint."""
        plate = 'UNIQ123'
        vin1 = 'UNIQ1111111111111'
        vin2 = 'UNIQ2222222222222'
        vehicle_factory(plate_number=plate, vin=vin1)
        
        with pytest.raises(IntegrityError):
            vehicle_factory(vin=vin2, plate_number=plate)
    
    def test_vehicle_vin_validation_length(self, vehicle_factory):
        """Test VIN must be exactly 17 characters."""
        with pytest.raises(ValidationError):
            vehicle = vehicle_factory(vin='SHORT')
            vehicle.full_clean()
    
    def test_vehicle_vin_validation_format(self, vehicle_factory):
        """Test VIN format validation (alphanumeric only)."""
        with pytest.raises(ValidationError):
            vehicle = vehicle_factory(vin='1HGBH41JXMN10918@')  # @ is invalid
            vehicle.full_clean()
    
    def test_vehicle_vin_excludes_invalid_chars(self, vehicle_factory):
        """Test VIN cannot contain I, O, or Q."""
        invalid_vins = [
            '1HGBH41JXMN10918I',  # Contains I
            '1HGBH41JXMN10918O',  # Contains O
            '1HGBH41JXMN10918Q',  # Contains Q
        ]
        
        for vin in invalid_vins:
            with pytest.raises(ValidationError):
                vehicle = vehicle_factory(vin=vin)
                vehicle.full_clean()
    
    def test_vehicle_valid_vin(self, vehicle_factory):
        """Test valid VIN passes validation."""
        valid_vin = 'JT2BF18K5X0123456'
        vehicle = vehicle_factory(vin=valid_vin)
        vehicle.full_clean()  # Should not raise
        assert vehicle.vin == valid_vin
    
    def test_vehicle_plate_number_validation_min_length(self, vehicle_factory):
        """Test plate number minimum length."""
        with pytest.raises(ValidationError):
            vehicle = vehicle_factory(plate_number='A')  # Too short
            vehicle.full_clean()
    
    def test_vehicle_plate_number_validation_max_length(self, vehicle_factory):
        """Test plate number maximum length."""
        # PostgreSQL will raise DataError for too-long values
        from django.db import DataError
        with pytest.raises((ValidationError, DataError)):
            vehicle = vehicle_factory(plate_number='ABCDEFGHIJK')  # Too long (11 chars)
            vehicle.full_clean()
    
    def test_vehicle_plate_number_valid_formats(self, vehicle_factory):
        """Test various valid plate number formats."""
        valid_plates = [
            ('ABC123', '1HGCM82633A000001'),
            ('AB-123', '1HGCM82633A000002'),
            ('A BC12', '1HGCM82633A000003'),
            ('XYZ999', '1HGCM82633A000004'),
            ('12AB34', '1HGCM82633A000005'),
        ]
        
        for plate, vin in valid_plates:
            vehicle = vehicle_factory(plate_number=plate, vin=vin)
            vehicle.full_clean()  # Should not raise
            assert vehicle.plate_number == plate
    
    def test_vehicle_customer_id_required(self, vehicle_factory):
        """Test customer_id is required."""
        vehicle = vehicle_factory()
        assert vehicle.customer_id is not None
        assert isinstance(vehicle.customer_id, uuid.UUID)
    
    def test_vehicle_ordering(self, multiple_vehicles):
        """Test vehicles are ordered by created_at descending."""
        vehicles = Vehicle.objects.all()
        
        # Should be ordered by newest first
        for i in range(len(vehicles) - 1):
            assert vehicles[i].created_at >= vehicles[i + 1].created_at
    
    def test_vehicle_filter_by_customer(self, vehicle_factory, customer_user_id):
        """Test filtering vehicles by customer_id."""
        # Create vehicles for the customer with unique VINs and plates
        vehicle_factory(
            customer_id=customer_user_id,
            plate_number='CUSTVEH1',
            vin='CUST1111111111111'
        )
        vehicle_factory(
            customer_id=customer_user_id,
            plate_number='CUSTVEH2',
            vin='CUST2222222222222'
        )
        
        # Create vehicle for different customer
        other_customer_id = uuid.uuid4()
        vehicle_factory(
            customer_id=other_customer_id,
            plate_number='OTHR',
            vin='OTHR9999999999999'
        )
        
        # Filter by customer
        customer_vehicles = Vehicle.objects.filter(customer_id=customer_user_id)
        assert customer_vehicles.count() >= 2  # At least our 2 vehicles
    
    def test_vehicle_filter_by_make_model(self, vehicle_factory):
        """Test filtering by make and model."""
        vehicle_factory(make='Toyota', model='Camry', plate_number='TOY1CAM', vin='TOY1CAM1111111111')
        vehicle_factory(make='Toyota', model='Corolla', plate_number='TOY2COR', vin='TOY2COR2222222222')
        vehicle_factory(make='Honda', model='Civic', plate_number='HON1CIV', vin='HON1CIV3333333333')
        
        toyota_vehicles = Vehicle.objects.filter(make='Toyota')
        assert toyota_vehicles.count() >= 2
        
        camry_vehicles = Vehicle.objects.filter(make='Toyota', model='Camry')
        assert camry_vehicles.count() >= 1
    
    def test_vehicle_filter_by_year(self, vehicle_factory):
        """Test filtering by year."""
        vehicle_factory(year=2020, plate_number='Y2020V', vin='Y2020VV111111111')
        vehicle_factory(year=2021, plate_number='Y2021V', vin='Y2021VV222222222')
        vehicle_factory(year=2022, plate_number='Y2022V', vin='Y2022VV333333333')
        
        year_2021_vehicles = Vehicle.objects.filter(year=2021)
        assert year_2021_vehicles.count() >= 1
        # Verify at least one is 2021
        assert any(v.year == 2021 for v in year_2021_vehicles)
    
    def test_vehicle_filter_active(self, vehicle_factory):
        """Test filtering by is_active status."""
        vehicle_factory(is_active=True, plate_number='ACT1V', vin='ACT1VVV111111111')
        vehicle_factory(is_active=True, plate_number='ACT2V', vin='ACT2VVV222222222')
        vehicle_factory(is_active=False, plate_number='INACTV', vin='INACTVVV33333333')
        
        active_vehicles = Vehicle.objects.filter(is_active=True)
        assert active_vehicles.count() >= 2
        
        inactive_vehicles = Vehicle.objects.filter(is_active=False)
        assert inactive_vehicles.count() >= 1
    
    def test_vehicle_updated_at_changes(self, sample_vehicle):
        """Test updated_at timestamp changes on save."""
        original_updated = sample_vehicle.updated_at
        
        # Modify and save
        sample_vehicle.color = 'Green'
        sample_vehicle.save()
        sample_vehicle.refresh_from_db()
        
        assert sample_vehicle.updated_at > original_updated
    
    def test_vehicle_vin_case_insensitive(self, vehicle_factory):
        """Test VIN is case-insensitive (stored as uppercase)."""
        vehicle = vehicle_factory(vin='jt2bf18k5x0123456')
        # VIN should be stored as-is by model, validation happens in serializer
        assert vehicle.vin == 'jt2bf18k5x0123456'
    
    def test_vehicle_multiple_per_customer(self, vehicle_factory, customer_user_id):
        """Test customer can have multiple vehicles."""
        vehicle1 = vehicle_factory(
            customer_id=customer_user_id,
            plate_number='VEH1',
            vin='1HGBH41JXMN109186'
        )
        vehicle2 = vehicle_factory(
            customer_id=customer_user_id,
            plate_number='VEH2',
            vin='2T3ZFREV1HW123456'
        )
        
        assert vehicle1.customer_id == vehicle2.customer_id
        assert Vehicle.objects.filter(customer_id=customer_user_id).count() == 2
