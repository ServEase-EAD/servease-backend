"""
Unit tests for TimeLog, Shift, and DailyTimeTotal models.
"""
import pytest
from datetime import date, timedelta
from django.utils import timezone
from timelogs.models import TimeLog, Shift, DailyTimeTotal
import uuid


@pytest.mark.django_db
class TestTimeLogModel:
    """Tests for the TimeLog model."""
    
    def test_create_timelog(self, timelog_factory):
        """Test creating a time log entry."""
        timelog = timelog_factory()
        
        assert timelog.log_id is not None
        assert timelog.employee_id is not None
        assert timelog.task_type == 'appointment'
    
    def test_timelog_str_representation(self, sample_timelog):
        """Test string representation of time log."""
        expected = f"{sample_timelog.task_type} - {sample_timelog.description}"
        assert str(sample_timelog) == expected
    
    def test_timelog_duration_formatted(self, timelog_factory):
        """Test duration formatting."""
        # 2 hours = 7200 seconds
        timelog = timelog_factory(duration_seconds=7200)
        assert timelog.duration_formatted == "02:00:00"
        
        # 1 hour 30 minutes 45 seconds = 5445 seconds
        timelog2 = timelog_factory(duration_seconds=5445)
        assert timelog2.duration_formatted == "01:30:45"
    
    def test_timelog_duration_zero(self, timelog_factory):
        """Test duration formatting for zero duration."""
        timelog = timelog_factory(duration_seconds=0)
        assert timelog.duration_formatted == "00:00:00"
    
    def test_timelog_task_type_project(self, timelog_factory):
        """Test time log with project task type."""
        timelog = timelog_factory(
            task_type='project',
            project_id='PROJ123',
            appointment_id=None
        )
        
        assert timelog.task_type == 'project'
        assert timelog.project_id == 'PROJ123'
    
    def test_timelog_task_type_appointment(self, timelog_factory):
        """Test time log with appointment task type."""
        timelog = timelog_factory(
            task_type='appointment',
            appointment_id='APP456',
            project_id=None
        )
        
        assert timelog.task_type == 'appointment'
        assert timelog.appointment_id == 'APP456'
    
    def test_timelog_status_choices(self, timelog_factory):
        """Test different status values."""
        inprogress = timelog_factory(status='inprogress')
        completed = timelog_factory(status='completed')
        paused = timelog_factory(status='paused')
        
        assert inprogress.status == 'inprogress'
        assert completed.status == 'completed'
        assert paused.status == 'paused'
    
    def test_timelog_auto_set_log_date(self, timelog_factory):
        """Test that log_date is automatically set from start_time."""
        start_time = timezone.now()
        timelog = timelog_factory(start_time=start_time)
        
        assert timelog.log_date == start_time.date()
    
    def test_timelog_with_shift(self, timelog_factory, active_shift):
        """Test time log associated with a shift."""
        timelog = timelog_factory(shift=active_shift)
        
        assert timelog.shift == active_shift
        assert timelog in active_shift.time_logs.all()
    
    def test_timelog_with_vehicle_and_service(self, timelog_factory):
        """Test time log with vehicle and service details."""
        timelog = timelog_factory(
            vehicle='BMW X5',
            service='Brake Inspection'
        )
        
        assert timelog.vehicle == 'BMW X5'
        assert timelog.service == 'Brake Inspection'
    
    def test_timelog_completion(self, sample_timelog):
        """Test completing a time log."""
        sample_timelog.end_time = timezone.now()
        sample_timelog.status = 'completed'
        sample_timelog.duration_seconds = 3600
        sample_timelog.save()
        
        sample_timelog.refresh_from_db()
        assert sample_timelog.status == 'completed'
        assert sample_timelog.end_time is not None
    
    def test_timelog_ordering(self, timelog_factory):
        """Test that time logs are ordered by date and time descending."""
        now = timezone.now()
        log1 = timelog_factory(start_time=now - timedelta(days=2))
        log2 = timelog_factory(start_time=now - timedelta(days=1))
        log3 = timelog_factory(start_time=now)
        
        logs = list(TimeLog.objects.all())
        assert logs[0].start_time >= logs[1].start_time
        assert logs[1].start_time >= logs[2].start_time


