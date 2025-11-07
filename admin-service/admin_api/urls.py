from django.urls import path
from . import views
from . import project_views
from . import appointment_views
from . import vehicle_employee_views

urlpatterns = [
    # ==================== HEALTH & STATISTICS ====================
    path('health/', views.health_check, name='admin-health-check'),
    path('statistics/', views.get_user_statistics, name='user-statistics'),
    path('dashboard/stats/', vehicle_employee_views.get_admin_dashboard_stats, name='dashboard-stats'),
    
    # ==================== USER MANAGEMENT ====================
    path('users/', views.list_users, name='list-users'),
    path('users/create/', views.create_user, name='create-user'),
    path('users/<str:user_id>/', views.get_user_detail, name='user-detail'),
    path('users/<str:user_id>/update/', views.update_user, name='update-user'),
    path('users/<str:user_id>/delete/', views.delete_user, name='delete-user'),
    path('users/<str:user_id>/change-role/', views.change_user_role, name='change-user-role'),
    path('users/<str:user_id>/toggle-status/', views.toggle_user_status, name='toggle-user-status'),
    
    # ==================== PROJECT MANAGEMENT ====================
    path('projects/', project_views.list_all_projects, name='admin-list-projects'),
    path('projects/pending/', project_views.get_pending_projects, name='admin-pending-projects'),
    path('projects/progress/', vehicle_employee_views.get_project_progress_summary, name='admin-project-progress'),
    path('projects/<str:project_id>/', project_views.get_project_detail, name='admin-project-detail'),
    path('projects/<str:project_id>/approve/', project_views.approve_project, name='admin-approve-project'),
    path('projects/<str:project_id>/reject/', project_views.reject_project, name='admin-reject-project'),
    path('projects/<str:project_id>/assign-employee/', project_views.assign_employee_to_project, name='admin-assign-employee'),
    path('projects/<str:project_id>/tasks/', project_views.get_tasks_by_project, name='admin-project-tasks'),
    
    # ==================== TASK MANAGEMENT ====================
    path('tasks/', project_views.list_all_tasks, name='admin-list-tasks'),
    path('tasks/create/', project_views.create_task, name='admin-create-task'),
    path('tasks/assign/', vehicle_employee_views.assign_employee_to_task, name='admin-assign-task'),
    path('tasks/unassign/', vehicle_employee_views.unassign_employee_from_task, name='admin-unassign-task'),
    path('tasks/<str:task_id>/', project_views.get_task_detail, name='admin-task-detail'),
    path('tasks/<str:task_id>/update/', project_views.update_task, name='admin-update-task'),
    path('tasks/<str:task_id>/delete/', project_views.delete_task, name='admin-delete-task'),
    
    # ==================== APPOINTMENT MANAGEMENT ====================
    path('appointments/', appointment_views.list_all_appointments, name='admin-list-appointments'),
    path('appointments/pending/', appointment_views.get_pending_appointments, name='admin-pending-appointments'),
    path('appointments/statistics/', appointment_views.get_appointment_statistics, name='admin-appointment-stats'),
    path('appointments/<str:appointment_id>/', appointment_views.get_appointment_detail, name='admin-appointment-detail'),
    path('appointments/<str:appointment_id>/approve/', appointment_views.approve_appointment, name='admin-approve-appointment'),
    path('appointments/<str:appointment_id>/reject/', appointment_views.reject_appointment, name='admin-reject-appointment'),
    path('appointments/<str:appointment_id>/assign/', appointment_views.assign_employees_to_appointment, name='admin-assign-appointment'),
    path('appointments/<str:appointment_id>/reschedule/', appointment_views.reschedule_appointment, name='admin-reschedule-appointment'),
    path('appointments/<str:appointment_id>/tasks/', appointment_views.get_appointment_tasks, name='admin-appointment-tasks'),
    path('appointments/<str:appointment_id>/tasks/create/', appointment_views.create_appointment_task, name='admin-create-appointment-task'),
    
    # Appointment Task Management
    path('appointment-tasks/<str:task_id>/', appointment_views.update_appointment_task, name='admin-update-appointment-task'),
    path('appointment-tasks/<str:task_id>/delete/', appointment_views.delete_appointment_task, name='admin-delete-appointment-task'),
    
    # ==================== VEHICLE MANAGEMENT ====================
    path('vehicles/', vehicle_employee_views.list_all_vehicles, name='admin-list-vehicles'),
    path('vehicles/<str:vehicle_id>/', vehicle_employee_views.get_vehicle_detail, name='admin-vehicle-detail'),
    path('vehicles/employee/<str:employee_id>/', vehicle_employee_views.get_vehicles_by_employee, name='admin-vehicles-by-employee'),
    path('vehicles/by-service-type/', vehicle_employee_views.get_vehicles_by_service_type, name='admin-vehicles-by-service-type'),
    
    # ==================== EMPLOYEE WORKLOAD MANAGEMENT ====================
    path('employees/workload/', vehicle_employee_views.get_all_employees_workload, name='admin-all-employees-workload'),
    path('employees/<str:employee_id>/workload/', vehicle_employee_views.get_employee_workload, name='admin-employee-workload'),
]
