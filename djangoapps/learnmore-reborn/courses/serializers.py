from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Module, Quiz, Enrollment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ModuleSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    prerequisites_info = serializers.SerializerMethodField()
    has_prerequisites = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'course', 'course_title', 'title', 'description', 'order',
            'content_type', 'estimated_time_minutes', 'is_required',
            'completion_criteria', 'content', 'prerequisites_info',
            'has_prerequisites'
        ]
        read_only_fields = ['id', 'course_title', 'prerequisites_info', 'has_prerequisites']
        
    def get_prerequisites_info(self, obj):
        """Return information about module prerequisites"""
        prerequisites = obj.get_prerequisite_modules()
        if not prerequisites.exists():
            return []
            
        return [
            {
                'id': prereq.id,
                'title': prereq.title,
                'content_type': prereq.content_type,
                'order': prereq.order
            }
            for prereq in prerequisites
        ]
        
    def get_has_prerequisites(self, obj):
        """Return whether this module has prerequisites"""
        return obj.has_prerequisites

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'module', 'title', 'description', 'is_survey']
        read_only_fields = ['id']

class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'status',
            'enrollment_type', 'max_students', 'start_date', 'end_date',
            'instructor', 'instructor_name', 'created_at', 'updated_at',
            'enrollment_count', 'is_full', 'is_active', 'enrolled'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() or obj.instructor.username
    
    def get_enrollment_count(self, obj):
        return obj.enrollment_count
    
    def get_is_full(self, obj):
        return obj.is_full
    
    def get_is_active(self, obj):
        return obj.is_active
        
    def get_enrolled(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and getattr(request.user, 'is_authenticated', False):
            return obj.enrollments.filter(user=request.user, status='active').exists()
        return False

class CourseDetailSerializer(CourseSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['modules']

class EnrollmentSerializer(serializers.ModelSerializer):
    user_username = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_username', 'course', 'course_title',
            'status', 'progress', 'enrolled_at', 'completed_at'
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Enrollment.objects.all(),
                fields=['user', 'course'],
                message="A user can only be enrolled once in a course."
            )
        ]
    
    def get_user_username(self, obj):
        return obj.user.username
    
    def get_course_title(self, obj):
        return obj.course.title
        
    def validate_progress(self, value):
        if value < 0:
            raise serializers.ValidationError("Progress cannot be negative.")
        return value