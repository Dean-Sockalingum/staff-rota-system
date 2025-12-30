"""
Report Builder Views
====================

Views for custom report builder interface and API.

Created: 30 December 2025
Task 40: Custom Report Builder
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
import json

from .models_reports import CustomReportTemplate, CustomSavedReport, ReportFavorite, ReportDataSource
from .report_builder import ReportExecutor, ReportExporter, ReportTemplateBuilder


@login_required
def report_builder_home(request):
    """
    Report builder home page - list of templates and saved reports.
    """
    # Get user's templates
    my_templates = ReportTemplate.objects.filter(created_by=request.user)
    
    # Get public templates
    public_templates = ReportTemplate.objects.filter(is_public=True).exclude(
        created_by=request.user
    )
    
    # Get recent saved reports
    recent_reports = SavedReport.objects.filter(
        generated_by=request.user
    ).order_by('-generated_at')[:10]
    
    # Get favorites
    favorites = ReportFavorite.objects.filter(user=request.user).select_related('template')
    
    context = {
        'my_templates': my_templates,
        'public_templates': public_templates,
        'recent_reports': recent_reports,
        'favorites': favorites,
        'page_title': 'Custom Report Builder'
    }
    
    return render(request, 'scheduling/reports/builder_home.html', context)


@login_required
def create_report_template(request):
    """
    Create new report template with drag-and-drop builder interface.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        
        template = ReportTemplate.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            report_type=data.get('report_type', 'CUSTOM'),
            created_by=request.user,
            data_sources=data.get('data_sources', {}),
            filters=data.get('filters', []),
            grouping=data.get('grouping', []),
            sorting=data.get('sorting', []),
            columns=data.get('columns', []),
            formatting=data.get('formatting', {}),
            default_export_format=data.get('export_format', 'PDF')
        )
        
        return JsonResponse({
            'success': True,
            'template_id': template.id,
            'message': 'Report template created successfully'
        })
    
    # GET request - show builder interface
    data_sources = ReportDataSource.objects.filter(is_active=True)
    
    context = {
        'data_sources': data_sources,
        'page_title': 'Create Report Template'
    }
    
    return render(request, 'scheduling/reports/builder_create.html', context)


@login_required
def edit_report_template(request, template_id):
    """
    Edit existing report template.
    """
    template = get_object_or_404(ReportTemplate, id=template_id)
    
    # Check permissions
    if template.created_by != request.user and not request.user.role.is_senior_management_team:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        
        template.name = data.get('name', template.name)
        template.description = data.get('description', template.description)
        template.data_sources = data.get('data_sources', template.data_sources)
        template.filters = data.get('filters', template.filters)
        template.grouping = data.get('grouping', template.grouping)
        template.sorting = data.get('sorting', template.sorting)
        template.columns = data.get('columns', template.columns)
        template.formatting = data.get('formatting', template.formatting)
        template.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Report template updated successfully'
        })
    
    data_sources = ReportDataSource.objects.filter(is_active=True)
    
    context = {
        'template': template,
        'data_sources': data_sources,
        'page_title': f'Edit: {template.name}'
    }
    
    return render(request, 'scheduling/reports/builder_edit.html', context)


@login_required
def execute_report(request, template_id):
    """
    Execute a report template and display/export results.
    """
    template = get_object_or_404(ReportTemplate, id=template_id)
    
    # Get parameters from request
    parameters = {}
    if request.GET.get('start_date'):
        parameters['start_date'] = request.GET.get('start_date')
    if request.GET.get('end_date'):
        parameters['end_date'] = request.GET.get('end_date')
    if request.GET.get('care_home_id'):
        parameters['care_home_id'] = int(request.GET.get('care_home_id'))
    if request.GET.get('unit_id'):
        parameters['unit_id'] = int(request.GET.get('unit_id'))
    
    # Execute report
    try:
        saved_report = ReportExecutor.execute(template, parameters, request.user)
        
        # Check if export requested
        export_format = request.GET.get('export')
        if export_format:
            return export_report(request, saved_report.id, export_format)
        
        # Otherwise display results
        return redirect('view_report', report_id=saved_report.id)
        
    except Exception as e:
        return render(request, 'scheduling/error.html', {
            'message': f'Error executing report: {str(e)}'
        })


