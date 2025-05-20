from django.urls import path, include
from . import views

app_name = 'analytics'

urlpatterns = [
    # Include API URLs
    path('api/', include('analytics.api_urls')),
    
    # Add views for web interface here in the future
]