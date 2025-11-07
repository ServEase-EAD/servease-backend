"""
Views for Appointment service
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count

from .models import Appointment, TimeSlot, AppointmentHistory
from .serializers import (
    AppointmentSerializer, AppointmentListSerializer,
    TimeSlotSerializer, AppointmentHistorySerializer,
    RescheduleSerializer, AssignEmployeeSerializer,
    StatusUpdateSerializer, AvailableSlotsQuerySerializer
)
from .permissions import IsAppointmentOwnerOrAdmin, IsEmployeeOrAdmin, IsCustomerOrEmployee
from .services.status_handler import (
    update_appointment_status, reschedule_appointment, assign_employee
)
from .services.time_slot_manager import get_available_slots


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter appointments based on user role and query parameters
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(scheduled_date__range=[start_date, end_date])
        
        # Filter by appointment type
        appointment_type = self.request.query_params.get('appointment_type')
        if appointment_type:
            queryset = queryset.filter(appointment_type=appointment_type)
        
        # Role-based filtering
        # Note: In production, implement proper role checking
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(assigned_employee_id=employee_id)
        
        return queryset.order_by('-scheduled_date', '-scheduled_time')
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action"""
        if self.action == 'list':
            return AppointmentListSerializer
        return AppointmentSerializer
    
    def get_serializer_context(self):
        """Add auth token to serializer context"""
        context = super().get_serializer_context()
        # Extract token from Authorization header if present
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            context['auth_token'] = auth_header.split(' ')[1]
        return context
    
    def create(self, request, *args, **kwargs):
        """Create a new appointment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send creation notification to customer
        from .services.service_clients import NotificationServiceClient
        try:
            NotificationServiceClient.send_appointment_notification(
                serializer.instance,
                'created',
                self.get_serializer_context().get('auth_token')
            )
        except Exception as e:
            print(f"Customer notification failed: {e}")
        
        # Send notification to admin users using RabbitMQ
        try:
            from notification_publisher import publish_notification
            
            # For now, send to known admin users
            known_admin_users = [
                "ec0e0759-bdd9-4d43-b971-67b5f2a3cbb9",  # dana@gmail.com
                "01f91762-0714-42fe-b8cf-858e75570562",  # admin@example.com
            ]
            
            appointment = serializer.instance
            admin_message = f"New {appointment.appointment_type} appointment created by customer and requires approval. Scheduled for {appointment.scheduled_date} at {appointment.scheduled_time}."
            
            # Send notification to each admin user via RabbitMQ
            for admin_user_id in known_admin_users:
                try:
                    publish_notification(
                        recipient_user_id=admin_user_id,
                        message=admin_message,
                        title="New Appointment - Action Required",
                        priority="high",
                        notification_type="APPOINTMENT",
                        metadata={
                            "appointment_id": str(appointment.id),
                            "customer_id": str(appointment.customer_id),
                            "scheduled_date": str(appointment.scheduled_date),
                            "scheduled_time": str(appointment.scheduled_time),
                            "appointment_type": appointment.appointment_type,
                            "status": appointment.status,
                            "action_required": "approval"
                        }
                    )
                    print(f"✓ Admin notification sent to user {admin_user_id}")
                except Exception as e:
                    print(f"Failed to send admin notification: {e}")
        
        except Exception as e:
            print(f"Admin notification process failed: {e}")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'], permission_classes=[IsEmployeeOrAdmin])
    def confirm(self, request, pk=None):
        """Confirm an appointment"""
        appointment = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_appointment = update_appointment_status(
            pk,
            'confirmed',
            request.user,
            serializer.validated_data.get('reason', ''),
            self.get_serializer_context().get('auth_token')
        )
        
        return Response({
            'status': 'confirmed',
            'message': 'Appointment confirmed successfully',
            'appointment': AppointmentSerializer(updated_appointment, context=self.get_serializer_context()).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsEmployeeOrAdmin])
    def start(self, request, pk=None):
        """Start an appointment (in-progress)"""
        appointment = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_appointment = update_appointment_status(
            pk,
            'in_progress',
            request.user,
            serializer.validated_data.get('reason', ''),
            self.get_serializer_context().get('auth_token')
        )
        
        return Response({
            'status': 'in_progress',
            'message': 'Appointment started',
            'appointment': AppointmentSerializer(updated_appointment, context=self.get_serializer_context()).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsEmployeeOrAdmin])
    def complete(self, request, pk=None):
        """Complete an appointment"""
        appointment = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_appointment = update_appointment_status(
            pk,
            'completed',
            request.user,
            serializer.validated_data.get('reason', ''),
            self.get_serializer_context().get('auth_token')
        )
        
        return Response({
            'status': 'completed',
            'message': 'Appointment completed successfully',
            'appointment': AppointmentSerializer(updated_appointment, context=self.get_serializer_context()).data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_appointment = update_appointment_status(
            pk,
            'cancelled',
            request.user,
            serializer.validated_data.get('reason', ''),
            self.get_serializer_context().get('auth_token')
        )
        
        return Response({
            'status': 'cancelled',
            'message': 'Appointment cancelled successfully',
            'appointment': AppointmentSerializer(updated_appointment, context=self.get_serializer_context()).data
        })
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment"""
        appointment = self.get_object()
        serializer = RescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_appointment = reschedule_appointment(
            pk,
            serializer.validated_data['new_date'],
            serializer.validated_data['new_time'],
            request.user,
            self.get_serializer_context().get('auth_token')
        )
        
        return Response({
            'status': 'rescheduled',
            'message': 'Appointment rescheduled successfully',
            'appointment': AppointmentSerializer(updated_appointment, context=self.get_serializer_context()).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsEmployeeOrAdmin])
    def assign(self, request, pk=None):
        """Assign an employee to appointment"""
        appointment = self.get_object()
        serializer = AssignEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_appointment = assign_employee(
            pk,
            serializer.validated_data['employee_id'],
            request.user,
            self.get_serializer_context().get('auth_token')
        )
        
        return Response({
            'status': 'assigned',
            'message': 'Employee assigned successfully',
            'appointment': AppointmentSerializer(updated_appointment, context=self.get_serializer_context()).data
        })
    
    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """Get available time slots"""
        serializer = AvailableSlotsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        slots = get_available_slots(
            serializer.validated_data['start_date'],
            serializer.validated_data['end_date'],
            serializer.validated_data.get('duration_minutes', 60)
        )
        
        return Response({
            'count': len(slots),
            'slots': slots
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get appointment statistics"""
        today = timezone.now().date()
        
        stats = {
            'total_appointments': Appointment.objects.count(),
            'pending': Appointment.objects.filter(status='pending').count(),
            'confirmed': Appointment.objects.filter(status='confirmed').count(),
            'in_progress': Appointment.objects.filter(status='in_progress').count(),
            'completed': Appointment.objects.filter(status='completed').count(),
            'cancelled': Appointment.objects.filter(status='cancelled').count(),
            'today': Appointment.objects.filter(scheduled_date=today).count(),
            'completed_today': Appointment.objects.filter(
                completed_at__date=today
            ).count(),
            'upcoming': Appointment.objects.filter(
                scheduled_date__gt=today,
                status__in=['pending', 'confirmed']
            ).count(),
        }
        
        # By appointment type
        stats['by_type'] = dict(
            Appointment.objects.values('appointment_type').annotate(
                count=Count('id')
            ).values_list('appointment_type', 'count')
        )
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get appointment history"""
        appointment = self.get_object()
        history = AppointmentHistory.objects.filter(appointment_id=pk).order_by('-changed_at')
        serializer = AppointmentHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def customer_appointments(self, request):
        """Get appointments for a specific customer"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'customer_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointments = self.get_queryset().filter(customer_id=customer_id)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def employee_schedule(self, request):
        """Get schedule for a specific employee"""
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response(
                {'error': 'employee_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointments = self.get_queryset().filter(assigned_employee_id=employee_id)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vehicle_history(self, request):
        """Get service history for a specific vehicle"""
        vehicle_id = request.query_params.get('vehicle_id')
        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointments = self.get_queryset().filter(vehicle_id=vehicle_id)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing time slots
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter time slots by date range if provided"""
        queryset = super().get_queryset()
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        return queryset.order_by('date', 'start_time')
    
    @action(detail=False, methods=['post'], permission_classes=[IsEmployeeOrAdmin])
    def bulk_create(self, request):
        """Bulk create time slots for a date range"""
        from .services.time_slot_manager import create_time_slots_for_date
        from datetime import datetime, timedelta
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        created_slots = []
        current_date = start
        
        while current_date <= end:
            slots = create_time_slots_for_date(current_date)
            created_slots.extend(slots)
            current_date += timedelta(days=1)
        
        return Response({
            'message': f'Created {len(created_slots)} time slots',
            'count': len(created_slots)
        }, status=status.HTTP_201_CREATED)


class AppointmentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for appointment history
    """
    queryset = AppointmentHistory.objects.all()
    serializer_class = AppointmentHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter history by appointment_id if provided"""
        queryset = super().get_queryset()
        
        appointment_id = self.request.query_params.get('appointment_id')
        if appointment_id:
            queryset = queryset.filter(appointment_id=appointment_id)
        
        return queryset.order_by('-changed_at')

