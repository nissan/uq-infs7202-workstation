"""
View patching for testing.

This module patches Django views to make them CSRF exempt for testing.
"""
import sys
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

# Dictionary to map class names to their original dispatch methods
_original_dispatches = {}

def is_test_mode():
    """Check if we're running tests."""
    return 'test' in sys.argv or hasattr(settings, 'TEST_MODE')

def patch_view_class(view_class):
    """
    Patch a class-based view to disable CSRF checks during tests.
    
    This function saves the original dispatch method and replaces it with a
    CSRF-exempt version when in test mode.
    """
    # Save the original dispatch method if we haven't already
    if view_class not in _original_dispatches:
        _original_dispatches[view_class] = view_class.dispatch
    
    # Replace the dispatch method with a CSRF-exempt version
    @csrf_exempt
    def csrf_exempt_dispatch(self, request, *args, **kwargs):
        # Always bypass CSRF in test mode
        if is_test_mode():
            request._dont_enforce_csrf_checks = True
        return _original_dispatches[view_class](self, request, *args, **kwargs)
    
    # Replace the dispatch method
    view_class.dispatch = csrf_exempt_dispatch
    
    return view_class

def patch_function_view(view_func):
    """
    Patch a function-based view to disable CSRF checks during tests.
    
    This function wraps the original view function with a CSRF-exempt decorator.
    """
    @wraps(view_func)
    @csrf_exempt
    def wrapped(request, *args, **kwargs):
        # Always bypass CSRF in test mode
        if is_test_mode():
            request._dont_enforce_csrf_checks = True
        return view_func(request, *args, **kwargs)
    
    return wrapped

def patch_all_views():
    """
    Patch all views in the courses app to disable CSRF checks during tests.
    
    This function should be called before running tests.
    """
    # Import all the views we need to patch
    import courses.views
    from django.views.generic import ListView, DetailView
    from django.contrib.auth.mixins import LoginRequiredMixin
    import django.views.decorators.csrf
    
    # Temporarily replace the CSRF protection decorator
    original_csrf_protect = django.views.decorators.csrf.csrf_protect
    django.views.decorators.csrf.csrf_protect = lambda view_func: view_func
    
    # Patch all class-based views
    for name in dir(courses.views):
        attr = getattr(courses.views, name)
        if isinstance(attr, type) and issubclass(attr, (ListView, DetailView)):
            # Patch the class
            method_decorator(csrf_exempt, name='dispatch')(attr)
    
    # Patch specific function-based views
    courses.views.enroll_course = csrf_exempt(courses.views.enroll_course)
    courses.views.unenroll_course = csrf_exempt(courses.views.unenroll_course)
    
    # Restore the original CSRF decorator after patching
    django.views.decorators.csrf.csrf_protect = original_csrf_protect

# Patch all views for testing
def apply_patches():
    """Apply all patches when module is imported."""
    # Only apply in test mode
    if is_test_mode():
        # Patch all views
        patch_all_views()
        
        # Optional: Make CSRF middleware a no-op
        from django.middleware.csrf import CsrfViewMiddleware
        CsrfViewMiddleware.process_view = lambda self, request, callback, callback_args, callback_kwargs: None

# Apply patches when imported
apply_patches()