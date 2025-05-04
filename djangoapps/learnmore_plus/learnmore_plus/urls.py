"""
URL configuration for learnmore_plus project.

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
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from apps.core import views as core_views
from apps.accounts import views as account_views
from apps.core.views_monitoring import metrics_view
from django.conf import settings
from django.conf.urls.static import static

# Simple health check endpoint for Railway
def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Removed path("", core_views.home, name="home") to resolve conflict
    path("accounts/", include("allauth.urls")),  # allauth URLs
    path("login/", account_views.login_view, name="login"),
    path("register/", account_views.register, name="register"),
    path("logout/", account_views.logout_view, name="logout"),
    path("health/", health_check, name="health_check"),
    path("metrics/", metrics_view, name="metrics"),
    path('admin-dashboard/', include(('apps.dashboard.urls', 'admin_dashboard'), namespace='admin_dashboard')),
    path('courses/', include('apps.courses.urls')),
    path('', include(('apps.core.urls', 'core'), namespace='core')),  # This already includes the home URL
    path('accounts/', include('apps.accounts.urls')),
    path('instructor/', include('apps.courses.instructor_urls')),
    path('coordinator/', include('apps.courses.coordinator_urls')),
    path('api/', include('apps.courses.api_urls')),  # API endpoints
    path('api/', include('apps.dashboard.api_urls')),  # Dashboard API endpoints
    path('qr/', include('apps.qr_codes.urls')),  # QR code URLs
    path('tutor/', include('apps.ai_tutor.urls')),  # AI Tutor URLs
    path('dashboard/', include(('apps.dashboard.urls', 'user_dashboard'), namespace='user_dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Temporarily disabled debug toolbar
    # import debug_toolbar
    # urlpatterns = [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns
