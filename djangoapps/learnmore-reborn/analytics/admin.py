from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserActivity, LearnerAnalytics, CourseAnalytics,
    UserAnalytics, QuizAnalytics, SystemAnalytics,
    ModuleEngagement, LearningPathAnalytics
)

@admin.register(CourseAnalytics)
class CourseAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('course', 'total_enrollments', 'active_enrollments', 
                   'completion_rate', 'engagement_score', 'last_updated')
    list_filter = ('last_updated', 'completion_rate', 'engagement_score')
    search_fields = ('course__title', 'course__code')
    readonly_fields = ('created_at', 'last_updated', 'last_calculated')
    actions = ['recalculate_metrics', 'export_analytics']
    
    fieldsets = (
        ('Course Information', {
            'fields': ('course',)
        }),
        ('Enrollment Statistics', {
            'fields': ('total_enrollments', 'active_enrollments', 'new_enrollments', 'enrollment_trend')
        }),
        ('Completion Metrics', {
            'fields': ('completion_rate', 'module_completion_rates', 'average_completion_time')
        }),
        ('Performance Metrics', {
            'fields': ('average_score', 'score_distribution', 'module_performance')
        }),
        ('Time Metrics', {
            'fields': ('average_time_per_module', 'total_learning_time', 'time_distribution')
        }),
        ('Engagement Metrics', {
            'fields': ('engagement_score', 'active_users', 'interaction_rates')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated', 'last_calculated'),
            'classes': ('collapse',)
        })
    )
    
    def recalculate_metrics(self, request, queryset):
        for analytics in queryset:
            analytics.calculate_metrics()
        self.message_user(request, f"Recalculated metrics for {queryset.count()} courses")
    recalculate_metrics.short_description = "Recalculate selected courses' analytics"
    
    def export_analytics(self, request, queryset):
        # Implementation for exporting analytics data
        pass
    export_analytics.short_description = "Export selected courses' analytics"

@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'courses_enrolled', 'courses_completed', 
                   'completion_rate', 'overall_engagement', 'last_active')
    list_filter = ('last_active', 'overall_engagement', 'completion_rate')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'last_updated', 'last_calculated')
    actions = ['recalculate_metrics', 'export_analytics']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Learning Progress', {
            'fields': ('courses_enrolled', 'courses_completed', 'current_courses', 'completion_rate')
        }),
        ('Activity Patterns', {
            'fields': ('last_active', 'active_days', 'average_session_duration', 'activity_heatmap')
        }),
        ('Performance Metrics', {
            'fields': ('average_score', 'quiz_completion_rate', 'module_completion_rate', 
                      'performance_by_category')
        }),
        ('Engagement Metrics', {
            'fields': ('overall_engagement', 'course_engagement', 'interaction_frequency')
        }),
        ('Learning Patterns', {
            'fields': ('preferred_learning_times', 'study_duration_patterns', 'content_preferences')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated', 'last_calculated'),
            'classes': ('collapse',)
        })
    )
    
    def recalculate_metrics(self, request, queryset):
        for analytics in queryset:
            analytics.calculate_metrics()
        self.message_user(request, f"Recalculated metrics for {queryset.count()} users")
    recalculate_metrics.short_description = "Recalculate selected users' analytics"
    
    def export_analytics(self, request, queryset):
        # Implementation for exporting analytics data
        pass
    export_analytics.short_description = "Export selected users' analytics"

@admin.register(QuizAnalytics)
class QuizAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'total_attempts', 'unique_attempters', 
                   'average_score', 'pass_rate', 'last_updated')
    list_filter = ('last_updated', 'pass_rate', 'average_score')
    search_fields = ('quiz__title', 'quiz__course__title')
    readonly_fields = ('created_at', 'last_updated', 'last_calculated')
    actions = ['recalculate_metrics', 'export_analytics']
    
    fieldsets = (
        ('Quiz Information', {
            'fields': ('quiz',)
        }),
        ('Question Performance', {
            'fields': ('question_difficulty', 'question_discrimination', 'question_statistics')
        }),
        ('Attempt Patterns', {
            'fields': ('total_attempts', 'unique_attempters', 'average_attempts', 'attempt_distribution')
        }),
        ('Score Analysis', {
            'fields': ('average_score', 'score_distribution', 'pass_rate')
        }),
        ('Time Analysis', {
            'fields': ('average_completion_time', 'time_distribution', 'time_by_question')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated', 'last_calculated'),
            'classes': ('collapse',)
        })
    )
    
    def recalculate_metrics(self, request, queryset):
        for analytics in queryset:
            analytics.calculate_metrics()
        self.message_user(request, f"Recalculated metrics for {queryset.count()} quizzes")
    recalculate_metrics.short_description = "Recalculate selected quizzes' analytics"
    
    def export_analytics(self, request, queryset):
        # Implementation for exporting analytics data
        pass
    export_analytics.short_description = "Export selected quizzes' analytics"

@admin.register(SystemAnalytics)
class SystemAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'active_users', 'concurrent_sessions', 
                   'error_rate', 'cpu_usage', 'memory_usage')
    list_filter = ('timestamp', 'error_rate')
    readonly_fields = ('timestamp', 'last_updated')
    actions = ['recalculate_metrics', 'export_analytics']
    
    fieldsets = (
        ('System Performance', {
            'fields': ('active_users', 'concurrent_sessions', 'average_response_time', 'error_rate')
        }),
        ('Resource Usage', {
            'fields': ('cpu_usage', 'memory_usage', 'database_connections', 'cache_hit_rate')
        }),
        ('Error Tracking', {
            'fields': ('error_counts', 'error_trends', 'critical_errors')
        }),
        ('User Sessions', {
            'fields': ('total_sessions', 'average_session_duration', 'session_distribution')
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'last_updated'),
            'classes': ('collapse',)
        })
    )
    
    def recalculate_metrics(self, request, queryset):
        for analytics in queryset:
            analytics.calculate_metrics()
        self.message_user(request, f"Recalculated metrics for {queryset.count()} system snapshots")
    recalculate_metrics.short_description = "Recalculate selected system analytics"
    
    def export_analytics(self, request, queryset):
        # Implementation for exporting analytics data
        pass
    export_analytics.short_description = "Export selected system analytics"
    
    def has_add_permission(self, request):
        # Only allow viewing, not manual creation
        return False

# Register existing models with enhanced admin interfaces
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'ip_address')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('timestamp',)
    
    def has_add_permission(self, request):
        # Only allow viewing, not manual creation
        return False

@admin.register(ModuleEngagement)
class ModuleEngagementAdmin(admin.ModelAdmin):
    list_display = ('module', 'user', 'view_count', 'time_spent', 'last_viewed', 'completion_date')
    list_filter = ('last_viewed', 'completion_date')
    search_fields = ('module__title', 'user__username')
    readonly_fields = ('last_viewed',)

@admin.register(LearningPathAnalytics)
class LearningPathAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('path_signature', 'user_count', 'success_rate', 
                   'average_completion_time', 'updated_at')
    list_filter = ('success_rate', 'updated_at')
    search_fields = ('path_description',)
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow viewing, not manual creation
        return False