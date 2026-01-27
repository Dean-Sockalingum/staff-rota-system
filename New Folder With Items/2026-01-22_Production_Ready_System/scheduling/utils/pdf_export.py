"""
PDF Export Utilities - Staff Rota System
December 2025

Provides PDF generation for:
- Weekly/monthly shift schedules
- Staff rotas
- Leave request reports
- Shift allocation summaries
- Custom date range reports

Uses WeasyPrint for HTML-to-PDF conversion with our existing print.css
"""

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from django.conf import settings
import os
from datetime import datetime, timedelta


class PDFGenerator:
    """
    Base PDF generator class using WeasyPrint
    """
    
    def __init__(self):
        self.font_config = FontConfiguration()
        
    def get_css_files(self):
        """
        Get list of CSS files to include in PDF
        """
        css_files = [
            os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'scheduling/static/css/design-system.css'),
            os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'scheduling/static/css/print.css'),
        ]
        return [CSS(filename=f, font_config=self.font_config) for f in css_files if os.path.exists(f)]
    
    def render_to_pdf(self, template_name, context, filename='document.pdf'):
        """
        Render a Django template to PDF
        
        Args:
            template_name: Path to Django template
            context: Template context dictionary
            filename: Output filename for download
            
        Returns:
            HttpResponse with PDF content
        """
        # Add common context
        context.update({
            'generated_date': datetime.now(),
            'is_pdf_export': True,
        })
        
        # Render HTML from template
        html_string = render_to_string(template_name, context)
        
        # Convert to PDF
        html = HTML(string=html_string, base_url=settings.STATIC_URL)
        pdf_file = html.write_pdf(stylesheets=self.get_css_files(), font_config=self.font_config)
        
        # Create HTTP response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_file)
        
        return response


class RotaPDFExporter(PDFGenerator):
    """
    Export shift rotas to PDF
    """
    
    def export_weekly_rota(self, home, week_start_date):
        """
        Export weekly rota for a specific home
        
        Args:
            home: Home model instance
            week_start_date: datetime object for start of week
            
        Returns:
            HttpResponse with PDF
        """
        from scheduling.models import Shift
        
        week_end_date = week_start_date + timedelta(days=6)
        
        # Get all shifts for the week
        shifts = Shift.objects.filter(
            home=home,
            shift_date__gte=week_start_date,
            shift_date__lte=week_end_date
        ).select_related('staff', 'home').order_by('shift_date', 'shift_type')
        
        # Organize shifts by date and type
        shifts_by_date = {}
        for day in range(7):
            current_date = week_start_date + timedelta(days=day)
            day_shifts = shifts.filter(shift_date=current_date)
            
            shifts_by_date[current_date] = {
                'early': day_shifts.filter(shift_type='Early'),
                'late': day_shifts.filter(shift_type='Late'),
                'night': day_shifts.filter(shift_type='Night'),
            }
        
        context = {
            'home': home,
            'week_start': week_start_date,
            'week_end': week_end_date,
            'shifts_by_date': shifts_by_date,
            'title': f'{home.name} - Weekly Rota',
            'report_type': 'Weekly Shift Schedule',
        }
        
        filename = f'{home.name}_Rota_Week_{week_start_date.strftime("%Y%m%d")}.pdf'
        
        return self.render_to_pdf('scheduling/pdf/weekly_rota.html', context, filename)
    
    def export_monthly_rota(self, home, month, year):
        """
        Export monthly rota for a specific home
        
        Args:
            home: Home model instance
            month: Month number (1-12)
            year: Year number
            
        Returns:
            HttpResponse with PDF
        """
        from scheduling.models import Shift
        from calendar import monthrange
        
        # Get first and last day of month
        first_day = datetime(year, month, 1).date()
        last_day_num = monthrange(year, month)[1]
        last_day = datetime(year, month, last_day_num).date()
        
        # Get all shifts for the month
        shifts = Shift.objects.filter(
            home=home,
            shift_date__gte=first_day,
            shift_date__lte=last_day
        ).select_related('staff', 'home').order_by('shift_date', 'shift_type')
        
        # Calculate statistics
        total_shifts = shifts.count()
        unique_staff = shifts.values('staff').distinct().count()
        shifts_by_type = {
            'Early': shifts.filter(shift_type='Early').count(),
            'Late': shifts.filter(shift_type='Late').count(),
            'Night': shifts.filter(shift_type='Night').count(),
        }
        
        context = {
            'home': home,
            'month': first_day.strftime('%B'),
            'year': year,
            'first_day': first_day,
            'last_day': last_day,
            'shifts': shifts,
            'total_shifts': total_shifts,
            'unique_staff': unique_staff,
            'shifts_by_type': shifts_by_type,
            'title': f'{home.name} - Monthly Rota',
            'report_type': 'Monthly Shift Schedule',
        }
        
        filename = f'{home.name}_Rota_{first_day.strftime("%B_%Y")}.pdf'
        
        return self.render_to_pdf('scheduling/pdf/monthly_rota.html', context, filename)
    
    def export_staff_schedule(self, staff, start_date, end_date):
        """
        Export individual staff member's schedule
        
        Args:
            staff: Staff model instance
            start_date: Start date for report
            end_date: End date for report
            
        Returns:
            HttpResponse with PDF
        """
        from scheduling.models import Shift
        
        shifts = Shift.objects.filter(
            staff=staff,
            shift_date__gte=start_date,
            shift_date__lte=end_date
        ).select_related('home').order_by('shift_date', 'shift_type')
        
        # Calculate statistics
        total_shifts = shifts.count()
        total_hours = sum([shift.get_hours() for shift in shifts])
        shifts_by_home = {}
        for shift in shifts:
            if shift.home.name not in shifts_by_home:
                shifts_by_home[shift.home.name] = 0
            shifts_by_home[shift.home.name] += 1
        
        context = {
            'staff': staff,
            'start_date': start_date,
            'end_date': end_date,
            'shifts': shifts,
            'total_shifts': total_shifts,
            'total_hours': total_hours,
            'shifts_by_home': shifts_by_home,
            'title': f'{staff.first_name} {staff.last_name} - Personal Schedule',
            'report_type': 'Individual Staff Schedule',
        }
        
        filename = f'{staff.first_name}_{staff.last_name}_Schedule_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf'
        
        return self.render_to_pdf('scheduling/pdf/staff_schedule.html', context, filename)


