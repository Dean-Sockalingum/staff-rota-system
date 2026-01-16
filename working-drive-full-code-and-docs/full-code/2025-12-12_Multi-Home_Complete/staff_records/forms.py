from django import forms

from .models import SicknessRecord, ContactLogEntry, StaffProfile
from scheduling.models import Unit


class SicknessRecordForm(forms.ModelForm):
    class Meta:
        model = SicknessRecord
        fields = [
            "first_working_day",
            "estimated_return_to_work",
            "actual_last_working_day",
            "reason",
            "notes",
            "trigger_outcome",
        ]
        widgets = {
            "first_working_day": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "estimated_return_to_work": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "actual_last_working_day": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "reason": forms.TextInput(attrs={"class": "form-control"}),
            "trigger_outcome": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        first_day = cleaned_data.get("first_working_day")
        estimated = cleaned_data.get("estimated_return_to_work")
        actual = cleaned_data.get("actual_last_working_day")

        if actual and first_day and actual < first_day:
            self.add_error("actual_last_working_day", "Actual last working day cannot be before the first working day.")

        if estimated and first_day and estimated < first_day:
            self.add_error("estimated_return_to_work", "Estimated return date cannot be before the first working day.")

        return cleaned_data


class ContactLogEntryForm(forms.ModelForm):
    class Meta:
        model = ContactLogEntry
        fields = [
            "contact_method",
            "contact_datetime",
            "summary",
            "follow_up_required",
            "follow_up_date",
        ]
        widgets = {
            "contact_method": forms.Select(attrs={"class": "form-control"}),
            "contact_datetime": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "summary": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "Brief summary of the contact..."}),
            "follow_up_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "follow_up_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


class StaffProfileForm(forms.ModelForm):
    """Form for editing staff profile information"""
    
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="-- Select Unit --"
    )
    
    class Meta:
        model = StaffProfile
        fields = [
            "start_date",
            "employment_status",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "employment_status": forms.Select(attrs={"class": "form-control"}),
            "emergency_contact_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Emergency contact name"}),
            "emergency_contact_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Emergency contact phone"}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set initial unit value from the user model
        if user:
            self.fields['unit'].initial = user.unit
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update the unit on the user model
        if 'unit' in self.cleaned_data:
            profile.user.unit = self.cleaned_data['unit']
            if commit:
                profile.user.save()
        
        if commit:
            profile.save()
        
        return profile
