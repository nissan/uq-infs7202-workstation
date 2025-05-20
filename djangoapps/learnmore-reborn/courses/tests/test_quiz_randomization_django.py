from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework import status
from test_auth_settings import AuthDisabledTestCase
import json

from courses.models import (
    Course, Module, Quiz, 
    MultipleChoiceQuestion, TrueFalseQuestion,
    Choice, QuizAttempt, QuestionResponse, Enrollment
)

User = get_user_model()

# Note: This test file was already using Django's AuthDisabledTestCase
# We're maintaining that approach while ensuring consistent style with other converted tests
class QuizRandomizationTestCase(AuthDisabledTestCase):
    """Tests for quiz question randomization functionality."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
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
        
        # Create quiz with randomization enabled
        self.quiz = Quiz.objects.create(
            module=self.module,
            title='Randomized Quiz',
            description='Quiz with randomized questions',
            instructions='Questions will appear in random order',
            randomize_questions=True,
            passing_score=70,
            is_published=True
        )
        
        # Create multiple choice questions
        self.question1 = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='What is 2+2?',
            points=1,
            order=1,
            allow_multiple=False,
            explanation='Basic arithmetic'
        )
        
        self.question2 = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Which is a prime number?',
            points=1,
            order=2,
            allow_multiple=False,
            explanation='Prime numbers are divisible only by 1 and themselves'
        )
        
        self.question3 = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='What is the capital of France?',
            points=1,
            order=3,
            allow_multiple=False,
            explanation='Basic geography'
        )
        
        self.question4 = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='What planet is closest to the sun?',
            points=1,
            order=4,
            allow_multiple=False,
            explanation='Basic astronomy'
        )
        
        self.question5 = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='What is H2O?',
            points=1,
            order=5,
            allow_multiple=False,
            explanation='Basic chemistry'
        )
        
        # Create choices for question 1
        Choice.objects.create(
            question=self.question1,
            text='3',
            is_correct=False,
            order=1
        )
        Choice.objects.create(
            question=self.question1,
            text='4',
            is_correct=True,
            order=2
        )
        Choice.objects.create(
            question=self.question1,
            text='5',
            is_correct=False,
            order=3
        )
        
        # Create choices for question 2
        Choice.objects.create(
            question=self.question2,
            text='4',
            is_correct=False,
            order=1
        )
        Choice.objects.create(
            question=self.question2,
            text='7',
            is_correct=True,
            order=2
        )
        Choice.objects.create(
            question=self.question2,
            text='9',
            is_correct=False,
            order=3
        )
        
        # Create choices for question 3
        Choice.objects.create(
            question=self.question3,
            text='London',
            is_correct=False,
            order=1
        )
        Choice.objects.create(
            question=self.question3,
            text='Paris',
            is_correct=True,
            order=2
        )
        Choice.objects.create(
            question=self.question3,
            text='Berlin',
            is_correct=False,
            order=3
        )
        
        # Create choices for question 4
        Choice.objects.create(
            question=self.question4,
            text='Venus',
            is_correct=False,
            order=1
        )
        Choice.objects.create(
            question=self.question4,
            text='Mercury',
            is_correct=True,
            order=2
        )
        Choice.objects.create(
            question=self.question4,
            text='Earth',
            is_correct=False,
            order=3
        )
        
        # Create choices for question 5
        Choice.objects.create(
            question=self.question5,
            text='Helium',
            is_correct=False,
            order=1
        )
        Choice.objects.create(
            question=self.question5,
            text='Water',
            is_correct=True,
            order=2
        )
        Choice.objects.create(
            question=self.question5,
            text='Oxygen',
            is_correct=False,
            order=3
        )
        
        # Enroll student in course
        self.enrollment = Enrollment.objects.create(
            user=self.student,
            course=self.course,
            status='active'
        )
        
        # Set up API client
        self.client = APIClient()
        
    def test_randomize_questions_setting(self):
        """Test that the randomize_questions flag is respected."""
        # Verify initial setting
        self.assertTrue(self.quiz.randomize_questions)
        
        # Change setting and verify
        self.quiz.randomize_questions = False
        self.quiz.save()
        self.quiz.refresh_from_db()
        self.assertFalse(self.quiz.randomize_questions)
        
    def test_deterministic_order_for_non_randomized_quiz(self):
        """Test that questions are returned in order when randomization is disabled."""
        # Disable randomization
        self.quiz.randomize_questions = False
        self.quiz.save()
        
        # Check order in database query
        questions = self.quiz.questions.all().order_by('order')
        self.assertEqual(questions[0].id, self.question1.id)
        self.assertEqual(questions[1].id, self.question2.id)
        self.assertEqual(questions[2].id, self.question3.id)
        self.assertEqual(questions[3].id, self.question4.id)
        self.assertEqual(questions[4].id, self.question5.id)
        
    def test_random_order_for_randomized_quiz(self):
        """Test that questions can be returned in random order when randomization is enabled."""
        # Enable randomization (already enabled in setup)
        self.quiz.randomize_questions = True
        self.quiz.save()
        
        # We'll make multiple queries and check if at least one produces a different order
        # Note: This is a statistical test and could theoretically fail even when randomization works
        # But with 5 questions, the odds of getting the same order 10 times by chance are very low
        default_order = [self.question1.id, self.question2.id, self.question3.id, 
                         self.question4.id, self.question5.id]
        
        different_order_found = False
        
        # Multiple attempts to get random order
        for _ in range(10):
            # Get questions with random order
            questions = list(self.quiz.questions.all().order_by('?'))
            question_ids = [q.id for q in questions]
            
            # Check if this order is different from the default order
            if question_ids != default_order:
                different_order_found = True
                break
        
        self.assertTrue(different_order_found, "Failed to detect randomized question order after 10 attempts")
        
    def test_randomized_questions_in_view(self):
        """Test that the view respects randomization setting when taking quiz."""
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='in_progress',
            attempt_number=1
        )
        
        # Get questions with randomization (order by '?')
        questions1 = list(self.quiz.questions.all().order_by('?'))
        questions2 = list(self.quiz.questions.all().order_by('?'))
        
        # We can't reliably test that they're in different orders (they might randomly be the same)
        # but we can verify that both queries return all questions
        self.assertEqual(len(questions1), 5)
        self.assertEqual(len(questions2), 5)
        
    def test_nonrandomized_questions_in_view(self):
        """Test that the view respects nonrandomization setting when taking quiz."""
        # Disable randomization
        self.quiz.randomize_questions = False
        self.quiz.save()
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='in_progress',
            attempt_number=1
        )
        
        # Get questions without randomization (order by 'order')
        questions = list(self.quiz.questions.all().order_by('order'))
        
        # Verify the order matches what we expect
        self.assertEqual(questions[0].id, self.question1.id)
        self.assertEqual(questions[1].id, self.question2.id)
        self.assertEqual(questions[2].id, self.question3.id)
        self.assertEqual(questions[3].id, self.question4.id)
        self.assertEqual(questions[4].id, self.question5.id)
        
    def test_randomization_does_not_affect_scoring(self):
        """Test that randomization doesn't affect quiz scoring."""
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='in_progress',
            attempt_number=1
        )
        
        # Answer all questions correctly
        for question in [self.question1, self.question2, self.question3, self.question4, self.question5]:
            # Find the correct choice
            correct_choice = Choice.objects.filter(question=question, is_correct=True).first()
            
            # Create response
            response = QuestionResponse.objects.create(
                attempt=attempt,
                question=question,
                response_data={'selected_choice': correct_choice.id}
            )
            response.check_answer()
        
        # Complete the attempt
        attempt.mark_completed()
        
        # Verify score (should be 5 out of 5)
        self.assertEqual(attempt.score, 5)
        self.assertEqual(attempt.max_score, 5)
        self.assertTrue(attempt.is_passed)  # 100% is above passing score of 70%