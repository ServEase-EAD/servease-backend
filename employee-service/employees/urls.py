from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeListCreateView,
    EmployeeRetrieveUpdateDestroyView,
    AssignedTasksViewSet,
)

router = DefaultRouter()
router.register(r'assigned-tasks', AssignedTasksViewSet, basename='assigned-tasks')

urlpatterns = [
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<uuid:pk>/', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-detail'),
    path('v1/employee/', include(router.urls)),
]