class LeaveReportPDFExporter(PDFGenerator):
    """
    Export leave request reports to PDF
    """
    
    def export_leave_summary(self, start_date, end_date, home=None):
        """
        Export leave request summary for date range
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            home: Optional Home filter
            
        Returns:
            HttpResponse with PDF
        """
        from scheduling.models import LeaveRequest
        
        queryset = LeaveRequest.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).select_related('staff')
        
        if home:
            queryset = queryset.filter(staff__primary_home=home)
        
        # Organize by status
        approved = queryset.filter(status='Approved')
        pending = queryset.filter(status='Pending')
        rejected = queryset.filter(status='Rejected')
        
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'home': home,
            'approved_requests': approved,
            'pending_requests': pending,
            'rejected_requests': rejected,
            'total_requests': queryset.count(),
            'title': 'Leave Request Summary',
            'report_type': 'Leave Request Report',
        }
        
        home_suffix = f'_{home.name}' if home else ''
        filename = f'Leave_Summary{home_suffix}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf'
        
        return self.render_to_pdf('scheduling/pdf/leave_summary.html', context, filename)


class ShiftAllocationPDFExporter(PDFGenerator):
    """
    Export shift allocation reports to PDF
    """
    
    def export_allocation_summary(self, home, week_start_date):
        """
        Export shift allocation summary showing staffing levels
        
        Args:
            home: Home model instance
            week_start_date: Start of week
            
        Returns:
            HttpResponse with PDF
        """
        from scheduling.models import Shift
        
        week_end_date = week_start_date + timedelta(days=6)
        
        # Get allocation by day and shift type
        allocation_data = []
        for day in range(7):
            current_date = week_start_date + timedelta(days=day)
            day_shifts = Shift.objects.filter(
                home=home,
                shift_date=current_date
            )
            
            allocation_data.append({
                'date': current_date,
                'early_count': day_shifts.filter(shift_type='Early').count(),
                'late_count': day_shifts.filter(shift_type='Late').count(),
                'night_count': day_shifts.filter(shift_type='Night').count(),
                'total_count': day_shifts.count(),
            })
        
        context = {
            'home': home,
            'week_start': week_start_date,
            'week_end': week_end_date,
            'allocation_data': allocation_data,
            'title': f'{home.name} - Shift Allocation Summary',
            'report_type': 'Staffing Levels Report',
        }
        
        filename = f'{home.name}_Allocation_Week_{week_start_date.strftime("%Y%m%d")}.pdf'
        
        return self.render_to_pdf('scheduling/pdf/allocation_summary.html', context, filename)
