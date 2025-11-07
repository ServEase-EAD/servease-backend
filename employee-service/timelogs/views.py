from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from decimal import Decimal
from .models import TimeLog, Shift, DailyTimeTotal
from .serializers import (
    TimeLogSerializer, 
    TimeLogListSerializer, 
    TimeLogStatusUpdateSerializer,
    ShiftSerializer, 
    DailyTimeTotalSerializer
)


def update_daily_total(employee_id, log_date):
    """Calculate and update daily total for an employee on a specific date"""
    # Get all completed logs for this employee on this date
    logs = TimeLog.objects.filter(
        employee_id=employee_id,
        log_date=log_date,
        status='completed'
    )
    
    # Calculate totals
    total_seconds = logs.aggregate(Sum('duration_seconds'))['duration_seconds__sum'] or 0
    total_hours = Decimal(total_seconds) / Decimal(3600)
    total_tasks = logs.count()
    
    # Calculate breakdown by task type
    project_logs = logs.filter(task_type='project')
    appointment_logs = logs.filter(task_type='appointment')
    
    project_seconds = project_logs.aggregate(Sum('duration_seconds'))['duration_seconds__sum'] or 0
    appointment_seconds = appointment_logs.aggregate(Sum('duration_seconds'))['duration_seconds__sum'] or 0
    
    project_hours = Decimal(project_seconds) / Decimal(3600)
    appointment_hours = Decimal(appointment_seconds) / Decimal(3600)
    
    # Update or create daily total
    daily_total, created = DailyTimeTotal.objects.update_or_create(
        employee_id=employee_id,
        log_date=log_date,
        defaults={
            'total_seconds': total_seconds,
            'total_hours': round(total_hours, 2),
            'total_tasks': total_tasks,
            'project_tasks_count': project_logs.count(),
            'appointment_tasks_count': appointment_logs.count(),
            'project_hours': round(project_hours, 2),
            'appointment_hours': round(appointment_hours, 2),
        }
    )
    
    return daily_total


