"""
Tests for Vehicle serializers in the vehicleandproject service.

Tests cover:
- VehicleSerializer
- VehicleCreateSerializer
- VehicleUpdateSerializer
- VehicleListSerializer
- Validation logic
- Computed fields
"""

import pytest
from datetime import datetime
from rest_framework.exceptions import ValidationError

from vehicles.serializers import (
    VehicleSerializer,
    VehicleCreateSerializer,
    VehicleUpdateSerializer,
    VehicleListSerializer
)


# ==================== VehicleSerializer Tests ====================

@pytest.mark.django_db
class TestVehicleSerializer:
    """Test cases for VehicleSerializer."""
    
    def test_serialize_vehicle(self, sample_vehicle):
        """Test serializing a vehicle instance."""
        serializer = VehicleSerializer(sample_vehicle)
        data = serializer.data
        
        assert data['vehicle_id'] == str(sample_vehicle.vehicle_id)
        assert data['make'] == sample_vehicle.make
        assert data['model'] == sample_vehicle.model
        assert data['year'] == sample_vehicle.year
        assert data['color'] == sample_vehicle.color
        assert data['vin'] == sample_vehicle.vin
        assert data['plate_number'] == sample_vehicle.plate_number
        assert data['customer_id'] == str(sample_vehicle.customer_id)
        assert data['is_active'] == sample_vehicle.is_active
    
    def test_serialize_vehicle_computed_fields(self, sample_vehicle):
        """Test computed fields (age, display_name)."""
        serializer = VehicleSerializer(sample_vehicle)
        data = serializer.data
        
        expected_age = datetime.now().year - sample_vehicle.year
        assert data['age'] == expected_age
        assert data['display_name'] == sample_vehicle.get_display_name()
    
    def test_serialize_all_fields(self, sample_vehicle):
        """Test all expected fields are present."""
        serializer = VehicleSerializer(sample_vehicle)
        data = serializer.data
        
        expected_fields = {
            'vehicle_id', 'make', 'model', 'year', 'color', 'vin',
            'plate_number', 'customer_id', 'is_active', 'created_at',
            'updated_at', 'age', 'display_name'
        }
        assert set(data.keys()) == expected_fields
    
    def test_read_only_fields(self, sample_vehicle):
        """Test read-only fields cannot be set."""
        serializer = VehicleSerializer(sample_vehicle)
        
        read_only = ['vehicle_id', 'created_at', 'updated_at', 'age', 'display_name']
        for field in read_only:
            assert field in serializer.fields
            assert serializer.fields[field].read_only
    
    def test_validate_year_too_old(self, valid_vehicle_data):
        """Test year validation rejects years before 1900."""
        valid_vehicle_data['year'] = 1899
        serializer = VehicleSerializer(data=valid_vehicle_data)
        
        assert not serializer.is_valid()
        assert 'year' in serializer.errors
    
    def test_validate_year_too_new(self, valid_vehicle_data):
        """Test year validation rejects years too far in future."""
        current_year = datetime.now().year
        valid_vehicle_data['year'] = current_year + 2
        serializer = VehicleSerializer(data=valid_vehicle_data)
        
        assert not serializer.is_valid()
        assert 'year' in serializer.errors
    
    def test_validate_year_current(self, valid_vehicle_data):
        """Test current year is valid."""
        current_year = datetime.now().year
        valid_vehicle_data['year'] = current_year
        serializer = VehicleSerializer(data=valid_vehicle_data)
        
        assert serializer.is_valid()
    
    def test_validate_year_next(self, valid_vehicle_data):
        """Test next year is valid (for new models)."""
        next_year = datetime.now().year + 1
        valid_vehicle_data['year'] = next_year
        serializer = VehicleSerializer(data=valid_vehicle_data)
        
        assert serializer.is_valid()
    
    def test_validate_vin_required(self, valid_vehicle_data):
        """Test VIN is required."""
        valid_vehicle_data['vin'] = ''
        serializer = VehicleSerializer(data=valid_vehicle_data)
        
        assert not serializer.is_valid()
        assert 'vin' in serializer.errors
    
    def test_validate_vin_invalid_chars(self, valid_vehicle_data):
        """Test VIN rejects invalid characters (I, O, Q)."""
        invalid_vins = [
            '1HGCM82633A88888I',  # Contains I
            '1HGCM82633A88888O',  # Contains O
            '1HGCM82633A88888Q',  # Contains Q
        ]
        
        for i, vin in enumerate(invalid_vins):
            valid_vehicle_data['vin'] = vin
            valid_vehicle_data['plate_number'] = f'INV{i}'  # unique plates
            serializer = VehicleSerializer(data=valid_vehicle_data)
            
            assert not serializer.is_valid()
            assert 'vin' in serializer.errors
    
    def test_validate_vin_valid(self, valid_vehicle_data):
        """Test valid VIN passes validation."""
        valid_vehicle_data['vin'] = 'JT2BF18K5X0123456'
        serializer = VehicleSerializer(data=valid_vehicle_data)
        
        assert serializer.is_valid()
    
    def test_validate_plate_number_required(self, valid_vehicle_data):
        """Test plate number is required."""
        valid_vehicle_data['plate_number'] = ''
        serializer = VehicleSerializer(data=valid_vehicle_data)
        
        assert not serializer.is_valid()
        assert 'plate_number' in serializer.errors
    
    def test_validate_plate_number_trim_spaces(self, valid_vehicle_data):
        """Test plate number trims extra spaces."""
        valid_vehicle_data['plate_number'] = '  XYZ789  '
        valid_vehicle_data['vin'] = '1HGCM82633A666666'  # unique VIN
        serializer = VehicleSerializer(data=valid_vehicle_data)
        
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['plate_number'] == 'XYZ789'
    
    def test_serialize_multiple_vehicles(self, multiple_vehicles):
        """Test serializing multiple vehicles."""
        serializer = VehicleSerializer(multiple_vehicles, many=True)
        data = serializer.data
        
        assert len(data) == len(multiple_vehicles)
        for i, vehicle_data in enumerate(data):
            assert vehicle_data['vehicle_id'] == str(multiple_vehicles[i].vehicle_id)


