from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course, Module, Quiz, Enrollment,
    Question, MultipleChoiceQuestion, TrueFalseQuestion,
    Choice, QuizAttempt, QuestionResponse
)

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

# Choice serializers
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'order', 'feedback']
        read_only_fields = ['id']

class ChoiceWithCorrectAnswerSerializer(ChoiceSerializer):
    class Meta(ChoiceSerializer.Meta):
        fields = ChoiceSerializer.Meta.fields + ['is_correct']

# Question serializers
class QuestionSerializer(serializers.ModelSerializer):
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'question_type_display', 'order', 'points', 'explanation']
        read_only_fields = ['id', 'question_type_display']

class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['id', 'text', 'question_type', 'order', 'points', 'explanation', 'allow_multiple', 'choices']
        read_only_fields = ['id', 'question_type']
        
class MultipleChoiceQuestionCreateSerializer(MultipleChoiceQuestionSerializer):
    choices = ChoiceWithCorrectAnswerSerializer(many=True)
    
    class Meta(MultipleChoiceQuestionSerializer.Meta):
        fields = MultipleChoiceQuestionSerializer.Meta.fields + ['quiz']
        
    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = MultipleChoiceQuestion.objects.create(**validated_data)
        
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
            
        return question
        
    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', [])
        
        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Get existing choices
        existing_choices = {choice.id: choice for choice in instance.choices.all()}
        
        # Update or create choices
        for choice_data in choices_data:
            choice_id = choice_data.get('id')
            if choice_id and choice_id in existing_choices:
                # Update existing choice
                choice = existing_choices[choice_id]
                for attr, value in choice_data.items():
                    setattr(choice, attr, value)
                choice.save()
            else:
                # Create new choice
                Choice.objects.create(question=instance, **choice_data)
                
        return instance

class TrueFalseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrueFalseQuestion
        fields = ['id', 'text', 'question_type', 'order', 'points', 'explanation', 'correct_answer']
        read_only_fields = ['id', 'question_type']
        
class TrueFalseQuestionCreateSerializer(TrueFalseQuestionSerializer):
    class Meta(TrueFalseQuestionSerializer.Meta):
        fields = TrueFalseQuestionSerializer.Meta.fields + ['quiz']

# Quiz serializers
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'module', 'title', 'description', 'is_survey']
        read_only_fields = ['id']

class QuizListSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'module', 'module_title', 'course_title',
            'time_limit_minutes', 'passing_score', 'question_count', 'is_published',
            'is_survey', 'allow_multiple_attempts', 'max_attempts'
        ]
        read_only_fields = ['id', 'module_title', 'course_title', 'question_count']
        
    def get_question_count(self, obj):
        return obj.questions.count()

class QuizDetailSerializer(QuizListSerializer):
    questions = serializers.SerializerMethodField()
    
    class Meta(QuizListSerializer.Meta):
        fields = QuizListSerializer.Meta.fields + ['instructions', 'randomize_questions', 'questions', 'created_at', 'updated_at']
        
    def get_questions(self, obj):
        # For instructor view - include correct answers
        if self.context.get('show_answers', False):
            questions = []
            
            for question in obj.questions.all().order_by('order'):
                if question.question_type == 'multiple_choice':
                    q = MultipleChoiceQuestionSerializer(question.multiplechoicequestion).data
                    q['choices'] = ChoiceWithCorrectAnswerSerializer(
                        question.multiplechoicequestion.choices.all().order_by('order'), 
                        many=True
                    ).data
                    questions.append(q)
                elif question.question_type == 'true_false':
                    questions.append(TrueFalseQuestionSerializer(question.truefalsequestion).data)
            
            return questions
            
        # For student view - exclude correct answers
        else:
            questions = []
            
            for question in obj.questions.all().order_by('order'):
                if question.question_type == 'multiple_choice':
                    q = QuestionSerializer(question).data
                    q['choices'] = ChoiceSerializer(
                        question.multiplechoicequestion.choices.all().order_by('order'), 
                        many=True
                    ).data
                    questions.append(q)
                elif question.question_type == 'true_false':
                    q = QuestionSerializer(question).data
                    q['is_true_false'] = True
                    questions.append(q)
            
            return questions

# Quiz attempt serializers
class QuestionResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    
    class Meta:
        model = QuestionResponse
        fields = [
            'id', 'question', 'question_text', 'question_type', 'response_data',
            'is_correct', 'points_earned', 'feedback', 'time_spent_seconds'
        ]
        read_only_fields = ['id', 'question_text', 'question_type', 'is_correct', 'points_earned', 'feedback']

class QuizAttemptSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    score_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'user', 'started_at', 'completed_at',
            'status', 'status_display', 'score', 'max_score', 'score_percentage',
            'time_spent_seconds', 'is_passed', 'attempt_number'
        ]
        read_only_fields = ['id', 'quiz_title', 'started_at', 'completed_at', 'status_display',
                           'score', 'max_score', 'score_percentage', 'time_spent_seconds',
                           'is_passed', 'attempt_number']
                           
    def get_score_percentage(self, obj):
        if obj.max_score > 0:
            return round((obj.score / obj.max_score) * 100, 1)
        return 0

class QuizAttemptDetailSerializer(QuizAttemptSerializer):
    responses = QuestionResponseSerializer(many=True, read_only=True)
    
    class Meta(QuizAttemptSerializer.Meta):
        fields = QuizAttemptSerializer.Meta.fields + ['responses']

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
            'enrollment_type', 'course_type', 'max_students', 'start_date', 'end_date',
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