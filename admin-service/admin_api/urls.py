from django.urls import path
from . import views
from . import project_views

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
    
    # ==================== PROJECT MANAGEMENT ====================
    # Project endpoints (Admin only)
    path('projects/', project_views.list_all_projects, name='admin-list-projects'),
    path('projects/pending/', project_views.get_pending_projects, name='admin-pending-projects'),
    path('projects/<str:project_id>/', project_views.get_project_detail, name='admin-project-detail'),
    path('projects/<str:project_id>/approve/', project_views.approve_project, name='admin-approve-project'),
    path('projects/<str:project_id>/reject/', project_views.reject_project, name='admin-reject-project'),
    path('projects/<str:project_id>/assign-employee/', project_views.assign_employee_to_project, name='admin-assign-employee'),
    
    # ==================== TASK MANAGEMENT ====================
    # Task endpoints (Admin only)
    path('tasks/', project_views.list_all_tasks, name='admin-list-tasks'),
    path('tasks/create/', project_views.create_task, name='admin-create-task'),
    path('tasks/<str:task_id>/', project_views.get_task_detail, name='admin-task-detail'),
    path('tasks/<str:task_id>/update/', project_views.update_task, name='admin-update-task'),
    path('tasks/<str:task_id>/delete/', project_views.delete_task, name='admin-delete-task'),
    path('projects/<str:project_id>/tasks/', project_views.get_tasks_by_project, name='admin-project-tasks'),
]
