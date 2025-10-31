from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'timestamp', 'token_count']
        read_only_fields = ['id', 'timestamp']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'session_id', 'user_id', 'created_at',
                  'updated_at', 'is_active', 'messages']
        read_only_fields = ['id', 'session_id', 'created_at', 'updated_at']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat request"""
    message = serializers.CharField(required=True)
    session_id = serializers.CharField(required=False, allow_blank=True)
    model = serializers.CharField(required=False, default="openai/gpt-4o")


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response"""
    session_id = serializers.CharField()
    message = serializers.CharField()
    role = serializers.CharField()
    timestamp = serializers.DateTimeField()
