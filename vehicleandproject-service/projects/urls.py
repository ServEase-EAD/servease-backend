from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TaskViewSet

# Create separate routers to avoid UUID/tasks conflict
project_router = DefaultRouter()
project_router.register(r'', ProjectViewSet, basename='project')

task_router = DefaultRouter()
task_router.register(r'', TaskViewSet, basename='task')

app_name = 'projects'

# UUID pattern for project IDs
uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

urlpatterns = [
    # Tasks endpoints - put these first to avoid conflicts
    path('tasks/', include(task_router.urls)),
    
    # Project list and custom actions (non-UUID paths)
    path('', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),
    path('by_vehicle/', ProjectViewSet.as_view({'get': 'by_vehicle'}), name='project-by-vehicle'),
    path('customer_projects/', ProjectViewSet.as_view({'get': 'customer_projects'}), name='project-customer-projects'),
    
    # Project detail with specific UUID pattern
    re_path(f'^(?P<project_id>{uuid_pattern})/$', 
            ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 
                                   'patch': 'partial_update', 'delete': 'destroy'}),
            name='project-detail'),
    re_path(f'^(?P<project_id>{uuid_pattern})/change_status/$', 
            ProjectViewSet.as_view({'post': 'change_status'}),
            name='project-change-status'),
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