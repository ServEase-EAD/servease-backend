from django.db import models
import uuid


class ChatSession(models.Model):
    """Store chat sessions for users with proper ownership tracking"""
    user_id = models.UUIDField(
        db_index=True)  # User ID from authentication service
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Fast lookup by user
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['user_id', 'is_active']),  # Fast filtering
        ]

    def __str__(self):
        return f"Session {self.session_id} - User {self.user_id}"

    @property
    def message_count(self):
        """Get the total number of messages in this session"""
        return self.messages.count()


class ChatMessage(models.Model):
    """Store individual chat messages"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    token_count = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            # Fast session message retrieval
            models.Index(fields=['session', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
