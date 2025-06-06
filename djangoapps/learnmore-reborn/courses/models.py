from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Sum, F, Q

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
    
    # QR code related fields
    qr_enabled = models.BooleanField(default=False, help_text='Enable QR code access for this course')
    
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
    
    # QR access level choices
    QR_ACCESS_CHOICES = [
        ('disabled', 'Disabled'),
        ('public', 'Public Access'),
        ('enrolled', 'Enrolled Students Only'),
        ('instructor', 'Instructors Only')
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
    
    # QR code related fields
    qr_access = models.CharField(max_length=20, choices=QR_ACCESS_CHOICES, default='disabled', 
                              help_text='QR code access level for this module')
    
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
    Quizzes can have prerequisites, which must be completed before the quiz can be taken.
    """
    module = models.ForeignKey('Module', related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, help_text='Instructions for taking the quiz')
    
    # Time limit settings
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, 
                                                     help_text='Time limit in minutes (leave blank for unlimited time)')
    grace_period_minutes = models.PositiveIntegerField(default=2, 
                                                       help_text='Grace period in minutes after time limit expires')
    allow_time_extension = models.BooleanField(default=False, 
                                              help_text='Whether instructors can grant time extensions')
    
    # Scoring settings
    passing_score = models.PositiveIntegerField(default=70, help_text='Passing score percentage (0-100)')
    
    # Randomization settings
    randomize_questions = models.BooleanField(default=False, help_text='Randomize question order for each attempt')
    randomize_choices = models.BooleanField(default=False, help_text='Randomize choice order for multiple choice questions')
    
    # QR code related fields
    qr_tracking = models.BooleanField(default=False, help_text='Track QR code scans for quiz access')
    
    # Attempt settings
    allow_multiple_attempts = models.BooleanField(default=True)
    max_attempts = models.PositiveIntegerField(default=3, help_text='Maximum number of attempts allowed (0 for unlimited)')
    
    # Feedback settings
    show_feedback_after = models.CharField(max_length=20, 
                                          choices=[
                                              ('each_question', 'After each question'),
                                              ('completion', 'After completion'),
                                              ('due_date', 'After due date'),
                                              ('never', 'Never')
                                          ],
                                          default='completion',
                                          help_text='When to show feedback to students')
    
    # Enhanced feedback fields
    general_feedback = models.TextField(blank=True, 
                                       help_text='General feedback shown to all students after quiz completion')
    
    # Score-based conditional feedback fields, stored as JSONField
    conditional_feedback = models.JSONField(default=dict, blank=True,
                                          help_text='Feedback shown based on score ranges (e.g., {"0-59": "...", "60-79": "...", "80-100": "..."})')
    
    feedback_delay_minutes = models.PositiveIntegerField(default=0,
                                                       help_text='Delay in minutes before feedback is shown (0 for immediate)')
    
    # Access control
    access_code = models.CharField(max_length=50, blank=True, 
                                  help_text='Optional access code required to take this quiz')
    available_from = models.DateTimeField(null=True, blank=True, 
                                         help_text='When this quiz becomes available')
    available_until = models.DateTimeField(null=True, blank=True, 
                                          help_text='When this quiz is no longer available')
    
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
    
    def get_prerequisites(self):
        """Return all prerequisite quizzes for this quiz"""
        return Quiz.objects.filter(
            required_for__quiz=self
        ).order_by('module__order')
        
    def get_survey_prerequisites(self):
        """Return all survey prerequisite quizzes for this quiz"""
        return Quiz.objects.filter(
            required_for__quiz=self,
            is_survey=True
        ).order_by('module__order')
        
    def has_prerequisites(self):
        """Check if this quiz has any prerequisites"""
        return self.prerequisites.exists()
        
    def has_survey_prerequisites(self):
        """Check if this quiz has any survey prerequisites"""
        return self.prerequisites.filter(prerequisite_quiz__is_survey=True).exists()
        
    def get_pending_survey_prerequisites(self, user):
        """
        Get all survey prerequisites that are not satisfied by the user.
        
        Args:
            user: The user to check
            
        Returns:
            QuerySet: All survey prerequisites that need to be completed
        """
        # Get all survey prerequisites
        prereqs = self.prerequisites.filter(prerequisite_quiz__is_survey=True)
        
        # Filter out the ones that are already satisfied
        pending_prereqs = []
        for prereq in prereqs:
            if not prereq.is_satisfied_by_user(user):
                pending_prereqs.append(prereq.id)
                
        return QuizPrerequisite.objects.filter(id__in=pending_prereqs)
        
    def are_prerequisites_satisfied(self, user):
        """
        Check if all prerequisites for this quiz are satisfied by the user.
        
        Args:
            user: The user to check
            
        Returns:
            bool: True if all prerequisites are satisfied, False otherwise
        """
        # Get all prerequisites for this quiz
        prereqs = self.prerequisites.all()
        
        # No prerequisites means all are satisfied
        if not prereqs.exists():
            return True
            
        # Check each prerequisite
        for prereq in prereqs:
            if not prereq.is_satisfied_by_user(user):
                return False
                
        return True

class Question(models.Model):
    """
    Base model for quiz questions.
    
    This is the parent class for different question types like
    multiple choice and true/false questions.
    """
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('essay', 'Essay'),
    ]
    
    quiz = models.ForeignKey('Quiz', related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True, help_text='Explanation shown after the question is answered')
    correct_feedback = models.TextField(blank=True, help_text='Feedback shown when answered correctly')
    incorrect_feedback = models.TextField(blank=True, help_text='Feedback shown when answered incorrectly')
    
    # Media fields
    image = models.FileField(upload_to='questions/%Y/%m/', blank=True, null=True, 
                            help_text='Image to display with the question')
    image_alt_text = models.CharField(max_length=255, blank=True, 
                                     help_text='Alternative text for the image (for accessibility)')
    external_media_url = models.URLField(blank=True, 
                                        help_text='URL to external media like videos or diagrams')
    media_caption = models.CharField(max_length=255, blank=True, 
                                    help_text='Caption for the media content')
    
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
    Supports partial credit scoring and score normalization.
    """
    NORMALIZATION_METHODS = [
        ('none', 'No Normalization'),
        ('zscore', 'Z-Score Normalization'),
        ('minmax', 'Min-Max Scaling'),
        ('percentile', 'Percentile Ranking'),
        ('custom', 'Custom Normalization')
    ]
    
    allow_multiple = models.BooleanField(default=False, help_text='Allow selecting multiple correct answers')
    use_partial_credit = models.BooleanField(default=False, help_text='Use partial credit scoring')
    minimum_score = models.IntegerField(default=0, help_text='Minimum score even with negative points')
    normalization_method = models.CharField(max_length=20, choices=NORMALIZATION_METHODS, default='none',
                                         help_text='Method to normalize scores across questions')
    normalization_parameters = models.JSONField(default=dict, blank=True,
                                              help_text='Parameters for the normalization method (e.g., {"mean": 0.5, "std_dev": 0.1})')
    
    def save(self, *args, **kwargs):
        self.question_type = 'multiple_choice'
        super().save(*args, **kwargs)
        
    def check_answer(self, selected_choices):
        if not isinstance(selected_choices, list):
            selected_choices = [selected_choices]
            
        # Get all choices for this question
        choices = Choice.objects.filter(question=self)
        correct_choices = choices.filter(is_correct=True)
        
        # If using partial credit scoring
        if self.use_partial_credit:
            # Get all selected choices objects
            selected_choices_objs = choices.filter(id__in=selected_choices)
            
            # Calculate points from selected choices
            points_earned = 0
            
            for choice in selected_choices_objs:
                # Skip neutral choices
                if choice.is_neutral:
                    continue
                    
                # Add points value (which can be positive or negative)
                points_earned += choice.points_value
                
            # Apply minimum score cap
            if points_earned < self.minimum_score:
                points_earned = self.minimum_score
                
            # Cap at maximum points
            if points_earned > self.points:
                points_earned = self.points
                
            # Determine if fully correct (for feedback purposes)
            all_correct = all(c.is_correct for c in selected_choices_objs)
            all_selected = len(selected_choices_objs) == len(correct_choices)
            is_correct = all_correct and all_selected
            
        # For questions with multiple correct answers (traditional scoring)
        elif self.allow_multiple:
            selected_choices_objs = choices.filter(id__in=selected_choices)
            
            # Check if all selected choices are correct and all correct choices are selected
            all_correct = all(c.is_correct for c in selected_choices_objs)
            all_selected = len(selected_choices_objs) == len(correct_choices)
            
            is_correct = all_correct and all_selected
            points_earned = self.points if is_correct else 0
            
        # For questions with a single correct answer (traditional scoring)
        else:
            if len(selected_choices) != 1:
                is_correct = False
                points_earned = 0
            else:
                choice = choices.filter(id=selected_choices[0]).first()
                is_correct = choice is not None and choice.is_correct
                points_earned = self.points if is_correct else 0
        
        # Apply score normalization if enabled
        if self.normalization_method != 'none':
            points_earned = self.normalize_score(points_earned)
        
        feedback = self.correct_feedback if is_correct else self.incorrect_feedback
        return (is_correct, points_earned, feedback)
        
    def normalize_score(self, points_earned):
        """Normalize the score based on the selected normalization method.
        
        Args:
            points_earned: The original points earned
            
        Returns:
            int: The normalized points score
        """
        # If no points or maximum points, normalization isn't needed
        if points_earned == 0 or points_earned == self.points:
            return points_earned
            
        # Get parameters with defaults if not specified
        params = self.normalization_parameters
        
        if self.normalization_method == 'zscore':
            # Z-score normalization: (x - mean) / std_dev
            # Default: mean = points/2, std_dev = points/6 (for a normal distribution)
            mean = params.get('mean', self.points / 2)
            std_dev = params.get('std_dev', self.points / 6)
            
            if std_dev == 0:  # Avoid division by zero
                std_dev = 1
                
            z_score = (points_earned - mean) / std_dev
            
            # Convert z-score back to points (centered around points/2)
            normalized = int(round((z_score * (self.points / 4)) + (self.points / 2)))
            
        elif self.normalization_method == 'minmax':
            # Min-Max scaling to [min, max] range
            output_min = params.get('output_min', 0)
            output_max = params.get('output_max', self.points)
            input_min = params.get('input_min', 0)
            input_max = params.get('input_max', self.points)
            
            # Avoid division by zero
            if input_max == input_min:
                normalized = output_min
            else:
                normalized = output_min + ((points_earned - input_min) * 
                                          (output_max - output_min) / 
                                          (input_max - input_min))
            normalized = int(round(normalized))
            
        elif self.normalization_method == 'percentile':
            # Percentile ranking using historical data
            # This requires analytics data for the question
            percentiles = params.get('percentiles', {})
            
            if not percentiles:  # Fall back to linear if no percentile data
                normalized = points_earned
            else:
                # Find the appropriate percentile
                score_percentage = (points_earned / self.points) * 100
                
                # Convert percentiles from string keys to float
                percentile_map = {float(k): v for k, v in percentiles.items()}
                
                # Get all percentile points
                percentile_points = sorted(percentile_map.keys())
                
                # Find the closest percentile point
                closest_percentile = min(percentile_points, 
                                        key=lambda x: abs(x - score_percentage))
                
                # Get the normalized value for this percentile
                normalized = int(round((percentile_map[closest_percentile] / 100) * self.points))
                
        elif self.normalization_method == 'custom':
            # Custom function defined in normalization_parameters
            # Default to original value if no custom function
            normalized = points_earned
            
            # Example structure for a custom mapping:
            # {"mapping": {"1": 2, "2": 3, "3": 5}}
            mapping = params.get('mapping', {})
            
            if mapping and str(points_earned) in mapping:
                normalized = int(mapping[str(points_earned)])
        else:
            # No normalization or unknown method
            normalized = points_earned
            
        # Ensure normalized score is within bounds
        normalized = max(0, min(normalized, self.points))
        return normalized

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

class EssayQuestion(Question):
    """
    A question that requires a written response and manual grading.
    
    Can be graded using a simple point system or with a detailed rubric
    for more objective and consistent grading.
    """
    min_word_count = models.PositiveIntegerField(default=0, help_text='Minimum word count required (0 for no minimum)')
    max_word_count = models.PositiveIntegerField(default=0, help_text='Maximum word count allowed (0 for no maximum)')
    rubric = models.TextField(blank=True, help_text='Legacy text rubric for simple grading')
    scoring_rubric = models.ForeignKey('ScoringRubric', on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='essay_questions',
                                     help_text='Advanced rubric with criteria for detailed grading')
    example_answer = models.TextField(blank=True, help_text='Example of a good answer (visible only to instructors)')
    allow_attachments = models.BooleanField(default=False, help_text='Allow students to upload attachments')
    use_detailed_rubric = models.BooleanField(default=False, 
                                             help_text='If true, use structured rubric instead of simple point allocation')
    
    def save(self, *args, **kwargs):
        self.question_type = 'essay'
        super().save(*args, **kwargs)
        
    def check_answer(self, response_text):
        """
        Essay questions need manual grading, so we just check if the response
        meets the minimum requirements.
        
        Args:
            response_text: The text of the essay response
            
        Returns:
            tuple: (is_pending_grading, points_earned, feedback)
        """
        if not response_text:
            return (False, 0, "No response provided")
            
        # Check word count if minimum is set
        if self.min_word_count > 0:
            word_count = len(response_text.split())
            if word_count < self.min_word_count:
                return (False, 0, f"Response is too short. Minimum {self.min_word_count} words required.")
                
        # Check word count if maximum is set
        if self.max_word_count > 0:
            word_count = len(response_text.split())
            if word_count > self.max_word_count:
                return (False, 0, f"Response exceeds maximum word count of {self.max_word_count} words.")
        
        # Mark as pending grading
        return (False, 0, "Response submitted successfully. Waiting for instructor grading.")
    
    def get_scoring_criteria(self):
        """
        Get the scoring criteria for this essay question.
        
        Returns:
            list: The criteria if using a detailed rubric, otherwise an empty list
        """
        if self.use_detailed_rubric and self.scoring_rubric:
            return self.scoring_rubric.criteria.all().order_by('order')
        return []
        
    def grade_response(self, response, points, feedback, graded_by, criterion_scores=None):
        """
        Grade an essay response.
        
        Args:
            response: QuestionResponse object
            points: Points to award (used for simple grading)
            feedback: Instructor feedback
            graded_by: User who graded the response
            criterion_scores: Optional dict of criterion_id -> score (for detailed rubric grading)
            
        Returns:
            QuestionResponse: The updated response object
        """
        # For detailed rubric grading
        if self.use_detailed_rubric and self.scoring_rubric and criterion_scores:
            # Save individual criterion feedback
            for criterion_id, score_data in criterion_scores.items():
                criterion = self.scoring_rubric.criteria.filter(id=criterion_id).first()
                if criterion:
                    # Create or update the criterion feedback
                    rubric_feedback, created = RubricFeedback.objects.update_or_create(
                        response=response,
                        criterion=criterion,
                        defaults={
                            'points_earned': min(score_data['points'], criterion.max_points),
                            'comments': score_data.get('comments', ''),
                            'performance_level': score_data.get('level', '')
                        }
                    )
            
            # Calculate total score based on criterion scores
            total_score, max_score, percentage = self.scoring_rubric.calculate_score(
                {int(k): v['points'] for k, v in criterion_scores.items()}
            )
            
            # Scale the score to the question's total points
            scaled_points = int((percentage / 100) * self.points)
            points = min(scaled_points, self.points)
        
        # Ensure points don't exceed the maximum
        if points > self.points:
            points = self.points
            
        # Update the response
        response.is_correct = (points > 0)
        response.points_earned = points
        response.feedback = feedback
        response.instructor_comment = feedback
        response.graded_at = timezone.now()
        response.graded_by = graded_by
        response.save()
        
        # Update the attempt's score
        response.attempt.calculate_score()
        
        return response

class Choice(models.Model):
    """
    A choice for a multiple choice question.
    """
    question = models.ForeignKey('MultipleChoiceQuestion', related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, help_text='Feedback specific to this choice')
    order = models.PositiveIntegerField(default=0)
    
    # Partial credit scoring
    points_value = models.IntegerField(default=0, 
                                      help_text='Points to award for this choice (negative for penalties)')
    is_neutral = models.BooleanField(default=False,
                                    help_text='If true, this choice neither adds nor subtracts points')
    
    # Media fields for choices
    image = models.FileField(upload_to='choices/%Y/%m/', blank=True, null=True,
                            help_text='Image to display with this choice')
    image_alt_text = models.CharField(max_length=255, blank=True,
                                     help_text='Alternative text for the image (for accessibility)')
    
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
    
    # Time extension fields
    time_extension_minutes = models.PositiveIntegerField(default=0, 
                                                        help_text='Additional time granted by instructor')
    extended_by = models.ForeignKey(User, null=True, blank=True, 
                                   related_name='extended_attempts', on_delete=models.SET_NULL,
                                   help_text='Instructor who granted the time extension')
    extension_reason = models.TextField(blank=True, 
                                       help_text='Reason for granting time extension')
    
    # Timing data
    last_activity_at = models.DateTimeField(null=True, blank=True, 
                                           help_text='Last recorded activity in this attempt')
    time_warning_sent = models.BooleanField(default=False, 
                                           help_text='Whether a time warning has been sent')
    
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
        
        # Save the updated scores
        self.save()
            
        return self.score, self.max_score
    
    def get_conditional_feedback(self):
        """
        Get the appropriate conditional feedback based on the score percentage.
        
        Returns:
            str: The conditional feedback for the current score, or empty string if none matches
        """
        if not self.quiz.conditional_feedback or self.max_score == 0:
            return ""
            
        score_percentage = (self.score / self.max_score) * 100
        
        # Check each score range to find a match
        for score_range, feedback in self.quiz.conditional_feedback.items():
            try:
                range_start, range_end = map(int, score_range.split('-'))
                if range_start <= score_percentage <= range_end:
                    return feedback
            except (ValueError, AttributeError):
                continue
                
        return ""
    
    def is_feedback_available(self):
        """
        Check if feedback should be shown to the user based on quiz settings.
        
        Returns:
            bool: True if feedback should be shown, False otherwise
        """
        if self.status != 'completed' and self.status != 'timed_out':
            return False
            
        if self.quiz.show_feedback_after == 'never':
            return False
            
        # Check feedback delay
        if self.quiz.feedback_delay_minutes > 0 and self.completed_at:
            delay = timezone.timedelta(minutes=self.quiz.feedback_delay_minutes)
            now = timezone.now()
            
            # If completed time + delay is still in the future, feedback is not available yet
            if self.completed_at + delay > now:
                return False
            
        if self.quiz.show_feedback_after == 'completion':
            return True
            
        if self.quiz.show_feedback_after == 'due_date':
            now = timezone.now()
            if self.quiz.available_until and now > self.quiz.available_until:
                return True
            return False
            
        # For 'each_question', feedback is handled differently
        return True
    
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
    instructor_comment = models.TextField(blank=True, help_text='Instructor feedback for essay questions')
    instructor_annotation = models.TextField(blank=True, help_text='Instructor annotation for any question type')
    annotation_added_at = models.DateTimeField(null=True, blank=True, help_text='When the annotation was added')
    annotated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='annotated_responses', help_text='Instructor who added the annotation')
    graded_at = models.DateTimeField(null=True, blank=True, help_text='When the essay was graded')
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_responses')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['attempt', 'question__order']
        unique_together = [['attempt', 'question']]
        
    def __str__(self):
        return f"Response to {self.question} by {self.attempt.user.username}"
        
    def check_answer(self):
        """Check if the answer is correct and update fields"""
        if self.question.question_type == 'multiple_choice':
            # Handle both single choice and multiple choices formats
            if 'selected_choice' in self.response_data:
                choices = [self.response_data.get('selected_choice')]
            else:
                choices = self.response_data.get('selected_choices', [])
            is_correct, points, feedback = self.question.multiplechoicequestion.check_answer(choices)
        elif self.question.question_type == 'true_false':
            answer = self.response_data.get('selected_answer')
            is_correct, points, feedback = self.question.truefalsequestion.check_answer(answer)
        elif self.question.question_type == 'essay':
            # Essay questions require manual grading
            essay_text = self.response_data.get('essay_text', '')
            is_correct, points, feedback = self.question.essayquestion.check_answer(essay_text)
        else:
            is_correct, points, feedback = False, 0, "Unknown question type"
            
        self.is_correct = is_correct
        self.points_earned = points
        self.feedback = feedback
        self.save()
        
        return is_correct, points

