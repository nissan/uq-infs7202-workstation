"""
URL configuration for learnmore_enhanced project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('learnmoreapp.urls')),
] 