from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from courses.models import Course, Module, Quiz, QuizAttempt, Question, QuestionResponse
from courses.models import MultipleChoiceQuestion, Choice
from datetime import timedelta
from api_test_utils import APITestCaseBase

User = get_user_model()

class EnhancedFeedbackTest(APITestCaseBase):
    """Test cases for enhanced feedback in quizzes"""
    
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
        
        # Create a quiz with conditional feedback
        self.quiz = Quiz.objects.create(
            module=self.module,
            title="Feedback Test Quiz",
            description="Testing enhanced feedback functionality",
            general_feedback="Thank you for taking this quiz!",
            conditional_feedback={
                "0-59": "You need more practice. Try reviewing the course material again.",
                "60-79": "Good effort! You're on the right track but still have room for improvement.",
                "80-100": "Excellent work! You have a solid understanding of the material."
            },
            passing_score=70,
            is_published=True
        )
        
        # Create a quiz with feedback delay
        self.delayed_feedback_quiz = Quiz.objects.create(
            module=self.module,
            title="Delayed Feedback Quiz",
            description="Testing feedback delay",
            general_feedback="Thank you for taking this quiz!",
            feedback_delay_minutes=30,
            is_published=True
        )
        
        # Create a multiple choice question - using inheritance
        self.question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text="What is 2+2?",
            question_type='multiple_choice',
            order=1,
            points=5
        )
        
        # Create choices
        self.choice1 = Choice.objects.create(
            question=self.question,
            text="4",
            is_correct=True,
            order=1
        )
        
        self.choice2 = Choice.objects.create(
            question=self.question,
            text="5",
            is_correct=False,
            order=2
        )
        
        # Create a quiz attempt
        self.attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='completed',
            started_at=timezone.now() - timedelta(minutes=30),
            completed_at=timezone.now() - timedelta(minutes=20),
            score=5,  # 100% score
            max_score=5,
            is_passed=True
        )
        
        # Create a question response
        self.response = QuestionResponse.objects.create(
            attempt=self.attempt,
            question=self.question,
            response_data={'selected_choice': self.choice1.id},
            is_correct=True,
            points_earned=5,
            feedback="Correct!"
        )
        
        # Create a recent attempt for the delayed feedback quiz
        self.recent_attempt = QuizAttempt.objects.create(
            quiz=self.delayed_feedback_quiz,
            user=self.user,
            status='completed',
            started_at=timezone.now() - timedelta(minutes=20),
            completed_at=timezone.now() - timedelta(minutes=10),
            score=4,
            max_score=5,
            is_passed=True
        )
    
    def test_conditional_feedback_in_api_response(self):
        """Test that conditional feedback is included in API response"""
        # Login as student
        self.login()
        
        # Get the attempt result via API
        url = reverse('quiz-attempt-result', args=[self.attempt.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['feedback_available'])
        self.assertIn("Excellent work!", response.data['conditional_feedback'])
    
    def test_feedback_delay(self):
        """Test that feedback respects delay settings"""
        # Login as student
        self.login()
        
        # Get the attempt result via API
        url = reverse('quiz-attempt-result', args=[self.recent_attempt.id])
        response = self.client.get(url)
        
        # Since the attempt was completed 10 minutes ago but delay is 30 minutes,
        # feedback should not be available yet
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['feedback_available'])
        self.assertEqual(response.data['conditional_feedback'], "")