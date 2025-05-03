from django.contrib import admin
from .models import TutorSession, TutorMessage, TutorContextItem, ContentEmbedding

class TutorContextItemInline(admin.TabularInline):
    model = TutorContextItem
    extra = 0
    fields = ('context_type', 'title', 'relevance_score', 'order')

class TutorMessageInline(admin.TabularInline):
    model = TutorMessage
    extra = 0
    fields = ('message_type', 'content', 'tokens_used', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(TutorSession)
class TutorSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'session_type', 'created_at', 'is_active', 'llm_model')
    list_filter = ('session_type', 'is_active', 'llm_model', 'created_at')
    search_fields = ('user__username', 'course__title', 'title')
    date_hierarchy = 'created_at'
    inlines = [TutorContextItemInline, TutorMessageInline]

@admin.register(TutorMessage)
class TutorMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'message_type', 'tokens_used', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('content', 'session__title', 'session__user__username')
    date_hierarchy = 'created_at'

@admin.register(TutorContextItem)
class TutorContextItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'context_type', 'title', 'relevance_score', 'order')
    list_filter = ('context_type', 'created_at')
    search_fields = ('title', 'content', 'session__title')

@admin.register(ContentEmbedding)
class ContentEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('content__title', 'chunk_text')
    date_hierarchy = 'updated_at'