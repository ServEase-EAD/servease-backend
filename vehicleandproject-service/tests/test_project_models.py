"""
Tests for Project and Task models in the vehicleandproject service.

Tests cover:
- Project model creation and validation
- Task model creation and validation
- Status and approval workflows
- Relationships and cascading
- Model methods and properties
"""

import pytest
import uuid
from datetime import date, timedelta
from django.db import IntegrityError

from projects.models import Project, Task
from vehicles.models import Vehicle


# ==================== Project Model Tests ====================

class TestProjectModel:
    """Test cases for Project model."""
    
    def test_create_project(self, sample_project):
        """Test basic project creation."""
        assert sample_project.project_id is not None
        assert isinstance(sample_project.project_id, uuid.UUID)
        assert sample_project.title == 'Engine Repair'
        assert sample_project.status == 'not_started'
        assert sample_project.approval_status == 'pending'
        assert sample_project.vehicle is not None
        assert sample_project.customer_id is not None
    
    def test_project_str_representation(self, sample_project):
        """Test project string representation."""
        assert str(sample_project) == sample_project.title
    
    def test_project_default_status(self, project_factory, sample_vehicle):
        """Test default project status is 'not_started'."""
        project = project_factory(vehicle=sample_vehicle)
        assert project.status == 'not_started'
    
    def test_project_default_approval_status(self, project_factory, sample_vehicle):
        """Test default approval status is 'pending'."""
        project = project_factory(vehicle=sample_vehicle)
        assert project.approval_status == 'pending'
    
    def test_project_status_choices(self, project_factory, sample_vehicle):
        """Test all valid project status choices."""
        valid_statuses = ['accepted', 'cancelled', 'not_started', 'in_progress', 'completed', 'on_hold']
        
        for status in valid_statuses:
            project = project_factory(
                vehicle=sample_vehicle,
                title=f'Project {status}',
                status=status
            )
            assert project.status == status
    
    def test_project_approval_status_choices(self, project_factory, sample_vehicle):
        """Test all valid approval status choices."""
        valid_approval_statuses = ['pending', 'approved', 'rejected']
        
        for approval_status in valid_approval_statuses:
            project = project_factory(
                vehicle=sample_vehicle,
                title=f'Project {approval_status}',
                approval_status=approval_status
            )
            assert project.approval_status == approval_status
    
    def test_project_vehicle_relationship(self, sample_project):
        """Test project-vehicle foreign key relationship."""
        assert isinstance(sample_project.vehicle, Vehicle)
        assert sample_project.vehicle.vehicle_id is not None
    
    def test_project_vehicle_protect_on_delete(self, project_factory, sample_vehicle):
        """Test vehicle cannot be deleted if projects exist (PROTECT)."""
        project_factory(vehicle=sample_vehicle)
        
        with pytest.raises(Exception):  # Django will raise ProtectedError
            sample_vehicle.delete()
    
    def test_project_customer_id_required(self, sample_project):
        """Test customer_id is required."""
        assert sample_project.customer_id is not None
        assert isinstance(sample_project.customer_id, uuid.UUID)
    
    def test_project_timestamps(self, sample_project):
        """Test created_at and updated_at timestamps."""
        assert sample_project.created_at is not None
        assert sample_project.updated_at is not None
        assert sample_project.updated_at >= sample_project.created_at
    
    def test_project_updated_at_changes(self, sample_project):
        """Test updated_at changes on save."""
        original_updated = sample_project.updated_at
        
        sample_project.status = 'in_progress'
        sample_project.save()
        sample_project.refresh_from_db()
        
        assert sample_project.updated_at > original_updated
    
    def test_project_expected_completion_date(self, sample_project):
        """Test expected_completion_date field."""
        assert isinstance(sample_project.expected_completion_date, date)
        assert sample_project.expected_completion_date > date.today()
    
    def test_project_filter_by_customer(self, project_factory, sample_vehicle, customer_user_id):
        """Test filtering projects by customer_id."""
        project_factory(vehicle=sample_vehicle, customer_id=customer_user_id, title='Project 1')
        project_factory(vehicle=sample_vehicle, customer_id=customer_user_id, title='Project 2')
        
        other_customer = uuid.uuid4()
        project_factory(vehicle=sample_vehicle, customer_id=other_customer, title='Other Project')
        
        customer_projects = Project.objects.filter(customer_id=customer_user_id)
        assert customer_projects.count() == 2
    
    def test_project_filter_by_status(self, project_factory, sample_vehicle):
        """Test filtering projects by status."""
        project_factory(vehicle=sample_vehicle, status='not_started', title='NS')
        project_factory(vehicle=sample_vehicle, status='in_progress', title='IP')
        project_factory(vehicle=sample_vehicle, status='completed', title='C')
        
        in_progress = Project.objects.filter(status='in_progress')
        assert in_progress.count() == 1
        assert in_progress.first().status == 'in_progress'
    
    def test_project_filter_by_approval_status(self, project_factory, sample_vehicle):
        """Test filtering projects by approval status."""
        project_factory(vehicle=sample_vehicle, approval_status='pending', title='Pending1')
        project_factory(vehicle=sample_vehicle, approval_status='approved', title='Approved1')
        project_factory(vehicle=sample_vehicle, approval_status='rejected', title='Rejected1')
        
        approved = Project.objects.filter(approval_status='approved')
        assert approved.count() >= 1
        assert all(p.approval_status == 'approved' for p in approved)
    
    def test_project_multiple_per_vehicle(self, project_factory, sample_vehicle):
        """Test vehicle can have multiple projects."""
        project1 = project_factory(vehicle=sample_vehicle, title='Project 1')
        project2 = project_factory(vehicle=sample_vehicle, title='Project 2')
        
        assert project1.vehicle == project2.vehicle
        assert sample_vehicle.projects.count() == 2


