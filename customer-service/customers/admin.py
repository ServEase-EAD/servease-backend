from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email',
                    'phone', 'is_verified', 'customer_since']
    list_filter = ['is_verified', 'customer_since', 'created_at']
    search_fields = ['first_name', 'last_name',
                     'email', 'phone', 'company_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'customer_since']

    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'user_id', 'first_name', 'last_name', 'email')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Business Information', {
            'fields': ('company_name',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'),
            'classes': ('collapse',)
        }),
        ('Status & Dates', {
            'fields': ('is_verified', 'customer_since', 'last_service_date', 'created_at', 'updated_at')
        })
    )
