from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny # For development; should be IsAuthenticated in production
from .models import Notification
from .serializers import NotificationSerializer
from django.utils import timezone

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Notification CRUD and custom actions.
    Should be filtered by the authenticated user's ID in production.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny] # Set to IsAuthenticated for production
    http_method_names = ['get', 'post', 'delete'] # Limit methods

    def get_queryset(self):
        """Filter notifications by recipient_user_id (in a real scenario)"""
        # In a real microservice, you would get the user ID from the Auth token
        # For now, we return all or allow filtering by query param for testing
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('recipient_user_id')
        if user_id:
            return queryset.filter(recipient_user_id=user_id)
        return queryset

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a specific notification as read."""
        try:
            notification = self.get_object()
            if not notification.read_at:
                notification.read_at = timezone.now()
                notification.save()
                return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
            return Response({'message': 'Notification already read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all unread notifications for a user as read."""
        # For simplicity, we'll mark all unread notifications as read. 
        # In production, this would be scoped to the authenticated user.
        unread_notifications = Notification.objects.filter(read_at__isnull=True)
        count = unread_notifications.update(read_at=timezone.now())
        
        return Response({
            'message': f'{count} notifications marked as read',
            'count': count
        }, status=status.HTTP_200_OK)
# Create your views here.