class QuizPrerequisite(models.Model):
    """
    Defines a prerequisite relationship between quizzes.
    
    For a user to take the target quiz, they must have completed the prerequisite quiz.
    This allows for surveys or introductory quizzes that gate access to subsequent quizzes.
    """
    quiz = models.ForeignKey('Quiz', related_name='prerequisites', on_delete=models.CASCADE,
                           help_text='The quiz that requires completion of prerequisites')
    prerequisite_quiz = models.ForeignKey('Quiz', related_name='required_for', on_delete=models.CASCADE,
                                        help_text='The quiz that must be completed first')
    required_passing = models.BooleanField(default=True, 
                                         help_text='Whether the prerequisite needs to be passed or just attempted')
    bypass_for_instructors = models.BooleanField(default=True,
                                              help_text='Whether instructors can bypass this prerequisite')
    
    class Meta:
        unique_together = [['quiz', 'prerequisite_quiz']]
        verbose_name = 'Quiz Prerequisite'
        verbose_name_plural = 'Quiz Prerequisites'
    
    def __str__(self):
        return f"{self.prerequisite_quiz.title} → {self.quiz.title}"
    
    def is_satisfied_by_user(self, user):
        """
        Check if this prerequisite is satisfied by the user.
        
        Args:
            user: The user to check
            
        Returns:
            bool: True if the prerequisite is satisfied, False otherwise
        """
        # Instructor bypass
        if self.bypass_for_instructors and hasattr(user, 'profile') and user.profile.is_instructor:
            return True
            
        # Look for a completed attempt
        attempts = QuizAttempt.objects.filter(
            quiz=self.prerequisite_quiz,
            user=user,
            status__in=['completed', 'timed_out']  # Both completed and timed-out attempts count
        )
        
        if not attempts.exists():
            return False
            
        # If passing is required, check if any attempt has passed
        if self.required_passing:
            return attempts.filter(is_passed=True).exists()
            
        # Otherwise, just having attempted it is enough
        return True


