from django.contrib import admin
from .models import (
    TutorSession, 
    TutorMessage, 
    TutorKnowledgeBase, 
    TutorFeedback,
    TutorConfiguration
)

@admin.register(TutorKnowledgeBase)
class TutorKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'module', 'created_at', 'updated_at')
    list_filter = ('course', 'module', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

@admin.register(TutorSession)
class TutorSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'course', 'module', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'course', 'created_at')
    search_fields = ('title', 'user__username', 'course__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

class TutorMessageInline(admin.TabularInline):
    model = TutorMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('message_type', 'content', 'created_at')

class TutorFeedbackInline(admin.TabularInline):
    model = TutorFeedback
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('user', 'message', 'rating', 'helpful', 'comment', 'created_at')

@admin.register(TutorMessage)
class TutorMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'message_type', 'short_content', 'created_at')
    list_filter = ('message_type', 'created_at', 'session')
    search_fields = ('content', 'session__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'

@admin.register(TutorFeedback)
class TutorFeedbackAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'rating', 'helpful', 'created_at')
    list_filter = ('rating', 'helpful', 'created_at')
    search_fields = ('comment', 'user__username', 'session__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

@admin.register(TutorConfiguration)
class TutorConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_provider', 'model_name', 'is_active', 'updated_at')
    list_filter = ('model_provider', 'is_active')
    search_fields = ('name', 'system_prompt')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active')
        }),
        ('Model Configuration', {
            'fields': ('model_provider', 'model_name', 'temperature', 'max_tokens')
        }),
        ('Prompt Configuration', {
            'fields': ('system_prompt',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )