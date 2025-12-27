"""
Rota Cost Analysis Views
Provides detailed cost analysis, visualizations, and export capabilities
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import json
from decimal import Decimal

from scheduling.models import Shift, Staff, Unit
from scheduling.models_overtime import OvertimeCoverageRequest, OvertimeCoverageResponse


@login_required
def rota_cost_analysis(request):
    """
    Main rota cost analysis dashboard
    Shows cost metrics, charts, and comparisons
    """
    
    # Get date range from request or default to last 30 days
    end_date = request.GET.get('end_date')
    start_date = request.GET.get('start_date')
    unit_id = request.GET.get('unit')
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)
    
    # Filter shifts by date range
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('staff', 'unit', 'shift_pattern')
    
    # Filter by unit if specified
    if unit_id:
        shifts = shifts.filter(unit_id=unit_id)
    
    # Calculate cost metrics
    total_shifts = shifts.count()
    
    # Staff costs by role (using standard hourly rates)
    HOURLY_RATES = {
        'RN': Decimal('22.00'),
        'SSW': Decimal('18.00'),
        'HCA': Decimal('14.00'),
    }
    
    SHIFT_HOURS = {
        'Early': 8,
        'Late': 8,
        'Night': 8,
        'Long': 12,
    }
    
    # Calculate total staff costs
    staff_cost_data = []
    total_staff_cost = Decimal('0.00')
    
    for role, hourly_rate in HOURLY_RATES.items():
        role_shifts = shifts.filter(staff__role=role)
        total_hours = 0
        
        for shift in role_shifts:
            shift_type = shift.shift_pattern.name if shift.shift_pattern else 'Early'
            hours = SHIFT_HOURS.get(shift_type, 8)
            total_hours += hours
        
        role_cost = Decimal(total_hours) * hourly_rate
        total_staff_cost += role_cost
        
        staff_cost_data.append({
            'role': role,
            'shifts': role_shifts.count(),
            'hours': total_hours,
            'hourly_rate': hourly_rate,
            'total_cost': role_cost
        })
    
    # Calculate agency costs (estimate based on typical markup)
    # In production, this would come from actual agency booking records
    agency_shifts = shifts.filter(is_agency=True) if hasattr(Shift, 'is_agency') else shifts.none()
    agency_markup = Decimal('1.4')  # 40% markup typical
    agency_cost = Decimal('0.00')
    
    for shift in agency_shifts:
        role = shift.staff.role if shift.staff else 'HCA'
        base_rate = HOURLY_RATES.get(role, Decimal('14.00'))
        shift_type = shift.shift_pattern.name if shift.shift_pattern else 'Early'
        hours = SHIFT_HOURS.get(shift_type, 8)
        agency_cost += Decimal(hours) * base_rate * agency_markup
    
    # Overtime costs
    overtime_requests = OvertimeCoverageRequest.objects.filter(
        shift_date__gte=start_date,
        shift_date__lte=end_date,
        status='FILLED'
    )
    
    if unit_id:
        overtime_requests = overtime_requests.filter(unit_id=unit_id)
    
    overtime_cost = Decimal('0.00')
    overtime_premium = Decimal('1.5')  # Time and a half
    
    for ot_request in overtime_requests:
        role = ot_request.required_role
        base_rate = HOURLY_RATES.get(role, Decimal('14.00'))
        shift_type = ot_request.shift_type
        hours = SHIFT_HOURS.get(shift_type, 8)
        overtime_cost += Decimal(hours) * base_rate * overtime_premium
    
    # Calculate budget variance
    # Assume budgeted cost is 95% of total staff cost + agency cost
    budgeted_cost = (total_staff_cost + agency_cost) * Decimal('0.95')
    actual_cost = total_staff_cost + agency_cost + overtime_cost
    variance = actual_cost - budgeted_cost
    variance_percent = (variance / budgeted_cost * 100) if budgeted_cost > 0 else 0
    
    # Cost per shift
    cost_per_shift = actual_cost / total_shifts if total_shifts > 0 else 0
    
    # Weekly breakdown for chart
    weekly_data = []
    current_date = start_date
    
    while current_date <= end_date:
        week_end = current_date + timedelta(days=6)
        if week_end > end_date:
            week_end = end_date
        
        week_shifts = shifts.filter(date__gte=current_date, date__lte=week_end)
        week_cost = Decimal('0.00')
        
        for shift in week_shifts:
            role = shift.staff.role if shift.staff else 'HCA'
            base_rate = HOURLY_RATES.get(role, Decimal('14.00'))
            shift_type = shift.shift_pattern.name if shift.shift_pattern else 'Early'
            hours = SHIFT_HOURS.get(shift_type, 8)
            week_cost += Decimal(hours) * base_rate
        
        weekly_data.append({
            'week_start': current_date.strftime('%b %d'),
            'cost': float(week_cost)
        })
        
        current_date = week_end + timedelta(days=1)
    
    # Cost by home
    home_costs = []
    units = Unit.objects.all()
    
    for unit in units:
        unit_shifts = shifts.filter(unit=unit)
        unit_cost = Decimal('0.00')
        
        for shift in unit_shifts:
            role = shift.staff.role if shift.staff else 'HCA'
            base_rate = HOURLY_RATES.get(role, Decimal('14.00'))
            shift_type = shift.shift_pattern.name if shift.shift_pattern else 'Early'
            hours = SHIFT_HOURS.get(shift_type, 8)
            unit_cost += Decimal(hours) * base_rate
        
        if unit_cost > 0:
            home_costs.append({
                'name': unit.name,
                'shifts': unit_shifts.count(),
                'cost': unit_cost
            })
    
    # Sort by cost descending
    home_costs.sort(key=lambda x: x['cost'], reverse=True)
    
    # Calculate savings from overtime system
    # Compare agency cost avoided by using internal OT
    ot_shifts_filled = overtime_requests.count()
    agency_cost_avoided = ot_shifts_filled * 8 * Decimal('22.00') * Decimal('0.4')  # 40% agency markup
    ot_system_savings = agency_cost_avoided - (overtime_cost - (ot_shifts_filled * 8 * Decimal('22.00')))
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'selected_unit': unit_id,
        'units': units,
        
        # Summary metrics
        'total_shifts': total_shifts,
        'total_staff_cost': total_staff_cost,
        'agency_cost': agency_cost,
        'overtime_cost': overtime_cost,
        'actual_cost': actual_cost,
        'budgeted_cost': budgeted_cost,
        'variance': variance,
        'variance_percent': variance_percent,
        'cost_per_shift': cost_per_shift,
        
        # Breakdown data
        'staff_cost_data': staff_cost_data,
        'weekly_data': json.dumps(weekly_data),
        'home_costs': home_costs,
        
        # Overtime system metrics
        'ot_requests': overtime_requests.count(),
        'ot_filled': ot_shifts_filled,
        'ot_response_rate': (overtime_requests.filter(total_responses__gt=0).count() / overtime_requests.count() * 100) if overtime_requests.count() > 0 else 0,
        'ot_system_savings': ot_system_savings,
        'agency_cost_avoided': agency_cost_avoided,
    }
    
    return render(request, 'scheduling/rota_cost_analysis.html', context)


@login_required
def export_cost_analysis_pdf(request):
    """Export cost analysis as PDF"""
    from django.template.loader import render_to_string
    from weasyprint import HTML
    
    # Get same data as main view
    # (In production, extract this to a shared function)
    
    html_string = render_to_string('scheduling/cost_analysis_pdf.html', {
        # Pass context here
    })
    
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rota_cost_analysis.pdf"'
    
    return response


@login_required
def export_cost_analysis_excel(request):
    """Export cost analysis as Excel"""
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    from io import BytesIO
    
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cost Analysis"
    
    # Header styling
    header_fill = PatternFill(start_color="0066CC", end_color="0066CC", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    
    # Title
    ws['A1'] = 'Rota Cost Analysis Report'
    ws['A1'].font = Font(size=16, bold=True)
    ws.merge_cells('A1:F1')
    
    # Date range
    start_date = request.GET.get('start_date', timezone.now().date() - timedelta(days=30))
    end_date = request.GET.get('end_date', timezone.now().date())
    ws['A2'] = f'Period: {start_date} to {end_date}'
    ws.merge_cells('A2:F2')
    
    # Summary section
    ws['A4'] = 'Summary Metrics'
    ws['A4'].font = Font(bold=True, size=14)
    
    summary_headers = ['Metric', 'Value']
    for col, header in enumerate(summary_headers, 1):
        cell = ws.cell(row=5, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    # Add summary data
    # (Would populate from actual calculations)
    
    # Cost by role section
    ws['A20'] = 'Cost by Role'
    ws['A20'].font = Font(bold=True, size=14)
    
    role_headers = ['Role', 'Shifts', 'Hours', 'Hourly Rate', 'Total Cost']
    for col, header in enumerate(role_headers, 1):
        cell = ws.cell(row=21, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    
    # Add role data
    # (Would populate from actual calculations)
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="rota_cost_analysis.xlsx"'
    
    return response


@login_required
def export_cost_analysis_csv(request):
    """Export cost analysis as CSV"""
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rota_cost_analysis.csv"'
    
    writer = csv.writer(response)
    
    # Headers
    writer.writerow(['Rota Cost Analysis Report'])
    writer.writerow([f'Period: {request.GET.get("start_date")} to {request.GET.get("end_date")}'])
    writer.writerow([])
    
    # Summary metrics
    writer.writerow(['Summary Metrics'])
    writer.writerow(['Metric', 'Value'])
    # (Would populate from actual calculations)
    
    writer.writerow([])
    
    # Cost by role
    writer.writerow(['Cost by Role'])
    writer.writerow(['Role', 'Shifts', 'Hours', 'Hourly Rate', 'Total Cost'])
    # (Would populate from actual calculations)
    
    return response
