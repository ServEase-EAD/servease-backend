from django.urls import path
from .views import (
    EmployeeListCreateView,
    EmployeeRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<uuid:pk>/', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-detail'),
]