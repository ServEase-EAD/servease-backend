from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TaskViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')  # Empty string since main URL already has 'projects/'

# Create a separate router for tasks to nest under projects
tasks_router = DefaultRouter()
tasks_router.register(r'tasks', TaskViewSet, basename='task')

app_name = 'projects'

urlpatterns = [
    # Include project router URLs
    path('', include(router.urls)),
    # Include tasks router URLs - tasks will be at /api/v1/projects/tasks/
    path('', include(tasks_router.urls)),
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
# Tasks (READ-ONLY, filtered by role):
# GET    /api/v1/projects/tasks/                        - List all tasks (filtered by role)
# GET    /api/v1/projects/tasks/{task_id}/              - Get specific task (read-only)
# GET    /api/v1/projects/tasks/by_project/?project_id=xxx - Get tasks by project
#
# ⚠️  ADMIN OPERATIONS MOVED TO ADMIN-SERVICE:
# The following operations are handled by admin-service, not here:
# - Approve/Reject projects
# - Assign employees to projects
# - Create/Update/Delete tasks
# - View pending approval projects
#
# Access Control:
# - Customer: Create projects (pending approval), view own projects, view tasks for own projects
# - Employee: View assigned projects only, update project status, view tasks for assigned projects
# - Admin: Use admin-service for project approval, employee assignment, and task management