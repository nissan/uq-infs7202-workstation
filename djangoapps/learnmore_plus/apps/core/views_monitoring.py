"""
Monitoring views for the application.
These views provide metrics and health check endpoints for Railway deployment.
"""
from django.http import HttpResponse
from django.db import connection
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def metrics_view(request):
    """
    Basic metrics endpoint for monitoring.
    Returns key metrics in Prometheus format.
    """
    # Database connection check
    db_connected = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_connected = False
    
    # Basic user metrics
    total_users = User.objects.count()
    active_today = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=1)
    ).count()
    
    # Format metrics in Prometheus format
    metrics = [
        "# HELP app_total_users Total number of registered users",
        "# TYPE app_total_users gauge",
        f"app_total_users {total_users}",
        
        "# HELP app_active_users_today Number of users active in the last 24 hours",
        "# TYPE app_active_users_today gauge",
        f"app_active_users_today {active_today}",
        
        "# HELP app_database_up Database connection status",
        "# TYPE app_database_up gauge",
        f"app_database_up {1 if db_connected else 0}",
    ]
    
    # Add additional metrics if appropriate apps are available
    try:
        from apps.courses.models import Course, Enrollment
        
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        
        metrics.extend([
            "# HELP app_total_courses Total number of courses",
            "# TYPE app_total_courses gauge",
            f"app_total_courses {total_courses}",
            
            "# HELP app_total_enrollments Total number of course enrollments",
            "# TYPE app_total_enrollments gauge",
            f"app_total_enrollments {total_enrollments}",
        ])
    except (ImportError, ModuleNotFoundError):
        pass
    
    try:
        from apps.ai_tutor.models import TutorSession, TutorMessage
        
        total_sessions = TutorSession.objects.count()
        total_messages = TutorMessage.objects.count()
        
        metrics.extend([
            "# HELP app_total_tutor_sessions Total number of AI tutor sessions",
            "# TYPE app_total_tutor_sessions gauge",
            f"app_total_tutor_sessions {total_sessions}",
            
            "# HELP app_total_tutor_messages Total number of AI tutor messages",
            "# TYPE app_total_tutor_messages gauge",
            f"app_total_tutor_messages {total_messages}",
        ])
    except (ImportError, ModuleNotFoundError):
        pass
    
    return HttpResponse("\n".join(metrics), content_type="text/plain")