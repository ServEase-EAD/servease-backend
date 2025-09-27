from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomAdminUser(UserAdmin):
    model = CustomUser
    
    # Configure fields for the admin interface
    list_display = ('email', 'first_name', 'last_name', 'user_role_badge', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('user_role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Role & Permissions', {'fields': ('user_role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'user_role', 'password1', 'password2'),
        }),
    )
    
    def user_role_badge(self, obj):
        """Display user role as a colored badge"""
        color_map = {
            'customer': '#28a745',  # green
            'employee': '#007bff',  # blue
            'admin': '#dc3545',     # red
        }
        color = color_map.get(obj.user_role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_user_role_display()
        )
    user_role_badge.short_description = 'Role'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show role information in the list
        return qs.select_related()

# Optional: Create separate admin views for different user types
class CustomerAdmin(CustomAdminUser):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_role='customer')

class EmployeeAdmin(CustomAdminUser):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_role='employee')

# Uncomment these if you want separate admin sections
# admin.site.register(CustomUser, CustomerAdmin)
# admin.site.register(CustomUser, EmployeeAdmin)
