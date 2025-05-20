from rest_framework import permissions

class IsAnalyticsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow analytics administrators to access analytics data.
    Analytics administrators are users with the 'analytics_admin' permission.
    """
    
    def has_permission(self, request, view):
        # Check if user has the analytics_admin permission
        return request.user.has_perm('analytics.analytics_admin')

class IsCourseInstructor(permissions.BasePermission):
    """
    Custom permission to only allow course instructors to access course-specific analytics.
    Course instructors can only access analytics for courses they teach.
    """
    
    def has_permission(self, request, view):
        # Allow read-only access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Only instructors can modify analytics
        return request.user.has_perm('courses.change_course')
    
    def has_object_permission(self, request, view, obj):
        # For course analytics, check if user is an instructor of the course
        if hasattr(obj, 'course'):
            return obj.course.instructors.filter(id=request.user.id).exists()
        # For quiz analytics, check if user is an instructor of the quiz's course
        elif hasattr(obj, 'quiz'):
            return obj.quiz.course.instructors.filter(id=request.user.id).exists()
        return False

class IsOwnAnalytics(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own analytics data.
    Users can only view their own analytics unless they are staff.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff can access all analytics
        if request.user.is_staff:
            return True
        # Users can only access their own analytics
        return obj.user == request.user 