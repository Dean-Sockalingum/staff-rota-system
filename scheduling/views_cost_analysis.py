from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import json

# Try to import optional libraries
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    from weasyprint import HTML
    PDF_AVAILABLE = True
except (ImportError, OSError) as e:
    PDF_AVAILABLE = False
    print(f"WeasyPrint not available in views_cost_analysis: {e}")

from scheduling.models import Shift, Unit
from scheduling.models_overtime import OvertimeCoverageRequest


def rota_cost_analysis(request):
    """
    Comprehensive rota cost analysis dashboard with metrics, charts, and export.
    """
    # Get date range from request or default to last 30 days
    end_date = request.GET.get('end_date')
    start_date = request.GET.get('start_date')
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = datetime.now().date()
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)
    
    # Get care home filter
    from scheduling.models_multi_home import CareHome
    care_home_id = request.GET.get('care_home')
    
    # Get shifts in date range
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home_id:
        shifts = shifts.filter(unit__care_home__name=care_home_id)
    
    # Calculate cost metrics
    total_shifts = shifts.count()
    
    # Hourly rates by shift classification
    HOURLY_RATES = {
        'REGULAR': Decimal('18.00'),
        'OVERTIME': Decimal('27.00'),  # 1.5x rate
        'AGENCY': Decimal('25.00'),
    }
    
    SHIFT_HOURS = 12  # Standard 12-hour shifts
    
    # Calculate costs by classification
    regular_shifts = shifts.filter(shift_classification='REGULAR')
    overtime_shifts = shifts.filter(shift_classification='OVERTIME')
    agency_shifts = shifts.filter(shift_classification='AGENCY')
    
    regular_cost = regular_shifts.count() * SHIFT_HOURS * HOURLY_RATES['REGULAR']
    overtime_cost = overtime_shifts.count() * SHIFT_HOURS * HOURLY_RATES['OVERTIME']
    agency_cost = agency_shifts.count() * SHIFT_HOURS * HOURLY_RATES['AGENCY']
    
    total_staff_cost = regular_cost
    
    # Cost breakdown data
    staff_cost_data = [
        {
            'role': 'Regular Shifts',
            'shifts': regular_shifts.count(),
            'hours': regular_shifts.count() * SHIFT_HOURS,
            'hourly_rate': HOURLY_RATES['REGULAR'],
            'total_cost': regular_cost
        },
        {
            'role': 'Overtime Shifts',
            'shifts': overtime_shifts.count(),
            'hours': overtime_shifts.count() * SHIFT_HOURS,
            'hourly_rate': HOURLY_RATES['OVERTIME'],
            'total_cost': overtime_cost
        },
        {
            'role': 'Agency Shifts',
            'shifts': agency_shifts.count(),
            'hours': agency_shifts.count() * SHIFT_HOURS,
            'hourly_rate': HOURLY_RATES['AGENCY'],
            'total_cost': agency_cost
        },
    ]
    
    # Calculate actual total cost
    actual_cost = total_staff_cost + agency_cost + overtime_cost
    
    # Budget calculation (95% of regular + agency costs)
    budgeted_cost = (total_staff_cost + agency_cost) * Decimal('0.95')
    variance = actual_cost - budgeted_cost
    variance_percent = (variance / budgeted_cost * 100) if budgeted_cost > 0 else 0
    
    cost_per_shift = actual_cost / total_shifts if total_shifts > 0 else 0
    
    # Time series breakdown for chart
    # Use monthly aggregation for date ranges > 90 days, weekly otherwise
    days_in_range = (end_date - start_date).days
    weekly_data = []
    
    if days_in_range > 90:
        # Monthly aggregation for long date ranges
        from django.db.models.functions import TruncMonth
        
        monthly_shifts = shifts.annotate(month=TruncMonth('date')).values('month').annotate(
            regular_count=Count('id', filter=Q(shift_classification='REGULAR')),
            overtime_count=Count('id', filter=Q(shift_classification='OVERTIME')),
            agency_count=Count('id', filter=Q(shift_classification='AGENCY'))
        ).order_by('month')
        
        for month_data in monthly_shifts:
            month_regular = month_data['regular_count'] * SHIFT_HOURS * HOURLY_RATES['REGULAR']
            month_overtime = month_data['overtime_count'] * SHIFT_HOURS * HOURLY_RATES['OVERTIME']
            month_agency = month_data['agency_count'] * SHIFT_HOURS * HOURLY_RATES['AGENCY']
            month_cost = month_regular + month_overtime + month_agency
            
            weekly_data.append({
                'week_start': month_data['month'].strftime('%b %Y'),
                'cost': float(month_cost)
            })
    else:
        # Weekly aggregation for shorter date ranges
        current_date = start_date
        
        while current_date <= end_date:
            week_end = current_date + timedelta(days=6)
            if week_end > end_date:
                week_end = end_date
            
            week_shifts = shifts.filter(date__gte=current_date, date__lte=week_end)
            week_regular = week_shifts.filter(shift_classification='REGULAR').count() * SHIFT_HOURS * HOURLY_RATES['REGULAR']
            week_overtime = week_shifts.filter(shift_classification='OVERTIME').count() * SHIFT_HOURS * HOURLY_RATES['OVERTIME']
            week_agency = week_shifts.filter(shift_classification='AGENCY').count() * SHIFT_HOURS * HOURLY_RATES['AGENCY']
            week_cost = week_regular + week_overtime + week_agency
            
            weekly_data.append({
                'week_start': current_date.strftime('%b %d'),
                'cost': float(week_cost)
            })
            
            current_date = week_end + timedelta(days=1)
    
    # Cost by home - use aggregation instead of loop
    home_costs = []
    
    # Group shifts by care home and calculate costs in one query
    from django.db.models import Sum, Case, When, IntegerField
    
    home_aggregates = shifts.values('unit__care_home__name', 'unit__care_home_id').annotate(
        total_shifts=Count('id'),
        regular_count=Count('id', filter=Q(shift_classification='REGULAR')),
        overtime_count=Count('id', filter=Q(shift_classification='OVERTIME')),
        agency_count=Count('id', filter=Q(shift_classification='AGENCY'))
    ).filter(total_shifts__gt=0)
    
    for home_data in home_aggregates:
        home_regular = home_data['regular_count'] * SHIFT_HOURS * HOURLY_RATES['REGULAR']
        home_overtime = home_data['overtime_count'] * SHIFT_HOURS * HOURLY_RATES['OVERTIME']
        home_agency = home_data['agency_count'] * SHIFT_HOURS * HOURLY_RATES['AGENCY']
        home_cost = home_regular + home_overtime + home_agency
        
        home_costs.append({
            'name': home_data['unit__care_home__name'] or 'Unknown',
            'shifts': home_data['total_shifts'],
            'cost': float(home_cost),
            'cost_per_shift': float(home_cost / home_data['total_shifts']) if home_data['total_shifts'] > 0 else 0
        })
    
    # Calculate percentage for each home
    for home in home_costs:
        home['percentage'] = (home['cost'] / float(actual_cost) * 100) if actual_cost > 0 else 0
    
    # Sort by cost descending
    home_costs.sort(key=lambda x: x['cost'], reverse=True)
    
    # OT system performance - TEMPORARILY DISABLED (table not migrated)
    # ot_requests = OvertimeCoverageRequest.objects.filter(
    #     shift_date__gte=start_date,
    #     shift_date__lte=end_date
    # )
    # 
    # if care_home_id:
    #     ot_requests = ot_requests.filter(unit__care_home__name=care_home_id)
    # 
    # ot_requests_total = ot_requests.count()
    # ot_filled = ot_requests.filter(status='FILLED').count()
    # ot_response_rate = (ot_filled / ot_requests_total * 100) if ot_requests_total > 0 else 0
    # 
    # # Estimate agency cost avoided by using OT
    # agency_cost_avoided = ot_filled * SHIFT_HOURS * (HOURLY_RATES['AGENCY'] - HOURLY_RATES['OVERTIME'])
    # ot_system_savings = agency_cost_avoided
    
    # Placeholder values until OT table is migrated
    ot_requests_total = 0
    ot_filled = 0
    ot_response_rate = 0
    ot_system_savings = 0
    agency_cost_avoided = 0
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'selected_care_home': care_home_id,
        'care_homes': CareHome.objects.filter(is_active=True).order_by('name'),
        'total_shifts': total_shifts,
        'total_staff_cost': total_staff_cost,
        'agency_cost': agency_cost,
        'overtime_cost': overtime_cost,
        'actual_cost': actual_cost,
        'budgeted_cost': budgeted_cost,
        'variance': variance,
        'variance_percent': variance_percent,
        'cost_per_shift': cost_per_shift,
        'staff_cost_data': staff_cost_data,
        'weekly_data': json.dumps(weekly_data),
        'home_costs': home_costs,
        'ot_requests': ot_requests_total,
        'ot_filled': ot_filled,
        'ot_response_rate': ot_response_rate,
        'ot_system_savings': ot_system_savings,
        'agency_cost_avoided': agency_cost_avoided,
    }
    
    return render(request, 'scheduling/rota_cost_analysis.html', context)


