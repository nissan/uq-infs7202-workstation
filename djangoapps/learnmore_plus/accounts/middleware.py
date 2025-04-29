from django.conf import settings

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