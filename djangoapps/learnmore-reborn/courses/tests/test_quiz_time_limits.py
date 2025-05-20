from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from test_auth_settings import AuthDisabledTestCase
import json

from courses.models import (
    Course, Module, Quiz, 
    MultipleChoiceQuestion, TrueFalseQuestion,
    Choice, QuizAttempt, QuestionResponse
)

User = get_user_model()

class QuizTimeLimitTests(AuthDisabledTestCase):
    """Tests for quiz time limit functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123'
        )
        
        # Create course and module
        self.course = Course.objects.create(
            title='Test Course',
            description='Test course description',
            instructor=self.instructor,
            status='published'
        )
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test module description',
            order=1
        )
        
        # Create quiz with time limit
        self.quiz = Quiz.objects.create(
            module=self.module,
            title='Timed Quiz',
            description='Quiz with time limit',
            instructions='Complete within the time limit',
            time_limit_minutes=30,  # 30-minute time limit
            passing_score=70,
            is_published=True
        )
        
        # Create a multiple choice question
        self.question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='What is 2+2?',
            points=1,
            order=1,
            allow_multiple=False,
            explanation='Basic arithmetic'
        )
        
        # Create choices for the question
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='4',
            is_correct=True,
            order=1
        )
        Choice.objects.create(
            question=self.question,
            text='3',
            is_correct=False,
            order=2
        )
        Choice.objects.create(
            question=self.question,
            text='5',
            is_correct=False,
            order=3
        )
        
        # Enroll student in course
        from courses.models import Enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.student,
            course=self.course,
            status='active'
        )
        
        # Set up API client
        self.client = APIClient()
        
    def test_time_limit_expiration_model(self):
        """Test that QuizAttempt.mark_completed() properly handles time expiration."""
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='in_progress',
            attempt_number=1
        )
        
        # Mark as completed with timed_out=True
        attempt.mark_completed(timed_out=True)
        
        # Verify status is 'timed_out'
        self.assertEqual(attempt.status, 'timed_out')
        self.assertIsNotNone(attempt.completed_at)
        
        # Check that score is calculated
        self.assertEqual(attempt.score, 0)  # No responses, so score should be 0
        self.assertEqual(attempt.max_score, 1)  # One question worth 1 point
        
    def test_time_limit_expiration_api(self):
        """Test the timeout API endpoint for quiz attempts."""
        # Log in as student
        self.client.force_authenticate(user=self.student)
        
        # Create a quiz attempt
        start_response = self.client.post(
            reverse('quiz-start-attempt', args=[self.quiz.id])
        )
        self.assertEqual(start_response.status_code, status.HTTP_201_CREATED)
        
        attempt_id = start_response.data['id']
        
        # Submit a response to the question
        response_data = {
            'question': self.question.id,
            'response_data': {'selected_choice': self.correct_choice.id},
            'time_spent_seconds': 120
        }
        submit_response = self.client.post(
            reverse('quiz-attempt-submit-response', args=[attempt_id]),
            response_data,
            format='json'
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        
        # Trigger timeout
        timeout_response = self.client.post(
            reverse('quiz-attempt-timeout', args=[attempt_id])
        )
        self.assertEqual(timeout_response.status_code, status.HTTP_200_OK)
        
        # Verify attempt is marked as timed out
        attempt = QuizAttempt.objects.get(id=attempt_id)
        self.assertEqual(attempt.status, 'timed_out')
        
        # Verify score has been calculated
        self.assertEqual(attempt.score, 1)  # Correct answer was submitted
        self.assertEqual(attempt.max_score, 1)
        
    def test_time_limit_expired_attempt_cannot_be_modified(self):
        """Test that timed-out attempts cannot be modified."""
        # Create and timeout an attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='in_progress',
            attempt_number=1
        )
        attempt.mark_completed(timed_out=True)
        
        # Try to submit a response after timeout
        self.client.force_authenticate(user=self.student)
        response_data = {
            'question': self.question.id,
            'response_data': {'selected_choice': self.correct_choice.id},
            'time_spent_seconds': 120
        }
        response = self.client.post(
            reverse('quiz-attempt-submit-response', args=[attempt.id]),
            response_data,
            format='json'
        )
        
        # Expect a 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already been completed', response.data['detail'])
        
    def test_simulated_time_expiration(self):
        """Test a complete scenario with a backdated start time to simulate expiration."""
        # Create an attempt with a start time in the past exceeding the time limit
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='in_progress',
            attempt_number=1,
            # Backdated to exceed time limit
            started_at=timezone.now() - timedelta(minutes=self.quiz.time_limit_minutes + 5)
        )
        
        # Add a response
        response = QuestionResponse.objects.create(
            attempt=attempt,
            question=self.question,
            response_data={'selected_choice': self.correct_choice.id}
        )
        response.check_answer()
        
        # Mark as timed out
        attempt.mark_completed(timed_out=True)
        
        # Verify time spent is calculated correctly (should be > time limit)
        self.assertGreaterEqual(attempt.time_spent_seconds, self.quiz.time_limit_minutes * 60)
        
        # Verify status and score
        self.assertEqual(attempt.status, 'timed_out')
        self.assertEqual(attempt.score, 1)  # Correct answer was submitted before timeout
        self.assertTrue(attempt.is_passed)  # Should pass with 100% (1/1)
        
    def test_timeout_with_unanswered_questions(self):
        """Test timeout behavior when not all questions have been answered."""
        # Add another question to make the test more realistic
        question2 = TrueFalseQuestion.objects.create(
            quiz=self.quiz,
            text='Is the sky blue?',
            points=1,
            order=2,
            correct_answer=True,
            explanation='Basic observation'
        )
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='in_progress',
            attempt_number=1
        )
        
        # Only answer the first question
        response = QuestionResponse.objects.create(
            attempt=attempt,
            question=self.question,
            response_data={'selected_choice': self.correct_choice.id}
        )
        response.check_answer()
        
        # Mark as timed out without answering the second question
        attempt.mark_completed(timed_out=True)
        
        # Verify score calculation (1 out of 2 questions answered correctly)
        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.max_score, 2)
        self.assertEqual(attempt.status, 'timed_out')
        self.assertFalse(attempt.is_passed)  # 50% is below passing score of 70%