@pytest.mark.django_db
class TestShiftModel:
    """Tests for the Shift model."""
    
    def test_create_shift(self, shift_factory):
        """Test creating a shift."""
        shift = shift_factory()
        
        assert shift.shift_id is not None
        assert shift.employee_id is not None
        assert shift.is_active is True
    
    def test_shift_str_representation(self, active_shift):
        """Test string representation of shift."""
        expected = f"Shift {active_shift.shift_date} - Employee {active_shift.employee_id}"
        assert str(active_shift) == expected
    
    def test_shift_with_end_time(self, shift_factory):
        """Test shift with end time."""
        now = timezone.now()
        shift = shift_factory(
            start_time=now - timedelta(hours=8),
            end_time=now,
            total_hours=8.0,
            is_active=False
        )
        
        assert shift.end_time is not None
        assert shift.total_hours == 8.0
        assert shift.is_active is False
    
    def test_shift_active_status(self, active_shift):
        """Test active shift status."""
        assert active_shift.is_active is True
        assert active_shift.end_time is None
    
    def test_shift_with_time_logs(self, active_shift, timelog_factory):
        """Test shift with associated time logs."""
        log1 = timelog_factory(shift=active_shift)
        log2 = timelog_factory(shift=active_shift)
        
        assert active_shift.time_logs.count() == 2
        assert log1 in active_shift.time_logs.all()
        assert log2 in active_shift.time_logs.all()
    
    def test_shift_ordering(self, shift_factory):
        """Test that shifts are ordered by date descending."""
        shift1 = shift_factory(shift_date=date.today() - timedelta(days=2))
        shift2 = shift_factory(shift_date=date.today() - timedelta(days=1))
        shift3 = shift_factory(shift_date=date.today())
        
        shifts = list(Shift.objects.all())
        assert shifts[0].shift_date >= shifts[1].shift_date
        assert shifts[1].shift_date >= shifts[2].shift_date


@pytest.mark.django_db
class TestDailyTimeTotalModel:
    """Tests for the DailyTimeTotal model."""
    
    def test_create_daily_total(self, daily_total_factory):
        """Test creating a daily time total."""
        total = daily_total_factory()
        
        assert total.id is not None
        assert total.employee_id is not None
        assert total.total_hours == 8.0
    
    def test_daily_total_str_representation(self, sample_daily_total):
        """Test string representation of daily total."""
        expected = f"Employee {sample_daily_total.employee_id} - {sample_daily_total.log_date}: {sample_daily_total.total_hours}h"
        assert str(sample_daily_total) == expected
    
    def test_daily_total_hours_formatted(self, daily_total_factory):
        """Test formatted total hours property."""
        total = daily_total_factory(total_hours=12.50)
        assert total.total_hours_formatted == "12.50h"
    
    def test_daily_total_task_breakdown(self, daily_total_factory):
        """Test task type breakdown."""
        total = daily_total_factory(
            total_tasks=10,
            project_tasks_count=4,
            appointment_tasks_count=6,
            project_hours=3.5,
            appointment_hours=4.5
        )
        
        assert total.total_tasks == 10
        assert total.project_tasks_count == 4
        assert total.appointment_tasks_count == 6
        assert total.project_hours == 3.5
        assert total.appointment_hours == 4.5
    
    def test_daily_total_unique_constraint(self, daily_total_factory):
        """Test unique constraint on employee_id and log_date."""
        employee_id = uuid.uuid4()
        log_date = date.today()
        
        daily_total_factory(employee_id=employee_id, log_date=log_date)
        
        # Attempting to create another for same employee and date should fail
        with pytest.raises(Exception):  # Django raises IntegrityError
            daily_total_factory(employee_id=employee_id, log_date=log_date)
    
    def test_daily_total_ordering(self, daily_total_factory):
        """Test that daily totals are ordered by date descending."""
        total1 = daily_total_factory(log_date=date.today() - timedelta(days=2))
        total2 = daily_total_factory(log_date=date.today() - timedelta(days=1))
        total3 = daily_total_factory(log_date=date.today())
        
        totals = list(DailyTimeTotal.objects.all())
        assert totals[0].log_date >= totals[1].log_date
        assert totals[1].log_date >= totals[2].log_date
    
    def test_daily_total_total_seconds(self, daily_total_factory):
        """Test storing total seconds."""
        # 8 hours = 28800 seconds
        total = daily_total_factory(total_hours=8.0, total_seconds=28800)
        
        assert total.total_seconds == 28800
        assert total.total_hours == 8.0
