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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('scheduling.management.urls')),
    path('staff-records/', include(('staff_records.urls', 'staff_records'), namespace='staff_records')),
    path('accounts/', include('django.contrib.auth.urls')),
    # Task 38: Mobile App API
    path('api/mobile/', include('scheduling.api_urls')),
    path('api-auth/', include('rest_framework.urls')),  # DRF browsable API login
]

# Task 51: Custom error handlers
handler404 = 'scheduling.views_errors.handler404'
handler500 = 'scheduling.views_errors.handler500'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)