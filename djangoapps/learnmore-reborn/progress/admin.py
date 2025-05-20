from django.contrib import admin
from .models import Progress, ModuleProgress

class ModuleProgressInline(admin.TabularInline):
    model = ModuleProgress
    extra = 0
    readonly_fields = ['last_activity']
    fields = ['module', 'status', 'duration_seconds', 'last_activity', 'completed_at', 'content_position']

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'completed_lessons', 'total_lessons', 
                   'completion_percentage', 'is_completed', 'last_accessed']
    list_filter = ['is_completed', 'course', 'user']
    search_fields = ['user__username', 'user__email', 'course__title']
    readonly_fields = ['last_accessed', 'total_duration']
    inlines = [ModuleProgressInline]
    fieldsets = (
        (None, {
            'fields': ('user', 'course')
        }),
        ('Progress Overview', {
            'fields': ('completed_lessons', 'total_lessons', 'completion_percentage', 
                      'is_completed', 'total_duration_seconds', 'total_duration')
        }),
        ('Timestamps', {
            'fields': ('last_accessed',)
        }),
    )

@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'module', 'status', 'duration_seconds', 'last_activity', 'completed_at']
    list_filter = ['status', 'module__course', 'module']
    search_fields = ['progress__user__username', 'progress__user__email', 'module__title']
    readonly_fields = ['last_activity']
    
    def get_user(self, obj):
        return obj.progress.user
    get_user.short_description = 'User'
    get_user.admin_order_field = 'progress__user__username'
