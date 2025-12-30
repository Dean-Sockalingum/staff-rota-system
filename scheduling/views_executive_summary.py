"""
Executive Summary Dashboard Views
Task 46: Advanced executive reporting with trends, forecasting, and insights
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
from .executive_summary_service import ExecutiveSummaryService
from .models import CareHome
import json


@login_required
def executive_summary_dashboard(request):
    """
    Main executive summary dashboard with KPIs, trends, and forecasts
    
    Access: Senior management only
    Features:
        - High-level KPIs with trend indicators
        - 12-week trend charts
        - 4-week forecasts
        - Comparative analysis across homes
        - AI-powered insights
    """
    # Permission check
    if not request.user.role.is_senior_management_team:
        return render(request, 'error.html', {
            'message': 'Access denied. Senior management only.'
        })
    
    # Get date range from request (default: last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if request.GET.get('start_date'):
        try:
            start_date = timezone.datetime.strptime(
                request.GET.get('start_date'), '%Y-%m-%d'
            ).date()
        except ValueError:
            pass
    
    if request.GET.get('end_date'):
        try:
            end_date = timezone.datetime.strptime(
                request.GET.get('end_date'), '%Y-%m-%d'
            ).date()
        except ValueError:
            pass
    
    # Get selected care home (None = all homes)
    care_home = None
    if request.GET.get('care_home_id'):
        try:
            care_home = CareHome.objects.get(
                id=request.GET.get('care_home_id'),
                is_active=True
            )
        except CareHome.DoesNotExist:
            pass
    
    # Get executive KPIs
    kpis = ExecutiveSummaryService.get_executive_kpis(care_home, start_date, end_date)
    
    # Get trend analysis (12 weeks)
    trends = ExecutiveSummaryService.get_trend_analysis(care_home, weeks=12)
    
    # Get forecasts (4 weeks ahead)
    forecasts = ExecutiveSummaryService.generate_forecast(care_home, weeks_ahead=4)
    
    # Get comparative analysis
    comparison = ExecutiveSummaryService.get_comparative_analysis(start_date, end_date)
    
    # Get insights
    insights = ExecutiveSummaryService.get_executive_insights(care_home)
    
    # Get all care homes for filter dropdown
    care_homes = CareHome.objects.filter(is_active=True).order_by('name')
    
    context = {
        'kpis': kpis,
        'trends': trends,
        'forecasts': forecasts,
        'comparison': comparison,
        'insights': insights,
        'care_homes': care_homes,
        'selected_home': care_home,
        'start_date': start_date,
        'end_date': end_date,
        'page_title': 'Executive Summary Dashboard',
    }
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'kpis': kpis,
            'trends': trends,
            'forecasts': forecasts,
            'insights': insights
        })
    
    return render(request, 'scheduling/executive_summary_dashboard.html', context)


@login_required
def executive_summary_export_pdf(request):
    """
    Export executive summary as PDF report for board meetings
    
    Requires: reportlab (pip install reportlab)
    """
    if not request.user.role.is_senior_management_team:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph,
            Spacer, PageBreak, Image
        )
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.linecharts import HorizontalLineChart
        from io import BytesIO
    except ImportError:
        return JsonResponse({
            'error': 'PDF export requires reportlab library. Install with: pip install reportlab'
        }, status=500)
    
    # Get data
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    care_home = None
    if request.GET.get('care_home_id'):
        try:
            care_home = CareHome.objects.get(id=request.GET.get('care_home_id'))
        except CareHome.DoesNotExist:
            pass
    
    kpis = ExecutiveSummaryService.get_executive_kpis(care_home, start_date, end_date)
    trends = ExecutiveSummaryService.get_trend_analysis(care_home, weeks=12)
    forecasts = ExecutiveSummaryService.generate_forecast(care_home, weeks_ahead=4)
    insights = ExecutiveSummaryService.get_executive_insights(care_home)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    # Build PDF content
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30
    )
    
    title = Paragraph(
        f"Executive Summary Report<br/>{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}",
        title_style
    )
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Key Performance Indicators
    story.append(Paragraph("Key Performance Indicators", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    kpi_data = [
        ['Metric', 'Current', 'Target', 'Trend', 'Status'],
        [
            'Fill Rate',
            f"{kpis['kpis']['fill_rate']['value']}%",
            f"{kpis['kpis']['fill_rate']['target']}%",
            f"{kpis['kpis']['fill_rate']['trend']['percentage']:+.1f}%",
            kpis['kpis']['fill_rate']['status'].upper()
        ],
        [
            'Agency Rate',
            f"{kpis['kpis']['agency_rate']['value']}%",
            f"{kpis['kpis']['agency_rate']['target']}%",
            f"{kpis['kpis']['agency_rate']['trend']['percentage']:+.1f}%",
            kpis['kpis']['agency_rate']['status'].upper()
        ],
        [
            'Total Shifts',
            str(kpis['kpis']['total_shifts']['value']),
            '-',
            f"{kpis['kpis']['total_shifts']['trend']['percentage']:+.1f}%",
            '-'
        ],
        [
            'Total Cost',
            kpis['kpis']['total_cost']['formatted'],
            '-',
            f"{kpis['kpis']['total_cost']['trend']['percentage']:+.1f}%",
            '-'
        ]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(kpi_table)
    story.append(Spacer(1, 20))
    
    # Insights & Recommendations
    story.append(Paragraph("Executive Insights", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    for insight in insights[:5]:  # Top 5 insights
        insight_text = f"<b>{insight['icon']} {insight['title']}</b><br/>"
        insight_text += f"{insight['message']}<br/>"
        insight_text += f"<i>Recommendation: {insight['recommendation']}</i>"
        story.append(Paragraph(insight_text, styles['Normal']))
        story.append(Spacer(1, 10))
    
    story.append(PageBreak())
    
    # Forecast Summary
    story.append(Paragraph("4-Week Forecast", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    if 'forecasts' in forecasts:
        forecast_data = [['Week', 'Fill Rate', 'Agency Rate', 'Est. Cost', 'Confidence']]
        for fc in forecasts['forecasts']:
            forecast_data.append([
                f"{fc['week_start'].strftime('%d %b')} - {fc['week_end'].strftime('%d %b')}",
                f"{fc['fill_rate']}%",
                f"{fc['agency_rate']}%",
                f"£{fc['cost']:,.0f}",
                f"{fc['confidence']}%"
            ])
        
        forecast_table = Table(forecast_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        forecast_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(forecast_table)
    
    story.append(Spacer(1, 20))
    
    # Footer
    footer = Paragraph(
        f"<i>Generated: {timezone.now().strftime('%d %b %Y %H:%M')}<br/>"
        f"Confidential - For Board Use Only</i>",
        styles['Normal']
    )
    story.append(Spacer(1, 30))
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    
    # Return PDF response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="executive_summary_{end_date.strftime("%Y%m%d")}.pdf"'
    
    return response


@login_required
def executive_summary_api_kpis(request):
    """
    API endpoint for fetching KPIs (AJAX/JSON)
    
    Query params:
        - care_home_id: Optional care home ID
        - start_date: YYYY-MM-DD
        - end_date: YYYY-MM-DD
    
    Returns:
        JSON: Executive KPIs with trends
    """
    if not request.user.role.is_senior_management_team:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if request.GET.get('start_date'):
        try:
            start_date = timezone.datetime.strptime(
                request.GET.get('start_date'), '%Y-%m-%d'
            ).date()
        except ValueError:
            pass
    
    if request.GET.get('end_date'):
        try:
            end_date = timezone.datetime.strptime(
                request.GET.get('end_date'), '%Y-%m-%d'
            ).date()
        except ValueError:
            pass
    
    care_home = None
    if request.GET.get('care_home_id'):
        try:
            care_home = CareHome.objects.get(id=request.GET.get('care_home_id'))
        except CareHome.DoesNotExist:
            pass
    
    kpis = ExecutiveSummaryService.get_executive_kpis(care_home, start_date, end_date)
    
    # Convert dates to strings for JSON serialization
    kpis['period']['start_date'] = kpis['period']['start_date'].isoformat()
    kpis['period']['end_date'] = kpis['period']['end_date'].isoformat()
    
    return JsonResponse(kpis)


@login_required
def executive_summary_api_trends(request):
    """
    API endpoint for trend data (AJAX/JSON)
    
    Query params:
        - care_home_id: Optional care home ID
        - weeks: Number of weeks (default: 12)
    
    Returns:
        JSON: Weekly trend data
    """
    if not request.user.role.is_senior_management_team:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    care_home = None
    if request.GET.get('care_home_id'):
        try:
            care_home = CareHome.objects.get(id=request.GET.get('care_home_id'))
        except CareHome.DoesNotExist:
            pass
    
    weeks = int(request.GET.get('weeks', 12))
    trends = ExecutiveSummaryService.get_trend_analysis(care_home, weeks=weeks)
    
    # Convert dates to strings
    for trend in trends:
        trend['week_start'] = trend['week_start'].isoformat()
        trend['week_end'] = trend['week_end'].isoformat()
    
    return JsonResponse({'trends': trends})


@login_required
def executive_summary_api_forecast(request):
    """
    API endpoint for forecasts (AJAX/JSON)
    
    Query params:
        - care_home_id: Optional care home ID
        - weeks_ahead: Number of weeks to forecast (default: 4)
    
    Returns:
        JSON: Forecast data
    """
    if not request.user.role.is_senior_management_team:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    care_home = None
    if request.GET.get('care_home_id'):
        try:
            care_home = CareHome.objects.get(id=request.GET.get('care_home_id'))
        except CareHome.DoesNotExist:
            pass
    
    weeks_ahead = int(request.GET.get('weeks_ahead', 4))
    forecasts = ExecutiveSummaryService.generate_forecast(care_home, weeks_ahead=weeks_ahead)
    
    # Convert dates to strings
    if 'forecasts' in forecasts:
        for forecast in forecasts['forecasts']:
            forecast['week_start'] = forecast['week_start'].isoformat()
            forecast['week_end'] = forecast['week_end'].isoformat()
    
    return JsonResponse(forecasts)


@login_required
def executive_summary_api_insights(request):
    """
    API endpoint for AI insights (AJAX/JSON)
    
    Query params:
        - care_home_id: Optional care home ID
    
    Returns:
        JSON: Insights and recommendations
    """
    if not request.user.role.is_senior_management_team:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    care_home = None
    if request.GET.get('care_home_id'):
        try:
            care_home = CareHome.objects.get(id=request.GET.get('care_home_id'))
        except CareHome.DoesNotExist:
            pass
    
    insights = ExecutiveSummaryService.get_executive_insights(care_home)
    
    return JsonResponse({'insights': insights})
