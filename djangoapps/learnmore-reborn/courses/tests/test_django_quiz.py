from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import (
    Course, Module, Quiz, MultipleChoiceQuestion, TrueFalseQuestion,
    Choice, QuizAttempt, QuestionResponse, Enrollment
)

User = get_user_model()

class QuizIntegrationTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='quiztestuser',
            email='quiztest@example.com',
            password='testpassword'
        )
        
        # Create user profile if needed
        if hasattr(User, 'profile'):
            from users.models import UserProfile
            try:
                profile = UserProfile.objects.get(user=self.user)
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(
                    user=self.user,
                    is_instructor=True  # Give instructor permissions
                )
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Course for quiz testing',
            instructor=self.user,
            status='published',
            enrollment_type='open'
        )
        
        # Create a module
        self.module = Module.objects.create(
            title='Test Module',
            course=self.course,
            description='Module for quiz testing',
            order=1
        )
        
        # Create a quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            module=self.module,
            description='A test quiz for integration testing',
            instructions='Answer all questions',
            time_limit_minutes=10,
            passing_score=70,
            is_published=True,
            allow_multiple_attempts=True
        )
        
        # Create a multiple choice question
        self.mcq = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='What is 2+2?',
            order=1,
            points=1,
            allow_multiple=False
        )
        
        # Create choices
        Choice.objects.create(question=self.mcq, text='3', is_correct=False, order=1)
        self.correct_choice = Choice.objects.create(question=self.mcq, text='4', is_correct=True, order=2)
        Choice.objects.create(question=self.mcq, text='5', is_correct=False, order=3)
        
        # Create a true/false question
        self.tf_question = TrueFalseQuestion.objects.create(
            quiz=self.quiz,
            text='The sky is blue.',
            order=2,
            points=1,
            correct_answer=True
        )
        
        # Enroll the user in the course
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )

    def test_start_quiz(self):
        """Test starting a quiz creates an attempt."""
        self.client.login(username='quiztestuser', password='testpassword')
        
        # Start the quiz
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Check if an attempt was created
        attempt = QuizAttempt.objects.filter(
            quiz=self.quiz,
            user=self.user,
            status='in_progress'
        ).first()
        
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.attempt_number, 1)