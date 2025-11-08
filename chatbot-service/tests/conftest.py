"""
Test fixtures for chatbot service tests.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from chatbot.models import ChatSession, ChatMessage
import factory
from factory.django import DjangoModelFactory

User = get_user_model()


# Factories
class ChatSessionFactory(DjangoModelFactory):
    """Factory for creating ChatSession instances."""
    
    class Meta:
        model = ChatSession
    
    user_id = factory.LazyFunction(uuid.uuid4)
    session_id = factory.Faker('uuid4')
    is_active = True
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class ChatMessageFactory(DjangoModelFactory):
    """Factory for creating ChatMessage instances."""
    
    class Meta:
        model = ChatMessage
    
    session = factory.SubFactory(ChatSessionFactory)
    role = factory.Iterator(['user', 'assistant', 'system'])
    content = factory.Faker('sentence', nb_words=10)
    timestamp = factory.LazyFunction(timezone.now)
    token_count = factory.Faker('random_int', min=10, max=100)


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
def test_user(db):
    """Create a test user."""
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    # Don't set user.id to UUID - Django User model uses integer ID
    # The user_id in ChatSession is UUID from external services
    user.user_role = 'customer'
    user.save()
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    User = get_user_model()
    user = User.objects.create_superuser(
        username='adminuser',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )
    # Don't set user.id to UUID - Django User model uses integer ID
    user.user_role = 'admin'
    user.save()
    return user


@pytest.fixture
def employee_user(db):
    """Create an employee user."""
    User = get_user_model()
    user = User.objects.create_user(
        username='empuser',
        email='employee@example.com',
        password='emppass123',
        first_name='Employee',
        last_name='User'
    )
    # Don't set user.id to UUID - Django User model uses integer ID
    user.user_role = 'employee'
    user.save()
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Provides an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Provides an authenticated admin API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def chat_session_factory():
    """Provides the ChatSessionFactory."""
    return ChatSessionFactory


@pytest.fixture
def chat_message_factory():
    """Provides the ChatMessageFactory."""
    return ChatMessageFactory


@pytest.fixture
def sample_session(sample_user_id):
    """Creates a sample chat session."""
    return ChatSessionFactory(
        user_id=sample_user_id,
        session_id=str(uuid.uuid4()),
        is_active=True
    )


@pytest.fixture
def inactive_session(sample_user_id):
    """Creates an inactive chat session."""
    return ChatSessionFactory(
        user_id=sample_user_id,
        session_id=str(uuid.uuid4()),
        is_active=False
    )


@pytest.fixture
def sample_message(sample_session):
    """Creates a sample chat message."""
    return ChatMessageFactory(
        session=sample_session,
        role='user',
        content='Hello, I need help with my vehicle service'
    )


@pytest.fixture
def assistant_message(sample_session):
    """Creates an assistant message."""
    return ChatMessageFactory(
        session=sample_session,
        role='assistant',
        content='Hello! I\'d be happy to help you with your vehicle service. What do you need assistance with?'
    )


@pytest.fixture
def chat_conversation(sample_session):
    """Creates a chat conversation with multiple messages."""
    messages = []
    messages.append(ChatMessageFactory(
        session=sample_session,
        role='user',
        content='What services do you offer?'
    ))
    messages.append(ChatMessageFactory(
        session=sample_session,
        role='assistant',
        content='We offer various vehicle services including maintenance, repairs, and inspections.'
    ))
    messages.append(ChatMessageFactory(
        session=sample_session,
        role='user',
        content='How much does an oil change cost?'
    ))
    return messages


@pytest.fixture
def chat_request_data():
    """Provides sample chat request data."""
    return {
        'message': 'I need to schedule an appointment',
        'model': 'openai/gpt-4o'
    }


@pytest.fixture
def mock_gemini_response(mocker):
    """Mocks the Gemini API response."""
    mock = mocker.patch('chatbot.gemini_client.generate_response')
    mock.return_value = "This is a mock AI response to your query."
    return mock
