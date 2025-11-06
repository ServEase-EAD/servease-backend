from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_id',
                    'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user_id']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_preview', 'timestamp']
    list_filter = ['role', 'timestamp']
    search_fields = ['content']

    def content_preview(self, obj):
        return obj.content[:100]
    content_preview.short_description = 'Content'
