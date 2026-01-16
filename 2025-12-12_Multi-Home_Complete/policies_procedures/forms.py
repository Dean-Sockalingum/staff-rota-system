"""
TQM Module 5: Policies & Procedures Forms
==========================================

Django forms for all policy management operations.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Policy, PolicyVersion, PolicyAcknowledgement, PolicyReview,
    Procedure, ProcedureStep, PolicyComplianceCheck, AuditTrail
)


class PolicyForm(forms.ModelForm):
    """Form for creating and editing policies"""
    
    class Meta:
        model = Policy
        fields = [
            'title', 'policy_number', 'category', 'effective_date',
            'next_review_date', 'review_frequency_months', 'status',
            'version', 'summary', 'keywords', 'regulatory_framework',
            'department', 'file_path', 'is_mandatory'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Policy title'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'POL-001'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'review_frequency_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '60'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'version': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief summary of policy'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'safeguarding, GDPR, infection control'}),
            'regulatory_framework': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'CQC regulation 10, Care Inspectorate standard 4.1'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nursing, Management, HR'}),
            'file_path': forms.FileInput(attrs={'class': 'form-control'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'policy_number': 'Unique identifier (e.g., POL-001)',
            'review_frequency_months': 'How often policy should be reviewed (1-60 months)',
            'keywords': 'Comma-separated keywords for search',
            'is_mandatory': 'Requires staff acknowledgement',
        }


class PolicyVersionForm(forms.ModelForm):
    """Form for creating new policy versions"""
    
    class Meta:
        model = PolicyVersion
        fields = ['version_number', 'change_summary', 'file_path', 'is_current', 'approval_date', 'approved_by']
        widgets = {
            'version_number': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'change_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Summary of changes'}),
            'file_path': forms.FileInput(attrs={'class': 'form-control'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'approval_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'approved_by': forms.Select(attrs={'class': 'form-select'}),
        }


class PolicyAcknowledgementForm(forms.ModelForm):
    """Form for staff to acknowledge policies"""
    
    agree = forms.BooleanField(
        required=True,
        label="I confirm I have read and understood this policy",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = PolicyAcknowledgement
        fields = ['signature', 'acknowledgement_method', 'comments']
        widgets = {
            'signature': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type your full name'}),
            'acknowledgement_method': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any questions or comments (optional)'}),
        }
        help_texts = {
            'signature': 'Type your full name as digital signature',
        }
    
    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature or len(signature) < 3:
            raise ValidationError('Please enter your full name')
        return signature


class PolicyReviewForm(forms.ModelForm):
    """Form for conducting policy reviews"""
    
    class Meta:
        model = PolicyReview
        fields = ['review_date', 'review_outcome', 'recommendations', 'next_review_date']
        widgets = {
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'review_outcome': forms.Select(attrs={'class': 'form-select'}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Reviewer recommendations and findings'}),
            'next_review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ProcedureForm(forms.ModelForm):
    """Form for creating and editing procedures"""
    
    class Meta:
        model = Procedure
        fields = ['title', 'procedure_number', 'policy', 'steps', 'equipment_required', 'safety_notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Procedure title'}),
            'procedure_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PROC-001'}),
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': '1. First step\n2. Second step\n3. Third step'}),
            'equipment_required': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List required equipment'}),
            'safety_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Safety precautions and warnings'}),
        }


class PolicyComplianceCheckForm(forms.ModelForm):
    """Form for conducting compliance checks"""
    
    class Meta:
        model = PolicyComplianceCheck
        fields = ['policy', 'check_date', 'compliance_status', 'findings', 'actions_required', 'due_date', 'completed']
        widgets = {
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'check_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'compliance_status': forms.Select(attrs={'class': 'form-select'}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed compliance findings'}),
            'actions_required': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Actions needed to achieve compliance'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