@login_required
def view_report(request, report_id):
    """
    View a saved report.
    """
    saved_report = get_object_or_404(SavedReport, id=report_id)
    
    # Check permissions
    if saved_report.generated_by != request.user and not request.user.role.is_senior_management_team:
        return render(request, 'scheduling/error.html', {
            'message': 'Permission denied'
        })
    
    # Pagination
    page_num = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 50))
    
    data_rows = saved_report.data.get('rows', [])
    paginator = Paginator(data_rows, per_page)
    page = paginator.get_page(page_num)
    
    context = {
        'report': saved_report,
        'page': page,
        'columns': list(data_rows[0].keys()) if data_rows else [],
        'page_title': saved_report.template.name
    }
    
    return render(request, 'scheduling/reports/view_report.html', context)


@login_required
def export_report(request, report_id, format='pdf'):
    """
    Export a saved report in the specified format.
    """
    saved_report = get_object_or_404(SavedReport, id=report_id)
    
    # Check permissions
    if saved_report.generated_by != request.user and not request.user.role.is_senior_management_team:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        if format.lower() == 'csv':
            content = ReportExporter.export_to_csv(saved_report)
            response = HttpResponse(content, content_type='text/csv')
            filename = f"{saved_report.template.name}_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
        elif format.lower() == 'excel':
            content = ReportExporter.export_to_excel(saved_report)
            response = HttpResponse(
                content.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f"{saved_report.template.name}_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
        elif format.lower() == 'pdf':
            content = ReportExporter.export_to_pdf(saved_report)
            response = HttpResponse(content.getvalue(), content_type='application/pdf')
            filename = f"{saved_report.template.name}_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
        elif format.lower() == 'json':
            content = ReportExporter.export_to_json(saved_report)
            response = HttpResponse(content, content_type='application/json')
            filename = f"{saved_report.template.name}_{timezone.now().strftime('%Y%m%d_%H%M')}.json"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
        else:
            return JsonResponse({'error': 'Invalid export format'}, status=400)
        
        return response
        
    except ImportError as e:
        return JsonResponse({
            'error': f'Export library not installed: {str(e)}'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'error': f'Export failed: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(['POST'])
def delete_report_template(request, template_id):
    """
    Delete a report template.
    """
    template = get_object_or_404(ReportTemplate, id=template_id)
    
    # Check permissions
    if template.created_by != request.user and not request.user.role.is_senior_management_team:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    template.delete()
    
    return JsonResponse({'success': True, 'message': 'Report template deleted'})


@login_required
@require_http_methods(['POST'])
def toggle_favorite(request, template_id):
    """
    Add or remove a report from favorites.
    """
    template = get_object_or_404(ReportTemplate, id=template_id)
    
    favorite, created = ReportFavorite.objects.get_or_create(
        user=request.user,
        template=template
    )
    
    if not created:
        favorite.delete()
        return JsonResponse({'success': True, 'favorited': False})
    
    return JsonResponse({'success': True, 'favorited': True})


# API Endpoints for builder interface

@login_required
def api_get_data_sources(request):
    """
    Get available data sources for report builder.
    """
    sources = ReportDataSource.objects.filter(is_active=True)
    
    data = [
        {
            'model_name': s.model_name,
            'display_name': s.display_name,
            'description': s.description,
            'fields': s.fields,
            'relationships': s.relationships
        }
        for s in sources
    ]
    
    return JsonResponse({'data_sources': data})


@login_required
def api_preview_report(request):
    """
    Preview report results without saving (for builder interface).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    data = json.loads(request.body)
    
    # Create temporary template (not saved)
    temp_template = ReportTemplate(
        name='Preview',
        created_by=request.user,
        data_sources=data.get('data_sources', {}),
        filters=data.get('filters', []),
        grouping=data.get('grouping', []),
        sorting=data.get('sorting', []),
        columns=data.get('columns', [])
    )
    
    try:
        # Execute without saving
        saved_report = ReportExecutor.execute(temp_template, data.get('parameters'), request.user)
        
        # Return preview data (limit to 100 rows)
        preview_data = saved_report.data.get('rows', [])[:100]
        
        return JsonResponse({
            'success': True,
            'row_count': len(preview_data),
            'total_rows': saved_report.row_count,
            'data': preview_data,
            'execution_time': saved_report.execution_time
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
