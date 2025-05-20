"""
Custom test client for testing.

This module provides a test client that combines Django and REST Framework capabilities.
"""
from django.test.client import Client
from rest_framework.test import APIClient

class TestClient(Client):
    """
    A test client that combines Django and DRF capabilities, with CSRF checks disabled.
    
    This client can be used for both template tests and API tests with the same interface.
    """
    
    def __init__(self, *args, **kwargs):
        # Ensure that CSRF checks are disabled
        enforce_csrf_checks = kwargs.pop('enforce_csrf_checks', False)
        super().__init__(enforce_csrf_checks=enforce_csrf_checks, *args, **kwargs)
        
        # Create a DRF API client
        self.api = APIClient()
        self.api.enforce_csrf_checks = False
        
        # Mark this client as a test client
        self._bypass_auth = True
        self.api._bypass_auth = True
    
    def credentials(self, **kwargs):
        """Set credentials for DRF authentication."""
        self.api.credentials(**kwargs)
        # Try to set cookies for Django authentication too
        if 'HTTP_AUTHORIZATION' in kwargs:
            self.defaults.update({'HTTP_AUTHORIZATION': kwargs['HTTP_AUTHORIZATION']})
        return self
    
    def force_authenticate(self, user=None, token=None):
        """Force authentication for both clients."""
        self.api.force_authenticate(user=user, token=token)
        if user:
            self.force_login(user)
        return self