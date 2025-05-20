from django.db import models
from django.conf import settings
from django.utils import timezone
from courses.models import Course, Module

class UserActivity(models.Model):
    """Tracks general user activity on the platform"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_activities')
    activity_type = models.CharField(max_length=50)  # login, view_course, view_module, etc.
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)  # Additional details specific to the activity type
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"

class CourseAnalyticsSummary(models.Model):
    """High-level analytics for a specific course"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='analytics_summary')
    total_enrollments = models.IntegerField(default=0)
    active_learners = models.IntegerField(default=0)  # Active in last 30 days
    completion_rate = models.FloatField(default=0.0)  # Percentage of enrolled users who completed
    average_rating = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)  # Composite score of engagement metrics
    last_updated = models.DateTimeField(auto_now=True)
    engagement_trend = models.JSONField(default=dict, blank=True)  # Time-series data for engagement
    
    class Meta:
        verbose_name_plural = "Course Analytics Summaries"
    
    def __str__(self):
        return f"Analytics Summary for {self.course.title}"
    
    def recalculate(self):
        """Recalculate analytics data from current enrollments and progress"""
        from datetime import timedelta
        
        # Get enrollments for this course
        enrollments = self.course.enrollments.all()
        self.total_enrollments = enrollments.count()
        
        # Calculate active learners (with activity in the last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users = set(UserActivity.objects.filter(
            timestamp__gte=thirty_days_ago,
            details__contains={'course_id': self.course.id}
        ).values_list('user_id', flat=True))
        
        self.active_learners = len(active_users)
        
        # Calculate completion rate
        completed = enrollments.filter(status='completed').count()
        self.completion_rate = (completed / self.total_enrollments * 100) if self.total_enrollments > 0 else 0
        
        # Save changes
        self.last_updated = timezone.now()
        self.save()

class ModuleEngagement(models.Model):
    """Tracks learner engagement with specific modules"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='module_engagements')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0)
    time_spent = models.DurationField(default=timezone.timedelta)  # Total time spent on this module
    last_viewed = models.DateTimeField(auto_now=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    interaction_data = models.JSONField(default=dict, blank=True)  # Detailed interaction data
    
    class Meta:
        unique_together = ('module', 'user')
        indexes = [
            models.Index(fields=['module', 'user']),
            models.Index(fields=['user', 'last_viewed']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.module.title}"
    
    def record_view(self, duration_seconds=None):
        """Record a view of this module"""
        self.view_count += 1
        
        if duration_seconds:
            import datetime
            self.time_spent += datetime.timedelta(seconds=duration_seconds)
            
        self.last_viewed = timezone.now()
        self.save()

class LearningPathAnalytics(models.Model):
    """Tracks analytics for common learning paths through courses"""
    path_signature = models.CharField(max_length=255, unique=True)  # Hash of the path
    path_description = models.TextField()
    path_modules = models.JSONField(default=list)  # List of module IDs in order
    user_count = models.IntegerField(default=0)
    average_completion_time = models.DurationField(null=True, blank=True)
    success_rate = models.FloatField(default=0.0)  # Percentage of users who complete this path
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Learning Path Analytics"
    
    def __str__(self):
        return f"Path: {self.path_description[:50]}..."
    
    @classmethod
    def identify_common_paths(cls, course, min_users=5):
        """
        Analyze user progress data to identify common learning paths
        through the course
        
        Args:
            course: The course to analyze
            min_users: Minimum number of users who must follow a path for it to be considered
            
        Returns:
            List of path signatures that were created or updated
        """
        # This would be implemented to analyze progress data
        # and identify common paths through the modules
        pass