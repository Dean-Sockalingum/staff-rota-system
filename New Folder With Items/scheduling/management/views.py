from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from scheduling.models import User
from scheduling import views as scheduling_views

@login_required
def team_shift_summary(request):
    # Use the real implementation from scheduling.views
    return scheduling_views.team_shift_summary(request)

@login_required
def update_team_assignment(request):
    # Use the real implementation from scheduling.views
    return scheduling_views.update_team_assignment(request)

# Staff Home Units View
@login_required
def staff_home_units(request):
    return scheduling_views.staff_home_units(request)

def team_management(request):
    return scheduling_views.team_management(request)

def staff_management(request):
    return scheduling_views.staff_management(request)

@login_required
def add_staff(request):
    return scheduling_views.add_staff(request)

@login_required
def staff_detail(request, sap):
    return scheduling_views.staff_detail(request, sap)

@login_required
def staff_guidance(request):
    return scheduling_views.staff_guidance(request)

@login_required
def manager_dashboard(request):
    return scheduling_views.manager_dashboard(request)

@login_required
def reports_dashboard(request):
    return scheduling_views.reports_dashboard(request)

@login_required
def rota_view(request):
    return scheduling_views.rota_view(request)

@login_required
def staff_dashboard(request):
    return scheduling_views.staff_dashboard(request)

@login_required
def request_leave(request):
    return scheduling_views.request_annual_leave(request)

@login_required
def request_shift_swap(request):
    return scheduling_views.request_shift_swap(request)

def leave_approval_dashboard(request):
    return scheduling_views.leave_approval_dashboard(request)

def staff_search_rota(request):
    return scheduling_views.staff_search_rota(request)

def edit_shift(request):
    return scheduling_views.edit_shift(request)

def add_shift(request):
    return scheduling_views.add_shift(request)

def login_view(request):
    """Login page with authentication"""
    if request.method == 'POST':
        sap = request.POST.get('sap', '').strip()
        password = request.POST.get('password', '')
        
        # Debug output
        print("="*50)
        print(f"POST data: {dict(request.POST)}")
        print(f"Login attempt - SAP: '{sap}', Password length: {len(password)}")
        
        if not sap or not password:
            print("ERROR: Missing SAP or password")
            messages.error(request, 'Please provide both SAP number and password')
            return render(request, 'scheduling/login.html')
        
        user = authenticate(request, username=sap, password=password)
        print(f"Authentication result: {user}")
        
        if user:
            if not user.is_active:
                print(f"ERROR: User {sap} is inactive")
                messages.error(request, 'Your account is inactive')
                return render(request, 'scheduling/login.html')
                
            login(request, user)
            print(f"✓ Login successful for {user.sap}")
            
            # Check for superuser first, then management, then staff
            if user.is_superuser or user.is_staff:
                print(f"Redirecting superuser/admin to manager dashboard")
                return redirect('manager_dashboard')
            elif user.role and user.role.is_management:
                print(f"Redirecting to manager_dashboard")
                return redirect('manager_dashboard')
            else:
                print(f"Redirecting to staff_dashboard")
                return redirect('staff_dashboard')
        else:
            print(f"✗ Authentication failed for SAP: '{sap}'")
            messages.error(request, 'Invalid SAP number or password')
        print("="*50)
    
    return render(request, 'scheduling/login.html')

def logout_view(request):
    """Logout and redirect to login"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')

# Homepage view
def home(request):
    return render(request, 'scheduling/home.html')

# Audit & Compliance Views (delegate to main scheduling.views)
@login_required
def audit_dashboard(request):
    return scheduling_views.audit_dashboard(request)

@login_required
def compliance_dashboard(request):
    return scheduling_views.compliance_dashboard(request)

@login_required
def data_change_log_list(request):
    return scheduling_views.data_change_log_list(request)

@login_required
def system_access_log_list(request):
    return scheduling_views.system_access_log_list(request)

@login_required
def compliance_violation_list(request):
    return scheduling_views.compliance_violation_list(request)

@login_required
def compliance_violation_detail(request, violation_id):
    return scheduling_views.compliance_violation_detail(request, violation_id)

@login_required
def audit_report_list(request):
    return scheduling_views.audit_report_list(request)

@login_required
def audit_report_detail(request, report_id):
    return scheduling_views.audit_report_detail(request, report_id)

@login_required
def generate_audit_report(request):
    return scheduling_views.generate_audit_report(request)

@login_required
def get_annual_leave_report(request):
    return scheduling_views.get_annual_leave_report(request)
