"""
Task 52: Workflow Views
Views for creating, managing, and executing workflows
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import json

from .models_workflow import (
    WorkflowTemplate, Workflow, WorkflowStep, 
    WorkflowExecution, WorkflowTrigger
)
from .workflow_engine import WorkflowEngine, WorkflowScheduler
from .decorators import manager_required


@login_required
def workflow_list(request):
    """
    List all workflows (with filtering and search)
    """
    # Get query parameters
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    # Base queryset
    workflows = Workflow.objects.all()
    
    # Apply filters
    if search_query:
        workflows = workflows.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        workflows = workflows.filter(status=status_filter)
    
    # Annotate with execution count
    workflows = workflows.annotate(
        execution_count=Count('executions')
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(workflows, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get workflow templates for quick creation
    templates = WorkflowTemplate.objects.filter(is_active=True).order_by('category', 'name')
    
    context = {
        'workflows': page_obj,
        'templates': templates,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_count': workflows.count(),
        'active_count': Workflow.objects.filter(status='active').count(),
        'draft_count': Workflow.objects.filter(status='draft').count(),
    }
    
    return render(request, 'scheduling/workflow_list.html', context)


@login_required
@manager_required
def workflow_create(request):
    """
    Create a new workflow (from scratch or from template)
    """
    if request.method == 'POST':
        # Create workflow
        template_id = request.POST.get('template_id')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if template_id:
            # Create from template
            template = get_object_or_404(WorkflowTemplate, id=template_id)
            workflow = Workflow.objects.create(
                template=template,
                name=name or template.name,
                description=description or template.description,
                configuration=template.configuration.copy(),
                created_by=request.user
            )
            messages.success(request, f'Workflow "{workflow.name}" created from template.')
        else:
            # Create blank workflow
            workflow = Workflow.objects.create(
                name=name,
                description=description,
                created_by=request.user
            )
            messages.success(request, f'Workflow "{workflow.name}" created.')
        
        return redirect('scheduling:workflow_builder', workflow_id=workflow.id)
    
    # GET request - show creation form
    templates = WorkflowTemplate.objects.filter(is_active=True).order_by('category', 'name')
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'scheduling/workflow_create.html', context)


@login_required
@manager_required
def workflow_builder(request, workflow_id):
    """
    Visual workflow builder interface
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    if request.method == 'POST':
        # Save workflow configuration
        try:
            configuration = json.loads(request.POST.get('configuration', '{}'))
            workflow.configuration = configuration
            workflow.save()
            
            # Also save/update workflow steps based on configuration
            _save_workflow_steps(workflow, configuration)
            
            messages.success(request, 'Workflow saved successfully.')
            return JsonResponse({'status': 'success'})
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid configuration JSON'}, status=400)
    
    # GET request - show builder interface
    steps = workflow.steps.all().order_by('order')
    triggers = workflow.triggers.all()
    
    context = {
        'workflow': workflow,
        'steps': steps,
        'triggers': triggers,
        'configuration_json': json.dumps(workflow.configuration),
    }
    
    return render(request, 'scheduling/workflow_builder.html', context)


@login_required
def workflow_detail(request, workflow_id):
    """
    View workflow details and execution history
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    # Get recent executions
    executions = workflow.executions.all().order_by('-created_at')[:20]
    
    # Get workflow steps
    steps = workflow.steps.all().order_by('order')
    
    # Get triggers
    triggers = workflow.triggers.all()
    
    context = {
        'workflow': workflow,
        'executions': executions,
        'steps': steps,
        'triggers': triggers,
        'execution_count': workflow.executions.count(),
        'success_count': workflow.executions.filter(status='completed').count(),
        'failure_count': workflow.executions.filter(status='failed').count(),
    }
    
    return render(request, 'scheduling/workflow_detail.html', context)


@login_required
@manager_required
@require_http_methods(["POST"])
def workflow_execute(request, workflow_id):
    """
    Manually execute a workflow
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    try:
        # Get context from request
        context = json.loads(request.POST.get('context', '{}'))
        
        # Execute workflow
        engine = WorkflowEngine(workflow)
        execution = engine.execute(context=context, triggered_by=request.user)
        
        messages.success(request, f'Workflow executed successfully. Execution ID: {execution.id}')
        return redirect('scheduling:workflow_execution_detail', execution_id=execution.id)
    
    except Exception as e:
        messages.error(request, f'Workflow execution failed: {str(e)}')
        return redirect('scheduling:workflow_detail', workflow_id=workflow_id)


