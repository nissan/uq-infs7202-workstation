import factory
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from ..models import (
    UserActivity, CourseAnalytics, UserAnalytics,
    QuizAnalytics, SystemAnalytics, CourseAnalyticsSummary
)
from courses.models import Course, Module, Quiz

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
    
    title = factory.Sequence(lambda n: f'Course {n}')
    description = factory.LazyAttribute(lambda obj: f'Description for {obj.title}')
    instructor = factory.SubFactory(UserFactory)
    status = 'active'
    enrollment_type = 'open'
    course_type = 'regular'
    analytics_enabled = True

class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Module
        
    title = factory.Sequence(lambda n: f'Module {n}')
    course = factory.SubFactory(CourseFactory)
    order = factory.Sequence(lambda n: n)

class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz
    
    title = factory.Sequence(lambda n: f'Quiz {n}')
    module = factory.SubFactory(ModuleFactory)
    is_published = True
    time_limit_minutes = 30
    passing_score = 70.0

class UserActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserActivity
    
    user = factory.SubFactory(UserFactory)
    activity_type = 'page_view'
    timestamp = factory.LazyFunction(timezone.now)
    ip_address = '127.0.0.1'
    user_agent = 'Mozilla/5.0'
    details = factory.Dict({
        'path': '/',
        'method': 'GET',
        'processing_time': 100,
        'status_code': 200
    })

class CourseAnalyticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseAnalytics
    
    course = factory.SubFactory(CourseFactory)
    total_enrollments = 10
    active_enrollments = 5
    completion_rate = 80.0
    average_score = 85.0
    engagement_score = 75.0
    last_updated = factory.LazyFunction(timezone.now)

class UserAnalyticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserAnalytics
    
    user = factory.SubFactory(UserFactory)
    courses_enrolled = 2
    courses_completed = 1
    completion_rate = 50.0
    average_score = 85.0
    overall_engagement = 75.0
    last_updated = factory.LazyFunction(timezone.now)

class QuizAnalyticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuizAnalytics
    
    quiz = factory.SubFactory(QuizFactory)
    total_attempts = 20
    unique_attempters = 15
    average_score = 85.0
    pass_rate = 80.0
    last_updated = factory.LazyFunction(timezone.now)

class SystemAnalyticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SystemAnalytics
    
    active_users = 100
    concurrent_sessions = 50
    average_response_time = 200.0
    error_rate = 0.1
    cpu_usage = 30.0
    memory_usage = 40.0
    database_connections = 10
    cache_hit_rate = 85.0
    total_sessions = 1000
    timestamp = factory.LazyFunction(timezone.now)
    last_updated = factory.LazyFunction(timezone.now)

class CourseAnalyticsSummaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseAnalyticsSummary
    
    course = factory.SubFactory(CourseFactory)
    total_enrollments = 10
    active_learners = 7
    completion_rate = 80.0
    average_rating = 4.5
    engagement_score = 75.0
    last_updated = factory.LazyFunction(timezone.now) 