class QuestionAnalytics(models.Model):
    """
    Analytics data for a specific question across all quiz attempts.
    
    This model aggregates information about how students are performing
    on a specific question to help instructors improve their assessments.
    """
    question = models.OneToOneField('Question', related_name='analytics', on_delete=models.CASCADE)
    
    # Performance metrics
    total_attempts = models.PositiveIntegerField(default=0)
    correct_attempts = models.PositiveIntegerField(default=0)
    incorrect_attempts = models.PositiveIntegerField(default=0)
    avg_time_seconds = models.FloatField(default=0.0)
    
    # Difficulty metrics
    difficulty_index = models.FloatField(default=0.0, 
                                        help_text='Percentage of students who answered correctly (0.0-1.0)')
    discrimination_index = models.FloatField(default=0.0,
                                           help_text='How well the question differentiates high and low performers (-1.0 to 1.0)')
    
    # Choice distribution (for multiple choice)
    choice_distribution = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    last_attempted_at = models.DateTimeField(null=True, blank=True)
    last_calculated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Question Analytics'
        verbose_name_plural = 'Question Analytics'
    
    def __str__(self):
        return f"Analytics for {self.question}"
    
    def recalculate(self):
        """Recalculate analytics based on question responses"""
        from django.db.models import Avg, Count, Case, When, F, Sum
        
        # Get all responses for this question
        responses = QuestionResponse.objects.filter(question=self.question)
        
        # Basic metrics
        self.total_attempts = responses.count()
        self.correct_attempts = responses.filter(is_correct=True).count()
        self.incorrect_attempts = self.total_attempts - self.correct_attempts
        
        # Calculate average time
        avg_time = responses.aggregate(avg_time=Avg('time_spent_seconds'))['avg_time']
        self.avg_time_seconds = avg_time if avg_time is not None else 0
        
        # Calculate difficulty index (p-value)
        self.difficulty_index = self.correct_attempts / self.total_attempts if self.total_attempts > 0 else 0
        
        # For multiple choice questions, calculate choice distribution
        if self.question.question_type == 'multiple_choice':
            choices = Choice.objects.filter(question=self.question.multiplechoicequestion)
            distribution = {}
            
            for choice in choices:
                # Count how many times this choice was selected
                count = responses.filter(response_data__selected_choices__contains=[choice.id]).count()
                distribution[str(choice.id)] = {
                    'choice_text': choice.text[:50],
                    'count': count,
                    'percentage': (count / self.total_attempts * 100) if self.total_attempts > 0 else 0,
                    'is_correct': choice.is_correct
                }
                
            self.choice_distribution = distribution
            
        # Update timestamps
        self.last_attempted_at = responses.aggregate(latest=models.Max('created_at'))['latest']
        self.last_calculated_at = timezone.now()
        self.save()


