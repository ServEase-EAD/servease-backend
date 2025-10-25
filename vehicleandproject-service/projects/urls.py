from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

app_name = 'projects'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]

# This generates the following URL patterns:
# GET    /api/v1/projects/                    - List all projects
# POST   /api/v1/projects/                    - Create new project
# GET    /api/v1/projects/{id}/               - Get specific project
# PUT    /api/v1/projects/{id}/               - Update project
# PATCH  /api/v1/projects/{id}/               - Partial update
# DELETE /api/v1/projects/{id}/

# Custom actions:
# POST /api/v1/projects/{project_id}/not_started/    - Mark project as not started(not started, in progress, completed, accepted, rejected)