# ==================== VehicleCreateSerializer Tests ====================

@pytest.mark.django_db
class TestVehicleCreateSerializer:
    """Test cases for VehicleCreateSerializer."""
    
    def test_create_serializer_fields(self):
        """Test VehicleCreateSerializer has only creation fields."""
        serializer = VehicleCreateSerializer()
        
        expected_fields = {'make', 'model', 'year', 'color', 'vin', 'plate_number'}
        assert set(serializer.fields.keys()) == expected_fields
    
    def test_create_vehicle_valid_data(self, valid_vehicle_data):
        """Test creating vehicle with valid data."""
        # Remove customer_id as it's not in create serializer
        create_data = {
            'make': valid_vehicle_data['make'],
            'model': valid_vehicle_data['model'],
            'year': valid_vehicle_data['year'],
            'color': valid_vehicle_data['color'],
            'vin': valid_vehicle_data['vin'],
            'plate_number': valid_vehicle_data['plate_number'],
        }
        
        serializer = VehicleCreateSerializer(data=create_data)
        assert serializer.is_valid()


# ==================== VehicleUpdateSerializer Tests ====================

@pytest.mark.django_db
class TestVehicleUpdateSerializer:
    """Test cases for VehicleUpdateSerializer."""
    
    def test_update_serializer_fields(self):
        """Test VehicleUpdateSerializer has only update fields."""
        serializer = VehicleUpdateSerializer()
        
        expected_fields = {'make', 'model', 'year', 'color', 'plate_number', 'is_active'}
        assert set(serializer.fields.keys()) == expected_fields
    
    def test_update_vin_not_included(self):
        """Test VIN is not updatable."""
        serializer = VehicleUpdateSerializer()
        assert 'vin' not in serializer.fields
    
    def test_update_vehicle_valid_data(self, sample_vehicle):
        """Test updating vehicle with valid data."""
        update_data = {
            'make': 'Updated Make',
            'model': 'Updated Model',
            'year': 2023,
            'color': 'Red',
            'plate_number': 'NEW123',
            'is_active': False,
        }
        
        serializer = VehicleUpdateSerializer(sample_vehicle, data=update_data, partial=True)
        assert serializer.is_valid()
    
    def test_update_partial(self, sample_vehicle):
        """Test partial update."""
        update_data = {'color': 'Purple'}
        
        serializer = VehicleUpdateSerializer(sample_vehicle, data=update_data, partial=True)
        assert serializer.is_valid()


# ==================== VehicleListSerializer Tests ====================

@pytest.mark.django_db
class TestVehicleListSerializer:
    """Test cases for VehicleListSerializer."""
    
    def test_list_serializer_fields(self, sample_vehicle):
        """Test VehicleListSerializer has expected fields."""
        serializer = VehicleListSerializer(sample_vehicle)
        data = serializer.data
        
        expected_fields = {
            'vehicle_id', 'customer_id', 'make', 'model', 'year',
            'display_name', 'plate_number', 'color', 'vin',
            'is_active', 'created_at', 'updated_at'
        }
        assert set(data.keys()) == expected_fields
    
    def test_list_serializer_display_name(self, sample_vehicle):
        """Test display_name in list serializer."""
        serializer = VehicleListSerializer(sample_vehicle)
        data = serializer.data
        
        assert data['display_name'] == sample_vehicle.get_display_name()
    
    def test_list_multiple_vehicles(self, multiple_vehicles):
        """Test listing multiple vehicles."""
        serializer = VehicleListSerializer(multiple_vehicles, many=True)
        data = serializer.data
        
        assert len(data) == len(multiple_vehicles)
