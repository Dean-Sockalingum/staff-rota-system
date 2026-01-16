"""
TQM Module 3: Experience & Feedback Forms

Django forms for satisfaction surveys across all respondent types.
"""

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import SatisfactionSurvey, SurveyType


class SatisfactionSurveyForm(forms.ModelForm):
    """
    Comprehensive satisfaction survey form for all survey types.
    Dynamically adjusts fields based on survey type.
    """
    
    class Meta:
        model = SatisfactionSurvey
        fields = [
            'survey_type',
            'care_home',
            'resident',
            'respondent_name',
            'relationship_to_resident',
            'is_anonymous',
            'overall_satisfaction',
            'quality_of_care',
            'staff_attitude',
            'communication',
            'environment_cleanliness',
            'meals_nutrition',
            'activities_engagement',
            'dignity_respect',
            'safety_security',
            'likelihood_recommend',
            'what_works_well',
            'areas_for_improvement',
            'additional_comments',
        ]
        
        widgets = {
            'survey_type': forms.Select(attrs={'class': 'form-select'}),
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'resident': forms.Select(attrs={'class': 'form-select'}),
            'respondent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name (optional)'}),
            'relationship_to_resident': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Daughter, Son, Self'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            # Rating scales (1-5)
            'overall_satisfaction': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'quality_of_care': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'staff_attitude': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'communication': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'environment_cleanliness': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'meals_nutrition': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'activities_engagement': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'dignity_respect': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'safety_security': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            
            # NPS scale (0-10)
            'likelihood_recommend': forms.RadioSelect(choices=[(i, i) for i in range(0, 11)]),
            
            # Text areas
            'what_works_well': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us what you appreciate...'}),
            'areas_for_improvement': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'How can we improve?'}),
            'additional_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Any other feedback...'}),
        }
        
        labels = {
            'overall_satisfaction': '1. Overall, how satisfied are you?',
            'quality_of_care': '2. Quality of care provided',
            'staff_attitude': '3. Staff friendliness and professionalism',
            'communication': '4. Communication with staff',
            'environment_cleanliness': '5. Cleanliness of the environment',
            'meals_nutrition': '6. Quality and variety of meals',
            'activities_engagement': '7. Activities and social opportunities',
            'dignity_respect': '8. Dignity and respect shown',
            'safety_security': '9. Feeling of safety and security',
            'likelihood_recommend': '10. How likely are you to recommend us to others?',
            'what_works_well': 'What works well?',
            'areas_for_improvement': 'What could we improve?',
            'additional_comments': 'Additional comments',
        }
    
    def __init__(self, *args, **kwargs):
        survey_type = kwargs.pop('survey_type', None)
        super().__init__(*args, **kwargs)
        
        # Make some fields optional for anonymous surveys
        self.fields['respondent_name'].required = False
        self.fields['relationship_to_resident'].required = False
        self.fields['resident'].required = False
        
        # Adjust fields based on survey type
        if survey_type:
            self.fields['survey_type'].initial = survey_type
            self.fields['survey_type'].widget = forms.HiddenInput()


class PublicSurveyForm(forms.ModelForm):
    """
    Simplified public-facing survey form (no login required).
    Used for public survey links sent to families/staff/professionals.
    """
    
    class Meta:
        model = SatisfactionSurvey
        fields = [
            'respondent_name',
            'relationship_to_resident',
            'is_anonymous',
            'overall_satisfaction',
            'quality_of_care',
            'staff_attitude',
            'communication',
            'environment_cleanliness',
            'meals_nutrition',
            'activities_engagement',
            'dignity_respect',
            'safety_security',
            'likelihood_recommend',
            'what_works_well',
            'areas_for_improvement',
            'additional_comments',
        ]
        
        widgets = {
            'respondent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional - leave blank for anonymous)'
            }),
            'relationship_to_resident': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Family Member, Staff, Healthcare Professional'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            'overall_satisfaction': forms.RadioSelect(),
            'quality_of_care': forms.RadioSelect(),
            'staff_attitude': forms.RadioSelect(),
            'communication': forms.RadioSelect(),
            'environment_cleanliness': forms.RadioSelect(),
            'meals_nutrition': forms.RadioSelect(),
            'activities_engagement': forms.RadioSelect(),
            'dignity_respect': forms.RadioSelect(),
            'safety_security': forms.RadioSelect(),
            'likelihood_recommend': forms.RadioSelect(),
            
            'what_works_well': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please tell us what works well...'
            }),
            'areas_for_improvement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What could we do better?'
            }),
            'additional_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Any other feedback you would like to share...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # All fields optional for public forms
        for field_name, field in self.fields.items():
            field.required = False
            
        # Overall satisfaction is the only required field
        self.fields['overall_satisfaction'].required = True
