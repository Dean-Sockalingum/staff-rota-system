"""
Forms for Risk Management (TQM Module 6)

Provides forms for:
- Risk Register entries
- Risk Mitigations
- Risk Reviews
- Risk Treatment Plans
- Risk Escalations
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    RiskRegister,
    RiskCategory,
    RiskMitigation,
    RiskReview,
    RiskTreatmentPlan,
    RiskEscalation
)


class RiskRegisterForm(forms.ModelForm):
    """Form for creating and editing risks in the risk register."""
    
    class Meta:
        model = RiskRegister
        fields = [
            'care_home',
            'risk_title',
            'risk_description',
            'category',
            'risk_owner',
            'likelihood_score',
            'impact_score',
            'inherent_risk_level',
            'current_controls',
            'likelihood_score_residual',
            'impact_score_residual',
            'residual_risk_level',
            'target_likelihood',
            'target_impact',
            'target_risk_level',
            'target_date',
            'status',
            'review_frequency',
            'next_review_date'
        ]
        widgets = {
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'risk_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title for the risk'
            }),
            'risk_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Detailed description of the risk'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'risk_owner': forms.Select(attrs={'class': 'form-select'}),
            'likelihood_score': forms.Select(attrs={'class': 'form-select'}),
            'impact_score': forms.Select(attrs={'class': 'form-select'}),
            'inherent_risk_level': forms.Select(attrs={'class': 'form-select'}),
            'current_controls': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Existing controls/measures in place to manage this risk'
            }),
            'likelihood_score_residual': forms.Select(attrs={'class': 'form-select'}),
            'impact_score_residual': forms.Select(attrs={'class': 'form-select'}),
            'residual_risk_level': forms.Select(attrs={'class': 'form-select'}),
            'target_likelihood': forms.Select(attrs={'class': 'form-select'}),
            'target_impact': forms.Select(attrs={'class': 'form-select'}),
            'target_risk_level': forms.Select(attrs={'class': 'form-select'}),
            'target_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'review_frequency': forms.Select(attrs={'class': 'form-select'}),
            'next_review_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        likelihood = cleaned_data.get('likelihood_score')
        impact = cleaned_data.get('impact_score')
        
        # Auto-calculate inherent risk level if not set
        if likelihood and impact:
            risk_score = likelihood * impact
            if risk_score >= 15:
                cleaned_data['inherent_risk_level'] = 'CRITICAL'
            elif risk_score >= 10:
                cleaned_data['inherent_risk_level'] = 'HIGH'
            elif risk_score >= 5:
                cleaned_data['inherent_risk_level'] = 'MEDIUM'
            else:
                cleaned_data['inherent_risk_level'] = 'LOW'
        
        return cleaned_data


class RiskMitigationForm(forms.ModelForm):
    """Form for risk mitigation actions."""
    
    class Meta:
        model = RiskMitigation
        fields = [
            'risk',
            'mitigation_action',
            'action_type',
            'responsible_person',
            'target_completion_date',
            'priority',
            'resources_required',
            'implementation_status',
            'actual_completion_date',
            'effectiveness_rating',
            'notes'
        ]
        widgets = {
            'risk': forms.Select(attrs={'class': 'form-select'}),
            'mitigation_action': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Describe the mitigation action in detail'
            }),
            'action_type': forms.Select(attrs={'class': 'form-select'}),
            'responsible_person': forms.Select(attrs={'class': 'form-select'}),
            'target_completion_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'resources_required': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Resources needed (budget, people, equipment)'
            }),
            'implementation_status': forms.Select(attrs={'class': 'form-select'}),
            'actual_completion_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'effectiveness_rating': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Additional notes'
            }),
        }


class RiskReviewForm(forms.ModelForm):
    """Form for periodic risk reviews."""
    
    class Meta:
        model = RiskReview
        fields = [
            'risk',
            'review_date',
            'reviewed_by',
            'risk_status_changed',
            'new_likelihood',
            'new_impact',
            'new_risk_level',
            'controls_effectiveness',
            'additional_controls_needed',
            'recommendations',
            'next_review_date',
            'review_outcome'
        ]
        widgets = {
            'risk': forms.Select(attrs={'class': 'form-select'}),
            'review_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reviewed_by': forms.Select(attrs={'class': 'form-select'}),
            'risk_status_changed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'new_likelihood': forms.Select(attrs={'class': 'form-select'}),
            'new_impact': forms.Select(attrs={'class': 'form-select'}),
            'new_risk_level': forms.Select(attrs={'class': 'form-select'}),
            'controls_effectiveness': forms.Select(attrs={'class': 'form-select'}),
            'additional_controls_needed': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Any additional controls needed?'
            }),
            'recommendations': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Recommendations from this review'
            }),
            'next_review_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'review_outcome': forms.Select(attrs={'class': 'form-select'}),
        }


class RiskTreatmentPlanForm(forms.ModelForm):
    """Form for comprehensive risk treatment plans."""
    
    class Meta:
        model = RiskTreatmentPlan
        fields = [
            'risk',
            'treatment_strategy',
            'treatment_plan_details',
            'budget_allocated',
            'start_date',
            'target_completion_date',
            'plan_owner',
            'approval_status',
            'approved_by',
            'approval_date',
            'implementation_status',
            'actual_completion_date',
            'success_criteria',
            'outcome_evaluation'
        ]
        widgets = {
            'risk': forms.Select(attrs={'class': 'form-select'}),
            'treatment_strategy': forms.Select(attrs={'class': 'form-select'}),
            'treatment_plan_details': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Detailed treatment plan'
            }),
            'budget_allocated': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'target_completion_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'plan_owner': forms.Select(attrs={'class': 'form-select'}),
            'approval_status': forms.Select(attrs={'class': 'form-select'}),
            'approved_by': forms.Select(attrs={'class': 'form-select'}),
            'approval_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'implementation_status': forms.Select(attrs={'class': 'form-select'}),
            'actual_completion_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'success_criteria': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'How will success be measured?'
            }),
            'outcome_evaluation': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Evaluation of the treatment plan outcomes'
            }),
        }


class RiskEscalationForm(forms.ModelForm):
    """Form for escalating high-priority risks."""
    
    class Meta:
        model = RiskEscalation
        fields = [
            'risk',
            'escalation_reason',
            'escalated_to',
            'escalation_date',
            'urgency_level',
            'escalation_notes',
            'escalation_status',
            'response_received_date',
            'response_details',
            'resolved_date',
            'resolution_outcome'
        ]
        widgets = {
            'risk': forms.Select(attrs={'class': 'form-select'}),
            'escalation_reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Why is this risk being escalated?'
            }),
            'escalated_to': forms.Select(attrs={'class': 'form-select'}),
            'escalation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'urgency_level': forms.Select(attrs={'class': 'form-select'}),
            'escalation_notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Additional context'
            }),
            'escalation_status': forms.Select(attrs={'class': 'form-select'}),
            'response_received_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'response_details': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Details of the response received'
            }),
            'resolved_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'resolution_outcome': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'How was this escalation resolved?'
            }),
        }
