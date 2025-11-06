from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatbotViewSet

router = DefaultRouter()
router.register(r'', ChatbotViewSet, basename='chatbot')

urlpatterns = [
    path('', include(router.urls)),
]

# api/v1/chatbot/ endpoints are now routed to ChatbotViewSet
# api/v1/chatbot/chat/ for chat interactions
# api/v1/chatbot/sessions/ for session management
# api/v1/chatbot/knowledge/ for knowledge base interactions
# api/v1/chatbot/analytics/ for analytics endpoints