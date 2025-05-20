from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()

class Course(models.Model):
    """
    Represents a course in the learning platform.
    
    The Course model automatically generates and updates its slug based on the title.
    Whenever a course title is changed, the slug will be automatically updated to match.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ]
    
    ENROLLMENT_TYPE_CHOICES = [
        ('open', 'Open'),
        ('restricted', 'Restricted')
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    
    # Catalog-specific fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    enrollment_type = models.CharField(max_length=20, choices=ENROLLMENT_TYPE_CHOICES, default='open')
    max_students = models.PositiveIntegerField(default=0, help_text='Maximum enrollment capacity (0 for unlimited)')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug from title.
        
        The slug is always generated from the title, ensuring that it stays
        in sync when the title is updated.
        """
        # Always generate the slug from the title
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        today = timezone.now().date()
        if self.status != 'published':
            return False
        if self.start_date and self.end_date:
            return self.start_date <= today <= self.end_date
        return self.status == 'published'
    
    @property
    def enrollment_count(self):
        return self.enrollments.filter(status='active').count()
    
    @property
    def is_full(self):
        return self.max_students > 0 and self.enrollment_count >= self.max_students
    
class Module(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('video', 'Video'),
        ('interactive', 'Interactive'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('mixed', 'Mixed Content'),
    ]
    
    course = models.ForeignKey('Course', related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    # Learning activity related fields
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text')
    estimated_time_minutes = models.PositiveIntegerField(default=30, help_text='Estimated time to complete in minutes')
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_for')
    is_required = models.BooleanField(default=True, help_text='Is this module required for course completion')
    completion_criteria = models.JSONField(default=dict, blank=True, help_text='Criteria for marking as complete (e.g. {"video_watched": true, "quiz_completed": true})')
    content = models.TextField(blank=True, help_text='Module content in markdown format')
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
        
    def get_prerequisite_modules(self):
        """Return a queryset of all prerequisite modules"""
        return self.prerequisites.all().order_by('order')
        
    @property
    def has_prerequisites(self):
        """Return True if this module has prerequisites"""
        return self.prerequisites.exists()
        
    @property
    def is_accessible(self, user):
        """
        Check if the module is accessible to the user.
        A module is accessible if:
        1. It has no prerequisites, or
        2. All its prerequisites have been completed by the user
        """
        if not self.has_prerequisites:
            return True
            
        # Get the progress record for the user and course
        from progress.models import Progress, ModuleProgress
        try:
            progress = Progress.objects.get(user=user, course=self.course)
        except Progress.DoesNotExist:
            return False
            
        # Check if all prerequisites are completed
        prereq_modules = self.get_prerequisite_modules()
        completed_prereqs = ModuleProgress.objects.filter(
            progress=progress,
            module__in=prereq_modules,
            status='completed'
        ).count()
        
        return completed_prereqs == prereq_modules.count()

class Quiz(models.Model):
    module = models.ForeignKey('Module', related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_survey = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.PositiveIntegerField(default=0) 
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'course')
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
