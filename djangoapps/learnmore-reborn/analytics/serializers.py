from rest_framework import serializers
from django.utils import timezone
from .models import (
    UserActivity, LearnerAnalytics, CourseAnalytics,
    UserAnalytics, QuizAnalytics, SystemAnalytics,
    ModuleEngagement, LearningPathAnalytics
)
from courses.serializers import CourseSerializer, QuizSerializer, ModuleSerializer
from users.serializers import UserSerializer

class UserActivitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'activity_type', 'timestamp', 'ip_address',
            'user_agent', 'session_id', 'details'
        ]
        read_only_fields = ['timestamp']

class ModuleEngagementSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ModuleEngagement
        fields = [
            'id', 'module', 'user', 'view_count', 'time_spent',
            'last_viewed', 'completion_date', 'interaction_data'
        ]
        read_only_fields = ['last_viewed']

class CourseAnalyticsSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = CourseAnalytics
        fields = [
            'id', 'course', 'total_enrollments', 'active_enrollments',
            'new_enrollments', 'enrollment_trend', 'completion_rate',
            'module_completion_rates', 'average_completion_time',
            'average_score', 'score_distribution', 'module_performance',
            'average_time_per_module', 'total_learning_time',
            'time_distribution', 'engagement_score', 'active_users',
            'interaction_rates', 'created_at', 'last_updated',
            'last_calculated'
        ]
        read_only_fields = ['created_at', 'last_updated', 'last_calculated']

class UserAnalyticsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserAnalytics
        fields = [
            'id', 'user', 'courses_enrolled', 'courses_completed',
            'current_courses', 'completion_rate', 'last_active',
            'active_days', 'average_session_duration', 'activity_heatmap',
            'average_score', 'quiz_completion_rate', 'module_completion_rate',
            'performance_by_category', 'overall_engagement',
            'course_engagement', 'interaction_frequency',
            'preferred_learning_times', 'study_duration_patterns',
            'content_preferences', 'created_at', 'last_updated',
            'last_calculated'
        ]
        read_only_fields = ['created_at', 'last_updated', 'last_calculated']

class QuizAnalyticsSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    
    class Meta:
        model = QuizAnalytics
        fields = [
            'id', 'quiz', 'question_difficulty', 'question_discrimination',
            'question_statistics', 'total_attempts', 'unique_attempters',
            'average_attempts', 'attempt_distribution', 'average_score',
            'score_distribution', 'pass_rate', 'average_completion_time',
            'time_distribution', 'time_by_question', 'created_at',
            'last_updated', 'last_calculated'
        ]
        read_only_fields = ['created_at', 'last_updated', 'last_calculated']

class SystemAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemAnalytics
        fields = [
            'id', 'active_users', 'concurrent_sessions',
            'average_response_time', 'error_rate', 'cpu_usage',
            'memory_usage', 'database_connections', 'cache_hit_rate',
            'error_counts', 'error_trends', 'critical_errors',
            'total_sessions', 'average_session_duration',
            'session_distribution', 'timestamp', 'last_updated'
        ]
        read_only_fields = ['timestamp', 'last_updated']

class LearningPathAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPathAnalytics
        fields = [
            'id', 'path_signature', 'path_description', 'path_modules',
            'user_count', 'average_completion_time', 'success_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class AnalyticsExportSerializer(serializers.Serializer):
    """Serializer for analytics export requests"""
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    analytics_type = serializers.ChoiceField(choices=[
        'course', 'user', 'quiz', 'system', 'all'
    ])
    format = serializers.ChoiceField(choices=['json', 'csv', 'xlsx'])
    include_details = serializers.BooleanField(default=False)
    
    def validate(self, data):
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError(
                    "End date must be after start date"
                )
        return data

class AnalyticsRecalculationSerializer(serializers.Serializer):
    """Serializer for analytics recalculation requests"""
    analytics_type = serializers.ChoiceField(choices=[
        'course', 'user', 'quiz', 'system', 'all'
    ])
    force_recalculation = serializers.BooleanField(default=False)
    specific_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    def validate(self, data):
        if 'specific_ids' in data and not data['specific_ids']:
            raise serializers.ValidationError(
                "Specific IDs list cannot be empty"
            )
        return data