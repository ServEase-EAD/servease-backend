"""
Test fixtures for notification service tests.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from app_notifications.models import Notification
import factory
from factory.django import DjangoModelFactory


# Factories
class NotificationFactory(DjangoModelFactory):
    """Factory for creating Notification instances."""
    
    class Meta:
        model = Notification
    
    id = factory.LazyFunction(uuid.uuid4)
    recipient_user_id = factory.LazyFunction(uuid.uuid4)
    message = factory.Faker('sentence', nb_words=10)
    type = factory.Iterator(['SYSTEM', 'APPOINTMENT', 'VEHICLE', 'OTHER'])
    read_at = None
    created_at = factory.LazyFunction(timezone.now)


# Fixtures
@pytest.fixture
def api_client():
    """Provides an API client for testing."""
    return APIClient()


@pytest.fixture
def sample_user_id():
    """Provides a sample user UUID."""
    return uuid.uuid4()


@pytest.fixture
def another_user_id():
    """Provides another user UUID for multi-user tests."""
    return uuid.uuid4()


@pytest.fixture
def notification_factory():
    """Provides the NotificationFactory."""
    return NotificationFactory


@pytest.fixture
def sample_notification(sample_user_id):
    """Creates a sample unread notification."""
    return NotificationFactory(
        recipient_user_id=sample_user_id,
        message="You have a new appointment scheduled for tomorrow",
        type='APPOINTMENT',
        read_at=None
    )


@pytest.fixture
def read_notification(sample_user_id):
    """Creates a sample read notification."""
    return NotificationFactory(
        recipient_user_id=sample_user_id,
        message="Your vehicle service has been completed",
        type='VEHICLE',
        read_at=timezone.now() - timedelta(hours=1)
    )


@pytest.fixture
def system_notification(sample_user_id):
    """Creates a system notification."""
    return NotificationFactory(
        recipient_user_id=sample_user_id,
        message="System maintenance scheduled for tonight",
        type='SYSTEM',
        read_at=None
    )


@pytest.fixture
def multiple_notifications(sample_user_id):
    """Creates multiple notifications for a user."""
    return [
        NotificationFactory(
            recipient_user_id=sample_user_id,
            type='APPOINTMENT',
            read_at=None
        ),
        NotificationFactory(
            recipient_user_id=sample_user_id,
            type='VEHICLE',
            read_at=None
        ),
        NotificationFactory(
            recipient_user_id=sample_user_id,
            type='SYSTEM',
            read_at=timezone.now() - timedelta(hours=2)
        )
    ]


@pytest.fixture
def notification_data(sample_user_id):
    """Provides sample notification creation data."""
    return {
        'recipient_user_id': str(sample_user_id),
        'message': 'Your appointment has been confirmed',
        'type': 'APPOINTMENT'
    }



