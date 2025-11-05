from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='admin-health-check'),
    
    # User management endpoints
    path('users/', views.list_users, name='list-users'),
    path('users/create/', views.create_user, name='create-user'),
    path('users/<str:user_id>/', views.get_user_detail, name='user-detail'),
    path('users/<str:user_id>/update/', views.update_user, name='update-user'),
    path('users/<str:user_id>/delete/', views.delete_user, name='delete-user'),
    path('users/<str:user_id>/change-role/', views.change_user_role, name='change-user-role'),
    path('users/<str:user_id>/toggle-status/', views.toggle_user_status, name='toggle-user-status'),
    
    # Statistics
    path('statistics/', views.get_user_statistics, name='user-statistics'),
]
