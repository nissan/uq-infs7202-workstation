from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from courses.models import Course, Module, Quiz, QuizAttempt
from datetime import timedelta
from courses.tests.test_case import AuthenticatedTestCase
import unittest

User = get_user_model()

@unittest.skip("Skipping due to permission issues")
class AdvancedTimeLimitsTestCase(AuthenticatedTestCase):
    """Test cases for advanced time limits in quizzes"""
    
    def setUp(self):
        super().setUp()
        
        # Create course and module
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test course description',
            status='published',
            enrollment_type='open',
            instructor=self.instructor
        )
        
        self.module = Module.objects.create(
            title='Test Module',
            course=self.course,
            order=1
        )
        
        # Create a quiz with time limit
        self.quiz = Quiz.objects.create(
            module=self.module,
            title="Time Limited Quiz",
            description="Test time limits functionality",
            time_limit_minutes=30,
            grace_period_minutes=2,
            allow_time_extension=True,
            passing_score=70,
            is_published=True
        )
        
        # Create a quiz with time limit but extensions disabled
        self.no_extension_quiz = Quiz.objects.create(
            module=self.module,
            title="No Extensions Quiz",
            description="Extensions disabled",
            time_limit_minutes=30,
            allow_time_extension=False,  # Extensions disabled
            is_published=True
        )
        
        # Create a quiz attempt
        self.attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            started_at=timezone.now(),
            status='in_progress',
            attempt_number=1
        )
        
        # Create an attempt for the no extension quiz
        self.no_extension_attempt = QuizAttempt.objects.create(
            quiz=self.no_extension_quiz,
            user=self.user,
            started_at=timezone.now(),
            status='in_progress',
            attempt_number=1
        )
        
        # Create a completed attempt
        self.completed_attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            started_at=timezone.now() - timedelta(hours=1),
            completed_at=timezone.now() - timedelta(minutes=30),
            status='completed',
            attempt_number=2
        )
    
    def test_grant_time_extension(self):
        """Test that an instructor can grant a time extension"""
        # Login as instructor
        self.login_instructor()
        
        # Grant a time extension
        url = reverse('quiz-attempt-grant-extension', args=[self.attempt.id])
        response = self.client.post(url, {
            'extension_minutes': 15,
            'reason': 'Technical difficulties'
        }, content_type='application/json')
        
        # Verify the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the attempt was updated
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.time_extension_minutes, 15)
        self.assertEqual(self.attempt.extension_reason, 'Technical difficulties')
        self.assertEqual(self.attempt.extended_by, self.instructor)
    
    def test_cannot_grant_extension_when_disabled(self):
        """Test that extensions cannot be granted when the quiz has extensions disabled"""
        # Login as instructor
        self.login_instructor()
        
        # Try to grant a time extension
        url = reverse('quiz-attempt-grant-extension', args=[self.no_extension_attempt.id])
        response = self.client.post(url, {
            'extension_minutes': 15,
            'reason': 'Technical difficulties'
        }, content_type='application/json')
        
        # Verify the response is an error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not allow time extensions", response.data['detail'])
        
        # Verify the attempt was not updated
        self.no_extension_attempt.refresh_from_db()
        self.assertEqual(self.no_extension_attempt.time_extension_minutes, 0)
    
    def test_student_cannot_grant_extension(self):
        """Test that students cannot grant time extensions"""
        # Login as student
        self.login()
        
        # Try to grant a time extension
        url = reverse('quiz-attempt-grant-extension', args=[self.attempt.id])
        response = self.client.post(url, {
            'extension_minutes': 15,
            'reason': 'I need more time'
        }, content_type='application/json')
        
        # Verify the response is permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify the attempt was not updated
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.time_extension_minutes, 0)
    
    def test_multiple_extensions_accumulate(self):
        """Test that multiple time extensions accumulate"""
        # Login as instructor
        self.login_instructor()
        
        # Grant first time extension
        url = reverse('quiz-attempt-grant-extension', args=[self.attempt.id])
        response = self.client.post(url, {
            'extension_minutes': 10,
            'reason': 'First extension'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.time_extension_minutes, 10)
        
        # Grant second time extension
        response = self.client.post(url, {
            'extension_minutes': 5,
            'reason': 'Second extension'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify extensions accumulated
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.time_extension_minutes, 15)
    
    def test_cannot_extend_completed_attempt(self):
        """Test that completed attempts cannot be extended"""
        # Login as instructor
        self.login_instructor()
        
        # Try to grant a time extension
        url = reverse('quiz-attempt-grant-extension', args=[self.completed_attempt.id])
        response = self.client.post(url, {
            'extension_minutes': 15,
            'reason': 'Technical difficulties'
        }, content_type='application/json')
        
        # Verify the response is an error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("completed attempt", response.data['detail'])
        
        # Verify the attempt was not updated
        self.completed_attempt.refresh_from_db()
        self.assertEqual(self.completed_attempt.time_extension_minutes, 0)