from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import Course, Module
from datetime import timedelta

User = get_user_model()

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress_records')
    completed_lessons = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    total_duration_seconds = models.PositiveIntegerField(default=0, help_text='Total time spent on course in seconds')
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name_plural = 'Progress Records'

    def __str__(self):
        return f"{self.user.username} progress in {self.course.title}"
    
    def update_completion_percentage(self):
        """Calculate and update the completion percentage based on module progress"""
        # Get all module progress records for this user and course
        module_progress_records = ModuleProgress.objects.filter(
            progress=self
        )
        
        # Count modules with complete status
        completed_modules = module_progress_records.filter(
            status='completed'
        ).count()
        
        # Get total modules count for this course
        total_modules = self.course.modules.count()
        
        # Update completed_lessons field
        self.completed_lessons = completed_modules
        self.total_lessons = total_modules
        
        if total_modules > 0:
            self.completion_percentage = (completed_modules / total_modules) * 100
        else:
            self.completion_percentage = 0.0
            
        # Set completed if all modules are done
        self.is_completed = (completed_modules == total_modules) and (total_modules > 0)
        
        self.save(update_fields=['completed_lessons', 'total_lessons', 
                                'completion_percentage', 'is_completed'])
    
    def add_duration(self, seconds):
        """Add time spent to the total duration"""
        self.total_duration_seconds += seconds
        self.save(update_fields=['total_duration_seconds'])
    
    @property
    def total_duration(self):
        """Return the formatted total duration"""
        return str(timedelta(seconds=self.total_duration_seconds))
        
    @property
    def remaining_modules(self):
        """Return a queryset of modules that are not yet completed"""
        completed_module_ids = ModuleProgress.objects.filter(
            progress=self, 
            status='completed'
        ).values_list('module_id', flat=True)
        
        return self.course.modules.exclude(id__in=completed_module_ids)
    
    @property
    def next_module(self):
        """Return the next module that should be completed"""
        incomplete_modules = self.remaining_modules.order_by('order')
        return incomplete_modules.first() if incomplete_modules.exists() else None


class ModuleProgress(models.Model):
    """
    Tracks user progress at the module level.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    progress = models.ForeignKey(Progress, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    last_activity = models.DateTimeField(auto_now=True)
    duration_seconds = models.PositiveIntegerField(default=0, help_text='Time spent on this module in seconds')
    completed_at = models.DateTimeField(null=True, blank=True)
    content_position = models.JSONField(default=dict, help_text='Stores position in module content (e.g. video timestamp)')
    
    class Meta:
        unique_together = ('progress', 'module')
        verbose_name_plural = 'Module Progress'
    
    def __str__(self):
        return f"{self.progress.user.username} - {self.module.title} - {self.get_status_display()}"
    
    def mark_completed(self):
        """Mark this module as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Update the parent progress record
        self.progress.update_completion_percentage()
    
    def add_duration(self, seconds):
        """Add time spent to the duration"""
        self.duration_seconds += seconds
        self.save(update_fields=['duration_seconds'])
        
        # Also update the parent progress record
        self.progress.add_duration(seconds)
    
    def update_content_position(self, position_data):
        """
        Update the content position with the provided data.
        
        Args:
            position_data (dict): Position data to store (e.g. {'video_time': 120, 'page': 3})
        """
        self.content_position.update(position_data)
        self.save(update_fields=['content_position'])
        
        # If not already in progress, mark as in progress
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.save(update_fields=['status'])