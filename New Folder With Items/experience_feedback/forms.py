"""
TQM Module 3: Experience & Feedback Forms

Django forms for satisfaction surveys across all respondent types.
"""

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    SatisfactionSurvey, 
    SurveyType, 
    YouSaidWeDidAction,
    FamilyMember,
    FamilyMessage,
)
from . import models


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


class YouSaidWeDidActionForm(forms.ModelForm):
    """
    Form for creating and managing 'You Said, We Did' actions.
    Used by staff to document feedback and responses.
    """
    
    class Meta:
        model = YouSaidWeDidAction
        fields = [
            'source_type',
            'related_survey',
            'related_complaint',
            'related_theme',
            'you_said',
            'feedback_date',
            'who_said_it',
            'category',
            'sentiment',
            'we_did',
            'action_taken_date',
            'responsible_person',
            'status',
            'impact_assessment',
            'communicated_to_residents',
            'communicated_date',
            'communication_method',
            'display_on_board',
            'display_until',
        ]
        
        widgets = {
            'source_type': forms.Select(attrs={'class': 'form-select'}),
            'related_survey': forms.Select(attrs={'class': 'form-select'}),
            'related_complaint': forms.Select(attrs={'class': 'form-select'}),
            'related_theme': forms.Select(attrs={'class': 'form-select'}),
            'you_said': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What did residents/families tell us? (e.g., "The activities are repetitive and boring")'
            }),
            'feedback_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'who_said_it': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name (optional for anonymity)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'sentiment': forms.Select(attrs={'class': 'form-select'}),
            'we_did': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What action did we take? (e.g., "Introduced new weekly music sessions and outdoor activities")'
            }),
            'action_taken_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'responsible_person': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'impact_assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What impact has this action had?'
            }),
            'communicated_to_residents': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'communicated_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'communication_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Notice board, newsletter, residents meeting'
            }),
            'display_on_board': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set fields that are required
        self.fields['you_said'].required = True
        self.fields['category'].required = True
        self.fields['sentiment'].required = True
        self.fields['source_type'].required = True
        
        # Help text
        self.fields['you_said'].help_text = "Document exactly what was said in the feedback"
        self.fields['we_did'].help_text = "Describe the specific actions taken in response"
        self.fields['display_on_board'].help_text = "Display this on the 'You Said, We Did' notice board for residents/families to see"


# ============================================================================
# COMPLAINT FORMS
# ============================================================================

from .models import (
    Complaint,
    ComplaintInvestigationStage,
    ComplaintStakeholder,
    ComplaintSeverity,
    ComplaintStatus,
)
from datetime import timedelta


class ComplaintForm(forms.ModelForm):
    """
    Form for creating and editing complaints.
    Calculates target dates based on severity.
    """
    
    class Meta:
        model = Complaint
        fields = [
            'care_home',
            'complaint_reference',
            'date_received',
            'complaint_category',
            'severity',
            'complainant_name',
            'complainant_relationship',
            'complainant_contact',
            'resident',
            'complaint_description',
            'desired_outcome',
        ]
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'complaint_description': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'desired_outcome': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'complaint_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'complaint_category': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'complainant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'complainant_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'complainant_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'resident': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make certain fields required
        self.fields['care_home'].required = True
        self.fields['date_received'].required = True
        self.fields['severity'].required = True
        self.fields['complaint_category'].required = True
        self.fields['complaint_description'].required = True
        
        # Set initial values for new complaints
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['date_received'].initial = timezone.now().date()
    
    def save(self, commit=True):
        from django.utils import timezone
        complaint = super().save(commit=False)
        
        # Auto-calculate target resolution date based on severity
        if not complaint.target_resolution_date and complaint.date_received:
            if complaint.severity == ComplaintSeverity.CRITICAL:
                complaint.target_resolution_date = complaint.date_received + timedelta(days=7)
            elif complaint.severity == ComplaintSeverity.SERIOUS:
                complaint.target_resolution_date = complaint.date_received + timedelta(days=14)
            else:
                complaint.target_resolution_date = complaint.date_received + timedelta(days=20)
        
        # Set initial status if new complaint
        if not complaint.pk and not complaint.status:
            complaint.status = ComplaintStatus.RECEIVED
        
        if commit:
            complaint.save()
        
        return complaint


