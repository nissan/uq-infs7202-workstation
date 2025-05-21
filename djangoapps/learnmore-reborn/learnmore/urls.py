"""
URL configuration for learnmore project.

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
from django.views.generic import RedirectView
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from allauth.socialaccount.providers.google.views import oauth2_login
from . import views  # Add this import

def root_view(request):
    try:
        from courses.models import Course
        if Course.objects.exists():
            return RedirectView.as_view(url='/courses/catalog/', permanent=False)(request)
        return JsonResponse({
            'message': 'Welcome to LearnMore',
            'status': 'No courses available yet',
            'endpoints': {
                'courses': '/courses/catalog/',
                'api/courses': '/api/courses/',
                'admin': '/admin/',
            }
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'An error occurred while accessing the root URL'
        }, status=500)

urlpatterns = [
    path('', views.landing_page, name='landing'),  # Move this to the top
    path('features/', views.features_page, name='features'),
    path('how-it-works/', views.how_it_works_page, name='how-it-works'),
    path('testimonials/', views.testimonials_page, name='testimonials'),
    path('admin/', admin.site.urls),
    # Template-based URLs
    path('core/', include('core.urls')),  # Core app for theme and accessibility
    path('courses/', include('courses.urls')),
    path('users/', include('users.urls')),  # Template-based user routes
    path('progress/', include('progress.urls')),  # Progress tracking and learning interface
    path('analytics/', include('analytics.urls')),  # Analytics dashboards and data
    path('ai-tutor/', include('ai_tutor.urls')),  # AI Tutor interface and API
    path('qr-codes/', include('qr_codes.urls')),  # QR code generation and scanning
    path('accounts/', include('allauth.urls')),
    path('accounts/google/login/', oauth2_login, name='google_login'),
    # API URLs
    path('api/core/', include('core.api_urls')),  # Core API for themes
    path('api/courses/', include('courses.api_urls')),
    path('api/progress/', include('progress.api_urls')),
    path('api/users/', include('users.api_urls')),
    path('api/analytics/', include('analytics.api_urls')),
    path('api/qr-codes/', include('qr_codes.api_urls')),  # QR code API
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)