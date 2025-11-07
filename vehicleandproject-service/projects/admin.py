from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'title', 'customer_id', 'status', 'approval_status', 'created_at']
    list_filter = ['status', 'approval_status', 'created_at']
    search_fields = ['title', 'description', 'customer_id']
    readonly_fields = ['project_id', 'created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project_id', 'title', 'description', 'vehicle', 'customer_id')
        }),
        ('Project Status', {
            'fields': ('status', 'approval_status')
        }),
        ('Timeline', {
            'fields': ('expected_completion_date', 'created_at', 'updated_at')
        }),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'title', 'project', 'status', 'priority', 'assigned_employee_id', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description', 'project__title', 'assigned_employee_id']
    readonly_fields = ['task_id', 'created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('task_id', 'project', 'title', 'description')
        }),
        ('Task Details', {
            'fields': ('status', 'priority', 'due_date', 'assigned_employee_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