class ComplaintInvestigationStageForm(forms.ModelForm):
    """Form for creating investigation stages."""
    
    class Meta:
        model = ComplaintInvestigationStage
        fields = [
            'stage_name',
            'assigned_to',
            'status',
            'start_date',
            'target_completion',
            'actual_completion',
            'findings',
            'evidence_collected',
            'actions_required',
            'sequence_order',
        ]
        widgets = {
            'stage_name': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'target_completion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_completion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'findings': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'evidence_collected': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'actions_required': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'sequence_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ComplaintStakeholderForm(forms.ModelForm):
    """Form for adding stakeholders to complaints."""
    
    class Meta:
        model = ComplaintStakeholder
        fields = [
            'stakeholder_type',
            'name',
            'role_title',
            'contact_details',
            'involvement_description',
            'date_contacted',
            'statement_received',
            'statement_date',
            'statement_notes',
            'requires_update',
            'update_frequency',
            'last_updated',
        ]
        widgets = {
            'stakeholder_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'role_title': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_details': forms.TextInput(attrs={'class': 'form-control'}),
            'date_contacted': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'statement_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'last_updated': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'involvement_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'statement_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'statement_received': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_update': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'update_frequency': forms.Select(attrs={'class': 'form-select'}),
        }


class ComplaintUpdateForm(forms.ModelForm):
    """
    Simplified form for updating complaint status and investigation progress.
    Used by investigators to record updates quickly.
    """
    
    update_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        help_text="Add notes about this status update"
    )
    
    class Meta:
        model = Complaint
        fields = [
            'status',
            'investigation_notes',
            'root_cause',
            'lessons_learned',
            'resolution_details',
            'date_acknowledged',
            'actual_resolution_date',
            'complainant_satisfied',
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'date_acknowledged': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_resolution_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'investigation_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'root_cause': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'lessons_learned': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'resolution_details': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'complainant_satisfied': forms.Select(
                choices=[(None, '---'), (True, 'Yes'), (False, 'No')],
                attrs={'class': 'form-select'}
            ),
        }


class ComplaintFilterForm(forms.Form):
    """Form for filtering complaints in the list view."""
    
    care_home = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + list(ComplaintStatus.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    severity = forms.ChoiceField(
        required=False,
        choices=[('', 'All Severities')] + list(ComplaintSeverity.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    overdue = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        from scheduling.models import CareHome
        super().__init__(*args, **kwargs)
        
        # Populate care home choices dynamically
        care_homes = CareHome.objects.all().order_by('name')
        choices = [('', 'All Care Homes')] + [(ch.id, ch.name) for ch in care_homes]
        self.fields['care_home'].choices = choices


class SurveyDistributionScheduleForm(forms.ModelForm):
    """Form for creating and editing survey distribution schedules."""
    
    class Meta:
        from .models import SurveyDistributionSchedule
        
        model = SurveyDistributionSchedule
        fields = [
            'schedule_name',  # Fixed: was 'name'
            'care_home',
            'survey_type',
            'distribution_frequency',  # Fixed: was 'trigger_type' and 'schedule_frequency'
            'days_after_event',  # Fixed: was 'days_after_admission'
            'day_of_month',  # Fixed: was 'schedule_day_of_month'
            'day_of_week',  # Fixed: was 'schedule_day_of_week'
            'is_active',
            'send_via_email',  # Fixed: was 'send_email'
            'send_via_sms',  # Fixed: was 'send_sms'
            'print_qr_code',
            'send_to_residents',
            'send_to_families',
            'email_subject',
            'email_intro',
            'send_reminder',  # Fixed: was 'enable_reminders'
            'reminder_days',
        ]
        
        widgets = {
            'schedule_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Post-Admission 2-Week Survey'
            }),
            'care_home': forms.Select(attrs={'class': 'form-select'}),
            'survey_type': forms.Select(attrs={'class': 'form-select'}),
            'distribution_frequency': forms.Select(attrs={'class': 'form-select'}),
            'days_after_event': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Days after admission/discharge'
            }),
            'day_of_month': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 31,
                'placeholder': 'Day of month (1-31)'
            }),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_via_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_via_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'print_qr_code': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_to_residents': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_to_families': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email subject line'
            }),
            'email_intro': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Introduction text for email'
            }),
            'send_reminder': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reminder_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Days before reminder'
            }),
        }
        
        help_texts = {
            'distribution_frequency': 'When should this survey be distributed?',
            'days_after_event': 'Only applies to admission/discharge trigger types',
            'day_of_week': 'Only applies to weekly surveys',
            'day_of_month': 'Only applies to monthly/quarterly/annual surveys',
            'send_via_email': 'Send survey via email',
            'send_via_sms': 'Send survey via SMS',
            'print_qr_code': 'Generate QR codes for printed materials',
            'send_to_residents': 'Send to residents directly',
            'send_to_families': 'Send to family contacts',
            'send_reminder': 'Automatically send reminders for non-responses',
            'reminder_days': 'Days to wait before sending reminder',
        }
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        distribution_frequency = cleaned_data.get('distribution_frequency')
        days_after_event = cleaned_data.get('days_after_event')
        send_via_email = cleaned_data.get('send_via_email')
        send_via_sms = cleaned_data.get('send_via_sms')
        print_qr_code = cleaned_data.get('print_qr_code')
        send_to_residents = cleaned_data.get('send_to_residents')
        send_to_families = cleaned_data.get('send_to_families')
        
        # Validate event-based surveys have days_after_event
        if distribution_frequency in ['ADMISSION', 'DISCHARGE'] and not days_after_event:
            self.add_error('days_after_event', 'Required for admission/discharge-triggered surveys')
        
        # Ensure at least one distribution channel is selected
        if not (send_via_email or send_via_sms or print_qr_code):
            raise forms.ValidationError('Select at least one distribution method (Email, SMS, or QR Code)')
        
        # Ensure at least one recipient type is selected
        if not (send_to_residents or send_to_families):
            raise forms.ValidationError('Select at least one recipient type (Residents or Families)')
        
        return cleaned_data


