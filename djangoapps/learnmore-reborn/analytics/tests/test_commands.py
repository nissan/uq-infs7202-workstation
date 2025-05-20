from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone
from django.core.cache import cache
from ..models import (
    UserActivity, CourseAnalytics, UserAnalytics,
    QuizAnalytics, SystemAnalytics
)
from .factories import (
    UserFactory, CourseFactory, QuizFactory,
    UserActivityFactory, CourseAnalyticsFactory,
    UserAnalyticsFactory, QuizAnalyticsFactory,
    SystemAnalyticsFactory
)

class CalculateAnalyticsCommandTest(TestCase):
    def setUp(self):
        # Create test data
        self.user = UserFactory()
        self.course = CourseFactory()
        self.quiz = QuizFactory(course=self.course)
        
        # Create some user activities
        for _ in range(5):
            UserActivityFactory(user=self.user)
        
        # Create initial analytics records
        self.course_analytics = CourseAnalyticsFactory(course=self.course)
        self.user_analytics = UserAnalyticsFactory(user=self.user)
        self.quiz_analytics = QuizAnalyticsFactory(quiz=self.quiz)
        self.system_analytics = SystemAnalyticsFactory()
        
        # Clear cache before each test
        cache.clear()
    
    def test_calculate_all_analytics(self):
        """Test calculating all analytics types"""
        # Run the command
        call_command('calculate_analytics', '--all')
        
        # Verify course analytics
        course_analytics = CourseAnalytics.objects.get(course=self.course)
        self.assertIsNotNone(course_analytics.last_calculated)
        self.assertGreater(course_analytics.total_enrollments, 0)
        
        # Verify user analytics
        user_analytics = UserAnalytics.objects.get(user=self.user)
        self.assertIsNotNone(user_analytics.last_calculated)
        self.assertGreater(user_analytics.total_activities, 0)
        
        # Verify quiz analytics
        quiz_analytics = QuizAnalytics.objects.get(quiz=self.quiz)
        self.assertIsNotNone(quiz_analytics.last_calculated)
        
        # Verify system analytics
        system_analytics = SystemAnalytics.objects.latest('timestamp')
        self.assertIsNotNone(system_analytics)
        self.assertGreater(system_analytics.active_users, 0)
    
    def test_calculate_specific_analytics(self):
        """Test calculating specific analytics types"""
        # Test course analytics
        call_command('calculate_analytics', '--type', 'course')
        course_analytics = CourseAnalytics.objects.get(course=self.course)
        self.assertIsNotNone(course_analytics.last_calculated)
        
        # Test user analytics
        call_command('calculate_analytics', '--type', 'user')
        user_analytics = UserAnalytics.objects.get(user=self.user)
        self.assertIsNotNone(user_analytics.last_calculated)
        
        # Test quiz analytics
        call_command('calculate_analytics', '--type', 'quiz')
        quiz_analytics = QuizAnalytics.objects.get(quiz=self.quiz)
        self.assertIsNotNone(quiz_analytics.last_calculated)
        
        # Test system analytics
        call_command('calculate_analytics', '--type', 'system')
        system_analytics = SystemAnalytics.objects.latest('timestamp')
        self.assertIsNotNone(system_analytics)
    
    def test_calculate_with_force(self):
        """Test force recalculation of analytics"""
        # Get initial calculation times
        initial_course_time = CourseAnalytics.objects.get(course=self.course).last_calculated
        initial_user_time = UserAnalytics.objects.get(user=self.user).last_calculated
        
        # Run command without force
        call_command('calculate_analytics', '--all')
        
        # Verify no recalculation occurred
        self.assertEqual(
            CourseAnalytics.objects.get(course=self.course).last_calculated,
            initial_course_time
        )
        self.assertEqual(
            UserAnalytics.objects.get(user=self.user).last_calculated,
            initial_user_time
        )
        
        # Run command with force
        call_command('calculate_analytics', '--all', '--force')
        
        # Verify recalculation occurred
        self.assertNotEqual(
            CourseAnalytics.objects.get(course=self.course).last_calculated,
            initial_course_time
        )
        self.assertNotEqual(
            UserAnalytics.objects.get(user=self.user).last_calculated,
            initial_user_time
        )
    
    def test_calculate_with_date_range(self):
        """Test calculating analytics for specific date range"""
        # Create activities with specific dates
        old_date = timezone.now() - timezone.timedelta(days=30)
        recent_date = timezone.now() - timezone.timedelta(days=1)
        
        UserActivityFactory(
            user=self.user,
            timestamp=old_date
        )
        UserActivityFactory(
            user=self.user,
            timestamp=recent_date
        )
        
        # Calculate analytics for recent period only
        call_command(
            'calculate_analytics',
            '--type', 'user',
            '--start-date', (timezone.now() - timezone.timedelta(days=7)).strftime('%Y-%m-%d'),
            '--end-date', timezone.now().strftime('%Y-%m-%d')
        )
        
        # Verify only recent activity is included
        user_analytics = UserAnalytics.objects.get(user=self.user)
        self.assertEqual(user_analytics.total_activities, 1)
    
    def test_calculate_with_invalid_type(self):
        """Test handling of invalid analytics type"""
        with self.assertRaises(SystemExit):
            call_command('calculate_analytics', '--type', 'invalid_type')
    
    def test_calculate_with_invalid_date_range(self):
        """Test handling of invalid date range"""
        with self.assertRaises(SystemExit):
            call_command(
                'calculate_analytics',
                '--start-date', 'invalid-date',
                '--end-date', 'invalid-date'
            )
    
    def test_calculate_with_cache(self):
        """Test that analytics calculations use caching"""
        # First calculation
        call_command('calculate_analytics', '--all')
        
        # Get cache keys
        cache_keys = [
            f'course_analytics_{self.course.id}',
            f'user_analytics_{self.user.id}',
            f'quiz_analytics_{self.quiz.id}',
            'system_analytics_current'
        ]
        
        # Verify cache is populated
        for key in cache_keys:
            self.assertIsNotNone(cache.get(key))
        
        # Second calculation should use cache
        call_command('calculate_analytics', '--all')
        
        # Verify cache is still valid
        for key in cache_keys:
            self.assertIsNotNone(cache.get(key))
        
        # Force recalculation should clear cache
        call_command('calculate_analytics', '--all', '--force')
        
        # Verify cache is updated
        for key in cache_keys:
            self.assertIsNotNone(cache.get(key))
    
    def test_calculate_with_error_handling(self):
        """Test error handling during analytics calculation"""
        # Create invalid data
        invalid_analytics = CourseAnalyticsFactory(course=None)
        
        # Run command with error handling
        call_command('calculate_analytics', '--all', '--continue-on-error')
        
        # Verify command completed despite error
        self.assertTrue(CourseAnalytics.objects.filter(course=self.course).exists())
        
        # Run command without error handling
        with self.assertRaises(Exception):
            call_command('calculate_analytics', '--all') 