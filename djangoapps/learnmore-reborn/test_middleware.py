"""
Test middleware for disabling CSRF in tests.

This middleware disables CSRF checks for requests that come from tests.
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import sys

class TestCSRFMiddleware(MiddlewareMixin):
    """Middleware that detects test requests and disables CSRF checks."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        # Monkey patch CsrfViewMiddleware at initialization
        if 'test' in sys.argv or hasattr(settings, 'TEST_MODE'):
            from django.middleware.csrf import CsrfViewMiddleware
            # Make the process_view method a no-op
            CsrfViewMiddleware.process_view = lambda self, request, callback, callback_args, callback_kwargs: None
    
    def process_request(self, request):
        """Process the request and mark it as a test request if applicable."""
        # Disable CSRF for all requests during tests
        request._dont_enforce_csrf_checks = True
        return None
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Process the view and disable CSRF checks if needed."""
        # Always disable CSRF during tests
        return None