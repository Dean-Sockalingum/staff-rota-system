"""
Forms for Incident & Safety Management (TQM Module 2)

Provides forms for:
- Root Cause Analysis (5 Whys + Fishbone)
- Corrective & Preventive Actions (CAPA)
- Duty of Candour Records
- Incident Trend Analysis
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    RootCauseAnalysis,
    CorrectivePreventiveAction,
    DutyOfCandourRecord,
    IncidentTrendAnalysis
)


class RootCauseAnalysisForm(forms.ModelForm):
    """Form for creating and editing Root Cause Analysis records."""
    
    class Meta:
        model = RootCauseAnalysis
        fields = [
            'incident',
            'analysis_method',
            'problem_statement',
            'why_1', 'why_2', 'why_3', 'why_4', 'why_5',
            'fishbone_people', 'fishbone_process', 'fishbone_equipment',
            'fishbone_materials', 'fishbone_environment', 'fishbone_management',
            'root_cause_identified',
            'contributing_factors',
            'evidence_collected',
            'analysis_completed_date',
            'reviewed_by',
            'status',
            'notes'
        ]
        widgets = {
            'problem_statement': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Clear statement of the problem or incident'
            }),
            'why_1': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Why did this happen?'
            }),
            'why_2': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Why did that occur?'
            }),
            'why_3': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Why was that the case?'
            }),
            'why_4': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Why did that happen?'
            }),
            'why_5': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Root cause (why did that occur?)'
            }),
            'fishbone_people': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Staff training, supervision, competence issues'
            }),
            'fishbone_process': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Procedures, workflows, communication breakdowns'
            }),
            'fishbone_equipment': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Equipment failures, maintenance issues'
            }),
            'fishbone_materials': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Supplies, medications, documentation'
            }),
            'fishbone_environment': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Physical environment, lighting, temperature'
            }),
            'fishbone_management': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Policies, resources, organizational culture'
            }),
            'root_cause_identified': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Primary root cause(s) identified from analysis'
            }),
            'contributing_factors': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Additional factors that contributed to the incident'
            }),
            'evidence_collected': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Evidence supporting the analysis (interviews, documents, etc.)'
            }),
            'analysis_completed_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reviewed_by': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Additional notes or observations'
            }),
        }


class CorrectivePreventiveActionForm(forms.ModelForm):
    """Form for CAPA (Corrective and Preventive Action) records."""
    
    class Meta:
        model = CorrectivePreventiveAction
        fields = [
            'rca',
            'action_type',
            'action_description',
            'responsible_person',
            'target_completion_date',
            'priority',
            'resources_required',
            'implementation_plan',
            'status',
            'actual_completion_date',
            'effectiveness_review_date',
            'effectiveness_rating',
            'effectiveness_notes',
            'barriers_encountered',
            'lessons_learned'
        ]
        widgets = {
            'rca': forms.Select(attrs={'class': 'form-select'}),
            'action_type': forms.Select(attrs={'class': 'form-select'}),
            'action_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Detailed description of the action to be taken'
            }),
            'responsible_person': forms.Select(attrs={'class': 'form-select'}),
            'target_completion_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'resources_required': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'People, budget, equipment, training needed'
            }),
            'implementation_plan': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Step-by-step plan to implement this action'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'actual_completion_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'effectiveness_review_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'effectiveness_rating': forms.Select(attrs={'class': 'form-select'}),
            'effectiveness_notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'How effective was this action in preventing recurrence?'
            }),
            'barriers_encountered': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Challenges or obstacles during implementation'
            }),
            'lessons_learned': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Key learnings from implementing this action'
            }),
        }


class DutyOfCandourForm(forms.ModelForm):
    """Form for Duty of Candour compliance records."""
    
    class Meta:
        model = DutyOfCandourRecord
        fields = [
            'incident',
            'harm_level',
            'family_notified_date',
            'family_notified_by',
            'notification_method',
            'family_reaction',
            'apology_provided',
            'explanation_provided',
            'support_offered',
            'follow_up_meeting_date',
            'follow_up_notes',
            'care_inspectorate_notified',
            'notification_date',
            'compliance_status',
            'non_compliance_reason',
            'learning_shared'
        ]
        widgets = {
            'incident': forms.Select(attrs={'class': 'form-select'}),
            'harm_level': forms.Select(attrs={'class': 'form-select'}),
            'family_notified_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'family_notified_by': forms.Select(attrs={'class': 'form-select'}),
            'notification_method': forms.Select(attrs={'class': 'form-select'}),
            'family_reaction': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'How did the family respond to the notification?'
            }),
            'apology_provided': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'explanation_provided': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'What explanation was provided about what happened?'
            }),
            'support_offered': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'What support was offered to the resident/family?'
            }),
            'follow_up_meeting_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'follow_up_notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Notes from follow-up meeting'
            }),
            'care_inspectorate_notified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notification_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'compliance_status': forms.Select(attrs={'class': 'form-select'}),
            'non_compliance_reason': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Reason if not compliant'
            }),
            'learning_shared': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'How was learning shared with team/organization?'
            }),
        }


class IncidentTrendAnalysisForm(forms.ModelForm):
    """Form for incident trend analysis records."""
    
    class Meta:
        model = IncidentTrendAnalysis
        fields = [
            'care_home',
            'analysis_period_start',
            'analysis_period_end',
            'incident_categories_analyzed',
            'total_incidents',
            'trends_identified',
            'high_risk_areas',
            'recommendations',
            'action_plan',
            'analyzed_by',
            'reviewed_by',
            'status'
        ]
        widgets = {
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'analysis_period_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'analysis_period_end': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'incident_categories_analyzed': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'List of incident categories included in this analysis'
            }),
            'total_incidents': forms.NumberInput(attrs={'class': 'form-control'}),
            'trends_identified': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Key trends and patterns identified'
            }),
            'high_risk_areas': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Areas identified as high risk'
            }),
            'recommendations': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Recommendations based on trends'
            }),
            'action_plan': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Action plan to address identified trends'
            }),
            'analyzed_by': forms.Select(attrs={'class': 'form-select'}),
            'reviewed_by': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
