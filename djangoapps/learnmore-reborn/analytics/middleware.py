import time
from django.utils import timezone
from django.core.cache import cache
from .models import UserActivity, SystemAnalytics

class AnalyticsMiddleware:
    """Middleware for collecting analytics data"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Start timing the request
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Only collect analytics for authenticated users and non-admin paths
        if hasattr(request, 'user') and request.user is not None and request.user.is_authenticated and not request.path.startswith('/admin/'):
            # Calculate request processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Record user activity
            self._record_user_activity(request, response, processing_time)
            
            # Update system metrics
            self._update_system_metrics(request, response, processing_time)
        
        return response
    
    def _record_user_activity(self, request, response, processing_time):
        """Record user activity data"""
        try:
            # Determine activity type based on request path and method
            activity_type = self._determine_activity_type(request)
            
            # Create activity record
            UserActivity.objects.create(
                user=request.user,
                activity_type=activity_type,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_id=request.session.session_key,
                details={
                    'path': request.path,
                    'method': request.method,
                    'processing_time': processing_time,
                    'status_code': response.status_code,
                    'referrer': request.META.get('HTTP_REFERER', ''),
                }
            )
        except Exception as e:
            # Log error but don't interrupt request processing
            print(f"Error recording user activity: {e}")
    
    def _update_system_metrics(self, request, response, processing_time):
        """Update system-wide metrics"""
        try:
            # Get or create current system metrics
            metrics, created = SystemAnalytics.objects.get_or_create(
                timestamp__date=timezone.now().date(),
                defaults={'timestamp': timezone.now()}
            )
            
            # Update metrics
            metrics.update_metrics({
                'request_count': 1,
                'processing_time': processing_time,
                'status_code': response.status_code,
                'path': request.path,
                'method': request.method,
            })
            
            # Cache current metrics for quick access
            cache_key = 'system_metrics_current'
            cache.set(cache_key, metrics.to_dict(), timeout=300)  # Cache for 5 minutes
            
        except Exception as e:
            # Log error but don't interrupt request processing
            print(f"Error updating system metrics: {e}")
    
    def _determine_activity_type(self, request):
        """Determine the type of activity based on request path and method"""
        path = request.path.lower()
        method = request.method
        
        # Course-related activities
        if '/courses/' in path:
            if method == 'GET':
                return 'course_view'
            elif method == 'POST':
                if '/enroll/' in path:
                    return 'course_enroll'
                elif '/complete/' in path:
                    return 'course_complete'
        
        # Quiz-related activities
        elif '/quizzes/' in path:
            if method == 'GET':
                return 'quiz_view'
            elif method == 'POST':
                if '/submit/' in path:
                    return 'quiz_submit'
                elif '/start/' in path:
                    return 'quiz_start'
        
        # Module-related activities
        elif '/modules/' in path:
            if method == 'GET':
                return 'module_view'
            elif method == 'POST':
                if '/complete/' in path:
                    return 'module_complete'
        
        # Analytics-related activities
        elif '/analytics/' in path:
            if method == 'GET':
                return 'analytics_view'
            elif method == 'POST':
                if '/export/' in path:
                    return 'analytics_export'
        
        # Default activity types
        if method == 'GET':
            return 'page_view'
        elif method == 'POST':
            return 'form_submit'
        else:
            return 'other'
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR') 