"""
Task 52: Workflow Automation Models
Define workflow structure, triggers, conditions, and actions
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class WorkflowTemplate(models.Model):
    """
    Pre-defined workflow templates for common scenarios
    E.g., "Leave Approval Workflow", "Shift Assignment Workflow"
    """
    
    CATEGORY_CHOICES = [
        ('leave', 'Leave Management'),
        ('shift', 'Shift Management'),
        ('compliance', 'Compliance'),
        ('notification', 'Notifications'),
        ('approval', 'Approval Process'),
        ('custom', 'Custom Workflow'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="System templates cannot be deleted")
    
    # Template configuration (JSON)
    # Stores the structure of triggers, conditions, and actions
    configuration = models.JSONField(default=dict)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='workflow_templates_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduling_workflow_template'
        ordering = ['category', 'name']
        verbose_name = 'Workflow Template'
        verbose_name_plural = 'Workflow Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def clone(self):
        """Create a copy of this template"""
        new_template = WorkflowTemplate.objects.create(
            name=f"{self.name} (Copy)",
            description=self.description,
            category=self.category,
            configuration=self.configuration.copy(),
            is_system=False,
        )
        return new_template


class Workflow(models.Model):
    """
    Active workflow instance (created from a template or from scratch)
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_instances'
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Workflow configuration (can be customized from template)
    configuration = models.JSONField(default=dict)
    
    # Trigger settings
    trigger_type = models.CharField(max_length=50, default='manual')  # manual, scheduled, event
    trigger_config = models.JSONField(default=dict)
    
    # Execution settings
    run_count = models.IntegerField(default=0)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Owner
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='workflows_created'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduling_workflow'
        ordering = ['-created_at']
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def activate(self):
        """Activate the workflow"""
        self.status = 'active'
        self.save()
    
    def pause(self):
        """Pause the workflow"""
        self.status = 'paused'
        self.save()
    
    def cancel(self):
        """Cancel the workflow"""
        self.status = 'cancelled'
        self.save()


class WorkflowStep(models.Model):
    """
    Individual step in a workflow
    """
    
    STEP_TYPE_CHOICES = [
        ('condition', 'Condition Check'),
        ('action', 'Execute Action'),
        ('delay', 'Wait/Delay'),
        ('branch', 'Branch/Split'),
        ('merge', 'Merge Branches'),
        ('end', 'End Workflow'),
    ]
    
    ACTION_TYPE_CHOICES = [
        ('send_email', 'Send Email'),
        ('send_notification', 'Send In-App Notification'),
        ('create_shift', 'Create Shift'),
        ('update_shift', 'Update Shift'),
        ('approve_leave', 'Approve Leave Request'),
        ('reject_leave', 'Reject Leave Request'),
        ('assign_staff', 'Assign Staff to Shift'),
        ('update_status', 'Update Status'),
        ('create_task', 'Create Task'),
        ('send_webhook', 'Send Webhook'),
        ('custom', 'Custom Action'),
    ]
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    
    step_type = models.CharField(max_length=50, choices=STEP_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Step configuration (JSON)
    # For actions: action_type, parameters
    # For conditions: condition_expression, true_path, false_path
    # For delays: duration, unit
    configuration = models.JSONField(default=dict)
    
    # For action steps
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES, blank=True)
    
    # Execution order
    order = models.IntegerField(default=0)
    
    # Parent step (for branching)
    parent_step = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_steps'
    )
    
    # Success/failure paths
    on_success = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='success_from'
    )
    on_failure = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='failure_from'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduling_workflow_step'
        ordering = ['workflow', 'order']
        verbose_name = 'Workflow Step'
        verbose_name_plural = 'Workflow Steps'
    
    def __str__(self):
        return f"{self.workflow.name} - Step {self.order}: {self.name}"


class WorkflowExecution(models.Model):
    """
    Record of a workflow execution (workflow run)
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Execution context (input data)
    context = models.JSONField(default=dict)
    
    # Execution results
    result = models.JSONField(default=dict)
    
    # Error information
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Triggered by
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_executions_triggered'
    )
    trigger_type = models.CharField(max_length=50, default='manual')  # manual, scheduled, event
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduling_workflow_execution'
        ordering = ['-created_at']
        verbose_name = 'Workflow Execution'
        verbose_name_plural = 'Workflow Executions'
        indexes = [
            models.Index(fields=['workflow', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')} ({self.get_status_display()})"
    
    def start(self):
        """Mark execution as started"""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()
    
    def complete(self, result=None):
        """Mark execution as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        if result:
            self.result = result
        self.save()
    
    def fail(self, error_message, error_details=None):
        """Mark execution as failed"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.error_message = error_message
        if error_details:
            self.error_details = error_details
        self.save()


class WorkflowStepExecution(models.Model):
    """
    Record of a single step execution within a workflow run
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name='step_executions'
    )
    
    step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Step input/output
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    
    # Error information
    error_message = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduling_workflow_step_execution'
        ordering = ['execution', 'step__order']
        verbose_name = 'Workflow Step Execution'
        verbose_name_plural = 'Workflow Step Executions'
    
    def __str__(self):
        return f"{self.step.name} - {self.get_status_display()}"


class WorkflowTrigger(models.Model):
    """
    Defines when a workflow should be triggered
    """
    
    TRIGGER_TYPE_CHOICES = [
        ('manual', 'Manual Trigger'),
        ('schedule', 'Scheduled (Cron)'),
        ('event', 'Event-Based'),
        ('webhook', 'Webhook'),
    ]
    
    EVENT_TYPE_CHOICES = [
        ('shift_created', 'Shift Created'),
        ('shift_updated', 'Shift Updated'),
        ('shift_deleted', 'Shift Deleted'),
        ('leave_requested', 'Leave Requested'),
        ('leave_approved', 'Leave Approved'),
        ('leave_rejected', 'Leave Rejected'),
        ('staff_assigned', 'Staff Assigned to Shift'),
        ('compliance_violation', 'Compliance Violation Detected'),
        ('training_due', 'Training Due'),
        ('custom', 'Custom Event'),
    ]
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='triggers'
    )
    
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPE_CHOICES)
    
    # For event triggers
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, blank=True)
    
    # For scheduled triggers (cron expression)
    schedule_expression = models.CharField(max_length=200, blank=True)
    
    # Trigger conditions (JSON)
    # E.g., only trigger if shift is at specific home, or leave duration > 5 days
    conditions = models.JSONField(default=dict)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduling_workflow_trigger'
        verbose_name = 'Workflow Trigger'
        verbose_name_plural = 'Workflow Triggers'
    
    def __str__(self):
        return f"{self.workflow.name} - {self.get_trigger_type_display()}"
