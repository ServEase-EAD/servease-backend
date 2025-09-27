from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Public authentication endpoints
    path("register/", UserRegistrationAPIView.as_view(), name="register-user"),
    path("login/", UserLoginAPIView.as_view(), name="login-user"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    
    # User profile endpoints
    path("profile/", current_user_profile, name="current-user-profile"),
    path("profile/update/", update_current_user_profile, name="update-user-profile"),
    
    # Admin endpoints
    path("admin/dashboard/stats/", admin_dashboard_stats, name="admin-dashboard-stats"),
    path("admin/employees/create/", EmployeeRegistrationAPIView.as_view(), name="create-employee"),
    path("admin/employees/", EmployeeListAPIView.as_view(), name="list-employees"),
    path("admin/users/", UserListAPIView.as_view(), name="list-all-users"),
    path("admin/users/<int:pk>/", UserDetailAPIView.as_view(), name="user-detail"),
    path("admin/users/<int:user_id>/toggle-status/", toggle_user_status, name="toggle-user-status"),
]