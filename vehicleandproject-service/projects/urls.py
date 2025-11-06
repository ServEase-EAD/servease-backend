from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TaskViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')  # Empty string since main URL already has 'projects/'

# Create a separate router for tasks
tasks_router = DefaultRouter()
tasks_router.register(r'', TaskViewSet, basename='task')  # Use empty string for task routes

app_name = 'projects'

urlpatterns = [
    # Task routes under /tasks/ prefix - these need to come first to avoid conflicts
    path('tasks/', include(tasks_router.urls)),
    # Project routes - these are at the root level
    path('', include(router.urls)),
]

# This generates the following URL patterns:
# 
# Projects (Customer-facing operations):
# GET    /api/v1/projects/                              - List all projects (filtered by role)
# POST   /api/v1/projects/                              - Create new project (Customer only)
# GET    /api/v1/projects/{project_id}/                 - Get specific project
# PUT    /api/v1/projects/{project_id}/                 - Update project (Customer - own projects)
# PATCH  /api/v1/projects/{project_id}/                 - Partial update (Customer - own projects)
# DELETE /api/v1/projects/{project_id}/                 - Delete project
# POST   /api/v1/projects/{project_id}/change_status/   - Change project status (Employee only)
# GET    /api/v1/projects/by_vehicle/?vehicle_id=xxx    - Get projects by vehicle
# GET    /api/v1/projects/customer_projects/            - Get customer's own projects
#
# Tasks (READ-ONLY for employees/customers, full CRUD for admins):
# GET    /api/v1/projects/tasks/                        - List all tasks (filtered by role)
# POST   /api/v1/projects/tasks/                        - Create task (Admin only)
# GET    /api/v1/projects/tasks/{task_id}/              - Get specific task
# PUT    /api/v1/projects/tasks/{task_id}/              - Update task (Admin only)
# PATCH  /api/v1/projects/tasks/{task_id}/              - Partial update task (Admin only)
# DELETE /api/v1/projects/tasks/{task_id}/              - Delete task (Admin only)
# GET    /api/v1/projects/tasks/by_project/?project_id=xxx - Get tasks by project
#
# ⚠️  IMPORTANT NOTES:
# - Tasks can also be managed via admin-service for centralized admin operations
# - Employees see only tasks assigned to them (filtered by assigned_employee_id from JWT)
# - Customers see only tasks for their projects (filtered by project__customer_id from JWT)
# - Admins can see and manage all tasks
#
# Access Control:
# - Customer: Create projects (pending approval), view own projects, view tasks for own projects
# - Employee: View assigned projects, update project status, view tasks assigned to them
# - Admin: Full access to all projects and tasks