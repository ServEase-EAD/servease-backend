from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import uuid

from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer
)
from .gemini_client import GeminiClient


class ChatbotViewSet(viewsets.ViewSet):
    """
    ViewSet for handling chatbot operations
    """
    # permission_classes = [IsAuthenticated]  # Uncomment when authentication is ready

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gemini_client = GeminiClient()

    @action(detail=False, methods=['post'], url_path='chat')
    def chat(self, request):
        """
        Handle chat messages and get AI responses

        POST /api/v1/chatbot/chat/
        Body: {
            "message": "Your question here",
            "session_id": "optional-session-id",
            "model": "openai/gpt-4o"  # optional
        }
        """
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        model = serializer.validated_data.get(
            'model', 'gemini-1.5-flash')  # Default to free Gemini

        # Get or create user ID (from JWT token when authentication is implemented)
        user_id = request.user.id if hasattr(
            request.user, 'id') and request.user.is_authenticated else 1

        # Get or create chat session
        if session_id:
            session = get_object_or_404(ChatSession, session_id=session_id)
        else:
            session = ChatSession.objects.create(
                user_id=user_id,
                session_id=str(uuid.uuid4())
            )

        # Save user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )

        # Get conversation history
        messages = self._get_conversation_history(session)

        try:
            # Use Google Gemini API (default for local development)
            response_data = self.gemini_client.create_chat_completion(
                messages=messages,
                model=model
            )
            assistant_message = self.gemini_client.extract_response_content(
                response_data)

            # Save assistant message
            chat_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=assistant_message
            )

            return Response({
                'session_id': session.session_id,
                'message': assistant_message,
                'role': 'assistant',
                'timestamp': chat_message.timestamp
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Failed to get AI response'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='sessions')
    def list_sessions(self, request):
        """
        List all chat sessions for the current user

        GET /api/v1/chatbot/sessions/
        """
        user_id = request.user.id if hasattr(
            request.user, 'id') and request.user.is_authenticated else 1
        sessions = ChatSession.objects.filter(user_id=user_id, is_active=True)
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='session/(?P<session_id>[^/.]+)')
    def get_session(self, request, session_id=None):
        """
        Get a specific chat session with all messages

        GET /api/v1/chatbot/session/{session_id}/
        """
        session = get_object_or_404(ChatSession, session_id=session_id)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='session/(?P<session_id>[^/.]+)/delete')
    def delete_session(self, request, session_id=None):
        """
        Delete (deactivate) a chat session

        DELETE /api/v1/chatbot/session/{session_id}/delete/
        """
        session = get_object_or_404(ChatSession, session_id=session_id)
        session.is_active = False
        session.save()
        return Response({'message': 'Session deleted successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='session/(?P<session_id>[^/.]+)/clear')
    def clear_session(self, request, session_id=None):
        """
        Clear all messages in a session

        POST /api/v1/chatbot/session/{session_id}/clear/
        """
        session = get_object_or_404(ChatSession, session_id=session_id)
        ChatMessage.objects.filter(session=session).delete()
        return Response({'message': 'Session cleared successfully'}, status=status.HTTP_200_OK)

    def _get_conversation_history(self, session, max_messages=10):
        """
        Get the conversation history for context

        Args:
            session: ChatSession object
            max_messages: Maximum number of messages to include

        Returns:
            list: List of message dictionaries for the AI API
        """
        messages = ChatMessage.objects.filter(
            session=session).order_by('-timestamp')[:max_messages]
        messages = reversed(list(messages))

        return [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in messages
        ]

    # Note: OpenRouter-specific credit checking has been removed.
    # This service now uses Google Gemini by default. For quota/usage
    # checks consult your Google Cloud console or implement a
    # provider-specific status endpoint if needed.
