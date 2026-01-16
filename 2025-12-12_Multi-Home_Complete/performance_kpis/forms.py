"""
Forms for Performance KPIs (TQM Module 7)

Provides forms for:
- KPI Definitions
- KPI Measurements
- Performance Targets
- Dashboard Configuration
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    KPIDefinition,
    KPIMeasurement,
    ExecutiveDashboard,
    DashboardKPI,
    PerformanceTarget,
    BenchmarkData,
    BalancedScorecardPerspective
)


class KPIDefinitionForm(forms.ModelForm):
    """Form for creating and editing KPI definitions."""
    
    class Meta:
        model = KPIDefinition
        fields = [
            'name',
            'code',
            'description',
            'category',
            'perspective',
            'unit_of_measure',
            'calculation_method',
            'data_source',
            'measurement_frequency',
            'target_type',
            'good_performance_direction',
            'is_active',
            'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'KPI name (e.g., "Falls per 1000 bed days")'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unique code (e.g., "QI-001")'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Detailed description of what this KPI measures'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'perspective': forms.Select(attrs={'class': 'form-select'}),
            'unit_of_measure': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "per 1000 bed days", "percentage", "count"'
            }),
            'calculation_method': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Formula or method to calculate this KPI'
            }),
            'data_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Where is the data collected from?'
            }),
            'measurement_frequency': forms.Select(attrs={'class': 'form-select'}),
            'target_type': forms.Select(attrs={'class': 'form-select'}),
            'good_performance_direction': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Additional notes'
            }),
        }


class KPIMeasurementForm(forms.ModelForm):
    """Form for recording KPI measurements."""
    
    class Meta:
        model = KPIMeasurement
        fields = [
            'kpi',
            'care_home',
            'measurement_date',
            'value',
            'target_value',
            'threshold_minimum',
            'threshold_maximum',
            'data_quality',
            'notes',
            'recorded_by'
        ]
        widgets = {
            'kpi': forms.Select(attrs={'class': 'form-select'}),
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'measurement_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Measured value'
            }),
            'target_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Target for this period'
            }),
            'threshold_minimum': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Minimum acceptable value'
            }),
            'threshold_maximum': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Maximum acceptable value'
            }),
            'data_quality': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Context or notes about this measurement'
            }),
            'recorded_by': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data.get('value')
        threshold_min = cleaned_data.get('threshold_minimum')
        threshold_max = cleaned_data.get('threshold_maximum')
        
        # Validate thresholds
        if threshold_min and threshold_max and threshold_min > threshold_max:
            raise ValidationError('Minimum threshold cannot be greater than maximum threshold.')
        
        return cleaned_data


class PerformanceTargetForm(forms.ModelForm):
    """Form for setting performance targets."""
    
    class Meta:
        model = PerformanceTarget
        fields = [
            'kpi',
            'care_home',
            'target_period_start',
            'target_period_end',
            'target_value',
            'stretch_target',
            'minimum_acceptable',
            'rationale',
            'set_by',
            'approved_by',
            'approval_date',
            'status'
        ]
        widgets = {
            'kpi': forms.Select(attrs={'class': 'form-select'}),
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'target_period_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'target_period_end': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'target_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Target value'
            }),
            'stretch_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Aspirational target'
            }),
            'minimum_acceptable': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Minimum acceptable performance'
            }),
            'rationale': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Why was this target set?'
            }),
            'set_by': forms.Select(attrs={'class': 'form-select'}),
            'approved_by': forms.Select(attrs={'class': 'form-select'}),
            'approval_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ExecutiveDashboardForm(forms.ModelForm):
    """Form for creating custom executive dashboards."""
    
    class Meta:
        model = ExecutiveDashboard
        fields = [
            'name',
            'description',
            'owner',
            'is_public',
            'shared_with',
            'layout_config',
            'refresh_interval'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dashboard name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Brief description of this dashboard'
            }),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shared_with': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'layout_config': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'JSON layout configuration (optional)'
            }),
            'refresh_interval': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-refresh in minutes (optional)'
            }),
        }


class DashboardKPIForm(forms.ModelForm):
    """Form for adding KPIs to dashboards."""
    
    class Meta:
        model = DashboardKPI
        fields = [
            'dashboard',
            'kpi',
            'display_order',
            'chart_type',
            'time_range',
            'show_target',
            'show_trend',
            'color_scheme'
        ]
        widgets = {
            'dashboard': forms.Select(attrs={'class': 'form-select'}),
            'kpi': forms.Select(attrs={'class': 'form-select'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'chart_type': forms.Select(attrs={'class': 'form-select'}),
            'time_range': forms.Select(attrs={'class': 'form-select'}),
            'show_target': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_trend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'color_scheme': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "success", "warning", "danger"'
            }),
        }


class BenchmarkDataForm(forms.ModelForm):
    """Form for entering benchmark comparison data."""
    
    class Meta:
        model = BenchmarkData
        fields = [
            'kpi',
            'benchmark_period',
            'sector_average',
            'top_quartile',
            'bottom_quartile',
            'data_source',
            'notes'
        ]
        widgets = {
            'kpi': forms.Select(attrs={'class': 'form-select'}),
            'benchmark_period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "Q4 2025", "FY 2025"'
            }),
            'sector_average': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Sector average value'
            }),
            'top_quartile': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Top 25% performance'
            }),
            'bottom_quartile': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Bottom 25% performance'
            }),
            'data_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Source of benchmark data'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Additional context'
            }),
        }
