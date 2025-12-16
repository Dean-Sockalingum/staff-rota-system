from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView

from scheduling.models import User

from .forms import SicknessRecordForm, ContactLogEntryForm, StaffProfileForm
from .models import StaffProfile, SicknessRecord, ContactLogEntry


def management_required(user):
    """Allows access only to management staff."""

    return bool(user.is_authenticated and getattr(getattr(user, "role", None), "is_management", False))


@method_decorator([login_required, user_passes_test(management_required)], name="dispatch")
class StaffProfileListView(ListView):
    """Display staff profiles with simple search to get the UI started."""

    model = StaffProfile
    paginate_by = 25
    template_name = "staff_records/profile_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        query = StaffProfile.objects.select_related("user", "user__role", "user__unit")
        term = self.request.GET.get("q")
        status = self.request.GET.get("status")
        if term:
            query = query.filter(
                Q(user__first_name__icontains=term)
                | Q(user__last_name__icontains=term)
                | Q(user__sap__icontains=term)
            )
        if status:
            query = query.filter(employment_status=status)
        return query.order_by("user__last_name", "user__first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employment_status_choices"] = StaffProfile.EMPLOYMENT_STATUS_CHOICES
        return context


@method_decorator([login_required, user_passes_test(management_required)], name="dispatch")
class StaffProfileDetailView(View):
    """Initial detail screen stub showing profile while forms are built."""

    template_name = "staff_records/profile_detail.html"

    def get(self, request, sap):
        user = get_object_or_404(User.objects.select_related("role", "unit"), sap=sap)
        profile, _ = StaffProfile.objects.get_or_create(user=user)
        sickness_form = SicknessRecordForm()
        contact_form = ContactLogEntryForm()
        profile_form = StaffProfileForm(instance=profile, user=user)
        return self._render_profile(request, user, profile, sickness_form, contact_form, profile_form)

    def post(self, request, sap):
        user = get_object_or_404(User.objects.select_related("role", "unit"), sap=sap)
        profile, _ = StaffProfile.objects.get_or_create(user=user)
        
        # Determine which form was submitted
        if 'submit_sickness' in request.POST:
            return self._handle_sickness_form(request, user, profile)
        elif 'submit_contact' in request.POST:
            return self._handle_contact_form(request, user, profile)
        elif 'submit_profile' in request.POST:
            return self._handle_profile_form(request, user, profile)
        
        messages.error(request, "Invalid form submission.")
        return redirect(reverse("staff_records:profile_detail", args=[user.sap]))
    
    def _handle_sickness_form(self, request, user, profile):
        form = SicknessRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.profile = profile
            record.reported_by = request.user
            record.status = SicknessRecord.STATUS_CHOICES[0][0]
            record.save()
            messages.success(request, "Sickness record logged and rota updated.")
            return redirect(reverse("staff_records:profile_detail", args=[user.sap]))
        
        messages.error(request, "Please correct the errors below to log the sickness record.")
        contact_form = ContactLogEntryForm()
        profile_form = StaffProfileForm(instance=profile, user=user)
        return self._render_profile(request, user, profile, form, contact_form, profile_form)
    
    def _handle_contact_form(self, request, user, profile):
        form = ContactLogEntryForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.profile = profile
            contact.recorded_by = request.user
            contact.save()
            messages.success(request, "Contact log entry added successfully.")
            return redirect(reverse("staff_records:profile_detail", args=[user.sap]))
        
        messages.error(request, "Please correct the errors below to add the contact entry.")
        sickness_form = SicknessRecordForm()
        profile_form = StaffProfileForm(instance=profile, user=user)
        return self._render_profile(request, user, profile, sickness_form, form, profile_form)
    
    def _handle_profile_form(self, request, user, profile):
        form = StaffProfileForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff profile updated successfully.")
            return redirect(reverse("staff_records:profile_detail", args=[user.sap]))
        
        messages.error(request, "Please correct the errors below to update the profile.")
        sickness_form = SicknessRecordForm()
        contact_form = ContactLogEntryForm()
        return self._render_profile(request, user, profile, sickness_form, contact_form, form)

    def _render_profile(self, request, user, profile, sickness_form, contact_form, profile_form):
        context = {
            "profile": profile,
            "user_obj": user,
            "sickness_records": profile.sickness_records.select_related("reported_by").all(),
            "contact_log": profile.contact_log.select_related("recorded_by").all(),
            "supervision_records": user.supervision_sessions.select_related("supervisor").order_by("-session_date").all(),
            "sickness_form": sickness_form,
            "contact_form": contact_form,
            "profile_form": profile_form,
        }
        return render(request, self.template_name, context)
