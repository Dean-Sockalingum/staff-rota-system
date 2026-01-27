"""
QIA Evidence Pack Generator for Care Inspectorate Submissions
Generates comprehensive PDF reports aggregating QIA data by Quality Indicators
"""

import os
import django
from datetime import datetime, timedelta
from collections import defaultdict
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.platypus import Frame, PageTemplate, KeepTogether
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from quality_audits.models import QualityImprovementAction, QIAUpdate, QIAReview


class QIAEvidencePackGenerator:
    """Generate comprehensive evidence packs for Care Inspectorate submissions"""
    
    # Scottish Care Quality Indicators mapping
    QI_MAPPING = {
        '1.1': 'People experience compassion, dignity and respect',
        '1.2': 'People get the most out of life',
        '1.3': "People's health benefits from their care and support",
        '2.1': 'Children and young people are safe and protected',
        '2.2': 'Children and young people are respected and experience compassionate care',
        '3.1': "People's health and wellbeing improves",
        '4.1': 'People experience high quality facilities',
        '4.2': "The environment promotes people's health, safety and wellbeing",
        '5.1': "People's needs are met by the right number of staff",
        '5.2': 'People experience high quality care and support',
        '5.3': 'People experience effective leadership and management',
        '7.1': 'People are safe and protected from avoidable harm',
        '7.2': 'Infection prevention and control practices support a safe environment',
        '7.3': "People's needs are met safely",
    }
    
    def __init__(self, filename='QIA_Evidence_Pack.pdf'):
        self.filename = filename
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2*cm
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a4d7a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#555555'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#1a4d7a'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            borderColor=HexColor('#1a4d7a'),
            borderRadius=None,
        ))
        
        # QI Heading
        self.styles.add(ParagraphStyle(
            name='QIHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=HexColor('#2c5f8d'),
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body justified
        self.styles.add(ParagraphStyle(
            name='BodyJustified',
            parent=self.styles['BodyText'],
            alignment=TA_JUSTIFY,
            fontSize=10,
            spaceAfter=6
        ))
    
    def add_header_footer(self, canvas_obj, doc):
        """Add header and footer to each page"""
        canvas_obj.saveState()
        
        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(HexColor('#1a4d7a'))
        canvas_obj.drawString(2*cm, A4[1] - 1.5*cm, "Quality Improvement Actions - Evidence Pack")
        
        # Footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawString(2*cm, 1*cm, f"Generated: {datetime.now().strftime('%d %B %Y')}")
        canvas_obj.drawRightString(A4[0] - 2*cm, 1*cm, f"Page {doc.page}")
        
        canvas_obj.restoreState()
    
    def generate(self, start_date=None, end_date=None, qi_filter=None, 
                 source_filter=None, priority_filter=None):
        """Generate the complete evidence pack"""
        
        # Build queryset with filters
        qias = QualityImprovementAction.objects.all()
        
        if start_date:
            qias = qias.filter(created_at__gte=start_date)
        if end_date:
            qias = qias.filter(created_at__lte=end_date)
        if qi_filter:
            qias = qias.filter(regulatory_requirement__contains=qi_filter)
        if source_filter:
            qias = qias.filter(source_type=source_filter)
        if priority_filter:
            qias = qias.filter(priority=priority_filter)
        
        # Generate sections
        self._add_cover_page(qias, start_date, end_date)
        self._add_executive_summary(qias)
        self._add_qi_mapping_section(qias)
        self._add_source_analysis(qias)
        self._add_priority_tracking(qias)
        self._add_timeline_analysis(qias)
        self._add_effectiveness_reviews(qias)
        self._add_lessons_learned(qias)
        self._add_recommendations()
        
        # Build PDF
        self.doc.build(self.story, onFirstPage=self.add_header_footer, 
                      onLaterPages=self.add_header_footer)
        
        # Save to file
        pdf = self.buffer.getvalue()
        self.buffer.close()
        
        with open(self.filename, 'wb') as f:
            f.write(pdf)
        
        return self.filename
    
    def _add_cover_page(self, qias, start_date, end_date):
        """Generate cover page"""
        self.story.append(Spacer(1, 2*inch))
        
        # Title
        title = Paragraph("Quality Improvement Actions<br/>Evidence Pack", 
                         self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Subtitle with date range
        if start_date and end_date:
            subtitle_text = f"{start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}"
        else:
            subtitle_text = "All Records"
        subtitle = Paragraph(subtitle_text, self.styles['CustomSubtitle'])
        self.story.append(subtitle)
        
        self.story.append(Spacer(1, 1*inch))
        
        # Summary box
        summary_data = [
            ['Total QIAs', str(qias.count())],
            ['Active QIAs', str(qias.exclude(status__in=['CLOSED', 'REJECTED']).count())],
            ['Closed QIAs', str(qias.filter(status='CLOSED').count())],
            ['Completion Rate', f"{self._calculate_completion_rate(qias):.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0f8ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1a4d7a')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1a4d7a')),
        ]))
        
        self.story.append(summary_table)
        self.story.append(PageBreak())
    
    def _add_executive_summary(self, qias):
        """Generate executive summary"""
        self.story.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        total_count = qias.count()
        closed_count = qias.filter(status='CLOSED').count()
        completion_rate = self._calculate_completion_rate(qias)
        
        # Summary text
        summary_text = f"""
        This evidence pack summarises {total_count} Quality Improvement Actions (QIAs) 
        recorded in our Total Quality Management system. Of these, {closed_count} have been 
        successfully completed and closed, representing a completion rate of {completion_rate:.1f}%.
        <br/><br/>
        Our QIA system aligns with the Care Inspectorate's Quality Framework, ensuring systematic 
        identification, planning, implementation, and verification of improvement actions across 
        all aspects of care delivery.
        """
        
        self.story.append(Paragraph(summary_text, self.styles['BodyJustified']))
        self.story.append(Spacer(1, 0.3*inch))
        
        # Status breakdown table
        status_data = [['Status', 'Count', 'Percentage']]
        status_counts = qias.values('status').annotate(count=Count('id')).order_by('-count')
        
        for item in status_counts:
            status = item['status']
            count = item['count']
            percentage = (count / total_count * 100) if total_count > 0 else 0
            status_data.append([
                status.replace('_', ' ').title(),
                str(count),
                f"{percentage:.1f}%"
            ])
        
        status_table = Table(status_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a4d7a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        self.story.append(status_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_qi_mapping_section(self, qias):
        """Map QIAs to Care Inspectorate Quality Indicators"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Quality Indicator Mapping", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        intro_text = """
        The following section maps our Quality Improvement Actions to the Care Inspectorate's 
        Quality Indicators, demonstrating our systematic approach to quality assurance across 
        all key areas of care delivery.
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyJustified']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Group QIAs by QI
        qi_groups = defaultdict(list)
        for qia in qias:
            if qia.regulatory_requirement:
                # Extract QI codes (e.g., "QI 1.3" -> "1.3")
                import re
                qi_matches = re.findall(r'QI\s+(\d+\.\d+)', qia.regulatory_requirement)
                for qi_code in qi_matches:
                    qi_groups[qi_code].append(qia)
        
        # Generate section for each QI
        for qi_code in sorted(qi_groups.keys()):
            qi_qias = qi_groups[qi_code]
            qi_description = self.QI_MAPPING.get(qi_code, 'Quality Indicator')
            
            # QI heading
            qi_heading = f"QI {qi_code}: {qi_description}"
            self.story.append(Paragraph(qi_heading, self.styles['QIHeading']))
            
            # QIA summary for this QI
            qi_summary = f"{len(qi_qias)} QIA(s) addressing this Quality Indicator:"
            self.story.append(Paragraph(qi_summary, self.styles['BodyText']))
            self.story.append(Spacer(1, 0.1*inch))
            
            # Table of QIAs for this QI
            qi_table_data = [['Reference', 'Title', 'Status', 'Priority']]
            for qia in qi_qias[:10]:  # Limit to 10 per QI for space
                qi_table_data.append([
                    qia.reference_number,
                    qia.title[:50] + '...' if len(qia.title) > 50 else qia.title,
                    qia.get_status_display(),
                    qia.get_priority_display()
                ])
            
            qi_table = Table(qi_table_data, colWidths=[1.2*inch, 2.8*inch, 1*inch, 0.8*inch])
            qi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e6f2ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#1a4d7a')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            self.story.append(qi_table)
            self.story.append(Spacer(1, 0.2*inch))
    
    def _add_source_analysis(self, qias):
        """Analyze QIAs by source type"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Source Analysis", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        intro_text = """
        This section analyzes the sources of our Quality Improvement Actions, demonstrating 
        our multi-faceted approach to quality assurance through incidents, audits, risk 
        assessments, complaints, trend analysis, PDSA cycles, and inspection findings.
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyJustified']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Source breakdown
        source_counts = qias.values('source_type').annotate(count=Count('id')).order_by('-count')
        
        source_data = [['Source Type', 'Count', 'Percentage', 'Avg Completion %']]
        total_count = qias.count()
        
        for item in source_counts:
            source = item['source_type']
            count = item['count']
            percentage = (count / total_count * 100) if total_count > 0 else 0
            
            # Calculate average completion for this source
            source_qias = qias.filter(source_type=source)
            avg_completion = source_qias.aggregate(Avg('percent_complete'))['percent_complete__avg'] or 0
            
            source_data.append([
                source.replace('_', ' ').title(),
                str(count),
                f"{percentage:.1f}%",
                f"{avg_completion:.0f}%"
            ])
        
        source_table = Table(source_data, colWidths=[2*inch, 1*inch, 1.2*inch, 1.3*inch])
        source_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a4d7a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        self.story.append(source_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_priority_tracking(self, qias):
        """Track QIAs by priority level"""
        self.story.append(Paragraph("Priority Tracking", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Priority breakdown
        priority_counts = qias.values('priority').annotate(count=Count('id')).order_by('-count')
        
        priority_data = [['Priority', 'Total', 'Active', 'Closed', 'Overdue']]
        
        for item in priority_counts:
            priority = item['priority']
            total = item['count']
            active = qias.filter(priority=priority).exclude(status__in=['CLOSED', 'REJECTED']).count()
            closed = qias.filter(priority=priority, status='CLOSED').count()
            
            # Calculate overdue
            today = timezone.now().date()
            overdue = qias.filter(
                priority=priority,
                target_completion_date__lt=today
            ).exclude(status__in=['CLOSED', 'REJECTED']).count()
            
            priority_data.append([
                priority.title(),
                str(total),
                str(active),
                str(closed),
                str(overdue)
            ])
        
        priority_table = Table(priority_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        priority_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a4d7a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        self.story.append(priority_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_timeline_analysis(self, qias):
        """Analyze QIA timeline and trends"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Timeline Analysis", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        intro_text = """
        This section provides a timeline view of QIA creation and completion patterns, 
        helping identify trends and improvement opportunities in our quality management processes.
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyJustified']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Monthly breakdown
        from django.db.models.functions import TruncMonth
        
        monthly_data = qias.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            created=Count('id')
        ).order_by('-month')[:6]  # Last 6 months
        
        if monthly_data:
            timeline_data = [['Month', 'QIAs Created', 'QIAs Closed']]
            
            for item in monthly_data:
                month = item['month']
                created = item['created']
                
                # Count closed in same month
                closed = qias.filter(
                    closed_date__year=month.year,
                    closed_date__month=month.month
                ).count()
                
                timeline_data.append([
                    month.strftime('%B %Y'),
                    str(created),
                    str(closed)
                ])
            
            timeline_table = Table(timeline_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a4d7a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            self.story.append(timeline_table)
        else:
            self.story.append(Paragraph("No timeline data available.", self.styles['BodyText']))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_effectiveness_reviews(self, qias):
        """Show effectiveness review outcomes"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Effectiveness Reviews", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        intro_text = """
        Effectiveness reviews verify that implemented QIAs have achieved their intended outcomes 
        and that improvements are sustained over time. This section summarizes review findings.
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyJustified']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Get QIAs with reviews
        reviewed_qias = qias.filter(
            qiareview__isnull=False
        ).distinct()
        
        if reviewed_qias.exists():
            review_data = [['Reference', 'Title', 'Effective?', 'Sustainable?', 'Review Date']]
            
            for qia in reviewed_qias[:15]:  # Limit to 15
                reviews = QIAReview.objects.filter(qia=qia).order_by('-review_date')
                if reviews.exists():
                    latest_review = reviews.first()
                    review_data.append([
                        qia.reference_number,
                        qia.title[:40] + '...' if len(qia.title) > 40 else qia.title,
                        'Yes' if latest_review.is_effective else 'No',
                        'Yes' if latest_review.is_sustainable else 'No',
                        latest_review.review_date.strftime('%d/%m/%Y')
                    ])
            
            review_table = Table(review_data, colWidths=[1*inch, 2.3*inch, 0.8*inch, 0.9*inch, 1*inch])
            review_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a4d7a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (3, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            self.story.append(review_table)
        else:
            self.story.append(Paragraph("No effectiveness reviews recorded yet.", self.styles['BodyText']))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_lessons_learned(self, qias):
        """Compile lessons learned from QIAs"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Lessons Learned", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        intro_text = """
        Key lessons and insights captured from our quality improvement journey, supporting 
        knowledge sharing and continuous organizational learning.
        """
        self.story.append(Paragraph(intro_text, self.styles['BodyJustified']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Get QIAs with lessons learned
        qias_with_lessons = qias.filter(lessons_learned__isnull=False).exclude(lessons_learned='')
        
        if qias_with_lessons.exists():
            for qia in qias_with_lessons[:10]:  # Top 10
                lesson_title = f"{qia.reference_number}: {qia.title}"
                self.story.append(Paragraph(lesson_title, self.styles['QIHeading']))
                
                lesson_text = qia.lessons_learned[:500] + '...' if len(qia.lessons_learned) > 500 else qia.lessons_learned
                self.story.append(Paragraph(lesson_text, self.styles['BodyText']))
                self.story.append(Spacer(1, 0.15*inch))
        else:
            self.story.append(Paragraph("No lessons learned recorded yet.", self.styles['BodyText']))
    
    def _add_recommendations(self):
        """Add recommendations for spread and sustainability"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Recommendations", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        recommendations = """
        Based on the QIA data presented in this evidence pack, we recommend the following 
        actions to further strengthen our quality improvement processes:
        <br/><br/>
        <b>1. Spread Successful Improvements:</b> Identify high-performing QIAs and develop 
        plans to spread effective practices across other service areas.
        <br/><br/>
        <b>2. Address Overdue Actions:</b> Prioritize completion of overdue QIAs, particularly 
        those rated as critical or high priority.
        <br/><br/>
        <b>3. Enhance Effectiveness Reviews:</b> Ensure all implemented QIAs undergo formal 
        effectiveness reviews to verify sustained improvement.
        <br/><br/>
        <b>4. Strengthen QI Mapping:</b> Continue aligning all QIAs with Care Inspectorate 
        Quality Indicators to demonstrate systematic quality assurance.
        <br/><br/>
        <b>5. Share Learning:</b> Disseminate lessons learned through team meetings, training 
        sessions, and organizational knowledge management systems.
        """
        
        self.story.append(Paragraph(recommendations, self.styles['BodyJustified']))
    
    def _calculate_completion_rate(self, qias):
        """Calculate percentage of closed QIAs"""
        total = qias.count()
        if total == 0:
            return 0
        closed = qias.filter(status='CLOSED').count()
        return (closed / total) * 100


def generate_evidence_pack(start_date=None, end_date=None, filename='QIA_Evidence_Pack.pdf'):
    """
    Convenience function to generate evidence pack
    
    Args:
        start_date: Filter QIAs from this date
        end_date: Filter QIAs to this date
        filename: Output PDF filename
    
    Returns:
        Path to generated PDF file
    """
    generator = QIAEvidencePackGenerator(filename=filename)
    return generator.generate(start_date=start_date, end_date=end_date)


if __name__ == '__main__':
    # Example: Generate evidence pack for last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    today = datetime.now()
    
    print("Generating QIA Evidence Pack...")
    pdf_path = generate_evidence_pack(
        start_date=six_months_ago,
        end_date=today,
        filename='QIA_Evidence_Pack_6_Months.pdf'
    )
    print(f"✓ Evidence pack generated: {pdf_path}")