class ScoringRubric(models.Model):
    """
    A rubric for scoring essay questions.
    
    A rubric consists of multiple criteria, each with a weight and description.
    Instructors use these criteria to objectively grade essay responses.
    """
    name = models.CharField(max_length=255, help_text='Name of the rubric')
    description = models.TextField(blank=True, help_text='Description of the rubric and its purpose')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rubrics')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False, help_text='If true, this rubric can be used by all instructors')
    total_points = models.PositiveIntegerField(default=0, help_text='Total possible points for this rubric')
    
    class Meta:
        verbose_name = 'Scoring Rubric'
        verbose_name_plural = 'Scoring Rubrics'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Calculate total points from criteria
        if self.pk:  # Only if the rubric already exists
            self.total_points = sum(criterion.max_points for criterion in self.criteria.all())
        super().save(*args, **kwargs)
    
    def calculate_score(self, criterion_scores):
        """
        Calculate the total score based on scores for each criterion.
        
        Args:
            criterion_scores: Dict mapping criterion IDs to scores
            
        Returns:
            tuple: (total_score, max_score, percentage)
        """
        total_score = 0
        max_score = 0
        
        for criterion in self.criteria.all():
            max_score += criterion.max_points
            if criterion.id in criterion_scores:
                total_score += min(criterion_scores[criterion.id], criterion.max_points)
        
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        return total_score, max_score, percentage