# ==================== Task Model Tests ====================

class TestTaskModel:
    """Test cases for Task model."""
    
    def test_create_task(self, sample_task):
        """Test basic task creation."""
        assert sample_task.task_id is not None
        assert isinstance(sample_task.task_id, uuid.UUID)
        assert sample_task.title == 'Remove Engine Cover'
        assert sample_task.status == 'not_started'
        assert sample_task.priority == 'high'
        assert sample_task.project is not None
    
    def test_task_str_representation(self, sample_task):
        """Test task string representation."""
        expected = f"{sample_task.project.title} - {sample_task.title}"
        assert str(sample_task) == expected
    
    def test_task_default_status(self, task_factory, sample_project):
        """Test default task status is 'not_started'."""
        task = task_factory(project=sample_project)
        assert task.status == 'not_started'
    
    def test_task_default_priority(self, task_factory, sample_project):
        """Test default task priority is 'medium'."""
        task = task_factory(project=sample_project)
        assert task.priority == 'medium'
    
    def test_task_default_duration(self, task_factory, sample_project):
        """Test default duration_seconds is 0."""
        task = task_factory(project=sample_project)
        assert task.duration_seconds == 0
    
    def test_task_status_choices(self, task_factory, sample_project):
        """Test all valid task status choices."""
        valid_statuses = ['not_started', 'in_progress', 'completed', 'blocked']
        
        for status in valid_statuses:
            task = task_factory(
                project=sample_project,
                title=f'Task {status}',
                status=status
            )
            assert task.status == status
    
    def test_task_priority_choices(self, task_factory, sample_project):
        """Test all valid priority choices."""
        valid_priorities = ['low', 'medium', 'high', 'critical']
        
        for priority in valid_priorities:
            task = task_factory(
                project=sample_project,
                title=f'Task {priority}',
                priority=priority
            )
            assert task.priority == priority
    
    def test_task_project_relationship(self, sample_task):
        """Test task-project foreign key relationship."""
        assert isinstance(sample_task.project, Project)
        assert sample_task.project.project_id is not None
    
    def test_task_cascade_delete_with_project(self, sample_project, sample_task):
        """Test tasks are deleted when project is deleted (CASCADE)."""
        project_id = sample_project.project_id
        task_id = sample_task.task_id
        
        # Delete project
        sample_project.delete()
        
        # Task should be deleted
        assert not Task.objects.filter(task_id=task_id).exists()
    
    def test_task_assigned_employee_optional(self, task_factory, sample_project):
        """Test assigned_employee_id is optional."""
        task = task_factory(project=sample_project, assigned_employee_id=None)
        assert task.assigned_employee_id is None
    
    def test_task_assigned_employee_id(self, sample_task, employee_user_id):
        """Test assigned_employee_id stores UUID."""
        assert isinstance(sample_task.assigned_employee_id, uuid.UUID)
    
    def test_task_due_date_optional(self, task_factory, sample_project):
        """Test due_date is optional."""
        task = task_factory(project=sample_project, due_date=None)
        assert task.due_date is None
    
    def test_task_due_date(self, sample_task):
        """Test due_date field."""
        assert isinstance(sample_task.due_date, date)
    
    def test_task_description_optional(self, task_factory, sample_project):
        """Test description is optional (blank allowed)."""
        task = task_factory(project=sample_project, description='')
        assert task.description == ''
    
    def test_task_duration_formatted_zero(self, task_factory, sample_project):
        """Test duration_formatted for zero duration."""
        task = task_factory(project=sample_project, duration_seconds=0)
        assert task.duration_formatted == '00:00:00'
    
    def test_task_duration_formatted_seconds(self, task_factory, sample_project):
        """Test duration_formatted for seconds only."""
        task = task_factory(project=sample_project, duration_seconds=45)
        assert task.duration_formatted == '00:00:45'
    
    def test_task_duration_formatted_minutes(self, task_factory, sample_project):
        """Test duration_formatted for minutes."""
        task = task_factory(project=sample_project, duration_seconds=300)  # 5 minutes
        assert task.duration_formatted == '00:05:00'
    
    def test_task_duration_formatted_hours(self, task_factory, sample_project):
        """Test duration_formatted for hours."""
        task = task_factory(project=sample_project, duration_seconds=7200)  # 2 hours
        assert task.duration_formatted == '02:00:00'
    
    def test_task_duration_formatted_complex(self, task_factory, sample_project):
        """Test duration_formatted for complex time."""
        # 2 hours, 15 minutes, 30 seconds = 8130 seconds
        task = task_factory(project=sample_project, duration_seconds=8130)
        assert task.duration_formatted == '02:15:30'
    
    def test_task_timestamps(self, sample_task):
        """Test created_at and updated_at timestamps."""
        assert sample_task.created_at is not None
        assert sample_task.updated_at is not None
        assert sample_task.updated_at >= sample_task.created_at
    
    def test_task_updated_at_changes(self, sample_task):
        """Test updated_at changes on save."""
        original_updated = sample_task.updated_at
        
        sample_task.status = 'in_progress'
        sample_task.save()
        sample_task.refresh_from_db()
        
        assert sample_task.updated_at > original_updated
    
    def test_task_ordering(self, multiple_tasks):
        """Test tasks are ordered by created_at descending."""
        tasks = Task.objects.all()
        
        for i in range(len(tasks) - 1):
            assert tasks[i].created_at >= tasks[i + 1].created_at
    
    def test_task_filter_by_project(self, sample_project, multiple_tasks):
        """Test filtering tasks by project."""
        project_tasks = Task.objects.filter(project=sample_project)
        assert project_tasks.count() == len(multiple_tasks)
    
    def test_task_filter_by_status(self, multiple_tasks):
        """Test filtering tasks by status."""
        completed_tasks = Task.objects.filter(status='completed')
        assert completed_tasks.count() >= 1
        
        not_started_tasks = Task.objects.filter(status='not_started')
        assert not_started_tasks.count() >= 1
    
    def test_task_filter_by_priority(self, multiple_tasks):
        """Test filtering tasks by priority."""
        high_priority = Task.objects.filter(priority='high')
        assert high_priority.count() == 1
        
        critical_priority = Task.objects.filter(priority='critical')
        assert critical_priority.count() == 1
    
    def test_task_filter_by_assigned_employee(self, task_factory, sample_project, employee_user_id):
        """Test filtering tasks by assigned employee."""
        task_factory(project=sample_project, assigned_employee_id=employee_user_id, title='T1')
        task_factory(project=sample_project, assigned_employee_id=employee_user_id, title='T2')
        
        other_employee = uuid.uuid4()
        task_factory(project=sample_project, assigned_employee_id=other_employee, title='T3')
        
        employee_tasks = Task.objects.filter(assigned_employee_id=employee_user_id)
        assert employee_tasks.count() == 2
    
    def test_project_tasks_relationship(self, sample_project, multiple_tasks):
        """Test project.tasks reverse relationship."""
        assert sample_project.tasks.count() == len(multiple_tasks)
        
        for task in sample_project.tasks.all():
            assert task.project == sample_project
    
    def test_multiple_tasks_per_project(self, task_factory, sample_project):
        """Test project can have multiple tasks."""
        task1 = task_factory(project=sample_project, title='Task 1')
        task2 = task_factory(project=sample_project, title='Task 2')
        task3 = task_factory(project=sample_project, title='Task 3')
        
        assert sample_project.tasks.count() == 3
