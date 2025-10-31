from django.contrib import admin
from .models import Appointment, TimeSlot, AppointmentHistory


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_id', 'vehicle_id', 'appointment_type', 
                    'scheduled_date', 'scheduled_time', 'status', 'created_at']
    list_filter = ['status', 'appointment_type', 'scheduled_date']
    search_fields = ['customer_id', 'vehicle_id', 'service_description']
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at', 'completed_at']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'is_available', 'max_concurrent_appointments']
    list_filter = ['is_available', 'date']
    ordering = ['date', 'start_time']


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'previous_status', 'new_status', 'changed_by_user_id', 'changed_at']
    list_filter = ['previous_status', 'new_status', 'changed_at']
    readonly_fields = ['changed_at']
    ordering = ['-changed_at']