class TimeLogViewSet(viewsets.ModelViewSet):
    """ViewSet for TimeLog CRUD operations"""
    queryset = TimeLog.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'log_id'
    # Disable destroy action - employees cannot delete timelogs
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    
    def get_employee_id(self):
        """Extract employee_id from JWT token"""
        if hasattr(self.request, 'user') and hasattr(self.request.user, 'id'):
            return self.request.user.id
        return None
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return TimeLogListSerializer
        elif self.action in ['update', 'partial_update']:
            # Employees can only update status, not other details
            return TimeLogStatusUpdateSerializer
        return TimeLogSerializer
    
    def get_queryset(self):
        """Filter queryset by employee_id from JWT token"""
        queryset = TimeLog.objects.all()
        employee_id = self.get_employee_id()
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Override create to set employee_id from JWT token and update daily totals"""
        employee_id = self.get_employee_id()
        if not employee_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"error": "Unable to extract employee_id from token"})
        
        # Check if there's already a task in progress for this employee
        existing_in_progress = TimeLog.objects.filter(
            employee_id=employee_id,
            status='inprogress'
        ).exists()
        
        if existing_in_progress and serializer.validated_data.get('status') == 'inprogress':
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "error": "Cannot start a new task. Another task is already in progress. Please pause or complete the current task first."
            })
        
        # Check if this specific task already has an active log (non-completed)
        task_type = serializer.validated_data.get('task_type')
        if task_type == 'appointment':
            appointment_id = serializer.validated_data.get('appointment_id')
            existing_log = TimeLog.objects.filter(
                employee_id=employee_id,
                task_type='appointment',
                appointment_id=appointment_id,
                status__in=['inprogress', 'paused']
            ).exists()
        else:  # project
            project_id = serializer.validated_data.get('project_id')
            existing_log = TimeLog.objects.filter(
                employee_id=employee_id,
                task_type='project',
                project_id=project_id,
                status__in=['inprogress', 'paused']
            ).exists()
        
        if existing_log:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "error": "This task already has an active time log. Resume the existing log or complete it first."
            })
        
        instance = serializer.save(employee_id=employee_id)
        
        if instance.status == 'completed' and instance.log_date:
            update_daily_total(instance.employee_id, instance.log_date)
    
    def perform_update(self, serializer):
        """Override update to update daily totals and enforce immutability rules"""
        # Get the instance before updating
        instance = self.get_object()
        
        # Check if the timelog is completed - completed timelogs are immutable
        if instance.status == 'completed':
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "error": "Cannot edit a completed timelog. Completed timelogs are immutable."
            })
        
        instance = serializer.save()
        if instance.log_date:
            update_daily_total(instance.employee_id, instance.log_date)
    
    def update(self, request, *args, **kwargs):
        """Update timelog - employees can only change status, and completed timelogs are immutable"""
        instance = self.get_object()
        
        # Check if timelog is completed - completed timelogs cannot be edited
        if instance.status == 'completed':
            return Response(
                {'error': 'Cannot edit a completed timelog. Completed timelogs are immutable.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Employees can only update the status field, no other fields
        # Check if any fields other than 'status' are being updated
        allowed_fields = {'status'}
        attempted_fields = set(request.data.keys())
        
        if not attempted_fields.issubset(allowed_fields):
            disallowed_fields = attempted_fields - allowed_fields
            return Response(
                {
                    'error': f'Employees can only update the status field. Cannot update: {", ".join(disallowed_fields)}',
                    'allowed_fields': list(allowed_fields)
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            # Return full timelog details after status update
            response_serializer = TimeLogSerializer(instance)
            return Response(
                {
                    'message': 'Timelog status updated successfully',
                    'data': response_serializer.data
                }
            )
        return Response(
            {
                'message': 'Error updating timelog',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def employee_logs(self, request):
        """Get time logs for logged-in employee with filtering"""
        employee_id = self.get_employee_id()
        
        if not employee_id:
            return Response(
                {'error': 'Unable to extract employee_id from token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter by time period
        time_filter = request.query_params.get('filter', 'all_time')
        logs = TimeLog.objects.filter(employee_id=employee_id)
        
        now = datetime.now()
        if time_filter == 'today':
            logs = logs.filter(log_date=now.date())
        elif time_filter == 'this_week':
            start_week = now - timedelta(days=now.weekday())
            logs = logs.filter(log_date__gte=start_week.date())
        elif time_filter == 'this_month':
            logs = logs.filter(log_date__year=now.year, log_date__month=now.month)
        
        # Group by date
        logs_by_date = {}
        for log in logs:
            date_key = log.log_date.strftime('%Y-%m-%d')
            if date_key not in logs_by_date:
                logs_by_date[date_key] = []
            logs_by_date[date_key].append(TimeLogSerializer(log).data)
        
        return Response({
            'employee_id': employee_id,
            'filter': time_filter,
            'time_logs': list(logs.values()),  # Convert to list for serialization
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics for logged-in employee time logs"""
        employee_id = self.get_employee_id()
        
        if not employee_id:
            return Response({'error': 'Unable to extract employee_id from token'}, status=400)
        
        time_filter = request.query_params.get('filter', 'all_time')
        logs = TimeLog.objects.filter(employee_id=employee_id, status='completed')
        
        # Apply time filter
        now = datetime.now()
        if time_filter == 'today':
            logs = logs.filter(log_date=now.date())
        elif time_filter == 'this_week':
            start_week = now - timedelta(days=now.weekday())
            logs = logs.filter(log_date__gte=start_week.date())
        elif time_filter == 'this_month':
            logs = logs.filter(log_date__year=now.year, log_date__month=now.month)
        
        total_seconds = logs.aggregate(Sum('duration_seconds'))['duration_seconds__sum'] or 0
        total_hours = total_seconds / 3600
        total_entries = logs.count()
        
        # Calculate average hours per day
        days_with_logs = logs.values('log_date').distinct().count()
        avg_hours = (total_hours / days_with_logs) if days_with_logs > 0 else 0
        
        # Breakdown by task type
        project_count = logs.filter(task_type='project').count()
        appointment_count = logs.filter(task_type='appointment').count()
        
        return Response({
            'employee_id': employee_id,
            'total_hours': f"{total_hours:.1f}h",
            'total_entries': total_entries,
            'avg_hours_per_day': f"{avg_hours:.1f}h",
            'days_worked': days_with_logs,
            'breakdown': {
                'project_tasks': project_count,
                'appointment_tasks': appointment_count
            },
            'filter': time_filter
        })
    
    @action(detail=False, methods=['post'])
    def fix_durations(self, request):
        """Fix duration_seconds for completed logs that have 0 duration but have start_time and end_time"""
        employee_id = self.get_employee_id()
        
        if not employee_id:
            return Response({'error': 'Unable to extract employee_id from token'}, status=400)
        
        # Find completed logs with 0 duration but have both start_time and end_time
        broken_logs = TimeLog.objects.filter(
            employee_id=employee_id,
            status='completed',
            duration_seconds=0
        ).exclude(
            Q(start_time__isnull=True) | Q(end_time__isnull=True)
        )
        
        fixed_count = 0
        for log in broken_logs:
            # Calculate duration from start_time to end_time
            duration = int((log.end_time - log.start_time).total_seconds())
            if duration > 0:
                log.duration_seconds = duration
                log.save()
                fixed_count += 1
                
                # Update daily totals
                if log.log_date:
                    update_daily_total(log.employee_id, log.log_date)
        
        return Response({
            'message': f'Fixed {fixed_count} time log(s)',
            'fixed_count': fixed_count
        })
    
    @action(detail=True, methods=['post'])
    def start(self, request, log_id=None):
        """Start/resume a time log - resets start_time to track current session"""
        log = self.get_object()
        if log.status == 'completed':
            return Response(
                {'error': 'Cannot restart a completed timelog. Completed timelogs are immutable.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if there's another task already in progress for this employee
        employee_id = self.get_employee_id()
        existing_in_progress = TimeLog.objects.filter(
            employee_id=employee_id,
            status='inprogress'
        ).exclude(log_id=log_id).exists()
        
        if existing_in_progress:
            return Response(
                {'error': 'Cannot start this task. Another task is already in progress. Please pause or complete the current task first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        log.status = 'inprogress'
        log.start_time = timezone.now()  # Reset start_time to track new session
        log.save()
        
        return Response(TimeLogSerializer(log).data)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, log_id=None):
        """Pause a time log - accumulates duration from current session"""
        log = self.get_object()
        
        if log.status == 'completed':
            return Response(
                {'error': 'Cannot pause a completed timelog. Completed timelogs are immutable.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if log.status != 'inprogress':
            return Response(
                {'error': 'Timelog is not in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate elapsed time in current session and add to accumulated duration
        if log.start_time:
            from django.utils import timezone
            elapsed_seconds = int((timezone.now() - log.start_time).total_seconds())
            log.duration_seconds += elapsed_seconds
        
        log.status = 'paused'
        log.save()
        
        return Response(TimeLogSerializer(log).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, log_id=None):
        """Complete a time log - once completed, timelog becomes immutable"""
        log = self.get_object()
        if log.status == 'completed':
            return Response(
                {'error': 'Timelog is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        current_status = log.status  # Store current status before changing
        log.end_time = timezone.now()
        
        # If currently in progress, add the current session time to duration
        if current_status == 'inprogress' and log.start_time:
            elapsed_seconds = int((log.end_time - log.start_time).total_seconds())
            log.duration_seconds += elapsed_seconds
        
        # If paused with 0 duration but has start_time, calculate total duration from start to now
        # This handles edge cases where duration wasn't properly accumulated
        if log.duration_seconds == 0 and log.start_time:
            total_seconds = int((log.end_time - log.start_time).total_seconds())
            log.duration_seconds = total_seconds
        
        log.status = 'completed'
        log.save()
        
        # Sync duration back to the original task/appointment
        self._sync_duration_to_source(log)
        
        # Update daily totals after completion
        if log.log_date:
            update_daily_total(log.employee_id, log.log_date)
        
        return Response(
            {
                'message': 'Timelog completed successfully. Note: Completed timelogs are immutable.',
                'data': TimeLogSerializer(log).data
            }
        )

    def _sync_duration_to_source(self, log):
        """Sync the duration back to the original task or appointment"""
        import requests
        from django.conf import settings
        
        try:
            if log.task_type == 'appointment' and log.appointment_id:
                # Update appointment duration via API
                appointment_service_url = getattr(settings, 'APPOINTMENT_SERVICE_URL', 'http://appointment-service:8000')
                url = f"{appointment_service_url}/api/v1/appointments/{log.appointment_id}/"
                
                # Get JWT token from request if available
                token = None
                if hasattr(self, 'request') and self.request:
                    auth_header = self.request.headers.get('Authorization', '')
                    if auth_header.startswith('Bearer '):
                        token = auth_header.split(' ')[1]
                
                headers = {'Authorization': f'Bearer {token}'} if token else {}
                
                response = requests.patch(
                    url,
                    json={'duration_seconds': log.duration_seconds},
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"✅ Synced duration to appointment {log.appointment_id}: {log.duration_seconds}s")
                else:
                    print(f"⚠️ Failed to sync duration to appointment {log.appointment_id}: {response.status_code}")
                    
            elif log.task_type == 'project' and log.project_id:
                # Update project task duration via API
                project_service_url = getattr(settings, 'PROJECT_SERVICE_URL', 'http://vehicleandproject-service:8000')
                url = f"{project_service_url}/api/v1/projects/tasks/{log.project_id}/"
                
                # Get JWT token from request if available
                token = None
                if hasattr(self, 'request') and self.request:
                    auth_header = self.request.headers.get('Authorization', '')
                    if auth_header.startswith('Bearer '):
                        token = auth_header.split(' ')[1]
                
                headers = {'Authorization': f'Bearer {token}'} if token else {}
                
                response = requests.patch(
                    url,
                    json={'duration_seconds': log.duration_seconds},
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"✅ Synced duration to project task {log.project_id}: {log.duration_seconds}s")
                else:
                    print(f"⚠️ Failed to sync duration to project task {log.project_id}: {response.status_code}")
                    
        except Exception as e:
            print(f"⚠️ Error syncing duration to source: {str(e)}")
            # Don't fail the completion if sync fails


class ShiftViewSet(viewsets.ModelViewSet):
    """ViewSet for Shift management"""
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'shift_id'
    
    @action(detail=False, methods=['post'])
    def start_shift(self, request):
        """Start a new shift for employee"""
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id required'}, status=400)
        
        # Check if there's an active shift
        active_shift = Shift.objects.filter(
            employee_id=employee_id,
            is_active=True
        ).first()
        
        if active_shift:
            return Response({'error': 'Active shift already exists'}, status=400)
        
        shift = Shift.objects.create(
            employee_id=employee_id,
            shift_date=datetime.now().date(),
            start_time=datetime.now(),
            is_active=True
        )
        
        return Response(ShiftSerializer(shift).data, status=201)
    
    @action(detail=True, methods=['post'])
    def end_shift(self, request, shift_id=None):
        """End an active shift"""
        shift = self.get_object()
        if not shift.is_active:
            return Response({'error': 'Shift already ended'}, status=400)
        
        shift.end_time = datetime.now()
        shift.is_active = False
        
        # Calculate total hours
        duration = (shift.end_time - shift.start_time).total_seconds() / 3600
        shift.total_hours = round(duration, 2)
        shift.save()
        
        return Response(ShiftSerializer(shift).data)


class DailyTimeTotalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing daily time totals (read-only as they are auto-calculated)"""
    queryset = DailyTimeTotal.objects.all()
    serializer_class = DailyTimeTotalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_employee_id(self):
        """Extract employee_id from JWT token"""
        if hasattr(self.request, 'user') and hasattr(self.request.user, 'id'):
            return self.request.user.id
        return None
    
    def get_queryset(self):
        """Filter queryset by employee_id from JWT token"""
        queryset = DailyTimeTotal.objects.all()
        employee_id = self.get_employee_id()
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get daily totals for logged-in employee with date range filtering"""
        employee_id = self.get_employee_id()
        if not employee_id:
            return Response(
                {'error': 'Unable to extract employee_id from token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Date range filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = DailyTimeTotal.objects.filter(employee_id=employee_id)
        
        if start_date:
            queryset = queryset.filter(log_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(log_date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Calculate summary statistics
        total_hours_sum = queryset.aggregate(Sum('total_hours'))['total_hours__sum'] or 0
        total_tasks_sum = queryset.aggregate(Sum('total_tasks'))['total_tasks__sum'] or 0
        
        return Response({
            'employee_id': employee_id,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_hours': f"{total_hours_sum:.2f}h",
                'total_tasks': total_tasks_sum,
                'days_worked': queryset.count()
            },
            'daily_totals': serializer.data
        })