@login_required
@manager_required
@require_http_methods(["POST"])
def workflow_toggle_status(request, workflow_id):
    """
    Activate/pause a workflow
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    if workflow.status == 'active':
        workflow.pause()
        messages.success(request, f'Workflow "{workflow.name}" paused.')
    elif workflow.status in ['draft', 'paused']:
        workflow.activate()
        messages.success(request, f'Workflow "{workflow.name}" activated.')
    else:
        messages.error(request, f'Cannot change status of {workflow.get_status_display()} workflow.')
    
    return redirect('scheduling:workflow_detail', workflow_id=workflow_id)


@login_required
@manager_required
@require_http_methods(["POST"])
def workflow_delete(request, workflow_id):
    """
    Delete a workflow
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    workflow_name = workflow.name
    workflow.delete()
    
    messages.success(request, f'Workflow "{workflow_name}" deleted.')
    return redirect('scheduling:workflow_list')


@login_required
def workflow_execution_detail(request, execution_id):
    """
    View detailed execution log
    """
    execution = get_object_or_404(WorkflowExecution, id=execution_id)
    
    # Get step executions
    step_executions = execution.step_executions.all().order_by('step__order')
    
    context = {
        'execution': execution,
        'step_executions': step_executions,
        'context_json': json.dumps(execution.context, indent=2),
        'result_json': json.dumps(execution.result, indent=2) if execution.result else '{}',
    }
    
    return render(request, 'scheduling/workflow_execution_detail.html', context)


@login_required
def workflow_execution_list(request):
    """
    List all workflow executions (with filtering)
    """
    # Get query parameters
    workflow_id = request.GET.get('workflow')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    executions = WorkflowExecution.objects.select_related('workflow', 'triggered_by').all()
    
    # Apply filters
    if workflow_id:
        executions = executions.filter(workflow_id=workflow_id)
    
    if status_filter:
        executions = executions.filter(status=status_filter)
    
    executions = executions.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(executions, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get workflows for filter dropdown
    workflows = Workflow.objects.all().order_by('name')
    
    context = {
        'executions': page_obj,
        'workflows': workflows,
        'status_filter': status_filter,
        'workflow_filter': workflow_id,
        'total_count': executions.count(),
    }
    
    return render(request, 'scheduling/workflow_execution_list.html', context)


@login_required
@manager_required
def workflow_template_list(request):
    """
    List and manage workflow templates
    """
    templates = WorkflowTemplate.objects.all().order_by('category', 'name')
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'scheduling/workflow_template_list.html', context)


@login_required
@manager_required
def workflow_template_create(request):
    """
    Create a new workflow template
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        category = request.POST.get('category')
        
        template = WorkflowTemplate.objects.create(
            name=name,
            description=description,
            category=category,
            created_by=request.user
        )
        
        messages.success(request, f'Template "{template.name}" created.')
        return redirect('scheduling:workflow_template_list')
    
    context = {
        'categories': WorkflowTemplate.CATEGORY_CHOICES,
    }
    
    return render(request, 'scheduling/workflow_template_create.html', context)


# API endpoints for workflow builder

@login_required
@require_http_methods(["POST"])
def workflow_add_step(request, workflow_id):
    """
    Add a step to a workflow (AJAX)
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    try:
        step_data = json.loads(request.body)
        
        step = WorkflowStep.objects.create(
            workflow=workflow,
            step_type=step_data.get('step_type'),
            name=step_data.get('name'),
            description=step_data.get('description', ''),
            action_type=step_data.get('action_type', ''),
            configuration=step_data.get('configuration', {}),
            order=step_data.get('order', 0)
        )
        
        return JsonResponse({
            'status': 'success',
            'step_id': step.id,
            'step': {
                'id': step.id,
                'name': step.name,
                'step_type': step.step_type,
                'action_type': step.action_type,
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def workflow_update_step(request, step_id):
    """
    Update a workflow step (AJAX)
    """
    step = get_object_or_404(WorkflowStep, id=step_id)
    
    try:
        step_data = json.loads(request.body)
        
        # Update step fields
        for field in ['name', 'description', 'step_type', 'action_type', 'configuration', 'order']:
            if field in step_data:
                setattr(step, field, step_data[field])
        
        step.save()
        
        return JsonResponse({'status': 'success'})
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
def workflow_delete_step(request, step_id):
    """
    Delete a workflow step (AJAX)
    """
    step = get_object_or_404(WorkflowStep, id=step_id)
    step.delete()
    
    return JsonResponse({'status': 'success'})


# Helper functions

def _save_workflow_steps(workflow: Workflow, configuration: dict):
    """
    Save workflow steps from configuration
    """
    steps_data = configuration.get('steps', [])
    
    # Delete existing steps
    workflow.steps.all().delete()
    
    # Create new steps
    for step_data in steps_data:
        WorkflowStep.objects.create(
            workflow=workflow,
            step_type=step_data.get('type'),
            name=step_data.get('name'),
            description=step_data.get('description', ''),
            action_type=step_data.get('action_type', ''),
            configuration=step_data.get('config', {}),
            order=step_data.get('order', 0)
        )
