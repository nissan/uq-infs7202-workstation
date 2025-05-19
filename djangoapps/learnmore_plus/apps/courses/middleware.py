import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

class CourseViewErrorMiddleware:
    """
    Middleware to catch errors in course views and redirect to a safe page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Process exceptions during view execution"""
        # Only handle our target URLs
        if 'courses/student/dashboard' in request.path:
            logger.error(f"Error in student dashboard: {str(exception)}")
            
            # Add a message to inform the user
            messages.error(
                request, 
                "We encountered an error loading your dashboard. Our team has been notified."
            )
            
            # Redirect to home
            return redirect('home')

        return None