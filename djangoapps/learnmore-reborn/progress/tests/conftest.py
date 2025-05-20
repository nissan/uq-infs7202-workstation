# Test configuration for progress app tests
import pytest
import os
import django

# This ensures Django test settings are set up for pytest, if you're using it
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

@pytest.fixture
def api_client():
    """Returns an unauthenticated API client"""
    from rest_framework.test import APIClient
    return APIClient()