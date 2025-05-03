from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructors = models.ManyToManyField(User, related_name='teaching_courses')
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='coordinated_courses')
    cover_image = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    max_students = models.PositiveIntegerField(default=100, help_text='Maximum number of students allowed to enroll')
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('publish_course', 'Can publish course'),
            ('archive_course', 'Can archive course'),
            ('manage_courses', 'Can manage courses'),
            ('manage_enrollments', 'Can manage enrollments'),
            ('create_courses', 'Can create courses'),
            ('manage_modules', 'Can manage modules'),
            ('view_courses', 'Can view courses'),
            ('take_quizzes', 'Can take quizzes'),
        ]

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'published' and self.start_date <= today <= self.end_date

    @property
    def enrollment_count(self):
        return self.enrollments.filter(status='active').count()

    @property
    def is_full(self):
        return self.max_students > 0 and self.enrollment_count >= self.max_students

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Content(models.Model):
    CONTENT_TYPES = [
        ('text', 'Text'),
        ('video', 'Video'),
        ('file', 'File'),
        ('quiz', 'Quiz'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content = models.TextField()
    order = models.PositiveIntegerField()
    estimated_time = models.PositiveIntegerField(help_text='Estimated time in minutes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['module', 'order']
        unique_together = ['module', 'order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

class Quiz(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70)
    time_limit = models.PositiveIntegerField(help_text='Time limit in minutes', null=True, blank=True)
    attempts_allowed = models.PositiveIntegerField(default=3)
    shuffle_questions = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    is_prerequisite = models.BooleanField(default=False, help_text='Whether this quiz is a prerequisite for the module')
    is_pre_check = models.BooleanField(default=False, help_text='If true, this quiz is a survey/pre-check and not graded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quiz.title} - {self.question_text[:50]}"

class CourseEnrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.PositiveIntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class ModuleProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('enrollment', 'module')

    def __str__(self):
        return f"{self.enrollment} - {self.module.title}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question.question_text[:30]} - {self.choice_text}"

class QuizAttempt(models.Model):
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
    time_spent = models.IntegerField(default=0, help_text="Total time spent in seconds")
    last_activity = models.DateTimeField(auto_now=True, help_text="Last activity timestamp")

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_spent = models.IntegerField(default=0, help_text="Time spent on this question in seconds")
    last_modified = models.DateTimeField(auto_now=True, help_text="Last modification timestamp")

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"{self.attempt} - {self.question.question_text[:30]}"
