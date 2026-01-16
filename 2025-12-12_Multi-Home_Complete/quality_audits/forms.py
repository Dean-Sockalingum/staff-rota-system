"""
Django forms for PDSA Tracker application.
Simplified forms matching actual model field names.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import PDSAProject, PDSACycle, PDSADataPoint, PDSATeamMember


class PDSAProjectForm(forms.ModelForm):
    """Form for creating/editing PDSA projects."""
    
    class Meta:
        model = PDSAProject
        fields = [
            'title', 'aim_statement', 'problem_description', 'target_population',
            'care_home', 'unit', 'category', 'priority',
            'baseline_value', 'target_value', 'measurement_unit',
            'start_date', 'target_completion_date', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'aim_statement': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'problem_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'target_population': forms.TextInput(attrs={'class': 'form-control'}),
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'baseline_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'measurement_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'target_completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }


class PDSACycleForm(forms.ModelForm):
    """Form for creating/editing PDSA cycles."""
    
    class Meta:
        model = PDSACycle
        fields = [
            'project', 'cycle_number',
            'hypothesis', 'prediction', 'change_idea', 'data_collection_plan',
            'plan_start_date', 'plan_end_date',
            'execution_log', 'observations', 'deviations', 'staff_feedback',
            'do_start_date', 'do_end_date',
            'data_analysis', 'findings', 'comparison_to_prediction', 
            'lessons_learned', 'unexpected_outcomes',
            'act_decision', 'next_steps', 'new_cycle_planned', 'spread_plan'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'cycle_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'hypothesis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'prediction': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'change_idea': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'data_collection_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'plan_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plan_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'execution_log': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deviations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'staff_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'do_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'do_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'comparison_to_prediction': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lessons_learned': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'unexpected_outcomes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'act_decision': forms.Select(attrs={'class': 'form-select'}),
            'next_steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'new_cycle_planned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'spread_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }


class PDSADataPointForm(forms.ModelForm):
    """Form for adding data points."""
    
    class Meta:
        model = PDSADataPoint
        fields = ['cycle', 'measurement_date', 'value', 'notes']
        widgets = {
            'cycle': forms.Select(attrs={'class': 'form-select'}),
            'measurement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }


class PDSATeamMemberForm(forms.ModelForm):
    """Form for adding team members."""
    
    class Meta:
        model = PDSATeamMember
        fields = ['project', 'user', 'role']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'})
        }


# Formset for inline data point entry
from django.forms import inlineformset_factory

DataPointFormSet = inlineformset_factory(
    PDSACycle,
    PDSADataPoint,
    form=PDSADataPointForm,
    fields=['measurement_date', 'value', 'notes'],
    extra=3,
    can_delete=True
)
