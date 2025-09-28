from django.urls import path
from .views import CustomerViewSet
from rest_framework.routers import DefaultRouter

# Create router and register viewsets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = router.urls
