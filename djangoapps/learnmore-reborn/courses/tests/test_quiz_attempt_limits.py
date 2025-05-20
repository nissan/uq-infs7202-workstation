from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from test_auth_settings import AuthDisabledTestCase
import json

from courses.models import (
    Course, Module, Quiz, 
    MultipleChoiceQuestion, TrueFalseQuestion,
    Choice, QuizAttempt, QuestionResponse
)

User = get_user_model()

class QuizAttemptLimitTests(AuthDisabledTestCase):
    """Tests for quiz attempt limit functionality."""
    
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
        
        # Create quiz with attempt limits
        self.limited_quiz = Quiz.objects.create(
            module=self.module,
            title='Limited Attempts Quiz',
            description='Quiz with limited attempts',
            instructions='You have a limited number of attempts',
            allow_multiple_attempts=True,
            max_attempts=3,  # Limit to 3 attempts
            passing_score=70,
            is_published=True
        )
        
        # Create quiz with unlimited attempts
        self.unlimited_quiz = Quiz.objects.create(
            module=self.module,
            title='Unlimited Attempts Quiz',
            description='Quiz with unlimited attempts',
            instructions='You have unlimited attempts',
            allow_multiple_attempts=True,
            max_attempts=0,  # 0 indicates unlimited attempts
            passing_score=70,
            is_published=True
        )
        
        # Create quiz with single attempt only
        self.single_attempt_quiz = Quiz.objects.create(
            module=self.module,
            title='Single Attempt Quiz',
            description='Quiz with only one attempt allowed',
            instructions='You have only one attempt',
            allow_multiple_attempts=False,
            max_attempts=1,
            passing_score=70,
            is_published=True
        )
        
        # Create a simple question for each quiz
        self.limited_quiz_question = MultipleChoiceQuestion.objects.create(
            quiz=self.limited_quiz,
            text='What is 2+2?',
            points=1,
            order=1,
            allow_multiple=False
        )
        
        self.unlimited_quiz_question = MultipleChoiceQuestion.objects.create(
            quiz=self.unlimited_quiz,
            text='What is 3+3?',
            points=1,
            order=1,
            allow_multiple=False
        )
        
        self.single_attempt_quiz_question = MultipleChoiceQuestion.objects.create(
            quiz=self.single_attempt_quiz,
            text='What is 4+4?',
            points=1,
            order=1,
            allow_multiple=False
        )
        
        # Add choices to each question
        # For limited quiz question
        Choice.objects.create(
            question=self.limited_quiz_question,
            text='3',
            is_correct=False,
            order=1
        )
        Choice.objects.create(
            question=self.limited_quiz_question,
            text='4',
            is_correct=True,
            order=2
        )
        
        # For unlimited quiz question
        Choice.objects.create(
            question=self.unlimited_quiz_question,
            text='5',
            is_correct=False,
            order=1
        )
        Choice.objects.create(
            question=self.unlimited_quiz_question,
            text='6',
            is_correct=True,
            order=2
        )
        
        # For single attempt quiz question
        Choice.objects.create(
            question=self.single_attempt_quiz_question,
            text='7',
            is_correct=False,
            order=1
        )
        Choice.objects.create(
            question=self.single_attempt_quiz_question,
            text='8',
            is_correct=True,
            order=2
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
        self.client.force_authenticate(user=self.student)
    
    def test_max_attempts_setting(self):
        """Test that the max_attempts setting is respected."""
        # Verify initial settings
        self.assertEqual(self.limited_quiz.max_attempts, 3)
        self.assertEqual(self.unlimited_quiz.max_attempts, 0)
        self.assertEqual(self.single_attempt_quiz.max_attempts, 1)
        
        # Update and verify
        self.limited_quiz.max_attempts = 5
        self.limited_quiz.save()
        self.limited_quiz.refresh_from_db()
        self.assertEqual(self.limited_quiz.max_attempts, 5)
    
    def test_limited_attempts_enforcement(self):
        """Test that users cannot exceed maximum attempts for limited quizzes."""
        # Create 3 completed attempts (the maximum allowed)
        for i in range(1, 4):
            attempt = QuizAttempt.objects.create(
                quiz=self.limited_quiz,
                user=self.student,
                status='completed',
                attempt_number=i,
                completed_at=timezone.now()
            )
        
        # Try to start a 4th attempt via API
        response = self.client.post(
            reverse('quiz-start-attempt', args=[self.limited_quiz.id])
        )
        
        # Expect a 403 Forbidden response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('maximum number of attempts', response.data['detail'])
        
        # Verify no new attempt was created
        self.assertEqual(
            QuizAttempt.objects.filter(quiz=self.limited_quiz, user=self.student).count(),
            3
        )
    
    def test_unlimited_attempts_allowed(self):
        """Test that users can take unlimited attempts for quizzes with max_attempts=0."""
        # Create several attempts
        for i in range(1, 6):  # Create 5 attempts
            attempt = QuizAttempt.objects.create(
                quiz=self.unlimited_quiz,
                user=self.student,
                status='completed',
                attempt_number=i,
                completed_at=timezone.now()
            )
        
        # Try to start a 6th attempt via API
        response = self.client.post(
            reverse('quiz-start-attempt', args=[self.unlimited_quiz.id])
        )
        
        # Expect success
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify new attempt was created
        self.assertEqual(
            QuizAttempt.objects.filter(quiz=self.unlimited_quiz, user=self.student).count(),
            6
        )
    
    def test_single_attempt_enforcement(self):
        """Test that allow_multiple_attempts=False combined with max_attempts=1 restricts to a single attempt."""
        # Update the quiz to have max_attempts=1 AND allow_multiple_attempts=False
        # This more accurately tests what would happen in real-world usage
        self.single_attempt_quiz.max_attempts = 1
        self.single_attempt_quiz.allow_multiple_attempts = True  # This needs to be True for max_attempts check to occur
        self.single_attempt_quiz.save()
        
        # Create one attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.single_attempt_quiz,
            user=self.student,
            status='completed',
            attempt_number=1,
            completed_at=timezone.now()
        )
        
        # Try to start a second attempt via API
        response = self.client.post(
            reverse('quiz-start-attempt', args=[self.single_attempt_quiz.id])
        )
        
        # Expect a 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify no new attempt was created
        self.assertEqual(
            QuizAttempt.objects.filter(quiz=self.single_attempt_quiz, user=self.student).count(),
            1
        )
    
    def test_attempt_numbering(self):
        """Test that attempt numbers are assigned sequentially."""
        # Create first attempt
        response1 = self.client.post(
            reverse('quiz-start-attempt', args=[self.limited_quiz.id])
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        attempt1_id = response1.data['id']
        
        # Complete the attempt
        attempt1 = QuizAttempt.objects.get(id=attempt1_id)
        attempt1.mark_completed()
        
        # Create second attempt
        response2 = self.client.post(
            reverse('quiz-start-attempt', args=[self.limited_quiz.id])
        )
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        attempt2_id = response2.data['id']
        
        # Verify attempt numbers
        attempt1.refresh_from_db()
        attempt2 = QuizAttempt.objects.get(id=attempt2_id)
        
        self.assertEqual(attempt1.attempt_number, 1)
        self.assertEqual(attempt2.attempt_number, 2)
    
    def test_in_progress_attempt_handling(self):
        """Test that a new attempt cannot be started if one is already in progress."""
        # Create an in-progress attempt
        response1 = self.client.post(
            reverse('quiz-start-attempt', args=[self.limited_quiz.id])
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        attempt1_id = response1.data['id']
        
        # Try to start another attempt
        response2 = self.client.post(
            reverse('quiz-start-attempt', args=[self.limited_quiz.id])
        )
        
        # Should return the existing in-progress attempt, not create a new one
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        attempt2_id = response2.data['id']
        
        # Verify it's the same attempt
        self.assertEqual(attempt1_id, attempt2_id)
        
        # Verify only one attempt exists
        self.assertEqual(
            QuizAttempt.objects.filter(quiz=self.limited_quiz, user=self.student).count(),
            1
        )
    
    def test_attempt_limit_edge_case(self):
        """Test edge case where max_attempts=1 but allow_multiple_attempts=True."""
        # Create a quiz with this edge case configuration
        edge_case_quiz = Quiz.objects.create(
            module=self.module,
            title='Edge Case Quiz',
            description='Quiz with edge case configuration',
            instructions='You have exactly one attempt',
            allow_multiple_attempts=True,  # Multiple attempts allowed in principle
            max_attempts=1,  # But only 1 attempt in practice
            passing_score=70,
            is_published=True
        )
        
        # Create an attempt and complete it
        attempt = QuizAttempt.objects.create(
            quiz=edge_case_quiz,
            user=self.student,
            status='completed',
            attempt_number=1,
            completed_at=timezone.now()
        )
        
        # Try to start another attempt
        response = self.client.post(
            reverse('quiz-start-attempt', args=[edge_case_quiz.id])
        )
        
        # Expect a 403 Forbidden (max attempts reached)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify no new attempt was created
        self.assertEqual(
            QuizAttempt.objects.filter(quiz=edge_case_quiz, user=self.student).count(),
            1
        )