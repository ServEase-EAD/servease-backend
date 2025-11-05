from django.contrib import admin
from .models import TimeLog, Shift, DailyTimeTotal


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'employee_id', 'task_type', 'description', 'log_date', 'duration_formatted', 'status']
    list_filter = ['status', 'task_type', 'log_date']
    search_fields = ['employee_id', 'description', 'project_id', 'appointment_id']
    ordering = ['-log_date', '-start_time']
    readonly_fields = ['log_id', 'created_at', 'updated_at']


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['shift_id', 'employee_id', 'shift_date', 'start_time', 'end_time', 'total_hours', 'is_active']
    list_filter = ['is_active', 'shift_date']
    search_fields = ['employee_id']
    ordering = ['-shift_date']
    readonly_fields = ['shift_id', 'created_at', 'updated_at']


@admin.register(DailyTimeTotal)
class DailyTimeTotalAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_id', 'log_date', 'total_hours', 'total_tasks', 'project_tasks_count', 'appointment_tasks_count']
    list_filter = ['log_date']
    search_fields = ['employee_id']
    ordering = ['-log_date']
    readonly_fields = ['id', 'created_at', 'updated_at']

