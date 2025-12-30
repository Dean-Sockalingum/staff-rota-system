"""
Report Builder Service
======================

Service layer for building and executing custom reports.

Created: 30 December 2025
Task 40: Custom Report Builder
"""

from django.db.models import Count, Sum, Avg, Max, Min, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import json
import time

from .models import Shift, User, Unit, LeaveRequest, ShiftSwapRequest
from .models_multi_home import CareHome
from .models_reports import CustomReportTemplate, CustomSavedReport


class ReportQueryBuilder:
    """
    Builds Django ORM queries from report template configurations.
    """
    
    # Map of available models
    AVAILABLE_MODELS = {
        'Shift': Shift,
        'User': User,
        'Unit': Unit,
        'CareHome': CareHome,
        'LeaveRequest': LeaveRequest,
        'ShiftSwapRequest': ShiftSwapRequest,
    }
    
    # Map of aggregation functions
    AGGREGATIONS = {
        'count': Count,
        'sum': Sum,
        'avg': Avg,
        'max': Max,
        'min': Min,
    }
    
    @classmethod
    def build_query(cls, template):
        """
        Build a Django queryset from a report template.
        """
        # Get base model
        model_name = template.data_sources.get('base_model')
        if model_name not in cls.AVAILABLE_MODELS:
            raise ValueError(f"Invalid model: {model_name}")
        
        Model = cls.AVAILABLE_MODELS[model_name]
        queryset = Model.objects.all()
        
        # Apply filters
        filters = cls._build_filters(template.filters)
        if filters:
            queryset = queryset.filter(filters)
        
        # Apply select_related/prefetch_related for performance
        related_fields = template.data_sources.get('related_fields', [])
        if related_fields:
            queryset = queryset.select_related(*related_fields)
        
        return queryset
    
    @classmethod
    def _build_filters(cls, filter_config):
        """
        Build Q objects from filter configuration.
        """
        if not filter_config:
            return Q()
        
        q_objects = Q()
        
        for filter_item in filter_config:
            field = filter_item.get('field')
            operator = filter_item.get('operator', 'exact')
            value = filter_item.get('value')
            logical = filter_item.get('logical', 'AND')
            
            # Build lookup
            lookup = f"{field}__{operator}"
            filter_q = Q(**{lookup: value})
            
            # Combine with logical operator
            if logical == 'AND':
                q_objects &= filter_q
            elif logical == 'OR':
                q_objects |= filter_q
            elif logical == 'NOT':
                q_objects &= ~filter_q
        
        return q_objects
    
    @classmethod
    def apply_grouping(cls, queryset, grouping_config):
        """
        Apply grouping and aggregations to queryset.
        """
        if not grouping_config:
            return queryset
        
        group_fields = [g['field'] for g in grouping_config]
        
        # Get aggregations from config
        aggregations = {}
        for group in grouping_config:
            if 'aggregations' in group:
                for agg in group['aggregations']:
                    agg_func = cls.AGGREGATIONS.get(agg['function'])
                    if agg_func:
                        agg_field = agg['field']
                        agg_name = f"{agg['function']}_{agg_field}"
                        aggregations[agg_name] = agg_func(agg_field)
        
        if group_fields:
            queryset = queryset.values(*group_fields).annotate(**aggregations)
        
        return queryset
    
    @classmethod
    def apply_sorting(cls, queryset, sorting_config):
        """
        Apply sorting to queryset.
        """
        if not sorting_config:
            return queryset
        
        order_fields = []
        for sort in sorting_config:
            field = sort['field']
            direction = sort.get('direction', 'asc')
            
            if direction == 'desc':
                field = f"-{field}"
            
            order_fields.append(field)
        
        return queryset.order_by(*order_fields)


class ReportExecutor:
    """
    Executes report templates and generates results.
    """
    
    @staticmethod
    def execute(template, parameters=None, user=None):
        """
        Execute a report template and return results.
        
        Args:
            template: ReportTemplate instance
            parameters: Dict of runtime parameters
            user: User executing the report
        
        Returns:
            SavedReport instance
        """
        start_time = time.time()
        
        # Create saved report instance
        saved_report = SavedReport.objects.create(
            template=template,
            generated_by=user,
            parameters=parameters or {},
            status='GENERATING'
        )
        
        try:
            # Build and execute query
            queryset = ReportQueryBuilder.build_query(template)
            
            # Apply runtime parameters
            if parameters:
                queryset = ReportExecutor._apply_parameters(queryset, parameters)
            
            # Apply grouping
            if template.grouping:
                queryset = ReportQueryBuilder.apply_grouping(queryset, template.grouping)
            
            # Apply sorting
            if template.sorting:
                queryset = ReportQueryBuilder.apply_sorting(queryset, template.sorting)
            
            # Extract data
            data = list(queryset.values())
            
            # Apply column selection
            if template.columns:
                column_names = [col['field'] for col in template.columns]
                data = [
                    {k: v for k, v in row.items() if k in column_names}
                    for row in data
                ]
            
            # Update saved report
            execution_time = time.time() - start_time
            
            saved_report.data = {'rows': data}
            saved_report.row_count = len(data)
            saved_report.execution_time = execution_time
            saved_report.status = 'COMPLETED'
            saved_report.save()
            
            # Update template statistics
            template.increment_run_count(execution_time)
            
            return saved_report
            
        except Exception as e:
            # Handle errors
            execution_time = time.time() - start_time
            
            saved_report.status = 'FAILED'
            saved_report.error_message = str(e)
            saved_report.execution_time = execution_time
            saved_report.save()
            
            raise
    
    @staticmethod
    def _apply_parameters(queryset, parameters):
        """
        Apply runtime parameters to queryset.
        """
        # Date range parameters
        if 'start_date' in parameters:
            queryset = queryset.filter(date__gte=parameters['start_date'])
        if 'end_date' in parameters:
            queryset = queryset.filter(date__lte=parameters['end_date'])
        
        # Care home filter
        if 'care_home_id' in parameters:
            queryset = queryset.filter(
                unit__care_home_id=parameters['care_home_id']
            )
        
        # Unit filter
        if 'unit_id' in parameters:
            queryset = queryset.filter(unit_id=parameters['unit_id'])
        
        # User filter
        if 'user_sap' in parameters:
            queryset = queryset.filter(user__sap=parameters['user_sap'])
        
        return queryset


