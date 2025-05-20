"""
Test middleware for disabling CSRF in tests.

This middleware disables CSRF checks for requests that come from tests.
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class TestCSRFMiddleware(MiddlewareMixin):
    """Middleware that detects test requests and disables CSRF checks."""
    
    def process_request(self, request):
        """Process the request and mark it as a test request if applicable."""
        # Mark the request as a test request if it comes from our test client
        if hasattr(request, '_bypass_auth') and request._bypass_auth:
            request._dont_enforce_csrf_checks = True
        
        # When running tests, always disable CSRF checks
        if settings.DEBUG and 'test' in settings.DATABASES:
            request._dont_enforce_csrf_checks = True
        
        return None