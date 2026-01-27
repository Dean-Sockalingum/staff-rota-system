"""
URL configuration for rotasystems project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import FileResponse
from rotasystems import saml_views
import os

def service_worker_view(request):
    """Serve the service worker from the root path with proper headers."""
    file_path = os.path.join(settings.BASE_DIR, 'scheduling', 'static', 'js', 'service-worker.js')
    response = FileResponse(open(file_path, 'rb'), content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    # Prevent Cloudflare from caching
    response['CDN-Cache-Control'] = 'no-store'
    response['Cloudflare-CDN-Cache-Control'] = 'no-store'
    return response

urlpatterns = [
    path('service-worker.js', service_worker_view, name='service-worker'),
    path('admin/', admin.site.urls),
    path('', include('scheduling.management.urls')),
    path('', include('scheduling.urls_activity')),  # Task 55: Activity Feed
    path('', include('scheduling.urls_compliance')),  # Task 56: Compliance Widgets
    path('', include('scheduling.urls_calendar')),  # Task 59: Leave Calendar
    path('', include('scheduling.urls')),  # Main scheduling app URLs - includes search
    path('staff-records/', include(('staff_records.urls', 'staff_records'), namespace='staff_records')),
    path('accounts/', include('django.contrib.auth.urls')),
    # TQM Module 1: Quality Audits (PDSA Tracker)
    path('quality-audits/', include('quality_audits.urls')),
    # TQM Module 2: Incident & Safety Management
    path('incident-safety/', include('incident_safety.urls')),
    # TQM Module 3: Experience & Feedback
    path('experience-feedback/', include('experience_feedback.urls')),
    # TQM Module 4: Training & Competency
    path('training_competency/', include('training_competency.urls')),
    # TQM Module 5: Policies & Procedures (New)
    path('policies/', include('policies_procedures.urls')),
    # TQM Module 5: Document & Policy Management (Legacy)
    path('documents/', include('document_management.urls')),
    # TQM Module 6: Risk Management
    path('risk-management/', include('risk_management.urls')),
    # TQM Module 7: Performance Metrics & KPIs
    path('performance-kpis/', include('performance_kpis.urls')),
    # Task 38: Mobile App API
    path('api/mobile/', include('scheduling.api_urls')),
    path('api-auth/', include('rest_framework.urls')),  # DRF browsable API login
    # SAML 2.0 Single Sign-On (CGI SSO Integration)
    path('saml/', include([
        path('login/', saml_views.saml_login, name='saml_login'),
        path('acs/', saml_views.saml_acs, name='saml_acs'),
        path('logout/', saml_views.saml_logout, name='saml_logout'),
        path('sls/', saml_views.saml_sls, name='saml_sls'),
        path('metadata/', saml_views.saml_metadata, name='saml_metadata'),
        path('status/', saml_views.saml_status, name='saml_status'),
    ])),
]

# Task 51: Custom error handlers
handler404 = 'scheduling.views_errors.handler404'
handler500 = 'scheduling.views_errors.handler500'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)