class ReportExporter:
    """
    Exports reports to various formats (PDF, Excel, CSV).
    """
    
    @staticmethod
    def export_to_csv(saved_report):
        """
        Export report data to CSV format.
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        
        data = saved_report.data.get('rows', [])
        if not data:
            return ''
        
        # Get column names from first row
        columns = list(data[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    @staticmethod
    def export_to_excel(saved_report):
        """
        Export report data to Excel format using openpyxl.
        """
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            from io import BytesIO
        except ImportError:
            raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
        
        wb = Workbook()
        ws = wb.active
        ws.title = saved_report.template.name[:31]  # Excel sheet name limit
        
        data = saved_report.data.get('rows', [])
        if not data:
            return BytesIO()
        
        # Get columns
        columns = list(data[0].keys())
        
        # Add header row with formatting
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        for col_num, column_name in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = column_name.replace('_', ' ').title()
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Add data rows
        for row_num, row_data in enumerate(data, 2):
            for col_num, column_name in enumerate(columns, 1):
                ws.cell(row=row_num, column=col_num, value=row_data.get(column_name))
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
    
    @staticmethod
    def export_to_pdf(saved_report):
        """
        Export report data to PDF format using ReportLab.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from io import BytesIO
        except ImportError:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")
        
        output = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(letter),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#366092'),
            spaceAfter=12
        )
        elements.append(Paragraph(saved_report.template.name, title_style))
        
        # Metadata
        meta_text = f"Generated: {saved_report.generated_at.strftime('%Y-%m-%d %H:%M')} | "
        meta_text += f"Rows: {saved_report.row_count} | "
        meta_text += f"Execution time: {saved_report.execution_time:.2f}s"
        elements.append(Paragraph(meta_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Data table
        data = saved_report.data.get('rows', [])
        if data:
            columns = list(data[0].keys())
            
            # Prepare table data
            table_data = [
                [col.replace('_', ' ').title() for col in columns]
            ]
            
            for row in data:
                table_data.append([str(row.get(col, '')) for col in columns])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        output.seek(0)
        
        return output
    
    @staticmethod
    def export_to_json(saved_report):
        """
        Export report data to JSON format.
        """
        return json.dumps(saved_report.data, indent=2, default=str)


class ReportTemplateBuilder:
    """
    Helper class for building report templates programmatically.
    """
    
    @staticmethod
    def create_staff_attendance_report(user):
        """
        Create a pre-configured staff attendance report template.
        """
        template = ReportTemplate.objects.create(
            name='Staff Attendance Report',
            description='Track staff attendance rates and patterns',
            report_type='STAFF',
            created_by=user,
            data_sources={
                'base_model': 'Shift',
                'related_fields': ['user', 'shift_type', 'unit']
            },
            filters=[
                {
                    'field': 'status',
                    'operator': 'in',
                    'value': ['COMPLETED', 'CONFIRMED'],
                    'logical': 'AND'
                }
            ],
            grouping=[
                {
                    'field': 'user__full_name',
                    'aggregations': [
                        {'function': 'count', 'field': 'id'},
                    ]
                }
            ],
            columns=[
                {'field': 'user__full_name', 'display_name': 'Staff Name', 'width': 200},
                {'field': 'count_id', 'display_name': 'Shifts Worked', 'width': 150},
            ],
            sorting=[
                {'field': 'count_id', 'direction': 'desc'}
            ],
            default_export_format='EXCEL'
        )
        
        return template
    
    @staticmethod
    def create_budget_analysis_report(user):
        """
        Create a pre-configured budget analysis report.
        """
        template = ReportTemplate.objects.create(
            name='Budget Analysis Report',
            description='Analyze overtime and agency spending by care home',
            report_type='BUDGET',
            created_by=user,
            data_sources={
                'base_model': 'Shift',
                'related_fields': ['unit__care_home', 'shift_type']
            },
            filters=[
                {
                    'field': 'is_overtime',
                    'operator': 'exact',
                    'value': True,
                    'logical': 'AND'
                }
            ],
            grouping=[
                {
                    'field': 'unit__care_home__name',
                    'aggregations': [
                        {'function': 'count', 'field': 'id'},
                    ]
                }
            ],
            columns=[
                {'field': 'unit__care_home__name', 'display_name': 'Care Home', 'width': 200},
                {'field': 'count_id', 'display_name': 'Overtime Shifts', 'width': 150},
            ],
            default_export_format='PDF'
        )
        
        return template
