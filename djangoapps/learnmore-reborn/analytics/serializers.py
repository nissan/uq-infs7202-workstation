from rest_framework import serializers
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    UserActivity, LearnerAnalytics, CourseAnalytics,
    UserAnalytics, QuizAnalytics, SystemAnalytics,
    ModuleEngagement, LearningPathAnalytics, CourseAnalyticsSummary
)
from courses.models import Course
from courses.serializers import CourseSerializer, QuizSerializer, ModuleSerializer
from users.serializers import UserSerializer
import json

class JSONFieldValidator:
    """Validator for JSON fields to ensure proper structure"""
    def __init__(self, schema=None):
        self.schema = schema

    def __call__(self, value):
        if not isinstance(value, (dict, list)):
            raise serializers.ValidationError("Value must be a valid JSON object or array")
        if self.schema:
            # Here you could add JSON schema validation if needed
            pass

class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activity tracking.
    
    Tracks various user activities on the platform including logins, views,
    and other interactions. All fields are read-only except for activity_type
    and details which can be set during creation.
    """
    user = UserSerializer(read_only=True)
    details = serializers.JSONField(
        validators=[JSONFieldValidator()],
        help_text="Additional activity-specific details in JSON format"
    )
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'activity_type', 'timestamp', 'ip_address',
            'user_agent', 'session_id', 'details'
        ]
        read_only_fields = ['timestamp']
    
    def validate_activity_type(self, value):
        """Validate activity type is one of the expected values"""
        valid_types = ['login', 'logout', 'view_course', 'view_module', 
                      'take_quiz', 'complete_module', 'update_profile']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Activity type must be one of: {', '.join(valid_types)}"
            )
        return value

class ModuleEngagementSerializer(serializers.ModelSerializer):
    """
    Serializer for module engagement tracking.
    
    Tracks how users interact with specific modules, including view counts,
    time spent, and detailed interaction data.
    """
    module = ModuleSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    interaction_data = serializers.JSONField(
        validators=[JSONFieldValidator()],
        help_text="Detailed interaction data in JSON format"
    )
    time_spent = serializers.DurationField(
        help_text="Total time spent on this module"
    )
    
    class Meta:
        model = ModuleEngagement
        fields = [
            'id', 'module', 'user', 'view_count', 'time_spent',
            'last_viewed', 'completion_date', 'interaction_data'
        ]
        read_only_fields = ['last_viewed']
    
    def validate_view_count(self, value):
        """Ensure view count is non-negative"""
        if value < 0:
            raise serializers.ValidationError("View count cannot be negative")
        return value

class CourseAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for comprehensive course analytics.
    
    Provides detailed analytics about course performance, engagement,
    and learning metrics. All fields are read-only as they are
    calculated automatically.
    """
    course = CourseSerializer(read_only=True)
    completion_rate = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Course completion rate as a percentage"
    )
    engagement_score = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Overall engagement score (0-100)"
    )
    
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
    
    def to_representation(self, instance):
        """Optimize representation by using cached data when available"""
        data = super().to_representation(instance)
        # Add any cached data if available
        cache_key = f'course_analytics_{instance.course.id}'
        cached_data = instance.calculate_metrics()
        if cached_data:
            data.update(cached_data)
        return data

class UserAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for user-specific analytics.
    
    Tracks individual user performance, engagement, and learning patterns.
    All fields are read-only as they are calculated automatically.
    """
    user = UserSerializer(read_only=True)
    completion_rate = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Overall completion rate as a percentage"
    )
    overall_engagement = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Overall engagement score (0-100)"
    )
    
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
    """
    Serializer for quiz-specific analytics.
    
    Provides detailed analytics about quiz performance, including
    question difficulty, discrimination, and attempt patterns.
    All fields are read-only as they are calculated automatically.
    """
    quiz = QuizSerializer(read_only=True)
    pass_rate = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Quiz pass rate as a percentage"
    )
    average_score = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Average quiz score as a percentage"
    )
    
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
    """
    Serializer for system-wide analytics.
    
    Tracks system performance, resource usage, and error metrics.
    All fields are read-only as they are collected automatically.
    """
    error_rate = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="System error rate as a percentage"
    )
    cpu_usage = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="CPU usage as a percentage"
    )
    memory_usage = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Memory usage as a percentage"
    )
    cache_hit_rate = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Cache hit rate as a percentage"
    )
    
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
    """
    Serializer for learning path analytics.
    
    Tracks common learning paths through courses and their effectiveness.
    All fields are read-only as they are calculated automatically.
    """
    success_rate = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Path success rate as a percentage"
    )
    path_modules = serializers.JSONField(
        validators=[JSONFieldValidator()],
        help_text="List of module IDs in the learning path"
    )
    
    class Meta:
        model = LearningPathAnalytics
        fields = [
            'id', 'path_signature', 'path_description', 'path_modules',
            'user_count', 'average_completion_time', 'success_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CourseAnalyticsSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for course analytics summary.
    
    Provides a high-level summary of course analytics for quick access.
    All fields are read-only as they are calculated automatically.
    """
    course = CourseSerializer(read_only=True)
    completion_rate = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Course completion rate as a percentage"
    )
    engagement_score = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Overall engagement score (0-100)"
    )
    
    class Meta:
        model = CourseAnalyticsSummary
        fields = [
            'id', 'course', 'total_enrollments', 'active_learners',
            'completion_rate', 'average_rating', 'engagement_score',
            'engagement_trend', 'last_updated'
        ]
        read_only_fields = ['last_updated']

class LearnerAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for learner-specific analytics.
    
    Provides comprehensive analytics about individual learner performance,
    including quiz results, study patterns, and progress tracking.
    All fields are read-only as they are calculated automatically.
    """
    user = UserSerializer(read_only=True)
    strengths = serializers.JSONField(
        validators=[JSONFieldValidator()],
        help_text="List of learner's strengths"
    )
    areas_for_improvement = serializers.JSONField(
        validators=[JSONFieldValidator()],
        help_text="List of areas needing improvement"
    )
    performance_by_category = serializers.JSONField(
        validators=[JSONFieldValidator()],
        help_text="Performance metrics by category"
    )
    
    class Meta:
        model = LearnerAnalytics
        fields = [
            'id', 'user', 'total_quizzes_taken', 'total_quizzes_passed',
            'total_questions_answered', 'total_correct_answers',
            'average_time_per_question', 'total_study_time',
            'strengths', 'areas_for_improvement', 'learning_pattern_data',
            'quiz_performance_history', 'progress_over_time',
            'performance_by_category', 'course_completion_data',
            'percentile_ranking', 'created_at', 'last_updated'
        ]
        read_only_fields = ['created_at', 'last_updated']

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

class CourseDashboardSerializer(serializers.ModelSerializer):
    analytics = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'analytics']
    
    def get_analytics(self, obj):
        # Try to get the related CourseAnalyticsSummary or CourseAnalytics
        summary = getattr(obj, 'analytics_summary', None)
        if summary:
            return {
                'total_enrollments': summary.total_enrollments,
                'active_learners': summary.active_learners,
                'completion_rate': summary.completion_rate,
            }
        # Fallback: return zeros
        return {
            'total_enrollments': 0,
            'active_learners': 0,
            'completion_rate': 0.0,
        }

class LearnerComparisonSerializer(serializers.Serializer):
    """Serializer for comparing learner analytics data"""
    user = UserSerializer(read_only=True)
    percentile_rankings = serializers.DictField(
        child=serializers.FloatField(),
        help_text='Percentile rankings by category'
    )
    relative_performance = serializers.DictField(
        child=serializers.FloatField(),
        help_text='Performance relative to peer average (0-100)'
    )
    category_comparisons = serializers.DictField(
        child=serializers.DictField(),
        help_text='Detailed comparisons by category'
    )
    time_comparisons = serializers.DictField(
        child=serializers.FloatField(),
        help_text='Time-based metrics compared to peers'
    )
    strengths_relative = serializers.ListField(
        child=serializers.CharField(),
        help_text='Areas where learner performs better than peers'
    )
    areas_for_improvement_relative = serializers.ListField(
        child=serializers.CharField(),
        help_text='Areas where learner performs worse than peers'
    )