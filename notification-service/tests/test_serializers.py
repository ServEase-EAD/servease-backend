"""
Unit tests for notification service serializers.
"""
import pytest
import uuid
from django.utils import timezone
from app_notifications.models import Notification
from app_notifications.serializers import NotificationSerializer


@pytest.mark.django_db
class TestNotificationSerializer:
    """Tests for NotificationSerializer."""
    
    def test_serialize_notification(self, sample_notification):
        """Test serializing a notification."""
        serializer = NotificationSerializer(sample_notification)
        data = serializer.data
        
        assert data['id'] == str(sample_notification.id)
        assert data['recipient_user_id'] == str(sample_notification.recipient_user_id)
        assert data['message'] == sample_notification.message
        assert data['type'] == sample_notification.type
        assert data['read_at'] is None
        assert 'created_at' in data
    
    def test_serialize_read_notification(self, read_notification):
        """Test serializing a read notification."""
        serializer = NotificationSerializer(read_notification)
        data = serializer.data
        
        assert data['read_at'] is not None
        assert data['id'] == str(read_notification.id)
    
    def test_serialize_all_fields(self, sample_notification):
        """Test that all model fields are serialized."""
        serializer = NotificationSerializer(sample_notification)
        data = serializer.data
        
        expected_fields = {'id', 'recipient_user_id', 'message', 'type', 'read_at', 'created_at'}
        assert set(data.keys()) == expected_fields
    
    def test_deserialize_valid_data(self, sample_user_id):
        """Test deserializing valid notification data."""
        data = {
            'recipient_user_id': str(sample_user_id),
            'message': 'New appointment notification',
            'type': 'APPOINTMENT'
        }
        
        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid()
        
        notification = serializer.save()
        assert notification.recipient_user_id == sample_user_id
        assert notification.message == data['message']
        assert notification.type == data['type']
    
    def test_deserialize_without_type(self, sample_user_id):
        """Test deserializing without type (should use default)."""
        data = {
            'recipient_user_id': str(sample_user_id),
            'message': 'Message without type'
        }
        
        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid()
        
        notification = serializer.save()
        assert notification.type == 'OTHER'
    
    def test_deserialize_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        data = {'message': 'Missing recipient'}
        
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'recipient_user_id' in serializer.errors
    
    def test_deserialize_empty_message(self, sample_user_id):
        """Test validation fails with empty message."""
        data = {
            'recipient_user_id': str(sample_user_id),
            'message': ''
        }
        
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'message' in serializer.errors
    
    def test_deserialize_invalid_type(self, sample_user_id):
        """Test validation fails with invalid type choice."""
        data = {
            'recipient_user_id': str(sample_user_id),
            'message': 'Test message',
            'type': 'INVALID_TYPE'
        }
        
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'type' in serializer.errors
    
    def test_deserialize_invalid_uuid(self):
        """Test validation fails with invalid UUID."""
        data = {
            'recipient_user_id': 'not-a-valid-uuid',
            'message': 'Test message'
        }
        
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'recipient_user_id' in serializer.errors
    
    def test_read_only_fields(self, sample_notification):
        """Test that read-only fields cannot be updated."""
        original_id = sample_notification.id
        original_created = sample_notification.created_at
        
        data = {
            'id': str(uuid.uuid4()),  # Try to change ID
            'message': 'Updated message',
            'created_at': timezone.now().isoformat(),  # Try to change created_at
            'read_at': timezone.now().isoformat()  # Try to change read_at
        }
        
        serializer = NotificationSerializer(sample_notification, data=data, partial=True)
        assert serializer.is_valid()
        
        updated = serializer.save()
        assert updated.id == original_id  # ID should not change
        assert updated.created_at == original_created  # created_at should not change
        assert updated.message == 'Updated message'  # message should update
    
    def test_update_notification(self, sample_notification):
        """Test updating a notification."""
        data = {
            'message': 'Updated notification message',
            'type': 'SYSTEM'
        }
        
        serializer = NotificationSerializer(sample_notification, data=data, partial=True)
        assert serializer.is_valid()
        
        updated = serializer.save()
        assert updated.message == data['message']
        assert updated.type == data['type']
        assert updated.id == sample_notification.id
    
    def test_serialize_multiple_notifications(self, multiple_notifications):
        """Test serializing multiple notifications."""
        serializer = NotificationSerializer(multiple_notifications, many=True)
        data = serializer.data
        
        assert len(data) == 3
        assert all('id' in item for item in data)
        assert all('message' in item for item in data)
    
    def test_validate_all_notification_types(self, sample_user_id):
        """Test that all notification type choices are valid."""
        types = ['SYSTEM', 'APPOINTMENT', 'VEHICLE', 'OTHER']
        
        for notif_type in types:
            data = {
                'recipient_user_id': str(sample_user_id),
                'message': f'Test {notif_type} notification',
                'type': notif_type
            }
            
            serializer = NotificationSerializer(data=data)
            assert serializer.is_valid(), f"Type {notif_type} should be valid"
            notification = serializer.save()
            assert notification.type == notif_type
    
    def test_serializer_meta_fields(self):
        """Test serializer meta configuration."""
        serializer = NotificationSerializer()
        meta = serializer.Meta
        
        assert meta.model == Notification
        assert meta.fields == '__all__'
        assert 'id' in meta.read_only_fields
        assert 'created_at' in meta.read_only_fields
        assert 'read_at' in meta.read_only_fields