def export_cost_analysis_pdf(request):
    """Export cost analysis as PDF."""
    if not PDF_AVAILABLE:
        return HttpResponse("PDF export requires weasyprint library", status=501)
    
    # Get filter parameters
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    care_home_id = request.GET.get('care_home', '')
    
    # Parse dates
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = (datetime.now() - timedelta(days=30)).date()
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = datetime.now().date()
    
    # Get shifts data (reusing same logic as main view)
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('user', 'user__role', 'shift_type', 'unit', 'unit__care_home')
    
    if care_home_id:
        shifts = shifts.filter(unit__care_home__name=care_home_id)
    
    total_shifts = shifts.count()
    
    # Cost calculations
    HOURLY_RATES = {
        'REGULAR': Decimal('21.60'),
        'OVERTIME': Decimal('32.40'),
        'AGENCY': Decimal('38.88'),
    }
    SHIFT_HOURS = Decimal('8.0')
    
    regular_shifts = shifts.filter(Q(shift_classification='REGULAR') | Q(shift_classification__isnull=True))
    regular_cost = regular_shifts.count() * SHIFT_HOURS * HOURLY_RATES['REGULAR']
    
    overtime_shifts = shifts.filter(shift_classification='OVERTIME')
    overtime_cost = overtime_shifts.count() * SHIFT_HOURS * HOURLY_RATES['OVERTIME']
    
    agency_shifts = shifts.filter(shift_classification='AGENCY')
    agency_cost = agency_shifts.count() * SHIFT_HOURS * HOURLY_RATES['AGENCY']
    
    total_staff_cost = regular_cost + overtime_cost + agency_cost
    actual_cost = total_staff_cost
    
    # Budget calculation
    days_in_period = (end_date - start_date).days + 1
    DAILY_BUDGET = Decimal('17003.37')
    budgeted_cost = DAILY_BUDGET * days_in_period
    budget_variance = actual_cost - budgeted_cost
    
    # Cost per shift
    cost_per_shift = (actual_cost / total_shifts) if total_shifts > 0 else Decimal('0')
    
    # Generate HTML for PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 8px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .date-range {{
                text-align: center;
                color: #7f8c8d;
                margin-bottom: 20px;
                font-size: 14px;
            }}
            .metrics {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin: 20px 0;
            }}
            .metric {{
                flex: 1;
                min-width: 200px;
                padding: 15px;
                background: #ecf0f1;
                border-radius: 5px;
            }}
            .metric-label {{
                font-size: 12px;
                color: #7f8c8d;
                text-transform: uppercase;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #34495e;
                color: white;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .cost-breakdown {{
                margin: 20px 0;
                padding: 20px;
                background: #f8f9fa;
                border-left: 4px solid #3498db;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                text-align: center;
                font-size: 12px;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Rota Cost Analysis Report</h1>
            <div class="date-range">
                {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}
                {f'<br>Care Home: {care_home_id}' if care_home_id else '<br>All Care Homes'}
            </div>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Total Shifts</div>
                <div class="metric-value">{total_shifts:,}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Staff Cost</div>
                <div class="metric-value">£{total_staff_cost:,.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Cost Per Shift</div>
                <div class="metric-value">£{cost_per_shift:.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Budget Variance</div>
                <div class="metric-value">£{budget_variance:,.2f}</div>
            </div>
        </div>
        
        <h2>Cost Breakdown</h2>
        <div class="cost-breakdown">
            <table>
                <tr>
                    <th>Category</th>
                    <th>Shifts</th>
                    <th>Cost</th>
                </tr>
                <tr>
                    <td>Regular Shifts</td>
                    <td>{regular_shifts.count():,}</td>
                    <td>£{regular_cost:,.2f}</td>
                </tr>
                <tr>
                    <td>Overtime Shifts</td>
                    <td>{overtime_shifts.count():,}</td>
                    <td>£{overtime_cost:,.2f}</td>
                </tr>
                <tr>
                    <td>Agency Shifts</td>
                    <td>{agency_shifts.count():,}</td>
                    <td>£{agency_cost:,.2f}</td>
                </tr>
                <tr style="font-weight: bold; background-color: #ecf0f1;">
                    <td>Total</td>
                    <td>{total_shifts:,}</td>
                    <td>£{total_staff_cost:,.2f}</td>
                </tr>
            </table>
        </div>
        
        <h2>Budget Comparison</h2>
        <table>
            <tr>
                <th>Item</th>
                <th>Amount</th>
            </tr>
            <tr>
                <td>Budgeted Cost</td>
                <td>£{budgeted_cost:,.2f}</td>
            </tr>
            <tr>
                <td>Actual Cost</td>
                <td>£{actual_cost:,.2f}</td>
            </tr>
            <tr style="font-weight: bold;">
                <td>Variance</td>
                <td style="color: {'#e74c3c' if budget_variance > 0 else '#27ae60'}">
                    £{budget_variance:,.2f} ({(budget_variance / budgeted_cost * 100):.1f}%)
                </td>
            </tr>
        </table>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>© 2026 Glasgow HSCP - Staff Rota Management System</p>
        </div>
    </body>
    </html>
    """
    
    pdf = HTML(string=html_content).write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cost_analysis_{start_date}_{end_date}.pdf"'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def export_cost_analysis_excel(request):
    """Export cost analysis as Excel."""
    if not EXCEL_AVAILABLE:
        return HttpResponse("Excel export requires openpyxl library", status=501)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Cost Analysis"
    
    # Add headers
    headers = ['Period', 'Total Shifts', 'Staff Cost', 'Agency Cost', 'OT Cost', 'Total Cost']
    ws.append(headers)
    
    # Add sample data (would be real data in production)
    ws.append(['Last 30 days', 100, 21600, 15000, 16200, 52800])
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="cost_analysis.xlsx"'
    wb.save(response)
    
    return response


def export_cost_analysis_csv(request):
    """Export cost analysis as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cost_analysis.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Period', 'Total Shifts', 'Staff Cost', 'Agency Cost', 'OT Cost', 'Total Cost'])
    writer.writerow(['Last 30 days', '100', '21600', '15000', '16200', '52800'])
    
    return response
