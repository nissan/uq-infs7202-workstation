from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Course, Module, Quiz, Enrollment,
    Question, MultipleChoiceQuestion, TrueFalseQuestion,
    Choice, QuizAttempt, QuestionResponse
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'status', 'enrollment_type', 'enrollment_count', 'is_full', 'is_active')
    list_filter = ('status', 'enrollment_type', 'instructor')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'instructor')
        }),
        ('Catalog Settings', {
            'fields': ('status', 'enrollment_type', 'max_students', 'start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'content_type')
    list_filter = ('course', 'content_type')
    search_fields = ('title', 'description')

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    min_num = 2

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'points', 'order')
    readonly_fields = ('question_type',)
    show_change_link = True
    can_delete = False

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'get_course', 'is_published', 'is_survey', 
                    'time_limit_minutes', 'passing_score', 'get_question_count')
    list_filter = ('module__course', 'is_published', 'is_survey')
    search_fields = ('title', 'module__title', 'module__course__title')
    fieldsets = (
        (None, {
            'fields': ('module', 'title', 'description', 'instructions', 'is_published', 'is_survey')
        }),
        ('Settings', {
            'fields': ('time_limit_minutes', 'passing_score', 'randomize_questions',
                      'allow_multiple_attempts', 'max_attempts')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [QuestionInline]
    
    def get_course(self, obj):
        return obj.module.course.title
    get_course.short_description = 'Course'
    
    def get_question_count(self, obj):
        return obj.questions.count()
    get_question_count.short_description = 'Questions'

@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type', 'points', 'get_quiz_module', 'allow_multiple')
    list_filter = ('quiz__module__course', 'quiz', 'allow_multiple')
    search_fields = ('text', 'quiz__title')
    inlines = [ChoiceInline]
    
    def get_quiz_module(self, obj):
        return obj.quiz.module.title
    get_quiz_module.short_description = 'Module'

@admin.register(TrueFalseQuestion)
class TrueFalseQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type', 'points', 'get_quiz_module', 'correct_answer')
    list_filter = ('quiz__module__course', 'quiz', 'correct_answer')
    search_fields = ('text', 'quiz__title')
    
    def get_quiz_module(self, obj):
        return obj.quiz.module.title
    get_quiz_module.short_description = 'Module'

class QuestionResponseInline(admin.TabularInline):
    model = QuestionResponse
    extra = 0
    readonly_fields = ('question', 'response_data', 'is_correct', 'points_earned', 'feedback', 'time_spent_seconds')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'get_course', 'attempt_number', 
                    'score_display', 'status', 'is_passed', 'started_at')
    list_filter = ('quiz__module__course', 'quiz', 'status', 'is_passed')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('user', 'quiz', 'started_at', 'completed_at', 'status', 
                       'score', 'max_score', 'time_spent_seconds', 'is_passed',
                       'attempt_number')
    inlines = [QuestionResponseInline]
    
    def get_course(self, obj):
        return obj.quiz.module.course.title
    get_course.short_description = 'Course'
    
    def score_display(self, obj):
        if obj.max_score > 0:
            percentage = (obj.score / obj.max_score * 100)
        else:
            percentage = 0
        color = 'green' if obj.is_passed else 'red'
        return format_html('<span style="color: {};">{}/{} ({}%)</span>', 
                          color, obj.score, obj.max_score, round(percentage, 1))
    score_display.short_description = 'Score'
    
    def has_add_permission(self, request):
        return False

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'progress', 'enrolled_at')
    list_filter = ('status', 'course')
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('enrolled_at', 'completed_at')
    date_hierarchy = 'enrolled_at'