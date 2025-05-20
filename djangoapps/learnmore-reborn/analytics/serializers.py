from rest_framework import serializers
from .models import (
    UserActivity,
    CourseAnalyticsSummary,
    ModuleEngagement,
    LearningPathAnalytics
)
from courses.models import Course, Module

class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity data"""
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'username', 'activity_type', 'timestamp',
            'ip_address', 'user_agent', 'details'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_username(self, obj):
        return obj.user.username

class CourseAnalyticsSummarySerializer(serializers.ModelSerializer):
    """Serializer for course analytics summary data"""
    course_title = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseAnalyticsSummary
        fields = [
            'id', 'course', 'course_title', 'total_enrollments', 'active_learners',
            'completion_rate', 'average_rating', 'engagement_score',
            'engagement_trend', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated', 'course_title']
    
    def get_course_title(self, obj):
        return obj.course.title

class ModuleEngagementSerializer(serializers.ModelSerializer):
    """Serializer for module engagement data"""
    username = serializers.SerializerMethodField()
    module_title = serializers.SerializerMethodField()
    
    class Meta:
        model = ModuleEngagement
        fields = [
            'id', 'module', 'module_title', 'user', 'username', 'view_count',
            'time_spent', 'last_viewed', 'completion_date', 'interaction_data'
        ]
        read_only_fields = ['id', 'last_viewed']
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_module_title(self, obj):
        return obj.module.title

class LearningPathAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for learning path analytics data"""
    module_titles = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPathAnalytics
        fields = [
            'id', 'path_signature', 'path_description', 'path_modules', 
            'module_titles', 'user_count', 'average_completion_time',
            'success_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_module_titles(self, obj):
        """Return titles of modules in this learning path"""
        try:
            module_ids = obj.path_modules
            modules = Module.objects.filter(id__in=module_ids)
            return [m.title for m in modules]
        except Exception:
            return []

# Dashboard-specific serializers that combine multiple analytics types
class CourseDashboardSerializer(serializers.ModelSerializer):
    """Serializer for course dashboard that includes comprehensive analytics"""
    analytics = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'analytics']
    
    def get_analytics(self, obj):
        """Get comprehensive analytics for the course"""
        try:
            analytics = obj.analytics_summary
        except CourseAnalyticsSummary.DoesNotExist:
            # Create analytics object if it doesn't exist
            analytics = CourseAnalyticsSummary.objects.create(course=obj)
            
        # Serialize the analytics
        serializer = CourseAnalyticsSummarySerializer(analytics)
        
        # Add additional analytics data
        result = serializer.data
        
        # Module engagement statistics
        module_engagement = {}
        modules = obj.modules.all()
        for module in modules:
            try:
                engagement_count = ModuleEngagement.objects.filter(module=module).count()
                completion_count = ModuleEngagement.objects.filter(
                    module=module, 
                    completion_date__isnull=False
                ).count()
                
                module_engagement[module.id] = {
                    'title': module.title,
                    'engagement_count': engagement_count,
                    'completion_count': completion_count,
                    'completion_rate': (completion_count / engagement_count * 100) if engagement_count > 0 else 0
                }
            except Exception:
                pass
                
        result['module_engagement'] = module_engagement
        
        return result