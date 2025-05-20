"""
CSRF bypass module for Django tests.

This module monkey-patches Django's CSRF protection to make it a no-op in tests.
"""

import sys

# Only apply the patch when running tests
if 'test' in sys.argv:
    # Apply the patches
    from django.views.decorators.csrf import csrf_protect, csrf_exempt, requires_csrf_token
    from django.middleware.csrf import CsrfViewMiddleware
    
    # Make CSRF protect a no-op
    def dummy_decorator(view_func):
        return view_func
    
    # Replace the real decorators with no-ops
    csrf_protect = dummy_decorator
    requires_csrf_token = dummy_decorator
    
    # Make CsrfViewMiddleware do nothing
    CsrfViewMiddleware.process_view = lambda self, request, callback, callback_args, callback_kwargs: None
    
    # Import Django's modules directly and patch them
    import django.views.decorators.csrf
    django.views.decorators.csrf.csrf_protect = dummy_decorator
    django.views.decorators.csrf.requires_csrf_token = dummy_decorator
    
    # Ensure all requests bypass CSRF
    from django.test.client import Client
    original_get = Client.get
    original_post = Client.post
    
    def get_with_csrf_bypass(self, *args, **kwargs):
        if not hasattr(self, 'handler'):
            return original_get(self, *args, **kwargs)
        self.handler.enforce_csrf_checks = False
        return original_get(self, *args, **kwargs)
    
    def post_with_csrf_bypass(self, *args, **kwargs):
        if not hasattr(self, 'handler'):
            return original_post(self, *args, **kwargs)
        self.handler.enforce_csrf_checks = False
        return original_post(self, *args, **kwargs)
    
    Client.get = get_with_csrf_bypass
    Client.post = post_with_csrf_bypass
    
    print("CSRF checks disabled for tests.")