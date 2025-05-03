from django.contrib import admin
from .models import Category, Course, Module, Content, Quiz, Question, CourseEnrollment, ModuleProgress

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'coordinator', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('coordinator', 'instructors')
    filter_horizontal = ('instructors',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    ordering = ('course', 'order')

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'content_type', 'order')
    list_filter = ('module__course', 'content_type')
    search_fields = ('title', 'content')
    ordering = ('module', 'order')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'passing_score')
    list_filter = ('content__module__course',)
    search_fields = ('title', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'question_type')
    list_filter = ('quiz__content__module__course', 'question_type')
    search_fields = ('question_text',)

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'enrolled_at', 'completed_at')
    list_filter = ('status', 'course')
    search_fields = ('student__username', 'course__title')
    raw_id_fields = ('student', 'course')

@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'module', 'status', 'progress')
    list_filter = ('status', 'module__course')
    search_fields = ('enrollment__student__username', 'module__title')
    raw_id_fields = ('enrollment', 'module')
