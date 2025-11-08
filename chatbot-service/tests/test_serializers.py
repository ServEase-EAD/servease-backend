"""
Unit tests for chatbot service serializers.
"""
import pytest
import uuid
from django.utils import timezone
from chatbot.models import ChatSession, ChatMessage
from chatbot.serializers import (
    ChatMessageSerializer,
    ChatSessionSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer
)


@pytest.mark.django_db
class TestChatMessageSerializer:
    """Tests for ChatMessageSerializer."""
    
    def test_serialize_message(self, sample_message):
        """Test serializing a chat message."""
        serializer = ChatMessageSerializer(sample_message)
        data = serializer.data
        
        assert data['id'] == sample_message.id
        assert data['role'] == sample_message.role
        assert data['content'] == sample_message.content
        assert 'timestamp' in data
        assert data['token_count'] == sample_message.token_count
    
    def test_serialize_all_fields(self, sample_message):
        """Test that all fields are included."""
        serializer = ChatMessageSerializer(sample_message)
        data = serializer.data
        
        expected_fields = {'id', 'role', 'content', 'timestamp', 'token_count'}
        assert set(data.keys()) == expected_fields
    
    def test_read_only_fields(self):
        """Test that certain fields are read-only."""
        serializer = ChatMessageSerializer()
        meta = serializer.Meta
        
        assert 'id' in meta.read_only_fields
        assert 'timestamp' in meta.read_only_fields
    
    def test_serialize_multiple_messages(self, chat_conversation):
        """Test serializing multiple messages."""
        serializer = ChatMessageSerializer(chat_conversation, many=True)
        data = serializer.data
        
        assert len(data) == 3
        assert all('id' in item for item in data)
        assert all('content' in item for item in data)


@pytest.mark.django_db
class TestChatSessionSerializer:
    """Tests for ChatSessionSerializer."""
    
    def test_serialize_session(self, sample_session):
        """Test serializing a chat session."""
        serializer = ChatSessionSerializer(sample_session)
        data = serializer.data
        
        assert data['id'] == sample_session.id
        assert data['session_id'] == sample_session.session_id
        assert str(data['user_id']) == str(sample_session.user_id)
        assert data['is_active'] == sample_session.is_active
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'messages' in data
    
    def test_serialize_session_with_messages(self, sample_session, chat_conversation):
        """Test serializing a session with messages."""
        serializer = ChatSessionSerializer(sample_session)
        data = serializer.data
        
        assert len(data['messages']) == 3
        assert all('content' in msg for msg in data['messages'])
    
    def test_serialize_all_fields(self, sample_session):
        """Test that all fields are included."""
        serializer = ChatSessionSerializer(sample_session)
        data = serializer.data
        
        expected_fields = {'id', 'session_id', 'user_id', 'created_at', 
                          'updated_at', 'is_active', 'messages'}
        assert set(data.keys()) == expected_fields
    
    def test_read_only_fields(self):
        """Test that certain fields are read-only."""
        serializer = ChatSessionSerializer()
        meta = serializer.Meta
        
        assert 'id' in meta.read_only_fields
        assert 'session_id' in meta.read_only_fields
        assert 'created_at' in meta.read_only_fields
        assert 'updated_at' in meta.read_only_fields
    
    def test_messages_field_read_only(self):
        """Test that messages field is read-only."""
        serializer = ChatSessionSerializer()
        # Messages should be read_only through the nested serializer
        assert serializer.fields['messages'].read_only is True


class TestChatRequestSerializer:
    """Tests for ChatRequestSerializer."""
    
    def test_valid_request_with_all_fields(self):
        """Test validation with all fields."""
        data = {
            'message': 'Hello, how can I schedule an appointment?',
            'session_id': str(uuid.uuid4()),
            'model': 'openai/gpt-4o'
        }
        
        serializer = ChatRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['message'] == data['message']
        assert serializer.validated_data['session_id'] == data['session_id']
        assert serializer.validated_data['model'] == data['model']
    
    def test_valid_request_minimum_fields(self):
        """Test validation with only required fields."""
        data = {'message': 'Hello'}
        
        serializer = ChatRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['message'] == 'Hello'
    
    def test_default_model_value(self):
        """Test that model has default value."""
        data = {'message': 'Test message'}
        
        serializer = ChatRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['model'] == 'openai/gpt-4o'
    
    def test_missing_message_field(self):
        """Test validation fails without message."""
        data = {'session_id': str(uuid.uuid4())}
        
        serializer = ChatRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'message' in serializer.errors
    
    def test_empty_message_field(self):
        """Test validation fails with empty message."""
        data = {'message': ''}
        
        serializer = ChatRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'message' in serializer.errors
    
    def test_session_id_optional(self):
        """Test that session_id is optional."""
        data = {'message': 'Test message'}
        
        serializer = ChatRequestSerializer(data=data)
        assert serializer.is_valid()
        # session_id should not be in validated_data or be None/empty
    
    def test_blank_session_id_allowed(self):
        """Test that blank session_id is allowed."""
        data = {
            'message': 'Test message',
            'session_id': ''
        }
        
        serializer = ChatRequestSerializer(data=data)
        assert serializer.is_valid()


class TestChatResponseSerializer:
    """Tests for ChatResponseSerializer."""
    
    def test_valid_response_serialization(self):
        """Test serializing a valid chat response."""
        data = {
            'session_id': str(uuid.uuid4()),
            'message': 'Here is the information you requested.',
            'role': 'assistant',
            'timestamp': timezone.now()
        }
        
        serializer = ChatResponseSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['session_id'] == data['session_id']
        assert serializer.validated_data['message'] == data['message']
        assert serializer.validated_data['role'] == data['role']
    
    def test_all_fields_present(self):
        """Test that all fields are required and present."""
        data = {
            'session_id': str(uuid.uuid4()),
            'message': 'Response message',
            'role': 'assistant',
            'timestamp': timezone.now()
        }
        
        serializer = ChatResponseSerializer(data=data)
        assert serializer.is_valid()
        
        expected_fields = {'session_id', 'message', 'role', 'timestamp'}
        assert set(serializer.validated_data.keys()) == expected_fields
    
    def test_missing_required_fields(self):
        """Test validation fails with missing fields."""
        data = {'message': 'Incomplete response'}
        
        serializer = ChatResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'session_id' in serializer.errors
        assert 'role' in serializer.errors
        assert 'timestamp' in serializer.errors
    
    def test_timestamp_field_type(self):
        """Test that timestamp is a DateTimeField."""
        serializer = ChatResponseSerializer()
        assert hasattr(serializer.fields['timestamp'], 'to_representation')
        # DateTimeField should be present
        from rest_framework import serializers as drf_serializers
        assert isinstance(serializer.fields['timestamp'], drf_serializers.DateTimeField)
