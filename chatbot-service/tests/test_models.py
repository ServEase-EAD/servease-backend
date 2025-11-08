"""
Unit tests for chatbot service models.
"""
import pytest
import uuid
from datetime import timedelta
from django.utils import timezone
from chatbot.models import ChatSession, ChatMessage


@pytest.mark.django_db
class TestChatSessionModel:
    """Tests for the ChatSession model."""
    
    def test_create_chat_session(self, sample_user_id):
        """Test creating a chat session."""
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            user_id=sample_user_id,
            session_id=session_id
        )
        
        assert session.id is not None
        assert session.user_id == sample_user_id
        assert session.session_id == session_id
        assert session.is_active is True
        assert session.created_at is not None
        assert session.updated_at is not None
    
    def test_session_str_representation(self, sample_session):
        """Test the string representation of a session."""
        expected = f"Session {sample_session.session_id} - User {sample_session.user_id}"
        assert str(sample_session) == expected
    
    def test_session_unique_session_id(self, sample_user_id):
        """Test that session_id must be unique."""
        session_id = str(uuid.uuid4())
        ChatSession.objects.create(
            user_id=sample_user_id,
            session_id=session_id
        )
        
        # Try to create another session with same session_id
        with pytest.raises(Exception):  # IntegrityError
            ChatSession.objects.create(
                user_id=sample_user_id,
                session_id=session_id
            )
    
    def test_session_default_is_active(self, sample_user_id):
        """Test that is_active defaults to True."""
        session = ChatSession.objects.create(
            user_id=sample_user_id,
            session_id=str(uuid.uuid4())
        )
        assert session.is_active is True
    
    def test_session_can_be_inactive(self, inactive_session):
        """Test that a session can be inactive."""
        assert inactive_session.is_active is False
    
    def test_session_ordering(self, sample_user_id):
        """Test that sessions are ordered by created_at descending."""
        old_session = ChatSession.objects.create(
            user_id=sample_user_id,
            session_id=str(uuid.uuid4())
        )
        old_session.created_at = timezone.now() - timedelta(hours=2)
        old_session.save()
        
        new_session = ChatSession.objects.create(
            user_id=sample_user_id,
            session_id=str(uuid.uuid4())
        )
        
        sessions = ChatSession.objects.all()
        assert sessions[0].id == new_session.id
        assert sessions[1].id == old_session.id
    
    def test_session_user_filtering(self, sample_user_id, another_user_id):
        """Test filtering sessions by user_id."""
        user1_session = ChatSession.objects.create(
            user_id=sample_user_id,
            session_id=str(uuid.uuid4())
        )
        user2_session = ChatSession.objects.create(
            user_id=another_user_id,
            session_id=str(uuid.uuid4())
        )
        
        user1_sessions = ChatSession.objects.filter(user_id=sample_user_id)
        assert user1_sessions.count() == 1
        assert user1_sessions.first().id == user1_session.id
    
    def test_session_message_count_property(self, sample_session, chat_message_factory):
        """Test the message_count property."""
        assert sample_session.message_count == 0
        
        # Add messages
        chat_message_factory(session=sample_session)
        chat_message_factory(session=sample_session)
        chat_message_factory(session=sample_session)
        
        assert sample_session.message_count == 3
    
    def test_session_cascade_delete(self, sample_session, sample_message):
        """Test that deleting a session deletes its messages."""
        session_id = sample_session.id
        message_id = sample_message.id
        
        # Verify message exists
        assert ChatMessage.objects.filter(id=message_id).exists()
        
        # Delete session
        sample_session.delete()
        
        # Verify message is also deleted
        assert not ChatSession.objects.filter(id=session_id).exists()
        assert not ChatMessage.objects.filter(id=message_id).exists()
    
    def test_session_updated_at_auto_update(self, sample_session):
        """Test that updated_at is automatically updated."""
        original_updated = sample_session.updated_at
        
        # Wait a bit and update
        import time
        time.sleep(0.1)
        
        sample_session.is_active = False
        sample_session.save()
        
        assert sample_session.updated_at > original_updated


@pytest.mark.django_db
class TestChatMessageModel:
    """Tests for the ChatMessage model."""
    
    def test_create_chat_message(self, sample_session):
        """Test creating a chat message."""
        message = ChatMessage.objects.create(
            session=sample_session,
            role='user',
            content='Test message content'
        )
        
        assert message.id is not None
        assert message.session == sample_session
        assert message.role == 'user'
        assert message.content == 'Test message content'
        assert message.timestamp is not None
    
    def test_message_str_representation(self, sample_message):
        """Test the string representation of a message."""
        expected = f"{sample_message.role}: {sample_message.content[:50]}"
        assert str(sample_message) == expected
    
    def test_message_str_truncated(self, sample_session):
        """Test string representation truncates long messages."""
        long_content = "A" * 100
        message = ChatMessage.objects.create(
            session=sample_session,
            role='user',
            content=long_content
        )
        
        str_repr = str(message)
        assert len(str_repr) <= 56  # "user: " + 50 chars
        assert str_repr == f"user: {long_content[:50]}"
    
    def test_message_role_choices(self, sample_session):
        """Test all valid message role choices."""
        roles = ['user', 'assistant', 'system']
        
        for role in roles:
            message = ChatMessage.objects.create(
                session=sample_session,
                role=role,
                content=f'Test {role} message'
            )
            assert message.role == role
    
    def test_message_ordering(self, sample_session):
        """Test that messages are ordered by timestamp."""
        old_message = ChatMessage.objects.create(
            session=sample_session,
            role='user',
            content='Old message'
        )
        old_message.timestamp = timezone.now() - timedelta(minutes=10)
        old_message.save()
        
        new_message = ChatMessage.objects.create(
            session=sample_session,
            role='assistant',
            content='New message'
        )
        
        messages = sample_session.messages.all()
        assert messages[0].id == old_message.id
        assert messages[1].id == new_message.id
    
    def test_message_token_count_optional(self, sample_session):
        """Test that token_count is optional."""
        message = ChatMessage.objects.create(
            session=sample_session,
            role='user',
            content='Test message'
        )
        assert message.token_count is None
        
        message.token_count = 50
        message.save()
        assert message.token_count == 50
    
    def test_message_session_relationship(self, sample_session, chat_conversation):
        """Test the relationship between session and messages."""
        messages = sample_session.messages.all()
        assert messages.count() == 3
        assert all(msg.session == sample_session for msg in messages)
    
    def test_message_content_field(self, sample_session):
        """Test that content field accepts long text."""
        long_content = "This is a very long message. " * 100
        message = ChatMessage.objects.create(
            session=sample_session,
            role='user',
            content=long_content
        )
        
        assert message.content == long_content
        assert len(message.content) > 1000
