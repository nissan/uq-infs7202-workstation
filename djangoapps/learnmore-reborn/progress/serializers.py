from rest_framework import serializers
from .models import Progress, ModuleProgress
from courses.models import Module
from courses.serializers import ModuleSerializer, CourseSerializer

class ModuleProgressSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)
    module_content_type = serializers.CharField(source='module.content_type', read_only=True)
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    
    class Meta:
        model = ModuleProgress
        fields = [
            'id', 'module', 'module_title', 'module_content_type', 'course_title',
            'status', 'last_activity', 'duration_seconds', 'completed_at', 
            'content_position'
        ]
        read_only_fields = ['id', 'module_title', 'module_content_type', 'course_title', 'last_activity']
        
class ModuleProgressDetailSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    
    class Meta:
        model = ModuleProgress
        fields = [
            'id', 'module', 'status', 'last_activity', 
            'duration_seconds', 'completed_at', 'content_position'
        ]
        read_only_fields = ['id', 'module', 'last_activity']
        
class ProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    module_progress_count = serializers.SerializerMethodField()
    percent_complete = serializers.FloatField(source='completion_percentage', read_only=True)
    total_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Progress
        fields = [
            'id', 'user', 'username', 'course', 'course_title', 'course_slug',
            'completed_lessons', 'total_lessons', 'last_accessed',
            'total_duration_seconds', 'completion_percentage', 'is_completed',
            'module_progress_count', 'percent_complete', 'total_duration'
        ]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Progress.objects.all(),
                fields=['user', 'course'],
                message="A progress record for this user and course already exists."
            )
        ]
        read_only_fields = ['id', 'username', 'course_title', 'course_slug', 
                           'last_accessed', 'total_duration', 'percent_complete',
                           'module_progress_count']
        
    def get_module_progress_count(self, obj):
        return obj.module_progress.count()
        
    def get_total_duration(self, obj):
        return obj.total_duration
        
    def validate_completed_lessons(self, value):
        if value < 0:
            raise serializers.ValidationError("Completed lessons cannot be negative.")
        return value
        
    def validate_total_lessons(self, value):
        if value < 0:
            raise serializers.ValidationError("Total lessons cannot be negative.")
        return value
        
class ProgressDetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    module_progress = ModuleProgressSerializer(many=True, read_only=True)
    next_module = serializers.SerializerMethodField()
    remaining_modules_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Progress
        fields = [
            'id', 'user', 'course', 'completed_lessons', 'total_lessons', 
            'last_accessed', 'total_duration_seconds', 'completion_percentage', 
            'is_completed', 'module_progress', 'next_module', 'remaining_modules_count'
        ]
        read_only_fields = ['id', 'last_accessed', 'module_progress', 
                           'next_module', 'remaining_modules_count']
    
    def get_next_module(self, obj):
        next_module = obj.next_module
        if next_module:
            return {
                'id': next_module.id,
                'title': next_module.title,
                'order': next_module.order,
                'content_type': next_module.content_type
            }
        return None
        
    def get_remaining_modules_count(self, obj):
        return obj.remaining_modules.count()