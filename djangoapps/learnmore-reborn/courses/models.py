from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Sum

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
    
    COURSE_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('self_paced', 'Self-Paced'),
        ('intensive', 'Intensive')
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
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='standard')
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
    """
    Represents a quiz or survey associated with a module.
    
    Quizzes can have time limits, passing scores, and other settings.
    Surveys are a special type of quiz that don't count toward grades.
    """
    module = models.ForeignKey('Module', related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, help_text='Instructions for taking the quiz')
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, 
                                                     help_text='Time limit in minutes (leave blank for unlimited time)')
    passing_score = models.PositiveIntegerField(default=70, help_text='Passing score percentage (0-100)')
    randomize_questions = models.BooleanField(default=False, help_text='Randomize question order for each attempt')
    allow_multiple_attempts = models.BooleanField(default=True)
    max_attempts = models.PositiveIntegerField(default=3, help_text='Maximum number of attempts allowed (0 for unlimited)')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    is_survey = models.BooleanField(default=False, help_text='If true, this quiz is a survey and does not count toward grades')
    
    class Meta:
        ordering = ['module__order', 'id']
        verbose_name_plural = "quizzes"
        
    def __str__(self):
        return f"{self.module.title} - {self.title}"
        
    def save(self, *args, **kwargs):
        # Update updated_at on save
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        
    def total_points(self):
        """Calculate total possible points for this quiz"""
        return self.questions.aggregate(total=Sum('points'))['total'] or 0
        
    def passing_points(self):
        """Calculate minimum points needed to pass"""
        return int(self.total_points() * (self.passing_score / 100))

class Question(models.Model):
    """
    Base model for quiz questions.
    
    This is the parent class for different question types like
    multiple choice and true/false questions.
    """
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]
    
    quiz = models.ForeignKey('Quiz', related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True, help_text='Explanation shown after the question is answered')
    correct_feedback = models.TextField(blank=True, help_text='Feedback shown when answered correctly')
    incorrect_feedback = models.TextField(blank=True, help_text='Feedback shown when answered incorrectly')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['quiz', 'order']
        
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.text[:50]}..."
    
    def save(self, *args, **kwargs):
        # Update updated_at on save
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        
    def check_answer(self, selected_choices):
        """
        Check if the selected choices are correct.
        
        Args:
            selected_choices: List of choice IDs or single choice ID
            
        Returns:
            tuple: (is_correct, points_earned, feedback)
        """
        raise NotImplementedError("Subclasses must implement check_answer()")

class MultipleChoiceQuestion(Question):
    """
    A question with multiple choice answers.
    
    Can be configured for single correct answer or multiple correct answers.
    """
    allow_multiple = models.BooleanField(default=False, help_text='Allow selecting multiple correct answers')
    
    def save(self, *args, **kwargs):
        self.question_type = 'multiple_choice'
        super().save(*args, **kwargs)
        
    def check_answer(self, selected_choices):
        if not isinstance(selected_choices, list):
            selected_choices = [selected_choices]
            
        # Get all choices for this question
        choices = Choice.objects.filter(question=self)
        correct_choices = choices.filter(is_correct=True)
        
        # For questions with multiple correct answers
        if self.allow_multiple:
            selected_choices_objs = choices.filter(id__in=selected_choices)
            
            # Check if all selected choices are correct and all correct choices are selected
            all_correct = all(c.is_correct for c in selected_choices_objs)
            all_selected = len(selected_choices_objs) == len(correct_choices)
            
            is_correct = all_correct and all_selected
            points_earned = self.points if is_correct else 0
            
        # For questions with a single correct answer
        else:
            if len(selected_choices) != 1:
                is_correct = False
                points_earned = 0
            else:
                choice = choices.filter(id=selected_choices[0]).first()
                is_correct = choice is not None and choice.is_correct
                points_earned = self.points if is_correct else 0
        
        feedback = self.correct_feedback if is_correct else self.incorrect_feedback
        return (is_correct, points_earned, feedback)

