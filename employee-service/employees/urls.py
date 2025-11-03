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
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<uuid:pk>/', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-detail'),
    path('v1/employee/', include(router.urls)),

    # Profile-related endpoints
    path('profile/', ProfileView.as_view(), name='employee-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='employee-profile-update'),
    path('profile/password/', ChangePasswordView.as_view(), name='employee-profile-password'),
]
