from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
from .permissions import IsAuthenticated, IsOwner


class ChatbotViewSet(viewsets.ViewSet):
    """
    ViewSet for handling chatbot operations with JWT authentication.
    All authenticated users (customer, employee, admin) can use the chatbot.
    Users can only access their own sessions.
    """
    permission_classes = [
        IsAuthenticated]  # Require authentication for all actions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gemini_client = GeminiClient()

    @action(detail=False, methods=['post'], url_path='chat')
    def chat(self, request):
        """
        Handle chat messages and get AI responses.
        Authenticated users can only access their own sessions.

        POST /api/v1/chatbot/chat/
        Headers: {
            "Authorization": "Bearer <jwt_token>"
        }
        Body: {
            "message": "Your question here",
            "session_id": "optional-session-id",
            "model": "gemini-2.5-flash"  # optional - valid models: gemini-2.5-flash, gemini-2.5-pro
        }
        """
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        model = serializer.validated_data.get(
            'model', 'gemini-2.5-flash')  # Default to free Gemini

        # Validate model is a Gemini model
        if not model.startswith('gemini'):
            return Response({
                'error': 'Invalid model',
                'message': f'Only Gemini models are supported. Use models like: gemini-2.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get authenticated user ID from JWT token
        user_id = request.user.id

        # Get or create chat session
        if session_id:
            # Ensure the session belongs to the authenticated user
            try:
                session = ChatSession.objects.get(
                    session_id=session_id,
                    user_id=user_id  # Only allow access to own sessions
                )
            except ChatSession.DoesNotExist:
                return Response({
                    'error': 'Session not found or access denied',
                    'message': 'You can only access your own chat sessions'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Create new session for this user
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
        List all chat sessions for the authenticated user.
        Each user can only see their own sessions.

        GET /api/v1/chatbot/sessions/
        Headers: {
            "Authorization": "Bearer <jwt_token>"
        }
        """
        user_id = request.user.id
        sessions = ChatSession.objects.filter(user_id=user_id, is_active=True)
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response({
            'count': sessions.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='session/(?P<session_id>[^/.]+)')
    def get_session(self, request, session_id=None):
        """
        Get a specific chat session with all messages.
        Users can only access their own sessions.

        GET /api/v1/chatbot/session/{session_id}/
        Headers: {
            "Authorization": "Bearer <jwt_token>"
        }
        """
        user_id = request.user.id
        try:
            session = ChatSession.objects.get(
                session_id=session_id,
                user_id=user_id  # Ensure ownership
            )
        except ChatSession.DoesNotExist:
            return Response({
                'error': 'Session not found or access denied',
                'message': 'You can only access your own chat sessions'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='session/(?P<session_id>[^/.]+)/delete')
    def delete_session(self, request, session_id=None):
        """
        Delete (deactivate) a chat session.
        Users can only delete their own sessions.

        DELETE /api/v1/chatbot/session/{session_id}/delete/
        Headers: {
            "Authorization": "Bearer <jwt_token>"
        }
        """
        user_id = request.user.id
        try:
            session = ChatSession.objects.get(
                session_id=session_id,
                user_id=user_id  # Ensure ownership
            )
        except ChatSession.DoesNotExist:
            return Response({
                'error': 'Session not found or access denied',
                'message': 'You can only delete your own chat sessions'
            }, status=status.HTTP_404_NOT_FOUND)

        session.is_active = False
        session.save()
        return Response({
            'message': 'Session deleted successfully',
            'session_id': session.session_id
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='session/(?P<session_id>[^/.]+)/clear')
    def clear_session(self, request, session_id=None):
        """
        Clear all messages in a session.
        Users can only clear their own sessions.

        POST /api/v1/chatbot/session/{session_id}/clear/
        Headers: {
            "Authorization": "Bearer <jwt_token>"
        }
        """
        user_id = request.user.id
        try:
            session = ChatSession.objects.get(
                session_id=session_id,
                user_id=user_id  # Ensure ownership
            )
        except ChatSession.DoesNotExist:
            return Response({
                'error': 'Session not found or access denied',
                'message': 'You can only clear your own chat sessions'
            }, status=status.HTTP_404_NOT_FOUND)

        ChatMessage.objects.filter(session=session).delete()
        return Response({
            'message': 'Session cleared successfully',
            'session_id': session.session_id
        }, status=status.HTTP_200_OK)

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
