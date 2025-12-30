"""
Task 52: Workflow Execution Engine
Core engine for executing workflows, evaluating conditions, and performing actions
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import timedelta
import logging
import json
import re
from typing import Dict, Any, Optional

from .models_workflow import (
    Workflow, WorkflowStep, WorkflowExecution, 
    WorkflowStepExecution, WorkflowTrigger
)
from .models import Shift, LeaveRequest, StaffProfile, CareHome

logger = logging.getLogger(__name__)
User = get_user_model()


class WorkflowEngine:
    """
    Main workflow execution engine
    """
    
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.execution = None
        self.context = {}
    
    @transaction.atomic
    def execute(self, context: Dict[str, Any] = None, triggered_by: User = None) -> WorkflowExecution:
        """
        Execute the workflow with given context
        
        Args:
            context: Input data for the workflow (e.g., shift_id, leave_request_id)
            triggered_by: User who triggered the workflow
        
        Returns:
            WorkflowExecution object
        """
        self.context = context or {}
        
        # Create execution record
        self.execution = WorkflowExecution.objects.create(
            workflow=self.workflow,
            context=self.context,
            triggered_by=triggered_by,
            trigger_type='manual' if triggered_by else 'system'
        )
        
        try:
            logger.info(f"Starting workflow execution: {self.workflow.name}")
            self.execution.start()
            
            # Get workflow steps in order
            steps = self.workflow.steps.filter(parent_step__isnull=True).order_by('order')
            
            # Execute each step
            result = {}
            for step in steps:
                step_result = self._execute_step(step)
                result[f'step_{step.id}'] = step_result
                
                # Check if step failed and workflow should stop
                if step_result.get('status') == 'failed' and not step.configuration.get('continue_on_error', False):
                    raise Exception(f"Step '{step.name}' failed: {step_result.get('error')}")
            
            # Mark execution as completed
            self.execution.complete(result=result)
            
            # Update workflow stats
            self.workflow.run_count += 1
            self.workflow.last_run = timezone.now()
            self.workflow.save()
            
            logger.info(f"Workflow execution completed: {self.workflow.name}")
            return self.execution
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            self.execution.fail(error_message=str(e))
            raise
    
    def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Execute a single workflow step
        
        Returns:
            Dict with step execution result
        """
        # Create step execution record
        step_exec = WorkflowStepExecution.objects.create(
            execution=self.execution,
            step=step,
            input_data=self.context
        )
        
        try:
            step_exec.started_at = timezone.now()
            step_exec.status = 'running'
            step_exec.save()
            
            logger.info(f"Executing step: {step.name} (Type: {step.step_type})")
            
            # Execute based on step type
            if step.step_type == 'condition':
                result = self._execute_condition(step)
            elif step.step_type == 'action':
                result = self._execute_action(step)
            elif step.step_type == 'delay':
                result = self._execute_delay(step)
            elif step.step_type == 'branch':
                result = self._execute_branch(step)
            else:
                result = {'status': 'completed', 'message': f'Unknown step type: {step.step_type}'}
            
            # Mark step as completed
            step_exec.status = 'completed'
            step_exec.output_data = result
            step_exec.completed_at = timezone.now()
            step_exec.duration_seconds = (step_exec.completed_at - step_exec.started_at).total_seconds()
            step_exec.save()
            
            return result
            
        except Exception as e:
            logger.error(f"Step execution failed: {str(e)}")
            step_exec.status = 'failed'
            step_exec.error_message = str(e)
            step_exec.completed_at = timezone.now()
            if step_exec.started_at:
                step_exec.duration_seconds = (step_exec.completed_at - step_exec.started_at).total_seconds()
            step_exec.save()
            
            return {'status': 'failed', 'error': str(e)}
    
    def _execute_condition(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Evaluate a condition and execute appropriate branch
        """
        condition_expr = step.configuration.get('condition')
        
        if not condition_expr:
            return {'status': 'failed', 'error': 'No condition expression defined'}
        
        # Evaluate condition
        result = self._evaluate_expression(condition_expr, self.context)
        
        logger.info(f"Condition '{condition_expr}' evaluated to: {result}")
        
        # Execute appropriate next step
        if result and step.on_success:
            return self._execute_step(step.on_success)
        elif not result and step.on_failure:
            return self._execute_step(step.on_failure)
        
        return {'status': 'completed', 'condition_result': result}
    
    def _execute_action(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Execute an action step
        """
        action_type = step.action_type
        config = step.configuration
        
        logger.info(f"Executing action: {action_type}")
        
        try:
            if action_type == 'send_email':
                return self._action_send_email(config)
            elif action_type == 'send_notification':
                return self._action_send_notification(config)
            elif action_type == 'create_shift':
                return self._action_create_shift(config)
            elif action_type == 'update_shift':
                return self._action_update_shift(config)
            elif action_type == 'approve_leave':
                return self._action_approve_leave(config)
            elif action_type == 'reject_leave':
                return self._action_reject_leave(config)
            elif action_type == 'assign_staff':
                return self._action_assign_staff(config)
            elif action_type == 'update_status':
                return self._action_update_status(config)
            else:
                return {'status': 'failed', 'error': f'Unknown action type: {action_type}'}
        
        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}
    
    def _execute_delay(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Execute a delay/wait step
        """
        # For now, just log the delay (in production, this would schedule the next step)
        duration = step.configuration.get('duration', 0)
        unit = step.configuration.get('unit', 'minutes')
        
        logger.info(f"Delay step: {duration} {unit}")
        
        return {
            'status': 'completed',
            'message': f'Delayed for {duration} {unit}',
            'next_run': timezone.now() + timedelta(**{unit: duration})
        }
    
    def _execute_branch(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Execute multiple branches in parallel
        """
        results = {}
        
        for child_step in step.child_steps.all().order_by('order'):
            child_result = self._execute_step(child_step)
            results[f'branch_{child_step.id}'] = child_result
        
        return {
            'status': 'completed',
            'branches': results
        }
    
    # Action implementations
    
    def _action_send_email(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email"""
        recipients = self._resolve_value(config.get('recipients', []))
        subject = self._resolve_value(config.get('subject', 'Workflow Notification'))
        message = self._resolve_value(config.get('message', ''))
        
        if isinstance(recipients, str):
            recipients = [recipients]
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            return {
                'status': 'completed',
                'message': f'Email sent to {len(recipients)} recipients'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _action_send_notification(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Send in-app notification"""
        # This would integrate with the notification system (Task 47)
        user_id = self._resolve_value(config.get('user_id'))
        message = self._resolve_value(config.get('message', ''))
        
        logger.info(f"Notification to user {user_id}: {message}")
        
        return {
            'status': 'completed',
            'message': 'Notification sent'
        }
    
    def _action_create_shift(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new shift"""
        try:
            shift_data = {
                'care_home_id': self._resolve_value(config.get('care_home_id')),
                'shift_date': self._resolve_value(config.get('shift_date')),
                'start_time': self._resolve_value(config.get('start_time')),
                'end_time': self._resolve_value(config.get('end_time')),
                'shift_type': self._resolve_value(config.get('shift_type', 'regular')),
            }
            
            shift = Shift.objects.create(**shift_data)
            
            return {
                'status': 'completed',
                'shift_id': shift.id,
                'message': f'Shift created: {shift.id}'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _action_update_shift(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing shift"""
        try:
            shift_id = self._resolve_value(config.get('shift_id'))
            shift = Shift.objects.get(id=shift_id)
            
            # Update fields
            for field, value in config.get('updates', {}).items():
                setattr(shift, field, self._resolve_value(value))
            
            shift.save()
            
            return {
                'status': 'completed',
                'message': f'Shift {shift_id} updated'
            }
        except Shift.DoesNotExist:
            return {'status': 'failed', 'error': f'Shift {shift_id} not found'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _action_approve_leave(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Approve a leave request"""
        try:
            leave_id = self._resolve_value(config.get('leave_request_id'))
            leave = LeaveRequest.objects.get(id=leave_id)
            
            leave.status = 'approved'
            leave.reviewed_by = self.execution.triggered_by
            leave.reviewed_at = timezone.now()
            leave.save()
            
            return {
                'status': 'completed',
                'message': f'Leave request {leave_id} approved'
            }
        except LeaveRequest.DoesNotExist:
            return {'status': 'failed', 'error': f'Leave request {leave_id} not found'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _action_reject_leave(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Reject a leave request"""
        try:
            leave_id = self._resolve_value(config.get('leave_request_id'))
            reason = self._resolve_value(config.get('reason', 'Rejected by workflow'))
            
            leave = LeaveRequest.objects.get(id=leave_id)
            
            leave.status = 'rejected'
            leave.reviewed_by = self.execution.triggered_by
            leave.reviewed_at = timezone.now()
            leave.rejection_reason = reason
            leave.save()
            
            return {
                'status': 'completed',
                'message': f'Leave request {leave_id} rejected'
            }
        except LeaveRequest.DoesNotExist:
            return {'status': 'failed', 'error': f'Leave request {leave_id} not found'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _action_assign_staff(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Assign staff to a shift"""
        try:
            shift_id = self._resolve_value(config.get('shift_id'))
            staff_id = self._resolve_value(config.get('staff_id'))
            
            shift = Shift.objects.get(id=shift_id)
            staff = StaffProfile.objects.get(id=staff_id)
            
            shift.assigned_staff.add(staff)
            shift.save()
            
            return {
                'status': 'completed',
                'message': f'Staff {staff_id} assigned to shift {shift_id}'
            }
        except (Shift.DoesNotExist, StaffProfile.DoesNotExist) as e:
            return {'status': 'failed', 'error': str(e)}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _action_update_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update status of an object"""
        try:
            model_type = config.get('model_type')
            object_id = self._resolve_value(config.get('object_id'))
            status = self._resolve_value(config.get('status'))
            
            # Get the appropriate model
            if model_type == 'shift':
                obj = Shift.objects.get(id=object_id)
            elif model_type == 'leave':
                obj = LeaveRequest.objects.get(id=object_id)
            else:
                return {'status': 'failed', 'error': f'Unknown model type: {model_type}'}
            
            obj.status = status
            obj.save()
            
            return {
                'status': 'completed',
                'message': f'{model_type} {object_id} status updated to {status}'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    # Helper methods
    
    def _resolve_value(self, value: Any) -> Any:
        """
        Resolve a value from context or use literal value
        
        Supports syntax like: "${context.shift_id}" or literal values
        """
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            # Extract variable path
            var_path = value[2:-1]
            
            # Navigate context
            parts = var_path.split('.')
            result = self.context
            
            for part in parts:
                if isinstance(result, dict):
                    result = result.get(part)
                else:
                    result = getattr(result, part, None)
                
                if result is None:
                    break
            
            return result
        
        return value
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a conditional expression
        
        Supports simple comparisons like:
        - "${context.shift.hours} > 8"
        - "${context.leave.days} <= 5"
        - "${context.user.role} == 'Manager'"
        """
        try:
            # Replace context variables
            for key, value in context.items():
                pattern = f'${{{key}}}'
                if pattern in expression:
                    if isinstance(value, str):
                        expression = expression.replace(pattern, f"'{value}'")
                    else:
                        expression = expression.replace(pattern, str(value))
            
            # Safely evaluate (limited to comparisons)
            # In production, use a proper expression parser for security
            result = eval(expression, {"__builtins__": {}}, {})
            
            return bool(result)
        
        except Exception as e:
            logger.error(f"Expression evaluation failed: {str(e)}")
            return False


class WorkflowScheduler:
    """
    Manages scheduled workflow execution
    """
    
    @staticmethod
    def check_and_run_scheduled_workflows():
        """
        Check for workflows that should run now and execute them
        This would be called by a Celery periodic task
        """
        from croniter import croniter
        
        now = timezone.now()
        
        # Get all active workflows with schedule triggers
        triggers = WorkflowTrigger.objects.filter(
            workflow__status='active',
            trigger_type='schedule',
            is_active=True
        )
        
        for trigger in triggers:
            cron_expr = trigger.schedule_expression
            
            try:
                # Check if workflow should run now
                cron = croniter(cron_expr, now)
                next_run = cron.get_next(datetime)
                
                # If next run is within the next minute, execute
                if next_run <= now + timedelta(minutes=1):
                    logger.info(f"Triggering scheduled workflow: {trigger.workflow.name}")
                    
                    engine = WorkflowEngine(trigger.workflow)
                    engine.execute()
                    
                    # Update workflow next run time
                    trigger.workflow.next_run = cron.get_next(datetime)
                    trigger.workflow.save()
            
            except Exception as e:
                logger.error(f"Failed to process scheduled workflow: {str(e)}")
    
    @staticmethod
    def trigger_event_workflows(event_type: str, context: Dict[str, Any]):
        """
        Trigger workflows based on an event
        
        Args:
            event_type: Type of event (e.g., 'shift_created', 'leave_requested')
            context: Event context data
        """
        # Get all active workflows with this event trigger
        triggers = WorkflowTrigger.objects.filter(
            workflow__status='active',
            trigger_type='event',
            event_type=event_type,
            is_active=True
        )
        
        for trigger in triggers:
            try:
                # Check trigger conditions
                if trigger.conditions:
                    engine = WorkflowEngine(trigger.workflow)
                    if not engine._evaluate_expression(trigger.conditions.get('expression', 'True'), context):
                        logger.info(f"Trigger condition not met for workflow: {trigger.workflow.name}")
                        continue
                
                logger.info(f"Triggering event-based workflow: {trigger.workflow.name}")
                
                engine = WorkflowEngine(trigger.workflow)
                engine.execute(context=context)
            
            except Exception as e:
                logger.error(f"Failed to trigger workflow: {str(e)}")
