"""
Settings package for the LearnMore Plus project.
"""
import os

# Set the default settings module
DJANGO_SETTINGS_MODULE = os.getenv('DJANGO_SETTINGS_MODULE', 'learnmore_plus.settings.local') 