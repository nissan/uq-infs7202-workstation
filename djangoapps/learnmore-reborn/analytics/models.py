from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Sum, Avg, F, Q, Case, When, Window, FloatField
from django.db.models.functions import Rank, PercentRank
from courses.models import Course, Module, Quiz, QuizAttempt, Question
import json
from datetime import timedelta

class UserActivity(models.Model):
    """Tracks general user activity on the platform"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_activities', null=True, blank=True)
    activity_type = models.CharField(max_length=50)  # login, view_course, view_module, etc.
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)  # Additional details specific to the activity type
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
        ]
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} - {self.activity_type} - {self.timestamp}"

class LearnerAnalytics(models.Model):
    """
    Analytics data tracking a learner's performance across quizzes and courses.
    
    This model aggregates information about an individual learner's performance
    to provide insights into their progress, strengths, weaknesses, and learning patterns.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learner_analytics')
    
    # Overall metrics
    total_quizzes_taken = models.PositiveIntegerField(default=0)
    total_quizzes_passed = models.PositiveIntegerField(default=0)
    total_questions_answered = models.PositiveIntegerField(default=0)
    total_correct_answers = models.PositiveIntegerField(default=0)
    
    # Time metrics
    average_time_per_question = models.FloatField(default=0.0, help_text='Average time in seconds spent per question')
    total_study_time = models.DurationField(default=timezone.timedelta, help_text='Total time spent on learning activities')
    
    # Performance insights
    strengths = models.JSONField(default=list, blank=True, help_text='Categories or topics where the learner excels')
    areas_for_improvement = models.JSONField(default=list, blank=True, help_text='Categories or topics where the learner struggles')
    
    # Learning patterns
    learning_pattern_data = models.JSONField(default=dict, blank=True, help_text='Data about learning patterns like time of day, duration, etc.')
    quiz_performance_history = models.JSONField(default=list, blank=True, help_text='Historical data of quiz performances')
    
    # Progress trends
    progress_over_time = models.JSONField(default=dict, blank=True, help_text='Chart data for progress visualization')
    performance_by_category = models.JSONField(default=dict, blank=True, help_text='Performance metrics grouped by question categories')
    
    # Course-specific metrics
    course_completion_data = models.JSONField(default=dict, blank=True, help_text='Completion rates and performance by course')
    
    # Comparative metrics
    percentile_ranking = models.JSONField(default=dict, blank=True, help_text='Percentile ranking compared to peers by category')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Learner Analytics'
        verbose_name_plural = 'Learner Analytics'
    
    def __str__(self):
        return f"Analytics for {self.user.username}"
    
    def calculate_overall_metrics(self):
        """Calculate the overall metrics from quiz attempts"""
        from django.db.models import Count, Sum, Avg, F, Q
        
        # Get all completed quiz attempts for this user
        attempts = QuizAttempt.objects.filter(
            user=self.user,
            status__in=['completed', 'timed_out']
        )
        
        # Basic metrics
        self.total_quizzes_taken = attempts.count()
        self.total_quizzes_passed = attempts.filter(is_passed=True).count()
        
        # Question metrics
        from courses.models import QuestionResponse
        responses = QuestionResponse.objects.filter(attempt__user=self.user)
        self.total_questions_answered = responses.count()
        self.total_correct_answers = responses.filter(is_correct=True).count()
        
        # Time metrics
        avg_time = responses.aggregate(avg_time=Avg('time_spent_seconds'))['avg_time']
        self.average_time_per_question = avg_time if avg_time is not None else 0
        
        # Calculate total study time from module engagements
        from analytics.models import ModuleEngagement
        engagements = ModuleEngagement.objects.filter(user=self.user)
        total_time = sum((e.time_spent for e in engagements), timezone.timedelta())
        self.total_study_time = total_time
        
        self.save()
        return True
    
    def calculate_performance_by_category(self):
        """Calculate performance metrics grouped by question category"""
        from django.db.models import Count, Sum, Avg, F, Q, Case, When
        
        # Get all responses for this user
        from courses.models import QuestionResponse
        responses = QuestionResponse.objects.filter(attempt__user=self.user)
        
        # Initialize the category performance data
        performance_data = {}
        
        # Define question categories (could be based on tags, question types, etc.)
        # For now, we'll use question types as categories
        question_types = ['multiple_choice', 'true_false', 'essay']
        
        for q_type in question_types:
            # Get responses for this question type
            type_responses = responses.filter(question__question_type=q_type)
            
            if type_responses.exists():
                correct = type_responses.filter(is_correct=True).count()
                total = type_responses.count()
                
                # Calculate average points earned as percentage of available points
                avg_points_pct = type_responses.aggregate(
                    avg_pct=Avg(
                        Case(
                            When(question__points__gt=0, 
                                 then=100 * F('points_earned') / F('question__points')),
                            default=0
                        )
                    )
                )['avg_pct'] or 0
                
                # Calculate average time spent
                avg_time = type_responses.aggregate(
                    avg_time=Avg('time_spent_seconds')
                )['avg_time'] or 0
                
                performance_data[q_type] = {
                    'correct': correct,
                    'total': total,
                    'accuracy': (correct / total * 100) if total > 0 else 0,
                    'avg_score_percentage': avg_points_pct,
                    'avg_time_seconds': avg_time
                }
        
        self.performance_by_category = performance_data
        self.save()
        return performance_data
    
    def identify_strengths_and_weaknesses(self):
        """Identify areas of strength and weakness based on performance data"""
        # Ensure we have performance data
        if not self.performance_by_category:
            self.calculate_performance_by_category()
            
        strengths = []
        weaknesses = []
        
        # Analyze performance by category
        for category, data in self.performance_by_category.items():
            # If accuracy is over 80%, consider it a strength
            if data['accuracy'] >= 80:
                strengths.append({
                    'category': category,
                    'accuracy': data['accuracy'],
                    'avg_score': data['avg_score_percentage']
                })
            # If accuracy is under 60%, consider it a weakness
            elif data['accuracy'] < 60:
                weaknesses.append({
                    'category': category,
                    'accuracy': data['accuracy'],
                    'avg_score': data['avg_score_percentage']
                })
        
        # Sort by accuracy (descending for strengths, ascending for weaknesses)
        strengths.sort(key=lambda x: x['accuracy'], reverse=True)
        weaknesses.sort(key=lambda x: x['accuracy'])
        
        self.strengths = strengths
        self.areas_for_improvement = weaknesses
        self.save()
        
        return strengths, weaknesses
    
    def calculate_progress_over_time(self):
        """Calculate progress metrics over time for visualization"""
        from django.db.models import Count, Avg, F
        import datetime
        
        # Get all completed quiz attempts for this user
        attempts = QuizAttempt.objects.filter(
            user=self.user,
            status__in=['completed', 'timed_out']
        ).order_by('completed_at')
        
        if not attempts.exists():
            return {}
            
        # Initialize progress data
        progress_data = {
            'dates': [],
            'scores': [],
            'cumulative_avg': [],
            'time_spent': [],
        }
        
        # Track running totals for calculating cumulative average
        total_score_pct = 0
        count = 0
        
        # Process each attempt chronologically
        for attempt in attempts:
            if attempt.completed_at and attempt.max_score > 0:
                # Calculate score percentage
                score_pct = (attempt.score / attempt.max_score) * 100
                
                # Update running totals
                count += 1
                total_score_pct += score_pct
                cumulative_avg = total_score_pct / count
                
                # Add data points
                progress_data['dates'].append(attempt.completed_at.strftime('%Y-%m-%d'))
                progress_data['scores'].append(round(score_pct, 1))
                progress_data['cumulative_avg'].append(round(cumulative_avg, 1))
                progress_data['time_spent'].append(attempt.time_spent_seconds)
        
        self.progress_over_time = progress_data
        self.save()
        
        return progress_data
    
    def calculate_percentile_ranking(self):
        """Calculate percentile ranking compared to peers"""
        from django.db.models import Count, Avg, F, Window, FloatField
        from django.db.models.functions import Rank, PercentRank
        
        # Initialize percentile data
        percentile_data = {}
        
        # Calculate overall score percentile
        from courses.models import QuizAttempt
        
        # Get this user's average score
        user_avg_score = QuizAttempt.objects.filter(
            user=self.user,
            status__in=['completed', 'timed_out'],
            max_score__gt=0
        ).aggregate(
            avg_score=Avg(100 * F('score') / F('max_score'))
        )['avg_score'] or 0
        
        # Get all users' average scores
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # This is a complex query that would calculate percentile ranking
        # For simplicity, we'll just get all scores and calculate manually
        all_user_scores = []
        
        for user in User.objects.all():
            avg_score = QuizAttempt.objects.filter(
                user=user,
                status__in=['completed', 'timed_out'],
                max_score__gt=0
            ).aggregate(
                avg_score=Avg(100 * F('score') / F('max_score'))
            )['avg_score'] or 0
            
            if avg_score > 0:  # Only include users who have taken quizzes
                all_user_scores.append(avg_score)
        
        # Calculate percentile manually
        if all_user_scores:
            all_user_scores.sort()
            rank = sum(1 for score in all_user_scores if score <= user_avg_score)
            percentile = (rank / len(all_user_scores)) * 100
            
            percentile_data['overall'] = {
                'percentile': percentile,
                'user_score': user_avg_score,
                'median_score': all_user_scores[len(all_user_scores) // 2] if all_user_scores else 0
            }
        
        self.percentile_ranking = percentile_data
        self.save()
        
        return percentile_data
    
    def recalculate_all(self):
        """Recalculate all analytics data"""
        self.calculate_overall_metrics()
        self.calculate_performance_by_category()
        self.identify_strengths_and_weaknesses()
        self.calculate_progress_over_time()
        self.calculate_percentile_ranking()
        
        return True

class CourseAnalyticsSummary(models.Model):
    """High-level analytics for a specific course"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='analytics_summary')
    total_enrollments = models.IntegerField(default=0)
    active_learners = models.IntegerField(default=0)  # Active in last 30 days
    completion_rate = models.FloatField(default=0.0)  # Percentage of enrolled users who completed
    average_rating = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)  # Composite score of engagement metrics
    last_updated = models.DateTimeField(auto_now=True)
    engagement_trend = models.JSONField(default=dict, blank=True)  # Time-series data for engagement
    
    class Meta:
        verbose_name_plural = "Course Analytics Summaries"
    
    def __str__(self):
        return f"Analytics Summary for {self.course.title}"
    
    def recalculate(self):
        """Recalculate analytics data from current enrollments and progress"""
        from datetime import timedelta
        
        # Get enrollments for this course
        enrollments = self.course.enrollments.all()
        self.total_enrollments = enrollments.count()
        
        # Calculate active learners (with activity in the last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users = set(UserActivity.objects.filter(
            timestamp__gte=thirty_days_ago,
            details__contains={'course_id': self.course.id}
        ).values_list('user_id', flat=True))
        
        self.active_learners = len(active_users)
        
        # Calculate completion rate
        completed = enrollments.filter(status='completed').count()
        self.completion_rate = (completed / self.total_enrollments * 100) if self.total_enrollments > 0 else 0
        
        # Save changes
        self.last_updated = timezone.now()
        self.save()

class ModuleEngagement(models.Model):
    """Tracks learner engagement with specific modules"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='module_engagements')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0)
    time_spent = models.DurationField(default=timezone.timedelta)  # Total time spent on this module
    last_viewed = models.DateTimeField(auto_now=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    interaction_data = models.JSONField(default=dict, blank=True)  # Detailed interaction data
    
    class Meta:
        unique_together = ('module', 'user')
        indexes = [
            models.Index(fields=['module', 'user']),
            models.Index(fields=['user', 'last_viewed']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.module.title}"
    
    def record_view(self, duration_seconds=None):
        """Record a view of this module"""
        self.view_count += 1
        
        if duration_seconds:
            import datetime
            self.time_spent += datetime.timedelta(seconds=duration_seconds)
            
        self.last_viewed = timezone.now()
        self.save()

class LearningPathAnalytics(models.Model):
    """Tracks analytics for common learning paths through courses"""
    path_signature = models.CharField(max_length=255, unique=True)  # Hash of the path
    path_description = models.TextField()
    path_modules = models.JSONField(default=list)  # List of module IDs in order
    user_count = models.IntegerField(default=0)
    average_completion_time = models.DurationField(null=True, blank=True)
    success_rate = models.FloatField(default=0.0)  # Percentage of users who complete this path
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Learning Path Analytics"
    
    def __str__(self):
        return f"Path: {self.path_description[:50]}..."
    
    @classmethod
    def identify_common_paths(cls, course, min_users=5):
        """
        Analyze user progress data to identify common learning paths
        through the course
        
        Args:
            course: The course to analyze
            min_users: Minimum number of users who must follow a path for it to be considered
            
        Returns:
            List of path signatures that were created or updated
        """
        # This would be implemented to analyze progress data
        # and identify common paths through the modules
        pass

class CourseAnalytics(models.Model):
    """Comprehensive analytics for course performance and engagement"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='course_analytics')
    
    # Enrollment statistics
    total_enrollments = models.PositiveIntegerField(default=0)
    active_enrollments = models.PositiveIntegerField(default=0)  # Active in last 30 days
    new_enrollments = models.PositiveIntegerField(default=0)  # New enrollments in last 30 days
    enrollment_trend = models.JSONField(default=dict, blank=True)  # Daily/weekly/monthly trends
    
    # Completion rates
    completion_rate = models.FloatField(default=0.0)  # Overall completion rate
    module_completion_rates = models.JSONField(default=dict, blank=True)  # Per-module completion rates
    average_completion_time = models.DurationField(null=True, blank=True)
    
    # Performance metrics
    average_score = models.FloatField(default=0.0)  # Average quiz score
    score_distribution = models.JSONField(default=dict, blank=True)  # Score distribution data
    module_performance = models.JSONField(default=dict, blank=True)  # Performance by module
    
    # Time spent metrics
    average_time_per_module = models.DurationField(null=True, blank=True)
    total_learning_time = models.DurationField(default=timedelta)
    time_distribution = models.JSONField(default=dict, blank=True)  # Time spent patterns
    
    # Engagement metrics
    engagement_score = models.FloatField(default=0.0)  # Composite engagement score
    active_users = models.PositiveIntegerField(default=0)  # Users active in last 7 days
    interaction_rates = models.JSONField(default=dict, blank=True)  # Various interaction metrics
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_calculated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Course Analytics'
        verbose_name_plural = 'Course Analytics'
        indexes = [
            models.Index(fields=['course', 'last_updated']),
            models.Index(fields=['completion_rate']),
            models.Index(fields=['engagement_score']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.course.title}"
    
    def calculate_metrics(self):
        """Calculate all analytics metrics for the course"""
        # Cache key for this course's analytics
        cache_key = f'course_analytics_{self.course.id}'
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # Calculate enrollment statistics
        self._calculate_enrollment_metrics()
        
        # Calculate completion rates
        self._calculate_completion_metrics()
        
        # Calculate performance metrics
        self._calculate_performance_metrics()
        
        # Calculate time metrics
        self._calculate_time_metrics()
        
        # Calculate engagement metrics
        self._calculate_engagement_metrics()
        
        # Update timestamps
        self.last_calculated = timezone.now()
        self.save()
        
        # Cache the results
        cache.set(cache_key, json.dumps(self.to_dict()), timeout=3600)  # Cache for 1 hour
        
        return self.to_dict()
    
    def _calculate_enrollment_metrics(self):
        """Calculate enrollment-related metrics"""
        # ... implementation details ...
    
    def _calculate_completion_metrics(self):
        """Calculate completion-related metrics"""
        # ... implementation details ...
    
    def _calculate_performance_metrics(self):
        """Calculate performance-related metrics"""
        # ... implementation details ...
    
    def _calculate_time_metrics(self):
        """Calculate time-related metrics"""
        # ... implementation details ...
    
    def _calculate_engagement_metrics(self):
        """Calculate engagement-related metrics"""
        # ... implementation details ...
    
    def to_dict(self):
        """Convert analytics data to dictionary format"""
        return {
            'enrollment_stats': {
                'total': self.total_enrollments,
                'active': self.active_enrollments,
                'new': self.new_enrollments,
                'trend': self.enrollment_trend
            },
            'completion_rates': {
                'overall': self.completion_rate,
                'by_module': self.module_completion_rates,
                'avg_time': str(self.average_completion_time) if self.average_completion_time else None
            },
            'performance': {
                'average_score': self.average_score,
                'score_distribution': self.score_distribution,
                'module_performance': self.module_performance
            },
            'time_metrics': {
                'avg_time_per_module': str(self.average_time_per_module) if self.average_time_per_module else None,
                'total_learning_time': str(self.total_learning_time),
                'distribution': self.time_distribution
            },
            'engagement': {
                'score': self.engagement_score,
                'active_users': self.active_users,
                'interaction_rates': self.interaction_rates
            },
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class UserAnalytics(models.Model):
    """Comprehensive analytics for individual user performance and engagement"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_analytics')
    
    # Learning progress
    courses_enrolled = models.PositiveIntegerField(default=0)
    courses_completed = models.PositiveIntegerField(default=0)
    current_courses = models.JSONField(default=list, blank=True)  # List of active course IDs
    completion_rate = models.FloatField(default=0.0)
    
    # Activity patterns
    last_active = models.DateTimeField(null=True, blank=True)
    active_days = models.PositiveIntegerField(default=0)  # Days active in last 30 days
    average_session_duration = models.DurationField(null=True, blank=True)
    activity_heatmap = models.JSONField(default=dict, blank=True)  # Activity by hour/day
    
    # Performance metrics
    average_score = models.FloatField(default=0.0)
    quiz_completion_rate = models.FloatField(default=0.0)
    module_completion_rate = models.FloatField(default=0.0)
    performance_by_category = models.JSONField(default=dict, blank=True)
    
    # Engagement scores
    overall_engagement = models.FloatField(default=0.0)
    course_engagement = models.JSONField(default=dict, blank=True)  # Engagement by course
    interaction_frequency = models.JSONField(default=dict, blank=True)
    
    # Learning patterns
    preferred_learning_times = models.JSONField(default=dict, blank=True)
    study_duration_patterns = models.JSONField(default=dict, blank=True)
    content_preferences = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_calculated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User Analytics'
        verbose_name_plural = 'User Analytics'
        indexes = [
            models.Index(fields=['user', 'last_active']),
            models.Index(fields=['overall_engagement']),
            models.Index(fields=['completion_rate']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.user.username}"
    
    def calculate_metrics(self):
        """Calculate all analytics metrics for the user"""
        # ... implementation details ...

class QuizAnalytics(models.Model):
    """Analytics for quiz performance and effectiveness"""
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, related_name='quiz_analytics')
    
    # Question performance
    question_difficulty = models.JSONField(default=dict, blank=True)  # Difficulty by question
    question_discrimination = models.JSONField(default=dict, blank=True)  # Discrimination index
    question_statistics = models.JSONField(default=dict, blank=True)  # Detailed stats per question
    
    # Attempt patterns
    total_attempts = models.PositiveIntegerField(default=0)
    unique_attempters = models.PositiveIntegerField(default=0)
    average_attempts = models.FloatField(default=0.0)
    attempt_distribution = models.JSONField(default=dict, blank=True)
    
    # Score distributions
    average_score = models.FloatField(default=0.0)
    score_distribution = models.JSONField(default=dict, blank=True)
    pass_rate = models.FloatField(default=0.0)
    
    # Time analysis
    average_completion_time = models.DurationField(null=True, blank=True)
    time_distribution = models.JSONField(default=dict, blank=True)
    time_by_question = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_calculated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Quiz Analytics'
        verbose_name_plural = 'Quiz Analytics'
        indexes = [
            models.Index(fields=['quiz', 'last_updated']),
            models.Index(fields=['average_score']),
            models.Index(fields=['pass_rate']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.quiz.title}"
    
    def calculate_metrics(self):
        """Calculate all analytics metrics for the quiz"""
        # ... implementation details ...

class SystemAnalytics(models.Model):
    """System-wide analytics and monitoring"""
    # System performance
    active_users = models.PositiveIntegerField(default=0)  # Users active in last hour
    concurrent_sessions = models.PositiveIntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)  # In milliseconds
    error_rate = models.FloatField(default=0.0)  # Percentage of requests with errors
    
    # Resource usage
    cpu_usage = models.FloatField(default=0.0)  # Percentage
    memory_usage = models.FloatField(default=0.0)  # Percentage
    database_connections = models.PositiveIntegerField(default=0)
    cache_hit_rate = models.FloatField(default=0.0)  # Percentage
    
    # Error tracking
    error_counts = models.JSONField(default=dict, blank=True)  # Counts by error type
    error_trends = models.JSONField(default=dict, blank=True)  # Error trends over time
    critical_errors = models.JSONField(default=list, blank=True)  # List of critical errors
    
    # User sessions
    total_sessions = models.PositiveIntegerField(default=0)  # In last hour
    average_session_duration = models.DurationField(null=True, blank=True)
    session_distribution = models.JSONField(default=dict, blank=True)  # By hour/day
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'System Analytics'
        verbose_name_plural = 'System Analytics'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['active_users']),
            models.Index(fields=['error_rate']),
        ]
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return f"System Analytics at {self.timestamp}"
    
    @classmethod
    def get_current_metrics(cls):
        """Get or create current system metrics"""
        # Try to get the latest metrics
        latest = cls.objects.order_by('-timestamp').first()
        
        # If no metrics exist or they're more than 5 minutes old, create new ones
        if not latest or (timezone.now() - latest.timestamp) > timedelta(minutes=5):
            latest = cls.objects.create()
            latest.calculate_metrics()
        
        return latest
    
    def calculate_metrics(self):
        """Calculate current system metrics"""
        # ... implementation details ...

    def update_metrics(self, data):
        """Update system metrics fields from a dictionary and save the instance."""
        # List of fields that can be updated
        updatable_fields = [
            'active_users', 'concurrent_sessions', 'average_response_time', 'error_rate',
            'cpu_usage', 'memory_usage', 'database_connections', 'cache_hit_rate',
            'error_counts', 'error_trends', 'critical_errors',
            'total_sessions', 'average_session_duration', 'session_distribution'
        ]
        updated = False
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
                updated = True
        if updated:
            self.save()
        return updated

    def to_dict(self):
        """Convert analytics data to dictionary format"""
        return {
            'system_performance': {
                'active_users': self.active_users,
                'concurrent_sessions': self.concurrent_sessions,
                'average_response_time': self.average_response_time,
                'error_rate': self.error_rate
            },
            'resource_usage': {
                'cpu_usage': self.cpu_usage,
                'memory_usage': self.memory_usage,
                'database_connections': self.database_connections,
                'cache_hit_rate': self.cache_hit_rate
            },
            'error_tracking': {
                'error_counts': self.error_counts,
                'error_trends': self.error_trends,
                'critical_errors': self.critical_errors
            },
            'user_sessions': {
                'total_sessions': self.total_sessions,
                'average_session_duration': str(self.average_session_duration) if self.average_session_duration else None,
                'session_distribution': self.session_distribution
            },
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

# Add analytics fields to Course model
Course.add_to_class('analytics_enabled', models.BooleanField(default=True))
Course.add_to_class('analytics_settings', models.JSONField(default=dict, blank=True))

# Add analytics fields to UserProfile model
from users.models import UserProfile
UserProfile.add_to_class('tracking_consent', models.BooleanField(default=True))
UserProfile.add_to_class('analytics_preferences', models.JSONField(default=dict, blank=True))

# Add analytics fields to Module model
Module.add_to_class('performance_metrics', models.JSONField(default=dict, blank=True))
Module.add_to_class('engagement_metrics', models.JSONField(default=dict, blank=True))