"""
Feedback Forms
==============

Forms for collecting user feedback and feature requests.
"""

from django import forms
from .models_feedback import DemoFeedback, FeatureRequest


class DemoFeedbackForm(forms.ModelForm):
    """
    User-friendly feedback form for demo testing
    """
    
    class Meta:
        model = DemoFeedback
        fields = [
            # User Info
            'user_role',
            'care_home',
            'session_duration_minutes',
            
            # Overall
            'overall_rating',
            'ease_of_use',
            'would_recommend',
            
            # Feature Ratings
            'rota_viewing_rating',
            'shift_swapping_rating',
            'leave_request_rating',
            'ai_assistant_rating',
            'dashboard_rating',
            'mobile_experience_rating',
            
            # Qualitative
            'most_useful_features',
            'least_useful_features',
            'missing_features',
            'navigation_issues',
            'confusing_areas',
            'design_feedback',
            
            # Comparison
            'currently_use_system',
            'better_than_current',
            'what_makes_it_better',
            
            # Readiness
            'ready_to_use_daily',
            'concerns_before_rollout',
            'training_needs',
            
            # Open
            'bugs_encountered',
            'additional_comments',
            
            # Follow-up
            'willing_to_followup',
            'contact_email',
        ]
        
        widgets = {
            # Star ratings
            'overall_rating': forms.RadioSelect(choices=[(i, f"{i} {'⭐' * i}") for i in range(1, 6)]),
            'ease_of_use': forms.RadioSelect(choices=[(i, f"{i} {'⭐' * i}") for i in range(1, 6)]),
            
            # Feature ratings
            'rota_viewing_rating': forms.Select(choices=[(None, 'Not Used')] + [(i, f"{i} Stars") for i in range(1, 6)]),
            'shift_swapping_rating': forms.Select(choices=[(None, 'Not Used')] + [(i, f"{i} Stars") for i in range(1, 6)]),
            'leave_request_rating': forms.Select(choices=[(None, 'Not Used')] + [(i, f"{i} Stars") for i in range(1, 6)]),
            'ai_assistant_rating': forms.Select(choices=[(None, 'Not Used')] + [(i, f"{i} Stars") for i in range(1, 6)]),
            'dashboard_rating': forms.Select(choices=[(None, 'Not Used')] + [(i, f"{i} Stars") for i in range(1, 6)]),
            'mobile_experience_rating': forms.Select(choices=[(None, 'Not Used')] + [(i, f"{i} Stars") for i in range(1, 6)]),
            
            # Text areas
            'most_useful_features': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us what you loved...'}),
            'least_useful_features': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What could be improved?'}),
            'missing_features': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What features would make this perfect for your work?'}),
            'navigation_issues': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any areas where you got lost or confused?'}),
            'confusing_areas': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What was unclear?'}),
            'design_feedback': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Feedback on colors, layout, fonts, etc.'}),
            'concerns_before_rollout': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What needs to be addressed first?'}),
            'training_needs': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What training would help you use this effectively?'}),
            'bugs_encountered': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe any errors, crashes, or unexpected behavior'}),
            'additional_comments': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Anything else you\'d like to share?'}),
            'what_makes_it_better': forms.Textarea(attrs={'rows': 3}),
            
            # Other
            'session_duration_minutes': forms.NumberInput(attrs={'min': 1, 'max': 240}),
            'care_home': forms.TextInput(attrs={'placeholder': 'e.g., Orchard Grove'}),
            'currently_use_system': forms.TextInput(attrs={'placeholder': 'e.g., Excel spreadsheets, other software'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com'}),
        }
        
        labels = {
            'overall_rating': '1. Overall, how would you rate your experience with the demo?',
            'ease_of_use': '2. How easy was the system to use?',
            'would_recommend': '3. Would you recommend this system to your colleagues?',
            'user_role': 'Your Role',
            'care_home': 'Your Care Home (optional)',
            'session_duration_minutes': 'How long did you use the demo? (minutes)',
            'most_useful_features': 'Most Useful Features',
            'least_useful_features': 'Least Useful Features',
            'missing_features': 'Missing Features',
            'navigation_issues': 'Navigation Issues',
            'confusing_areas': 'Confusing Areas',
            'design_feedback': 'Design Feedback',
            'currently_use_system': 'What system do you currently use?',
            'better_than_current': 'How does this compare to your current system?',
            'what_makes_it_better': 'What makes it better or worse?',
            'ready_to_use_daily': 'Is this system ready for daily use in your opinion?',
            'concerns_before_rollout': 'What concerns do you have before full rollout?',
            'training_needs': 'What training would you need?',
            'bugs_encountered': 'Bugs or Errors Encountered',
            'additional_comments': 'Additional Comments',
            'willing_to_followup': 'May we contact you with follow-up questions?',
            'contact_email': 'Email for Follow-up (optional)',
        }


class FeatureRequestForm(forms.ModelForm):
    """
    Quick feature request form
    """
    
    class Meta:
        model = FeatureRequest
        fields = ['title', 'description', 'category', 'priority']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Brief description of the feature...',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Detailed description of what you need and why...',
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'title': 'Feature Title',
            'description': 'Detailed Description',
            'category': 'Category',
            'priority': 'How Important Is This?',
        }
