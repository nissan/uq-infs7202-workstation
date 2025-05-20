"""
Custom test client for testing.

This module provides a test client that disables CSRF checking for tests.
"""
from django.test.client import Client

class NoCSRFClient(Client):
    """A test client that ignores CSRF checks."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the client with CSRF checks disabled."""
        # Ensure that CSRF checks are disabled
        enforce_csrf_checks = kwargs.pop('enforce_csrf_checks', False)
        super().__init__(enforce_csrf_checks=enforce_csrf_checks, *args, **kwargs)
    
    def post(self, *args, **kwargs):
        """
        Request a response from the server using POST, with CSRF checks disabled.
        """
        return super().post(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        """
        Request a response from the server using GET, with CSRF checks disabled.
        """
        return super().get(*args, **kwargs)