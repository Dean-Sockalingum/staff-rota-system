"""
Task 52: Workflow Celery Tasks
Background tasks for scheduled and event-driven workflow execution
"""

from celery import shared_task
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

from .models_workflow import Workflow, WorkflowExecution
from .workflow_engine import WorkflowEngine, WorkflowScheduler
from .models import Shift, LeaveRequest, StaffProfile

logger = logging.getLogger(__name__)


@shared_task
def execute_workflow_task(workflow_id, context=None, user_id=None):
    """
    Execute a workflow asynchronously
    
    Args:
        workflow_id: ID of the workflow to execute
        context: Workflow execution context (dict)
        user_id: ID of user triggering the workflow (optional)
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        workflow = Workflow.objects.get(id=workflow_id)
        
        # Get user if provided
        triggered_by = None
        if user_id:
            try:
                triggered_by = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found for workflow execution")
        
        # Execute workflow
        engine = WorkflowEngine(workflow)
        execution = engine.execute(context=context or {}, triggered_by=triggered_by)
        
        logger.info(f"Workflow {workflow_id} executed successfully. Execution ID: {execution.id}")
        return {'status': 'success', 'execution_id': execution.id}
    
    except Workflow.DoesNotExist:
        logger.error(f"Workflow {workflow_id} not found")
        return {'status': 'error', 'message': f'Workflow {workflow_id} not found'}
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}


@shared_task
def check_scheduled_workflows():
    """
    Periodic task to check and execute scheduled workflows
    This should run every minute via Celery Beat
    """
    try:
        logger.info("Checking scheduled workflows...")
        WorkflowScheduler.check_and_run_scheduled_workflows()
        logger.info("Scheduled workflow check completed")
        return {'status': 'success'}
    
    except Exception as e:
        logger.error(f"Failed to check scheduled workflows: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}


@shared_task
def cleanup_old_executions(days_to_keep=90):
    """
    Clean up old workflow executions
    
    Args:
        days_to_keep: Number of days to keep execution records
    """
    try:
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Delete old executions
        deleted_count = WorkflowExecution.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['completed', 'failed', 'cancelled']
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old workflow executions")
        return {'status': 'success', 'deleted_count': deleted_count}
    
    except Exception as e:
        logger.error(f"Failed to cleanup executions: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}


# Django signals for event-based workflow triggers

@receiver(post_save, sender=Shift)
def on_shift_saved(sender, instance, created, **kwargs):
    """
    Trigger workflows when a shift is created or updated
    """
    try:
        if created:
            # Shift created
            context = {
                'shift_id': instance.id,
                'care_home_id': instance.care_home.id if instance.care_home else None,
                'shift_date': str(instance.shift_date),
                'shift_type': instance.shift_type,
            }
            
            WorkflowScheduler.trigger_event_workflows('shift_created', context)
        else:
            # Shift updated
            context = {
                'shift_id': instance.id,
                'care_home_id': instance.care_home.id if instance.care_home else None,
            }
            
            WorkflowScheduler.trigger_event_workflows('shift_updated', context)
    
    except Exception as e:
        logger.error(f"Error triggering shift workflow: {str(e)}")


@receiver(post_delete, sender=Shift)
def on_shift_deleted(sender, instance, **kwargs):
    """
    Trigger workflows when a shift is deleted
    """
    try:
        context = {
            'shift_id': instance.id,
            'care_home_id': instance.care_home.id if instance.care_home else None,
        }
        
        WorkflowScheduler.trigger_event_workflows('shift_deleted', context)
    
    except Exception as e:
        logger.error(f"Error triggering shift deletion workflow: {str(e)}")


@receiver(post_save, sender=LeaveRequest)
def on_leave_request_saved(sender, instance, created, **kwargs):
    """
    Trigger workflows when a leave request is created or updated
    """
    try:
        if created:
            # Leave request created
            context = {
                'leave_request_id': instance.id,
                'staff_id': instance.staff.id if instance.staff else None,
                'leave_type': instance.leave_type,
                'start_date': str(instance.start_date),
                'end_date': str(instance.end_date),
                'days': instance.total_days,
            }
            
            WorkflowScheduler.trigger_event_workflows('leave_requested', context)
        
        else:
            # Leave request updated
            # Check if status changed
            if instance.status == 'approved':
                context = {
                    'leave_request_id': instance.id,
                    'staff_id': instance.staff.id if instance.staff else None,
                }
                WorkflowScheduler.trigger_event_workflows('leave_approved', context)
            
            elif instance.status == 'rejected':
                context = {
                    'leave_request_id': instance.id,
                    'staff_id': instance.staff.id if instance.staff else None,
                }
                WorkflowScheduler.trigger_event_workflows('leave_rejected', context)
    
    except Exception as e:
        logger.error(f"Error triggering leave request workflow: {str(e)}")


@receiver(post_save, sender=StaffProfile)
def on_staff_profile_updated(sender, instance, created, **kwargs):
    """
    Trigger workflows when staff profile is updated
    (e.g., check for compliance violations, training due)
    """
    if not created:  # Only for updates, not new profiles
        try:
            # Check for compliance issues
            # This is a placeholder - actual implementation would check certifications, training, etc.
            context = {
                'staff_id': instance.id,
                'user_id': instance.user.id if instance.user else None,
            }
            
            # Check if any certifications are expiring soon
            # (This would be implemented based on your certification tracking)
            
        except Exception as e:
            logger.error(f"Error triggering staff profile workflow: {str(e)}")


# Manual workflow trigger task

@shared_task
def trigger_workflow_for_event(event_type, context):
    """
    Manually trigger workflows for a specific event
    
    Args:
        event_type: Type of event (e.g., 'custom_event')
        context: Event context data (dict)
    """
    try:
        logger.info(f"Triggering workflows for event: {event_type}")
        WorkflowScheduler.trigger_event_workflows(event_type, context)
        return {'status': 'success'}
    
    except Exception as e:
        logger.error(f"Failed to trigger event workflows: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}
