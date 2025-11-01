"""
URL configuration for appointments app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, TimeSlotViewSet, AppointmentHistoryViewSet

# Create router
router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'time-slots', TimeSlotViewSet, basename='timeslot')
router.register(r'history', AppointmentHistoryViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
]

