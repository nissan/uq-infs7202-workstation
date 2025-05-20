from django.contrib import admin
from .models import (
    UserActivity,
    CourseAnalyticsSummary,
    ModuleEngagement,
    LearningPathAnalytics
)

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'ip_address')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'activity_type', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

@admin.register(CourseAnalyticsSummary)
class CourseAnalyticsSummaryAdmin(admin.ModelAdmin):
    list_display = ('course', 'total_enrollments', 'active_learners', 
                    'completion_rate', 'average_rating', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('course__title',)
    readonly_fields = ('last_updated',)
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    actions = ['recalculate_analytics']
    
    def recalculate_analytics(self, request, queryset):
        for analytics in queryset:
            analytics.recalculate()
        self.message_user(request, f"Recalculated analytics for {queryset.count()} courses.")
    recalculate_analytics.short_description = "Recalculate analytics for selected courses"

@admin.register(ModuleEngagement)
class ModuleEngagementAdmin(admin.ModelAdmin):
    list_display = ('module', 'user', 'view_count', 'time_spent', 
                    'last_viewed', 'completion_date')
    list_filter = ('last_viewed', 'completion_date')
    search_fields = ('module__title', 'user__username')
    date_hierarchy = 'last_viewed'
    readonly_fields = ('last_viewed',)

@admin.register(LearningPathAnalytics)
class LearningPathAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('path_signature', 'path_description', 'user_count', 
                   'success_rate', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('path_description',)
    date_hierarchy = 'updated_at'
    readonly_fields = ('created_at', 'updated_at')