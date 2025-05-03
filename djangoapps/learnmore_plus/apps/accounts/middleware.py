from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve

class AdminPreferencesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle admin preferences only for admin users
        if request.user.is_staff and request.path.startswith('/admin/'):
            # Initialize admin preferences in session if not present
            if 'admin_preferences' not in request.session:
                request.session['admin_preferences'] = {
                    'sidebar_open': True,
                    'theme': 'auto'
                }
            
            # Update preferences from request
            if request.method == 'POST':
                preferences = request.session.get('admin_preferences', {})
                if 'sidebar_state' in request.POST:
                    preferences['sidebar_open'] = request.POST['sidebar_state'] == 'true'
                if 'theme' in request.POST:
                    preferences['theme'] = request.POST['theme']
                request.session['admin_preferences'] = preferences
                request.session.modified = True

        response = self.get_response(request)
        return response 

class RoleBasedAccessMiddleware:
    """
    Middleware to handle role-based access to admin pages.
    This ensures that even if is_staff is True, the user must have the correct role.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is an admin page
        if request.path.startswith('/admin/'):
            # Allow superusers
            if request.user.is_superuser:
                return self.get_response(request)

            # Check if user is authenticated and has a profile
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to access this page.')
                return redirect('login')

            try:
                # Check if user has admin or coordinator role
                if request.user.profile.role.name not in ['admin', 'course_coordinator']:
                    messages.error(request, 'You do not have permission to access the admin interface.')
                    return redirect('home')
            except:
                messages.error(request, 'You do not have permission to access the admin interface.')
                return redirect('home')

        return self.get_response(request) 