from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Module, Quiz, Enrollment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description', 'order']
        read_only_fields = ['id']

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
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'status',
            'enrollment_type', 'max_students', 'start_date', 'end_date',
            'instructor', 'instructor_name', 'created_at', 'updated_at',
            'enrollment_count', 'is_full', 'is_active'
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