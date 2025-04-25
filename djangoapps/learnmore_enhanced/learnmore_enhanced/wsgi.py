"""
WSGI config for learnmore_enhanced project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore_enhanced.settings')

application = get_wsgi_application() 