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
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('courses/', include('courses.urls')),
    path('api/courses/', include('courses.api_urls')),
    path('api/progress/', include('progress.api_urls')),
    path('api/users/', include('users.api_urls')),
]