# ============================================================================
# FAMILY PORTAL FORMS
# ============================================================================

class FamilyMemberForm(forms.ModelForm):
    """Form for creating/editing family member accounts."""
    
    # User account fields
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text='Username for portal login (e.g., email address or unique ID)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'john.smith or john.smith@email.com'
        })
    )
    password = forms.CharField(
        max_length=128,
        required=False,
        help_text='Leave blank to keep existing password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Secure password'
        })
    )
    password_confirm = forms.CharField(
        max_length=128,
        required=False,
        help_text='Confirm password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = models.FamilyMember
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'resident',
            'relationship',
            'is_primary_contact',
            'is_power_of_attorney',
            'portal_access_granted',
            'access_level',
            'receive_email_notifications',
            'receive_sms_notifications',
            'receive_survey_requests',
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XXX XXXXXX'}),
            'resident': forms.Select(attrs={'class': 'form-select'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Daughter, Son, Spouse'}),
            'is_primary_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_power_of_attorney': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'portal_access_granted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'access_level': forms.Select(attrs={'class': 'form-select'}),
            'receive_email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_survey_requests': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        help_texts = {
            'email': 'Used for portal login and notifications',
            'resident': 'Resident this family member is associated with',
            'is_primary_contact': 'Primary contact receives all important notifications',
            'is_power_of_attorney': 'Has legal authority to make decisions',
            'access_level': 'Level of information access in the portal',
        }
    
    def clean(self):
        """Validate passwords match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password != password_confirm:
            raise forms.ValidationError('Passwords do not match')
        
        return cleaned_data


class FamilyMessageForm(forms.ModelForm):
    """Form for family members to send messages to care staff."""
    
    class Meta:
        model = models.FamilyMessage
        fields = ['subject', 'message', 'category', 'priority']
        
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief subject line',
                'maxlength': 200
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Type your message here...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
        
        help_texts = {
            'subject': 'Brief description of your query',
            'message': 'Please provide details of your question or feedback',
            'category': 'Select the most appropriate category',
            'priority': 'Mark as urgent only for time-sensitive matters',
        }


class FamilyMessageResponseForm(forms.ModelForm):
    """Form for staff to respond to family messages."""
    
    class Meta:
        model = models.FamilyMessage
        fields = ['response_text']
        
        widgets = {
            'response_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Type your response here...',
                'required': True
            }),
        }
        
        help_texts = {
            'response_text': 'Provide a detailed response to the family member\'s message',
        }


class FamilyPortalFilterForm(forms.Form):
    """Filter form for family portal dashboards."""
    
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search messages, surveys...'
        })
    )
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + list(models.FamilyMessage._meta.get_field('category').choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Messages'),
            ('unanswered', 'Awaiting Response'),
            ('answered', 'Responded'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
