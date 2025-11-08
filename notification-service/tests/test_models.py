"""
Unit tests for notification service models.
"""
import pytest
import uuid
from datetime import timedelta
from django.utils import timezone
from app_notifications.models import Notification


@pytest.mark.django_db
class TestNotificationModel:
    """Tests for the Notification model."""
    
    def test_create_notification(self, sample_user_id):
        """Test creating a notification with required fields."""
        notification = Notification.objects.create(
            recipient_user_id=sample_user_id,
            message="Test notification message",
            type='SYSTEM'
        )
        
        assert notification.id is not None
        assert isinstance(notification.id, uuid.UUID)
        assert notification.recipient_user_id == sample_user_id
        assert notification.message == "Test notification message"
        assert notification.type == 'SYSTEM'
        assert notification.read_at is None
        assert notification.created_at is not None
    
    def test_notification_str_representation(self, sample_notification):
        """Test the string representation of a notification."""
        expected = f"User {sample_notification.recipient_user_id}: {sample_notification.message[:50]}..."
        assert str(sample_notification) == expected
    
    def test_notification_str_short_message(self, sample_user_id):
        """Test string representation with short message."""
        notification = Notification.objects.create(
            recipient_user_id=sample_user_id,
            message="Short msg",
            type='OTHER'
        )
        expected = f"User {sample_user_id}: Short msg..."
        assert str(notification) == expected
    
    def test_notification_default_type(self, sample_user_id):
        """Test that default type is OTHER."""
        notification = Notification.objects.create(
            recipient_user_id=sample_user_id,
            message="Message without type"
        )
        assert notification.type == 'OTHER'
    
    def test_notification_type_choices(self, sample_user_id):
        """Test all valid notification type choices."""
        types = ['SYSTEM', 'APPOINTMENT', 'VEHICLE', 'OTHER']
        
        for notif_type in types:
            notification = Notification.objects.create(
                recipient_user_id=sample_user_id,
                message=f"Test {notif_type} notification",
                type=notif_type
            )
            assert notification.type == notif_type
    
    def test_notification_unread_by_default(self, sample_notification):
        """Test that notifications are unread by default."""
        assert sample_notification.read_at is None
    
    def test_mark_notification_as_read(self, sample_notification):
        """Test marking a notification as read."""
        assert sample_notification.read_at is None
        
        read_time = timezone.now()
        sample_notification.read_at = read_time
        sample_notification.save()
        
        sample_notification.refresh_from_db()
        assert sample_notification.read_at == read_time
    
    def test_notification_ordering(self, sample_user_id):
        """Test that notifications are ordered by created_at descending."""
        # Create notifications with different times
        old_notification = Notification.objects.create(
            recipient_user_id=sample_user_id,
            message="Old notification"
        )
        old_notification.created_at = timezone.now() - timedelta(hours=2)
        old_notification.save()
        
        new_notification = Notification.objects.create(
            recipient_user_id=sample_user_id,
            message="New notification"
        )
        
        notifications = Notification.objects.all()
        assert notifications[0].id == new_notification.id
        assert notifications[1].id == old_notification.id
    
    def test_notification_recipient_filtering(self, sample_user_id, another_user_id):
        """Test filtering notifications by recipient."""
        # Create notifications for different users
        user1_notif = Notification.objects.create(
            recipient_user_id=sample_user_id,
            message="Message for user 1"
        )
        user2_notif = Notification.objects.create(
            recipient_user_id=another_user_id,
            message="Message for user 2"
        )
        
        user1_notifications = Notification.objects.filter(recipient_user_id=sample_user_id)
        assert user1_notifications.count() == 1
        assert user1_notifications.first().id == user1_notif.id
    
    def test_notification_uuid_field(self, sample_user_id):
        """Test that recipient_user_id is a UUID field."""
        notification = Notification.objects.create(
            recipient_user_id=sample_user_id,
            message="UUID test"
        )
        assert isinstance(notification.recipient_user_id, uuid.UUID)
    
    def test_bulk_create_notifications(self, sample_user_id):
        """Test creating multiple notifications at once."""
        notifications = [
            Notification(
                recipient_user_id=sample_user_id,
                message=f"Notification {i}",
                type='SYSTEM'
            )
            for i in range(5)
        ]
        
        created = Notification.objects.bulk_create(notifications)
        assert len(created) == 5
        assert Notification.objects.filter(recipient_user_id=sample_user_id).count() == 5
    
    def test_notification_meta_verbose_names(self):
        """Test model meta verbose names."""
        assert Notification._meta.verbose_name == 'Notification'
        assert Notification._meta.verbose_name_plural == 'Notifications'
    
    def test_notification_field_constraints(self, sample_user_id):
        """Test field constraints and properties."""
        notification = Notification.objects.create(
            recipient_user_id=sample_user_id,
            message="A" * 1000  # Long message
        )
        
        # Message field should accept long text
        assert len(notification.message) == 1000
        
        # Type should have max_length=20
        assert Notification._meta.get_field('type').max_length == 20
