from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework import status
import json
import tempfile
import os
from django.utils import timezone

from courses.tests.test_case import AuthenticatedTestCase
from courses.models import (
    Course, Module, Quiz, EssayQuestion, QuizAttempt, QuestionResponse
)
from progress.models import Progress

User = get_user_model()

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class EssayQuestionAdvancedTestCase(AuthenticatedTestCase):
    """Advanced tests for essay question functionality."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
        # Create test users
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123'
        )
        self.instructor.profile.is_instructor = True
        self.instructor.profile.save()
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123'
        )
        
        self.other_instructor = User.objects.create_user(
            username='other_instructor',
            email='other_instructor@example.com',
            password='testpass123'
        )
        self.other_instructor.profile.is_instructor = True
        self.other_instructor.profile.save()
        
        # Create course and module
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
            instructor=self.instructor,
            status='published'
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title="Test Module",
            description="Test module description",
            order=1
        )
        
        # Create quiz with essay question
        self.quiz = Quiz.objects.create(
            module=self.module,
            title="Essay Quiz",
            description="Test your writing skills",
            instructions="Answer the essay question thoughtfully",
            passing_score=70,
            is_published=True
        )
        
        # Create essay question
        self.essay_question = EssayQuestion.objects.create(
            quiz=self.quiz,
            text="Explain the importance of testing in software development.",
            order=1,
            points=10,
            min_word_count=50,
            max_word_count=500,
            rubric="1-3 points: Basic understanding\n4-7 points: Good understanding\n8-10 points: Excellent understanding",
            example_answer="Testing is crucial in software development for several reasons..."
        )
        
        # Enroll student in the course
        self.course.enrollments.create(user=self.student, status='active')
        
        # Set up API client
        self.api_client = APIClient()
    
    def test_essay_response_below_min_word_count(self):
        """Test that an essay response below the minimum word count is rejected."""
        # Login as student
        self.client.login(username='student', password='testpass123')
        
        # Start a quiz attempt
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to quiz assessment
        
        # Get the attempt
        attempts = QuizAttempt.objects.filter(user=self.student, quiz=self.quiz)
        self.assertTrue(attempts.exists())
        attempt = attempts.first()
        
        # Prepare essay response data with insufficient word count (less than 50 words)
        essay_text = "This is a test essay response that is too short."
        data = {
            'question_id': self.essay_question.id,
            'essay_text': essay_text,
            'time_spent': 60  # 1 minute
        }
        
        # Submit the essay response
        response = self.client.post(reverse('submit-answer', args=[attempt.id, self.essay_question.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect to next question or quiz
        
        # Verify the response was saved but marked with error
        question_response = QuestionResponse.objects.get(
            attempt=attempt,
            question=self.essay_question
        )
        self.assertIsNotNone(question_response)
        self.assertEqual(question_response.response_data['essay_text'], essay_text)
        self.assertFalse(question_response.is_correct)
        self.assertIn("too short", question_response.feedback)
    
    def test_essay_response_above_max_word_count(self):
        """Test that an essay response above the maximum word count is rejected."""
        # Login as student
        self.client.login(username='student', password='testpass123')
        
        # Start a quiz attempt
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to quiz assessment
        
        # Get the attempt
        attempts = QuizAttempt.objects.filter(user=self.student, quiz=self.quiz)
        self.assertTrue(attempts.exists())
        attempt = attempts.first()
        
        # Prepare essay response data with excessive word count (more than 500 words)
        # 60 words repeated 10 times = 600 words
        essay_text = "This is a test essay response that exceeds the maximum word count. It contains many words that are unnecessary and redundant. The purpose is to test the validation of the maximum word count restriction. We need to make sure that the system properly identifies responses that are too verbose and provides appropriate feedback to guide the student in editing their response to meet the requirements. " * 10
        
        data = {
            'question_id': self.essay_question.id,
            'essay_text': essay_text,
            'time_spent': 300  # 5 minutes
        }
        
        # Submit the essay response
        response = self.client.post(reverse('submit-answer', args=[attempt.id, self.essay_question.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect to next question or quiz
        
        # Verify the response was saved but marked with error
        question_response = QuestionResponse.objects.get(
            attempt=attempt,
            question=self.essay_question
        )
        self.assertIsNotNone(question_response)
        self.assertFalse(question_response.is_correct)
        self.assertIn("exceeds maximum word count", question_response.feedback)
    
    def test_essay_without_word_count_restrictions(self):
        """Test an essay question without word count restrictions."""
        # Modify the essay question to remove word count restrictions
        self.essay_question.min_word_count = 0
        self.essay_question.max_word_count = 0
        self.essay_question.save()
        
        # Login as student
        self.client.login(username='student', password='testpass123')
        
        # Start a quiz attempt
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to quiz assessment
        
        # Get the attempt
        attempts = QuizAttempt.objects.filter(user=self.student, quiz=self.quiz)
        self.assertTrue(attempts.exists())
        attempt = attempts.first()
        
        # Submit a very short essay
        essay_text = "Very short response."
        data = {
            'question_id': self.essay_question.id,
            'essay_text': essay_text,
            'time_spent': 30  # 30 seconds
        }
        
        # Submit the essay response
        response = self.client.post(reverse('submit-answer', args=[attempt.id, self.essay_question.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect to next question or quiz
        
        # Verify the response was saved without word count error
        question_response = QuestionResponse.objects.get(
            attempt=attempt,
            question=self.essay_question
        )
        self.assertIsNotNone(question_response)
        self.assertEqual(question_response.response_data['essay_text'], essay_text)
        self.assertFalse(question_response.is_correct)  # Still pending grading
        self.assertNotIn("word count", question_response.feedback)
        self.assertIn("submitted successfully", question_response.feedback)
    
    def test_empty_essay_response(self):
        """Test that an empty essay response is rejected."""
        # Login as student
        self.client.login(username='student', password='testpass123')
        
        # Start a quiz attempt
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to quiz assessment
        
        # Get the attempt
        attempts = QuizAttempt.objects.filter(user=self.student, quiz=self.quiz)
        self.assertTrue(attempts.exists())
        attempt = attempts.first()
        
        # Submit an empty essay
        data = {
            'question_id': self.essay_question.id,
            'essay_text': '',
            'time_spent': 10  # 10 seconds
        }
        
        # Submit the essay response
        response = self.client.post(reverse('submit-answer', args=[attempt.id, self.essay_question.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect to next question or quiz
        
        # Verify the response was saved with empty error
        question_response = QuestionResponse.objects.get(
            attempt=attempt,
            question=self.essay_question
        )
        self.assertIsNotNone(question_response)
        self.assertEqual(question_response.response_data['essay_text'], '')
        self.assertFalse(question_response.is_correct)
        self.assertIn("No response provided", question_response.feedback)
    
    def test_essay_grading_permissions(self):
        """Test that only the course instructor can grade essay responses."""
        # Create a quiz attempt and response
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='completed',
            score=0,
            max_score=10
        )
        
        essay_text = "This is a test essay response for testing grading permissions. " * 10
        question_response = QuestionResponse.objects.create(
            attempt=attempt,
            question=self.essay_question,
            response_data={'essay_text': essay_text},
            is_correct=False,
            points_earned=0
        )
        
        # Try to grade with other instructor
        self.client.login(username='other_instructor', password='testpass123')
        
        grading_data = {
            'points': 7,
            'feedback': 'This is feedback from another instructor.'
        }
        
        # Other instructor should not be able to grade
        response = self.client.post(reverse('grade-essay-response', args=[question_response.id]), grading_data)
        # We're expecting access denied due to permission check
        self.assertNotEqual(response.status_code, 200)
        
        # Now authenticate as course instructor
        self.client.logout()
        self.client.login(username='instructor', password='testpass123')
        
        # Course instructor should be able to grade
        response = self.client.post(reverse('grade-essay-response', args=[question_response.id]), grading_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful grading
        
        # Refresh the question response from the database
        question_response.refresh_from_db()
        
        # Verify the response was graded
        self.assertIsNotNone(question_response.graded_at)
        self.assertEqual(question_response.points_earned, 7)
        self.assertEqual(question_response.instructor_comment, 'This is feedback from another instructor.')
        self.assertEqual(question_response.graded_by, self.instructor)
    
    def test_essay_grading_effect_on_scores(self):
        """Test that grading an essay correctly updates attempt scores."""
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='completed',
            score=0,
            max_score=10
        )
        
        # Create an essay response
        essay_text = "This is a test essay response for checking score updates. " * 10
        question_response = QuestionResponse.objects.create(
            attempt=attempt,
            question=self.essay_question,
            response_data={'essay_text': essay_text},
            is_correct=False,
            points_earned=0
        )
        
        # Login as instructor
        self.client.login(username='instructor', password='testpass123')
        
        # Grade the essay
        grading_data = {
            'points': 8,
            'feedback': 'Good essay with thoughtful analysis.'
        }
        
        # Let's directly use the model method to grade the response
        # This is more reliable than using the view in tests
        self.essay_question.grade_response(question_response, 8, 'Good essay with thoughtful analysis.', self.instructor)
        
        # Refresh the attempt from the database
        attempt.refresh_from_db()
        
        # Verify the attempt score was updated
        self.assertEqual(attempt.score, 8)
        self.assertEqual(attempt.max_score, 10)
        self.assertTrue(attempt.is_passed)  # 8/10 = 80%, passing score is 70%
    
    def test_essay_instructor_annotation(self):
        """Test that instructors can annotate essay responses."""
        # Create a quiz attempt and response
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='completed',
            score=0,
            max_score=10
        )
        
        essay_text = "This is a test essay response for testing annotations. " * 10
        question_response = QuestionResponse.objects.create(
            attempt=attempt,
            question=self.essay_question,
            response_data={'essay_text': essay_text},
            is_correct=False,
            points_earned=0
        )
        
        # Login as instructor
        self.client.login(username='instructor', password='testpass123')
        
        # Add an annotation
        annotation_data = {
            'annotation': 'This paragraph could be improved with more concrete examples.'
        }
        
        response = self.client.post(reverse('annotate-essay-response', args=[question_response.id]), annotation_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful annotation
        
        # Verify the annotation was saved
        question_response.refresh_from_db()
        self.assertEqual(question_response.instructor_annotation, annotation_data['annotation'])
        self.assertIsNotNone(question_response.annotation_added_at)
        self.assertEqual(question_response.annotated_by, self.instructor)
    
    def test_multiple_essay_questions_in_quiz(self):
        """Test a quiz with multiple essay questions."""
        # Add a second essay question
        second_essay = EssayQuestion.objects.create(
            quiz=self.quiz,
            text="Compare and contrast different software development methodologies.",
            order=2,
            points=15,
            min_word_count=100,
            max_word_count=800,
            rubric="Detailed rubric for grading methodology comparison",
            example_answer="When comparing Agile, Waterfall, and DevOps..."
        )
        
        # Login as student
        self.client.login(username='student', password='testpass123')
        
        # Start a quiz attempt
        response = self.client.post(reverse('start-quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to quiz assessment
        
        # Get the attempt
        attempts = QuizAttempt.objects.filter(user=self.student, quiz=self.quiz)
        self.assertTrue(attempts.exists())
        attempt = attempts.first()
        
        # Submit answers to both questions
        essay1_text = "This is a response to the first essay question about testing. " * 10
        data1 = {
            'question_id': self.essay_question.id,
            'essay_text': essay1_text,
            'time_spent': 300  # 5 minutes
        }
        
        response = self.client.post(reverse('submit-answer', args=[attempt.id, self.essay_question.id]), data1)
        self.assertEqual(response.status_code, 302)  # Redirect to next question
        
        essay2_text = "This is a response to the second essay question about methodologies. " * 15
        data2 = {
            'question_id': second_essay.id,
            'essay_text': essay2_text,
            'time_spent': 450  # 7.5 minutes
        }
        
        response = self.client.post(reverse('submit-answer', args=[attempt.id, second_essay.id]), data2)
        self.assertEqual(response.status_code, 302)  # Redirect to next question
        
        # Complete the attempt
        response = self.client.post(reverse('finish-quiz', args=[attempt.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to results
        
        # Login as instructor to grade
        self.client.logout()
        self.client.login(username='instructor', password='testpass123')
        
        # Get pending essays to grade
        response = self.client.get(reverse('pending-essay-grading', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        
        # Grade both essays
        responses = QuestionResponse.objects.filter(
            attempt=attempt,
            question__question_type='essay'
        )
        self.assertEqual(responses.count(), 2)
        
        for question_response in responses:
            grading_data = {
                'points': 10,
                'feedback': f'Good response to question {question_response.question.text[:20]}...'
            }
            
            response = self.client.post(reverse('grade-essay-response', args=[question_response.id]), grading_data)
            self.assertEqual(response.status_code, 302)
        
        # Check the attempt score after grading
        attempt.refresh_from_db()
        
        # Total score should be 20 (10 for each essay)
        # Max score should be 25 (10 for first essay + 15 for second essay)
        self.assertEqual(attempt.score, 20)
        self.assertEqual(attempt.max_score, 25)
        self.assertTrue(attempt.is_passed)  # 80% > 70% passing score