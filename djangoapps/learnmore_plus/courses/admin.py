from django.contrib import admin
from .models import CourseCategory, Course, CourseEnrollment, Module, CourseContent

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'status', 'start_date', 'end_date', 'price', 'enrollment_count', 'is_featured')
    list_filter = ('status', 'category', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('instructor', 'category')
    date_hierarchy = 'created_at'

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'status', 'enrolled_at', 'completed_at', 'progress')
    list_filter = ('status', 'enrolled_at')
    search_fields = ('course__title', 'student__username')
    raw_id_fields = ('course', 'student')
    date_hierarchy = 'enrolled_at'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'order', 'created_at', 'updated_at')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    raw_id_fields = ('course',)
    ordering = ('course', 'order')

@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ('module', 'title', 'content_type', 'order', 'is_required', 'estimated_time')
    list_filter = ('content_type', 'is_required')
    search_fields = ('title', 'content')
    raw_id_fields = ('module',)
    ordering = ('module', 'order')
