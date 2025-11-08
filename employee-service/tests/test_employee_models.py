"""
Unit tests for Employee and AssignedTask models.
"""
import pytest
import uuid
from datetime import date, timedelta
from django.contrib.auth.models import User
from employees.models import Employee, AssignedTask


@pytest.mark.django_db
class TestEmployeeModel:
    """Tests for the Employee model."""
    
    def test_create_employee(self, employee_factory):
        """Test creating an employee with required fields."""
        employee = employee_factory()
        
        assert employee.id is not None
        assert employee.user is not None
        assert isinstance(employee.id, uuid.UUID)
    
    def test_employee_str_representation(self, sample_employee):
        """Test string representation of employee."""
        expected = f"{sample_employee.user.first_name} {sample_employee.user.last_name}"
        assert str(sample_employee) == expected
    
    def test_employee_with_full_details(self, employee_factory):
        """Test creating employee with all fields."""
        employee = employee_factory(
            phone_number='+1234567890',
            gender='Female',
            date_of_birth=date(1985, 5, 15),
            address_line1='789 Pine St',
            address_line2='Apt 4B',
            city='Seattle',
            postal_code='98101',
            specialization='Electrician',
            experience_years=10,
            hourly_rate=35.50,
            is_available=True
        )
        
        assert employee.phone_number == '+1234567890'
        assert employee.gender == 'Female'
        assert employee.date_of_birth == date(1985, 5, 15)
        assert employee.address_line1 == '789 Pine St'
        assert employee.address_line2 == 'Apt 4B'
        assert employee.city == 'Seattle'
        assert employee.postal_code == '98101'
        assert employee.specialization == 'Electrician'
        assert employee.experience_years == 10
        assert employee.hourly_rate == 35.50
        assert employee.is_available is True
    
    def test_employee_default_values(self, test_user):
        """Test default values for employee fields."""
        employee = Employee.objects.create(
            id=uuid.uuid4(),
            user=test_user
        )
        
        assert employee.experience_years == 0
        assert employee.hourly_rate == 0
        assert employee.is_available is True
    
    def test_employee_user_relationship(self, sample_employee):
        """Test one-to-one relationship with User."""
        assert sample_employee.user is not None
        assert sample_employee.user.employee_profile == sample_employee
    
    def test_employee_availability_toggle(self, sample_employee):
        """Test toggling employee availability."""
        initial_status = sample_employee.is_available
        sample_employee.is_available = not initial_status
        sample_employee.save()
        
        sample_employee.refresh_from_db()
        assert sample_employee.is_available != initial_status
    
    def test_employee_update_specialization(self, sample_employee):
        """Test updating employee specialization."""
        sample_employee.specialization = 'Senior Mechanic'
        sample_employee.save()
        
        sample_employee.refresh_from_db()
        assert sample_employee.specialization == 'Senior Mechanic'
    
    def test_employee_update_hourly_rate(self, sample_employee):
        """Test updating employee hourly rate."""
        sample_employee.hourly_rate = 30.00
        sample_employee.save()
        
        sample_employee.refresh_from_db()
        assert sample_employee.hourly_rate == 30.00


@pytest.mark.django_db
class TestAssignedTaskModel:
    """Tests for the AssignedTask model."""
    
    def test_create_task(self, sample_employee, task_factory):
        """Test creating an assigned task."""
        task = task_factory(sample_employee)
        
        assert task.id is not None
        assert task.employee == sample_employee
        assert task.title == 'Test Task'
        assert task.status == 'Pending'
    
    def test_task_str_representation(self, sample_task):
        """Test string representation of task."""
        expected = f"{sample_task.title} - {sample_task.employee.user.username}"
        assert str(sample_task) == expected
    
    def test_task_status_choices(self, sample_employee, task_factory):
        """Test different task status values."""
        pending_task = task_factory(sample_employee, status='Pending')
        inprogress_task = task_factory(sample_employee, status='In Progress')
        completed_task = task_factory(sample_employee, status='Completed')
        
        assert pending_task.status == 'Pending'
        assert inprogress_task.status == 'In Progress'
        assert completed_task.status == 'Completed'
    
    def test_task_with_description(self, sample_employee, task_factory):
        """Test task with detailed description."""
        task = task_factory(
            sample_employee,
            title='Complex Repair',
            description='Detailed repair instructions for transmission system'
        )
        
        assert task.title == 'Complex Repair'
        assert 'transmission system' in task.description
    
    def test_task_with_due_date(self, sample_employee, task_factory):
        """Test task with due date."""
        due_date = date.today() + timedelta(days=14)
        task = task_factory(sample_employee, due_date=due_date)
        
        assert task.due_date == due_date
    
    def test_task_completion(self, sample_employee, task_factory):
        """Test marking task as completed."""
        task = task_factory(sample_employee, status='Pending')
        
        task.status = 'Completed'
        task.completed_at = date.today()
        task.save()
        
        task.refresh_from_db()
        assert task.status == 'Completed'
        assert task.completed_at == date.today()
    
    def test_task_assigned_date_auto_set(self, sample_employee, task_factory):
        """Test that assigned_date is automatically set."""
        task = task_factory(sample_employee)
        
        assert task.assigned_date is not None
        assert task.assigned_date == date.today()
    
    def test_employee_tasks_relationship(self, sample_employee, task_factory):
        """Test reverse relationship from employee to tasks."""
        task1 = task_factory(sample_employee, title='Task 1')
        task2 = task_factory(sample_employee, title='Task 2')
        
        tasks = sample_employee.tasks.all()
        assert tasks.count() == 2
        assert task1 in tasks
        assert task2 in tasks
    
    def test_task_update_status(self, sample_task):
        """Test updating task status."""
        sample_task.status = 'In Progress'
        sample_task.save()
        
        sample_task.refresh_from_db()
        assert sample_task.status == 'In Progress'
