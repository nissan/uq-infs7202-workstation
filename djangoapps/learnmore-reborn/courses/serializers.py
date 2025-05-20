from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course, Module, Quiz, Enrollment,
    Question, MultipleChoiceQuestion, TrueFalseQuestion, EssayQuestion,
    Choice, QuizAttempt, QuestionResponse, QuizPrerequisite,
    QuestionAnalytics, QuizAnalytics
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
    has_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Choice
        fields = ['id', 'text', 'order', 'feedback', 'image', 'image_alt_text', 'has_image']
        read_only_fields = ['id', 'has_image']
    
    def get_has_image(self, obj):
        return bool(obj.image)

class ChoiceWithCorrectAnswerSerializer(ChoiceSerializer):
    class Meta(ChoiceSerializer.Meta):
        fields = ChoiceSerializer.Meta.fields + [
            'is_correct', 'points_value', 'is_neutral'
        ]

# Question serializers
class QuestionSerializer(serializers.ModelSerializer):
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)
    has_image = serializers.SerializerMethodField()
    has_external_media = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'text', 'question_type', 'question_type_display', 
            'order', 'points', 'explanation', 'image', 'image_alt_text',
            'external_media_url', 'media_caption', 'has_image', 'has_external_media'
        ]
        read_only_fields = ['id', 'question_type_display', 'has_image', 'has_external_media']
    
    def get_has_image(self, obj):
        return bool(obj.image)
    
    def get_has_external_media(self, obj):
        return bool(obj.external_media_url)

class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = MultipleChoiceQuestion
        fields = [
            'id', 'text', 'question_type', 'order', 'points', 'explanation', 
            'allow_multiple', 'use_partial_credit', 'minimum_score', 'choices',
            'image', 'image_alt_text', 'external_media_url', 'media_caption'
        ]
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

class EssayQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayQuestion
        fields = [
            'id', 'text', 'question_type', 'order', 'points', 'explanation',
            'min_word_count', 'max_word_count', 'rubric', 'allow_attachments'
        ]
        read_only_fields = ['id', 'question_type']

class EssayQuestionCreateSerializer(EssayQuestionSerializer):
    class Meta(EssayQuestionSerializer.Meta):
        fields = EssayQuestionSerializer.Meta.fields + ['quiz', 'example_answer']

class EssayResponseSerializer(serializers.Serializer):
    essay_text = serializers.CharField(allow_blank=True)
    attachments = serializers.ListField(child=serializers.FileField(), required=False)

class EssayGradingSerializer(serializers.Serializer):
    points_awarded = serializers.IntegerField(min_value=0)
    feedback = serializers.CharField(allow_blank=True)

# Quiz prerequisite serializers
class QuizPrerequisiteSerializer(serializers.ModelSerializer):
    prerequisite_title = serializers.CharField(source='prerequisite_quiz.title', read_only=True)
    
    class Meta:
        model = QuizPrerequisite
        fields = [
            'id', 'quiz', 'prerequisite_quiz', 'prerequisite_title',
            'required_passing', 'bypass_for_instructors'
        ]
        read_only_fields = ['id', 'prerequisite_title']

# Quiz serializers
class QuizSerializer(serializers.ModelSerializer):
    has_prerequisites = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'module', 'title', 'description', 'is_survey',
            'has_prerequisites'
        ]
        read_only_fields = ['id', 'has_prerequisites']
    
    def get_has_prerequisites(self, obj):
        return obj.has_prerequisites()

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
    prerequisites = serializers.SerializerMethodField()
    prerequisites_satisfied = serializers.SerializerMethodField()
    
    class Meta(QuizListSerializer.Meta):
        fields = QuizListSerializer.Meta.fields + [
            'instructions', 'randomize_questions', 'randomize_choices',
            'show_feedback_after', 'grace_period_minutes', 'allow_time_extension',
            'access_code', 'available_from', 'available_until',
            'questions', 'prerequisites', 'prerequisites_satisfied',
            'created_at', 'updated_at'
        ]
    
    def get_prerequisites(self, obj):
        # Return prerequisite information
        prereqs = obj.prerequisites.all()
        if not prereqs.exists():
            return []
            
        return QuizPrerequisiteSerializer(prereqs, many=True).data
        
    def get_prerequisites_satisfied(self, obj):
        # Check if current user has satisfied prerequisites
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
            
        return obj.are_prerequisites_satisfied(request.user)
        
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
                elif question.question_type == 'essay':
                    # For instructors, include the example answer and full rubric
                    questions.append(EssayQuestionCreateSerializer(question.essayquestion).data)
            
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
                elif question.question_type == 'essay':
                    q = QuestionSerializer(question).data
                    q['is_essay'] = True
                    q['min_word_count'] = question.essayquestion.min_word_count
                    q['max_word_count'] = question.essayquestion.max_word_count
                    q['allow_attachments'] = question.essayquestion.allow_attachments
                    questions.append(q)
            
            return questions

# Quiz attempt serializers
class QuestionResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    pending_grading = serializers.SerializerMethodField()
    
    class Meta:
        model = QuestionResponse
        fields = [
            'id', 'question', 'question_text', 'question_type', 'response_data',
            'is_correct', 'points_earned', 'feedback', 'time_spent_seconds',
            'pending_grading', 'instructor_comment', 'graded_at'
        ]
        read_only_fields = [
            'id', 'question_text', 'question_type', 'is_correct', 'points_earned', 
            'feedback', 'pending_grading', 'instructor_comment', 'graded_at'
        ]
    
    def get_pending_grading(self, obj):
        """Check if this is an essay question that needs grading"""
        return (obj.question.question_type == 'essay' and 
                obj.graded_at is None and 
                'essay_text' in obj.response_data)

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

# Analytics serializers
class QuestionAnalyticsSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    
    class Meta:
        model = QuestionAnalytics
        fields = [
            'id', 'question', 'question_text', 'question_type',
            'total_attempts', 'correct_attempts', 'incorrect_attempts',
            'avg_time_seconds', 'difficulty_index', 'discrimination_index',
            'choice_distribution', 'last_attempted_at', 'last_calculated_at'
        ]
        read_only_fields = fields

class QuizAnalyticsSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    passing_rate = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAnalytics
        fields = [
            'id', 'quiz', 'quiz_title', 'total_attempts', 'completed_attempts',
            'passing_attempts', 'passing_rate', 'completion_rate',
            'avg_completion_time', 'avg_score', 'lowest_scoring_questions',
            'highest_scoring_questions', 'score_distribution',
            'last_attempted_at', 'last_calculated_at'
        ]
        read_only_fields = fields
    
    def get_passing_rate(self, obj):
        return (obj.passing_attempts / obj.completed_attempts * 100) if obj.completed_attempts > 0 else 0
    
    def get_completion_rate(self, obj):
        return (obj.completed_attempts / obj.total_attempts * 100) if obj.total_attempts > 0 else 0

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