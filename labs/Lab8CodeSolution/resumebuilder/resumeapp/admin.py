from django.contrib import admin
from .models import UserDetail, Qualification, WorkExperience

@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'firstname', 'surname', 'mobileno')  # Columns shown in the list view
    search_fields = ('firstname', 'surname', 'user__username')   # Enables search

@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'university', 'user', 'date_completed')
    search_fields = ('title', 'university', 'user__user__username')
    list_filter = ('university', 'date_completed')  # Adds filter sidebar

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'user', 'start_date', 'end_date')
    search_fields = ('job_title', 'company', 'user__user__username')
    list_filter = ('company', 'start_date')