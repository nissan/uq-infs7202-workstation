# Test configuration for progress app tests
import pytest
import os
import django
from django.conf import settings

# This ensures Django test settings are set up for pytest, if you're using it
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

# Set TEST_MODE to True for all tests
settings.TEST_MODE = True

@pytest.fixture
def api_client():
    """Returns an unauthenticated API client"""
    from rest_framework.test import APIClient
    return APIClient()