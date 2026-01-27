"""
TQM Module 4: Training & Competency Forms

Django forms for managing competency frameworks, assessments,
learning pathways, and staff development plans.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    CompetencyFramework,
    RoleCompetencyRequirement,
    CompetencyAssessment,
    TrainingMatrix,
    LearningPathway,
    PathwayCompetency,
    PathwayTraining,
    StaffLearningPlan
)
from scheduling.models import Role, TrainingCourse


class CompetencyFrameworkForm(forms.ModelForm):
    """
    Form for creating and editing competency frameworks
    """
    
    class Meta:
        model = CompetencyFramework
        fields = [
            'code',
            'title',
            'competency_type',
            'description',
            'assessment_criteria',
            'evidence_required',
            'review_frequency_months',
            'is_active',
        ]
        
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CLIN-001'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Person-Centered Care Planning'
            }),
            'competency_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Clear definition of what this competency means...'
            }),
            'assessment_criteria': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'How this competency will be assessed (observable behaviors)'
            }),
            'evidence_required': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What evidence demonstrates competency?'
            }),
            'review_frequency_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '60',
                'placeholder': '12'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        help_texts = {
            'assessment_criteria': 'How this competency will be assessed (observable behaviors)',
            'evidence_required': 'What evidence demonstrates competency (e.g., witness statements, portfolios)',
            'review_frequency_months': 'How often should this competency be reassessed?',
        }


class RoleCompetencyRequirementForm(forms.ModelForm):
    """
    Form for mapping competencies to roles
    """
    
    class Meta:
        model = RoleCompetencyRequirement
        fields = [
            'role',
            'competency',
            'required_level',
            'is_mandatory',
            'grace_period_days',
        ]
        
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'competency': forms.Select(attrs={'class': 'form-select'}),
            'required_level': forms.Select(attrs={'class': 'form-select'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'grace_period_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '90'
            }),
        }
        
        help_texts = {
            'grace_period_days': 'Days allowed to achieve competency after starting role',
        }


class CompetencyAssessmentForm(forms.ModelForm):
    """
    Form for conducting competency assessments
    """
    
    class Meta:
        model = CompetencyAssessment
        fields = [
            'staff_member',
            'competency',
            'achieved_level',
            'assessment_method',
            'outcome',
            'assessor_comments',
            'evidence_description',
            'staff_reflection',
            'development_needs_identified',
            'action_plan',
            'next_review_date',
        ]
        
        widgets = {
            'staff_member': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'competency': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'achieved_level': forms.Select(attrs={'class': 'form-select'}),
            'assessment_method': forms.Select(attrs={'class': 'form-select'}),
            'outcome': forms.Select(attrs={'class': 'form-select'}),
            'assessor_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide detailed feedback on the assessment...'
            }),
            'evidence_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What evidence did you observe? (e.g., interactions, documentation, skills demonstrated)'
            }),
            'staff_reflection': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Staff member\'s own reflection on their performance'
            }),
            'development_needs_identified': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What areas need further development?'
            }),
            'action_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Specific actions to address development needs'
            }),
            'next_review_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
        help_texts = {
            'next_review_date': 'When should this competency be reassessed?',
        }


class TrainingMatrixForm(forms.ModelForm):
    """
    Form for mapping training courses to roles
    """
    
    class Meta:
        model = TrainingMatrix
        fields = [
            'role',
            'training_course',
            'requirement_type',
            'must_complete_within_days',
            'must_complete_before_solo_work',
            'priority_order',
            'care_home',
            'rationale',
        ]
        
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'training_course': forms.Select(attrs={'class': 'form-select'}),
            'requirement_type': forms.Select(attrs={'class': 'form-select'}),
            'must_complete_within_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '90'
            }),
            'must_complete_before_solo_work': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'priority_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1'
            }),
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'rationale': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Why this training is required for this role'
            }),
        }
        
        help_texts = {
            'must_complete_within_days': 'For ESSENTIAL training: days allowed after starting role',
            'priority_order': 'Order in which training should be completed (1=highest priority)',
        }


class LearningPathwayForm(forms.ModelForm):
    """
    Form for creating learning pathways (career progression routes)
    """
    
    class Meta:
        model = LearningPathway
        fields = [
            'title',
            'from_role',
            'to_role',
            'description',
            'estimated_duration_months',
            'total_learning_hours',
            'status',
            'is_active',
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., SCW to SSCW Progression Pathway'
            }),
            'from_role': forms.Select(attrs={'class': 'form-select'}),
            'to_role': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe this learning pathway and what staff will achieve...'
            }),
            'estimated_duration_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '24',
                'placeholder': 'Estimated months to complete'
            }),
            'total_learning_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total hours'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        help_texts = {
            'estimated_duration_months': 'Expected time to complete pathway',
        }


class PathwayCompetencyForm(forms.ModelForm):
    """
    Form for adding competencies to learning pathways
    """
    
    class Meta:
        model = PathwayCompetency
        fields = [
            'pathway',
            'competency',
            'sequence_order',
            'required_level',
        ]
        
        widgets = {
            'pathway': forms.Select(attrs={'class': 'form-select'}),
            'competency': forms.Select(attrs={'class': 'form-select'}),
            'sequence_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Order in pathway (1, 2, 3...)'
            }),
            'required_level': forms.Select(attrs={'class': 'form-select'}),
        }


class PathwayTrainingForm(forms.ModelForm):
    """
    Form for adding training courses to learning pathways
    """
    
    class Meta:
        model = PathwayTraining
        fields = [
            'pathway',
            'training_course',
            'sequence_order',
            'is_mandatory',
        ]
        
        widgets = {
            'pathway': forms.Select(attrs={'class': 'form-select'}),
            'training_course': forms.Select(attrs={'class': 'form-select'}),
            'sequence_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Order in pathway'
            }),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StaffLearningPlanForm(forms.ModelForm):
    """
    Form for enrolling staff in learning pathways
    """
    
    class Meta:
        model = StaffLearningPlan
        fields = [
            'staff_member',
            'pathway',
            'mentor',
            'line_manager',
            'target_completion_date',
            'status',
            'staff_notes',
            'manager_notes',
        ]
        
        widgets = {
            'staff_member': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'pathway': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'mentor': forms.Select(attrs={
                'class': 'form-select',
                'required': False
            }),
            'line_manager': forms.Select(attrs={
                'class': 'form-select',
                'required': False
            }),
            'target_completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'staff_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Staff member\'s own notes and reflections...'
            }),
            'manager_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Line manager observations and support provided...'
            }),
        }
        
        help_texts = {
            'mentor': 'Designated mentor/coach',
            'target_completion_date': 'When should this pathway be completed?',
        }


class QuickAssessmentForm(forms.ModelForm):
    """
    Simplified form for quick competency assessments
    """
    
    class Meta:
        model = CompetencyAssessment
        fields = [
            'staff_member',
            'competency',
            'outcome',
            'assessor_comments',
        ]
        
        widgets = {
            'staff_member': forms.Select(attrs={'class': 'form-select'}),
            'competency': forms.Select(attrs={'class': 'form-select'}),
            'outcome': forms.RadioSelect(),
            'assessor_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief assessment notes...'
            }),
        }
