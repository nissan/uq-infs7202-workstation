from django.conf import settings
from django.urls import reverse
import datetime

def global_context(request):
    """
    Context processor that adds global variables to all templates.
    This is useful for items that are needed across the application.
    """
    return {
        'site_name': 'LearnMore Plus',
        'primary_color': 'blue',  # This can be used to set a theme color
        'current_year': datetime.datetime.now().year,
        'debug_mode': settings.DEBUG,
        
        # Common URLs
        'home_url': reverse('core:home'),
        'about_url': reverse('core:about'),
        'course_catalog_url': reverse('courses:course_catalog'),
        
        # Feature flags
        'enable_ai_tutor': True,
        'enable_qr_codes': True,
    }

def theme_processor(request):
    """
    Theme-related context data
    """
    return {
        'theme': {
            'primary_color': 'blue-600',
            'secondary_color': 'purple-600',
            'dark_mode_supported': True,
        }
    }