from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.cache import cache
from analytics.models import (
    CourseAnalytics, UserAnalytics, QuizAnalytics,
    SystemAnalytics, LearnerAnalytics
)
from courses.models import Course
from django.contrib.auth.models import User
from quizzes.models import Quiz
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Calculate analytics metrics for courses, users, and quizzes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recalculation of all analytics',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['course', 'user', 'quiz', 'system', 'all'],
            default='all',
            help='Type of analytics to calculate',
        )
        parser.add_argument(
            '--specific-ids',
            type=str,
            help='Comma-separated list of specific IDs to calculate',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        analytics_type = options['type']
        specific_ids = options['specific_ids']
        
        if specific_ids:
            specific_ids = [int(id.strip()) for id in specific_ids.split(',')]
        
        try:
            if analytics_type in ['course', 'all']:
                self._calculate_course_analytics(force, specific_ids)
            
            if analytics_type in ['user', 'all']:
                self._calculate_user_analytics(force, specific_ids)
            
            if analytics_type in ['quiz', 'all']:
                self._calculate_quiz_analytics(force, specific_ids)
            
            if analytics_type in ['system', 'all']:
                self._calculate_system_analytics(force)
            
            self.stdout.write(self.style.SUCCESS('Successfully calculated analytics'))
            
        except Exception as e:
            logger.error(f"Error calculating analytics: {e}")
            self.stdout.write(self.style.ERROR(f'Error calculating analytics: {e}'))
    
    def _calculate_course_analytics(self, force, specific_ids):
        """Calculate analytics for courses"""
        queryset = Course.objects.all()
        if specific_ids:
            queryset = queryset.filter(id__in=specific_ids)
        
        for course in queryset:
            try:
                analytics, created = CourseAnalytics.objects.get_or_create(course=course)
                
                if force or not analytics.last_calculated or \
                   (timezone.now() - analytics.last_calculated).days > 0:
                    analytics.calculate_metrics()
                    self.stdout.write(f'Calculated analytics for course: {course.title}')
                    
                    # Cache course analytics
                    cache_key = f'course_analytics_{course.id}'
                    cache.set(cache_key, analytics.to_dict(), timeout=3600)  # Cache for 1 hour
                    
            except Exception as e:
                logger.error(f"Error calculating analytics for course {course.id}: {e}")
                self.stdout.write(self.style.WARNING(
                    f'Error calculating analytics for course {course.title}: {e}'
                ))
    
    def _calculate_user_analytics(self, force, specific_ids):
        """Calculate analytics for users"""
        queryset = User.objects.filter(is_active=True)
        if specific_ids:
            queryset = queryset.filter(id__in=specific_ids)
        
        for user in queryset:
            try:
                analytics, created = UserAnalytics.objects.get_or_create(user=user)
                
                if force or not analytics.last_calculated or \
                   (timezone.now() - analytics.last_calculated).days > 0:
                    analytics.calculate_metrics()
                    self.stdout.write(f'Calculated analytics for user: {user.username}')
                    
                    # Cache user analytics
                    cache_key = f'user_analytics_{user.id}'
                    cache.set(cache_key, analytics.to_dict(), timeout=3600)  # Cache for 1 hour
                    
            except Exception as e:
                logger.error(f"Error calculating analytics for user {user.id}: {e}")
                self.stdout.write(self.style.WARNING(
                    f'Error calculating analytics for user {user.username}: {e}'
                ))
    
    def _calculate_quiz_analytics(self, force, specific_ids):
        """Calculate analytics for quizzes"""
        queryset = Quiz.objects.all()
        if specific_ids:
            queryset = queryset.filter(id__in=specific_ids)
        
        for quiz in queryset:
            try:
                analytics, created = QuizAnalytics.objects.get_or_create(quiz=quiz)
                
                if force or not analytics.last_calculated or \
                   (timezone.now() - analytics.last_calculated).days > 0:
                    analytics.calculate_metrics()
                    self.stdout.write(f'Calculated analytics for quiz: {quiz.title}')
                    
                    # Cache quiz analytics
                    cache_key = f'quiz_analytics_{quiz.id}'
                    cache.set(cache_key, analytics.to_dict(), timeout=3600)  # Cache for 1 hour
                    
            except Exception as e:
                logger.error(f"Error calculating analytics for quiz {quiz.id}: {e}")
                self.stdout.write(self.style.WARNING(
                    f'Error calculating analytics for quiz {quiz.title}: {e}'
                ))
    
    def _calculate_system_analytics(self, force):
        """Calculate system-wide analytics"""
        try:
            # Get or create current system metrics
            metrics, created = SystemAnalytics.objects.get_or_create(
                timestamp__date=timezone.now().date(),
                defaults={'timestamp': timezone.now()}
            )
            
            if force or not metrics.last_calculated or \
               (timezone.now() - metrics.last_calculated).hours > 0:
                metrics.calculate_metrics()
                self.stdout.write('Calculated system analytics')
                
                # Cache system metrics
                cache_key = 'system_metrics_current'
                cache.set(cache_key, metrics.to_dict(), timeout=300)  # Cache for 5 minutes
                
        except Exception as e:
            logger.error(f"Error calculating system analytics: {e}")
            self.stdout.write(self.style.WARNING(f'Error calculating system analytics: {e}')) 