class RubricCriterion(models.Model):
    """
    A criterion for a scoring rubric.
    
    Each criterion represents a specific aspect to evaluate in an essay response.
    """
    rubric = models.ForeignKey(ScoringRubric, on_delete=models.CASCADE, related_name='criteria')
    name = models.CharField(max_length=255, help_text='Name of the criterion')
    description = models.TextField(help_text='Description of what to evaluate')
    max_points = models.PositiveIntegerField(default=10, help_text='Maximum points for this criterion')
    weight = models.FloatField(default=1.0, help_text='Weight of this criterion in the total score')
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    
    # Performance levels (e.g., Excellent, Good, Fair, Poor)
    performance_levels = models.JSONField(default=dict, blank=True, 
                                         help_text='JSON definition of performance levels and point ranges')
    
    class Meta:
        ordering = ['rubric', 'order']
        verbose_name = 'Rubric Criterion'
        verbose_name_plural = 'Rubric Criteria'
    
    def __str__(self):
        return f"{self.name} ({self.max_points} pts)"
    
    def save(self, *args, **kwargs):
        # Create default performance levels if none exist
        if not self.performance_levels:
            self.performance_levels = {
                "Excellent": {
                    "points": self.max_points,
                    "description": f"Excellent level of achievement for {self.name}"
                },
                "Good": {
                    "points": int(self.max_points * 0.75),
                    "description": f"Good level of achievement for {self.name}"
                },
                "Satisfactory": {
                    "points": int(self.max_points * 0.5),
                    "description": f"Satisfactory level of achievement for {self.name}"
                },
                "Needs Improvement": {
                    "points": int(self.max_points * 0.25),
                    "description": f"Needs improvement for {self.name}"
                },
                "Unsatisfactory": {
                    "points": 0,
                    "description": f"Unsatisfactory level of achievement for {self.name}"
                }
            }
        
        super().save(*args, **kwargs)
        
        # Update the total points in the parent rubric
        if self.rubric:
            self.rubric.save()

