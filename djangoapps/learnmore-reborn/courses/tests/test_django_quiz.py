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
        
    def test_submit_answer(self):
        """Test submitting an answer to a question."""
        self.client.login(username='quiztestuser', password='testpassword')
        
        # Start the quiz
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        attempt = QuizAttempt.objects.get(quiz=self.quiz, user=self.user, status='in_progress')
        
        # Submit answer to multiple choice question
        response = self.client.post(
            reverse('submit-answer', args=[attempt.id, self.mcq.id]),
            {'choice': self.correct_choice.id, 'time_spent': 30}
        )
        
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Check if response was recorded
        question_response = QuestionResponse.objects.get(
            attempt=attempt,
            question=self.mcq
        )
        
        self.assertTrue(question_response.is_correct)
        self.assertEqual(question_response.points_earned, 1)
        
    def test_submit_wrong_answer(self):
        """Test submitting a wrong answer."""
        self.client.login(username='quiztestuser', password='testpassword')
        
        # Start the quiz
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        attempt = QuizAttempt.objects.get(quiz=self.quiz, user=self.user, status='in_progress')
        
        # Submit wrong answer to true/false question
        response = self.client.post(
            reverse('submit-answer', args=[attempt.id, self.tf_question.id]),
            {'answer': 'false', 'time_spent': 15}
        )
        
        # Check if response was recorded
        question_response = QuestionResponse.objects.get(
            attempt=attempt,
            question=self.tf_question
        )
        
        self.assertFalse(question_response.is_correct)
        self.assertEqual(question_response.points_earned, 0)
        
    def test_finish_quiz(self):
        """Test finishing a quiz and calculating score."""
        self.client.login(username='quiztestuser', password='testpassword')
        
        # Start the quiz
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        attempt = QuizAttempt.objects.get(quiz=self.quiz, user=self.user, status='in_progress')
        
        # Submit correct answers to both questions
        self.client.post(
            reverse('submit-answer', args=[attempt.id, self.mcq.id]),
            {'choice': self.correct_choice.id, 'time_spent': 30}
        )
        
        self.client.post(
            reverse('submit-answer', args=[attempt.id, self.tf_question.id]),
            {'answer': 'true', 'time_spent': 15}
        )
        
        # Finish the quiz
        response = self.client.post(reverse('finish-quiz', args=[attempt.id]))
        
        # Reload the attempt
        attempt.refresh_from_db()
        
        # Check status and score
        self.assertEqual(attempt.status, 'completed')
        self.assertEqual(attempt.score, 2)  # Both questions correct
        self.assertEqual(attempt.max_score, 2)
        self.assertTrue(attempt.is_passed)  # 100% > 70% passing score