class TrueFalseQuestion(Question):
    """
    A question with a true or false answer.
    """
    correct_answer = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        self.question_type = 'true_false'
        super().save(*args, **kwargs)
        
    def check_answer(self, selected_answer):
        if isinstance(selected_answer, list):
            selected_answer = selected_answer[0] if selected_answer else None
            
        if selected_answer in ('true', 'True', True, 1, '1'):
            user_answer = True
        elif selected_answer in ('false', 'False', False, 0, '0'):
            user_answer = False
        else:
            user_answer = None
            
        is_correct = user_answer == self.correct_answer
        points_earned = self.points if is_correct else 0
        feedback = self.correct_feedback if is_correct else self.incorrect_feedback
        
        return (is_correct, points_earned, feedback)

class Choice(models.Model):
    """
    A choice for a multiple choice question.
    """
    question = models.ForeignKey('MultipleChoiceQuestion', related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, help_text='Feedback specific to this choice')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['question', 'order']
        
    def __str__(self):
        return f"{self.question}: {self.text[:30]}... {'(Correct)' if self.is_correct else ''}"

class QuizAttempt(models.Model):
    """
    Represents a user's attempt at a quiz.
    
    Tracks start time, end time, and score.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timed_out', 'Timed Out'),
        ('abandoned', 'Abandoned')
    ]
    
    quiz = models.ForeignKey('Quiz', related_name='attempts', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='quiz_attempts', on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    is_passed = models.BooleanField(default=False)
    attempt_number = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['-started_at']
        unique_together = [['quiz', 'user', 'attempt_number']]
        
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} (Attempt {self.attempt_number})"
    
    def calculate_score(self):
        """Calculate the score based on answers"""
        responses = self.responses.all()
        total_earned = sum(response.points_earned for response in responses)
        question_count = self.quiz.questions.count()
        total_possible = self.quiz.total_points()
        
        self.score = total_earned
        self.max_score = total_possible
        
        # Calculate if passed
        if total_possible > 0:
            percentage = (total_earned / total_possible) * 100
            self.is_passed = percentage >= self.quiz.passing_score
        else:
            self.is_passed = True  # No questions = automatic pass
            
        return self.score, self.max_score
    
    def mark_completed(self, timed_out=False):
        """Mark this attempt as completed"""
        if self.status == 'in_progress':
            self.status = 'timed_out' if timed_out else 'completed'
            self.completed_at = timezone.now()
            
            # Calculate score
            self.calculate_score()
            
            # Calculate time spent
            if self.started_at:
                time_diff = (self.completed_at - self.started_at).total_seconds()
                self.time_spent_seconds = int(time_diff)
                
            self.save()
        
        return self.is_passed

class QuestionResponse(models.Model):
    """
    Represents a user's response to a question.
    """
    attempt = models.ForeignKey('QuizAttempt', related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', related_name='responses', on_delete=models.CASCADE)
    response_data = models.JSONField(default=dict, help_text='JSON data containing the user\'s response')
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveIntegerField(default=0)
    feedback = models.TextField(blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['attempt', 'question__order']
        unique_together = [['attempt', 'question']]
        
    def __str__(self):
        return f"Response to {self.question} by {self.attempt.user.username}"
        
    def check_answer(self):
        """Check if the answer is correct and update fields"""
        if self.question.question_type == 'multiple_choice':
            choices = self.response_data.get('selected_choices', [])
            is_correct, points, feedback = self.question.multiplechoicequestion.check_answer(choices)
        elif self.question.question_type == 'true_false':
            answer = self.response_data.get('selected_answer')
            is_correct, points, feedback = self.question.truefalsequestion.check_answer(answer)
        else:
            is_correct, points, feedback = False, 0, "Unknown question type"
            
        self.is_correct = is_correct
        self.points_earned = points
        self.feedback = feedback
        self.save()
        
        return is_correct, points

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