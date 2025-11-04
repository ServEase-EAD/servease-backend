from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeListCreateView,
    EmployeeRetrieveUpdateDestroyView,
    AssignedTasksViewSet,
    ProfileView,
    UpdateProfileView,
    ChangePasswordView,
)

router = DefaultRouter()
router.register(r'assigned-tasks', AssignedTasksViewSet, basename='assigned-tasks')

urlpatterns = [
    # Employee management endpoints
    path('', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('<uuid:pk>/', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-detail'),
    
    # Assigned tasks
    path('', include(router.urls)),

    # Profile-related endpoints
    path('profile/', ProfileView.as_view(), name='employee-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='employee-profile-update'),
    path('profile/password/', ChangePasswordView.as_view(), name='employee-profile-password'),
]
