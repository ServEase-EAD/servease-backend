from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimeLogViewSet, ShiftViewSet, DailyTimeTotalViewSet

# Create separate routers for different URL structures
default_router = DefaultRouter()
default_router.register(r'shifts', ShiftViewSet, basename='shift')
default_router.register(r'daily-totals', DailyTimeTotalViewSet, basename='daily-total')

app_name = 'timelogs'

urlpatterns = [
    # Employee-specific timelog endpoints (employee_id from JWT token)
    # Base endpoints for current logged-in employee
    path('', TimeLogViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='employee-timelogs-list'),
    
    # Individual log detail endpoints
    path('<uuid:log_id>/', TimeLogViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='employee-timelog-detail'),
    
    # Timelog actions
    path('<uuid:log_id>/start/', TimeLogViewSet.as_view({
        'post': 'start'
    }), name='employee-timelog-start'),
    
    path('<uuid:log_id>/pause/', TimeLogViewSet.as_view({
        'post': 'pause'
    }), name='employee-timelog-pause'),
    
    path('<uuid:log_id>/complete/', TimeLogViewSet.as_view({
        'post': 'complete'
    }), name='employee-timelog-complete'),
    
    # Employee stats and logs
    path('logs/', TimeLogViewSet.as_view({
        'get': 'employee_logs'
    }), name='employee-logs'),
    
    path('stats/', TimeLogViewSet.as_view({
        'get': 'stats'
    }), name='employee-stats'),
    
    # Daily totals for employee
    path('daily-totals/', DailyTimeTotalViewSet.as_view({
        'get': 'by_employee'
    }), name='employee-daily-totals'),
    
    # Include default router URLs for shifts and other resources
    path('', include(default_router.urls)),
]

# Generated URLs (employee_id extracted from JWT token):
# GET/POST   /api/v1/employees/timelogs/                         - List/Create time logs for logged-in employee
# GET        /api/v1/employees/timelogs/{log_id}/                - Get specific time log
# PUT/PATCH  /api/v1/employees/timelogs/{log_id}/                - Update time log
# DELETE     /api/v1/employees/timelogs/{log_id}/                - Delete time log
# POST       /api/v1/employees/timelogs/{log_id}/start/          - Start/resume log
# POST       /api/v1/employees/timelogs/{log_id}/pause/          - Pause log
# POST       /api/v1/employees/timelogs/{log_id}/complete/       - Complete log
# GET        /api/v1/employees/timelogs/logs/                    - Get employee logs with filters
# GET        /api/v1/employees/timelogs/stats/                   - Get employee statistics
# GET        /api/v1/employees/timelogs/daily-totals/            - Get daily totals for employee
# GET/POST   /api/v1/employees/timelogs/shifts/                  - List/Create shifts
# POST       /api/v1/employees/timelogs/shifts/start_shift/      - Start new shift
# POST       /api/v1/employees/timelogs/shifts/{id}/end_shift/   - End shift
# GET        /api/v1/employees/timelogs/daily-totals/            - List all daily totals