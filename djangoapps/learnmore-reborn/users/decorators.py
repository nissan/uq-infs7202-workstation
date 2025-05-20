"""
Custom decorators for the users app.
"""
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.conf import settings
from functools import wraps

def login_required_for_test(view_func):
    """
    Custom login required decorator that works properly with tests.
    
    This decorator checks if the request has a user attribute and if the user is authenticated.
    If not, it redirects to the login page. It also allows tests to bypass authentication
    if they set the _bypass_auth attribute on the request.
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        # Skip authentication check if we're in a test and auth is bypassed
        if hasattr(request, '_bypass_auth') and request._bypass_auth:
            return view_func(request, *args, **kwargs)
            
        # Normal login check
        if not request.user.is_authenticated:
            login_url = settings.LOGIN_URL if hasattr(settings, 'LOGIN_URL') else '/users/login/'
            return redirect(login_url)
        return view_func(request, *args, **kwargs)
    return wrapped