class RubricFeedback(models.Model):
    """
    Feedback for a specific criterion of a response.
    
    Stores instructor's evaluation and comments for each criterion.
    """
    response = models.ForeignKey('QuestionResponse', on_delete=models.CASCADE, related_name='criterion_feedback')
    criterion = models.ForeignKey(RubricCriterion, on_delete=models.CASCADE, related_name='feedback')
    points_earned = models.PositiveIntegerField(default=0)
    comments = models.TextField(blank=True)
    performance_level = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = [['response', 'criterion']]
    
    def __str__(self):
        return f"Feedback for {self.criterion} on {self.response}"

class QuizAnalytics(models.Model):
    """
    Analytics data for a specific quiz across all attempts.
    
    This model aggregates information about how students are performing
    on a quiz to help instructors evaluate its effectiveness.
    """
    quiz = models.OneToOneField('Quiz', related_name='analytics', on_delete=models.CASCADE)
    
    # Attempt metrics
    total_attempts = models.PositiveIntegerField(default=0)
    completed_attempts = models.PositiveIntegerField(default=0)
    passing_attempts = models.PositiveIntegerField(default=0)
    
    # Time metrics
    avg_completion_time = models.FloatField(default=0.0, help_text='Average completion time in seconds')
    avg_score = models.FloatField(default=0.0, help_text='Average score (percentage)')
    
    # Common problem areas
    lowest_scoring_questions = models.JSONField(default=list, blank=True)
    highest_scoring_questions = models.JSONField(default=list, blank=True)
    
    # Attempts distribution 
    score_distribution = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    last_attempted_at = models.DateTimeField(null=True, blank=True)
    last_calculated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Quiz Analytics'
        verbose_name_plural = 'Quiz Analytics'
    
    def __str__(self):
        return f"Analytics for {self.quiz.title}"
    
    def recalculate(self):
        """Recalculate analytics based on quiz attempts"""
        from django.db.models import Avg, Count, Case, When, F, Sum
        
        # Get all attempts for this quiz
        attempts = QuizAttempt.objects.filter(quiz=self.quiz)
        completed = attempts.filter(status__in=['completed', 'timed_out'])
        
        # Basic metrics
        self.total_attempts = attempts.count()
        self.completed_attempts = completed.count()
        self.passing_attempts = completed.filter(is_passed=True).count()
        
        # Calculate average completion time
        avg_time = completed.aggregate(avg_time=Avg('time_spent_seconds'))['avg_time']
        self.avg_completion_time = avg_time if avg_time is not None else 0
        
        # Calculate average score
        avg_score = completed.aggregate(
            avg_score=Avg(Case(
                When(max_score__gt=0, then=100 * F('score') / F('max_score')),
                default=0
            ))
        )['avg_score']
        self.avg_score = avg_score if avg_score is not None else 0
        
        # Calculate score distribution
        distribution = {}
        
        # Define score ranges
        ranges = [
            (0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
            (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)
        ]
        
        for start, end in ranges:
            count = completed.filter(
                max_score__gt=0,
                score__gte=start * F('max_score') / 100,
                score__lt=end * F('max_score') / 100
            ).count()
            
            distribution[f"{start}-{end}"] = count
            
        # Add 100% category
        perfect_count = completed.filter(
            max_score__gt=0,
            score=F('max_score')
        ).count()
        distribution["100"] = perfect_count
        
        self.score_distribution = distribution
        
        # Update timestamps
        self.last_attempted_at = attempts.aggregate(latest=models.Max('started_at'))['latest']
        self.last_calculated_at = timezone.now()
        self.save()


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