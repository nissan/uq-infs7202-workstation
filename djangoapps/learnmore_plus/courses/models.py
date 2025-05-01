from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

User = get_user_model()

class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(
        max_length=50,
        help_text="Heroicon name (e.g., 'academic-cap', 'code', 'beaker')",
        default='academic-cap'
    )
    color = models.CharField(
        max_length=7,
        validators=[RegexValidator(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')],
        help_text="Hex color code (e.g., '#3B82F6')",
        default='#3B82F6'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Course Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def courses_count(self):
        return self.courses.count()

    @property
    def active_courses_count(self):
        return self.courses.filter(status='published').count()

class Course(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    LEVEL_METADATA = {
        'beginner': {
            'icon': 'sparkles',
            'color': '#10B981',  # Emerald 500
            'description': 'Perfect for those just starting out. No prior experience needed.',
        },
        'intermediate': {
            'icon': 'fire',
            'color': '#F59E0B',  # Amber 500
            'description': 'For learners with basic knowledge seeking to expand their skills.',
        },
        'advanced': {
            'icon': 'star',
            'color': '#EF4444',  # Red 500
            'description': 'Deep dive into complex topics. Prior experience required.',
        }
    }

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_teaching')
    students = models.ManyToManyField(User, through='CourseEnrollment', related_name='courses_enrolled')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_students = models.PositiveIntegerField(default=0)  # 0 means unlimited
    is_featured = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        now = timezone.now()
        if self.start_date and self.end_date:
            return self.start_date <= now <= self.end_date
        return self.status == 'published'

    @property
    def enrollment_count(self):
        return self.students.count()

    @property
    def is_full(self):
        if self.max_students == 0:
            return False
        return self.enrollment_count >= self.max_students

    @property
    def is_free(self):
        return self.price == 0

    @property
    def level_metadata(self):
        return self.LEVEL_METADATA.get(self.level, {})

    @property
    def level_icon(self):
        return self.level_metadata.get('icon', 'academic-cap')

    @property
    def level_color(self):
        return self.level_metadata.get('color', '#3B82F6')

    @property
    def level_description(self):
        return self.level_metadata.get('description', '')

class CourseEnrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress = models.PositiveIntegerField(default=0)  # Percentage of completion

    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class Enrollment(models.Model):
    """Model representing a student's enrollment in a course"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress = models.IntegerField(default=0)  # Overall progress percentage
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress = 100
        self.save()

class ModuleProgress(models.Model):
    """Model tracking a student's progress in a specific module"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='progress_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress = models.IntegerField(default=0)  # Progress percentage for this module
    time_spent = models.IntegerField(default=0)  # Time spent in minutes
    last_accessed = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['enrollment', 'module']
        ordering = ['module__order']

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.module.title}"

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress = 100
        self.save()

        # Update enrollment progress
        total_modules = self.enrollment.course.modules.count()
        completed_modules = self.enrollment.module_progress.filter(status='completed').count()
        self.enrollment.progress = int((completed_modules / total_modules) * 100)
        
        if self.enrollment.progress == 100:
            self.enrollment.mark_completed()
        else:
            self.enrollment.status = 'in_progress'
            self.enrollment.save()

class Module(models.Model):
    """Model representing a course module"""
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    estimated_time = models.PositiveIntegerField(help_text="Estimated time in minutes")
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"

class CourseContent(models.Model):
    CONTENT_TYPES = [
        ('text', 'Text'),
        ('video', 'Video'),
        ('file', 'File'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content = models.TextField()
    file = models.FileField(upload_to='course_contents/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_required = models.BooleanField(default=True)
    estimated_time = models.PositiveIntegerField(default=0)  # in minutes

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['module', 'order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

class Quiz(models.Model):
    """Model representing a quiz in a course"""
    content = models.OneToOneField(CourseContent, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_pre_check = models.BooleanField(
        default=False,
        help_text="If True, this is a pre-requisite survey with no right/wrong answers"
    )
    passing_score = models.PositiveIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum score required to pass (0-100)"
    )
    time_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time limit in minutes (leave empty for no limit)"
    )
    attempts_allowed = models.PositiveIntegerField(
        default=3,
        help_text="Number of attempts allowed (0 for unlimited)"
    )
    shuffle_questions = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.content.module.title} - {self.title}"

class Question(models.Model):
    """Model representing a question in a quiz"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"

class Choice(models.Model):
    """Model representing a choice for a multiple choice question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.question.question_text[:50]} - Choice {self.order}"

class QuizAttempt(models.Model):
    """Model representing a student's attempt at a quiz"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.PositiveIntegerField(null=True, blank=True, help_text="Time taken in minutes")

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - Attempt {self.id}"

    @property
    def is_passed(self):
        if self.score is None:
            return False
        return self.score >= self.quiz.passing_score

    @property
    def remaining_attempts(self):
        if self.quiz.attempts_allowed == 0:
            return float('inf')
        attempts_made = self.quiz.attempts.filter(student=self.student).count()
        return max(0, self.quiz.attempts_allowed - attempts_made)

class Answer(models.Model):
    """Model representing a student's answer to a question"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(null=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['question__order', 'created_at']
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.question_text[:50]}"
