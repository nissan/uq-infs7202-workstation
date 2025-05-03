from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Course, Module, Content, Quiz, Question, Choice,
    CourseEnrollment, ModuleProgress, QuizAttempt
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id', 'slug']

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'question', 'choice_text', 'is_correct']
        read_only_fields = ['id']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'question_text', 'question_type', 'points', 'choices']
        read_only_fields = ['id']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'content', 'title', 'description', 'passing_score',
            'time_limit', 'attempts_allowed', 'shuffle_questions',
            'show_correct_answers', 'is_prerequisite', 'is_pre_check',
            'questions'
        ]
        read_only_fields = ['id']

class ContentSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = Content
        fields = [
            'id', 'module', 'title', 'content_type', 'content',
            'estimated_time', 'order', 'quiz'
        ]
        read_only_fields = ['id']

class ModuleSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description', 'order', 'contents']
        read_only_fields = ['id']

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    instructors = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'category',
            'status', 'max_students', 'start_date', 'end_date',
            'instructors', 'modules'
        ]
        read_only_fields = ['id', 'slug']

class ModuleProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleProgress
        fields = [
            'id', 'enrollment', 'module', 'status', 'progress',
            'started_at', 'completed_at'
        ]
        read_only_fields = ['id']

class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student', 'quiz', 'status', 'score',
            'started_at', 'submitted_at', 'graded_at'
        ]
        read_only_fields = ['id']

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    module_progress = ModuleProgressSerializer(many=True, read_only=True)
    quiz_attempts = QuizAttemptSerializer(many=True, read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'student', 'course', 'status', 'progress',
            'enrolled_at', 'completed_at', 'module_progress',
            'quiz_attempts'
        ]
        read_only_fields = ['id'] 