from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from django.utils import timezone
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
            raise ValueError("Unable to extract employee_id from token")
        
        instance = serializer.save(employee_id=employee_id)
        
        if instance.status == 'completed' and instance.log_date:
            update_daily_total(instance.employee_id, instance.log_date)
    
    def perform_update(self, serializer):
        """Override update to update daily totals and enforce immutability rules"""
        # Get the instance before updating
        instance = self.get_object()
        
        # Check if the timelog is completed - completed timelogs are immutable
        if instance.status == 'completed':
            raise ValueError('Cannot edit a completed timelog. Completed timelogs are immutable.')
        
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
    
    @action(detail=True, methods=['post'])
    def start(self, request, log_id=None):
        """Start/resume a time log"""
        log = self.get_object()
        
        if log.status == 'completed':
            return Response(
                {'error': 'Cannot restart a completed timelog. Completed timelogs are immutable.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Debug logging
        print(f"▶️ START/RESUME: Log {log.log_id}")
        print(f"   Previous status: {log.status}")
        print(f"   Accumulated duration: {log.duration_seconds}s")
        
        # Update status and reset start_time for new session
        log.status = 'inprogress'
        log.start_time = timezone.now()  # Use timezone-aware datetime
        log.end_time = None  # Clear end_time when starting/resuming
        
        print(f"   New start time: {log.start_time}")
        print(f"   Duration preserved: {log.duration_seconds}s")
        
        log.save()
        
        serializer = TimeLogSerializer(log)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, log_id=None):
        """Pause a time log and accumulate duration"""
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
        
        # Store previous duration for logging
        previous_duration = log.duration_seconds
        
        # Update status
        log.status = 'paused'
        
        # Calculate duration from current session and add to accumulated duration
        if log.start_time:
            current_session_duration = (timezone.now() - log.start_time).total_seconds()
            log.duration_seconds += int(current_session_duration)
            log.end_time = None  # Clear end_time when pausing (not completing)
            
            # Debug logging
            print(f"⏸️ PAUSE: Log {log.log_id}")
            print(f"   Previous accumulated: {previous_duration}s")
            print(f"   Session duration: {int(current_session_duration)}s")
            print(f"   New accumulated: {log.duration_seconds}s")
            print(f"   Start time was: {log.start_time}")
        
        log.save()
        
        serializer = TimeLogSerializer(log)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, log_id=None):
        """Complete a time log - once completed, timelog becomes immutable"""
        log = self.get_object()
        
        if log.status == 'completed':
            return Response(
                {'error': 'Timelog is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Store previous duration for logging
        previous_duration = log.duration_seconds
        
        # Update status and end time
        log.status = 'completed'
        log.end_time = timezone.now()  # Use timezone-aware datetime
        
        # Calculate final duration and add to accumulated duration
        if log.start_time:
            current_session_duration = (log.end_time - log.start_time).total_seconds()
            log.duration_seconds += int(current_session_duration)  # ADD to accumulated, don't overwrite!
            
            # Debug logging
            print(f"✅ COMPLETE: Log {log.log_id}")
            print(f"   Previous accumulated: {previous_duration}s")
            print(f"   Final session duration: {int(current_session_duration)}s")
            print(f"   Total duration: {log.duration_seconds}s")
            print(f"   Start time was: {log.start_time}")
            print(f"   End time: {log.end_time}")
        
        log.save()
        
        # Update daily totals after completion
        if log.log_date:
            update_daily_total(log.employee_id, log.log_date)
        
        serializer = TimeLogSerializer(log)
        return Response(
            {
                'message': 'Timelog completed successfully. Note: Completed timelogs are immutable.',
                'data': serializer.data
            }
        )


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
        
        now = timezone.now()
        shift = Shift.objects.create(
            employee_id=employee_id,
            shift_date=now.date(),
            start_time=now,
            is_active=True
        )
        
        return Response(ShiftSerializer(shift).data, status=201)
    
    @action(detail=True, methods=['post'])
    def end_shift(self, request, shift_id=None):
        """End an active shift"""
        shift = self.get_object()
        if not shift.is_active:
            return Response({'error': 'Shift already ended'}, status=400)
        
        shift.end_time = timezone.now()
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

