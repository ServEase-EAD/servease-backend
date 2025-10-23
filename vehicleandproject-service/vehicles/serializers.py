from rest_framework import serializers
from .models import Vehicle
from datetime import datetime

class VehicleSerializer(serializers.ModelSerializer):
    """Main serializer for Vehicle CRUD operations"""
    
    # Read-only computed fields
    age = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_id',
            'make',
            'model', 
            'year',
            'color',
            'vin',
            'plate_number',
            'customer_id',
            'is_active',
            'created_at',
            'updated_at',
            'age',  # computed field
            'display_name',  # computed field
        ]
        read_only_fields = ['vehicle_id', 'created_at', 'updated_at', 'age', 'display_name']
    
    def get_age(self, obj):
        """Calculate vehicle age"""
        return datetime.now().year - obj.year
    
    def get_display_name(self, obj):
        """Get user-friendly display name"""
        return obj.get_display_name()
    
    def validate_year(self, value):
        """Validate manufacturing year"""
        current_year = datetime.now().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Year must be between 1900 and {current_year + 1}"
            )
        return value
    
    def validate_vin(self, value):
        """Additional VIN validation"""
        if not value:
            raise serializers.ValidationError("VIN is required")
        
        # Convert to uppercase for consistency
        value = value.upper()
        
        # Check for invalid characters (I, O, Q not allowed in VIN)
        invalid_chars = set('IOQ') & set(value)
        if invalid_chars:
            raise serializers.ValidationError(
                f"VIN contains invalid characters: {', '.join(invalid_chars)}"
            )
        
        return value
    
    def validate_plate_number(self, value):
        """Validate and format plate number"""
        if not value:
            raise serializers.ValidationError("Plate number is required")
        
        # Convert to uppercase and remove extra spaces
        value = value.upper().strip()
        return value

class VehicleCreateSerializer(VehicleSerializer):
    """Specialized serializer for vehicle creation"""
    
    class Meta(VehicleSerializer.Meta):
        fields = [
            'make',
            'model', 
            'year',
            'color',
            'vin',
            'plate_number',
            'customer_id',
        ]

class VehicleUpdateSerializer(VehicleSerializer):
    """Specialized serializer for vehicle updates"""
    
    class Meta(VehicleSerializer.Meta):
        fields = [
            'make',
            'model', 
            'year',
            'color',
            'plate_number',  # Allow plate number updates
            'is_active',
        ]
        # VIN should not be updatable for data integrity

class VehicleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing vehicles"""
    
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_id',
            'customer_id',
            'display_name',
            'plate_number',
            'color',
            'vin',
            'is_active',
            'created_at'
        ]
    
    def get_display_name(self, obj):
        return obj.get_display_name()