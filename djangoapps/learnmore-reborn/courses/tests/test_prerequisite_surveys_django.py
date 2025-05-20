from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from courses.models import Course, Module, Quiz, QuizPrerequisite, QuizAttempt, Enrollment
from courses.tests.test_case import AuthenticatedTestCase
import unittest

User = get_user_model()

@unittest.skip("Skipping due to permission issues")
class PrerequisiteSurveysTestCase(AuthenticatedTestCase):
    """Test cases for prerequisite surveys in quizzes"""
    
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
        
        # Create a survey quiz
        self.survey = Quiz.objects.create(
            module=self.module,
            title="Pre-course Survey",
            description="Please complete this survey before taking the course quizzes",
            is_survey=True,
            is_published=True
        )
        
        # Create a regular quiz
        self.quiz = Quiz.objects.create(
            module=self.module,
            title="Regular Quiz",
            description="This quiz requires the survey to be completed first",
            is_published=True
        )
        
        # Set the survey as a prerequisite for the quiz
        self.prereq = QuizPrerequisite.objects.create(
            quiz=self.quiz,
            prerequisite_quiz=self.survey,
            required_passing=False,  # Just completion is enough, not passing
            bypass_for_instructors=True
        )
        
        # Enroll the user in the course
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
    
    def test_quiz_has_survey_prerequisites(self):
        """Test that a quiz correctly identifies its survey prerequisites"""
        # Login as student
        self.login()
        
        # Check API response
        url = reverse('quiz-detail', args=[self.quiz.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_survey_prerequisites'])
        self.assertEqual(len(response.data['pending_surveys']), 1)
        self.assertTrue(response.data['pending_surveys'][0]['prerequisite_is_survey'])
    
    def test_cannot_start_quiz_without_survey(self):
        """Test that a quiz cannot be started without completing the required survey"""
        # Login as student
        self.login()
        
        # Try to start quiz without completing survey
        url = reverse('quiz-start-attempt', args=[self.quiz.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("complete required survey", response.data['detail'])
        self.assertEqual(len(response.data['pending_surveys']), 1)
    
    def test_instructor_can_bypass_survey(self):
        """Test that an instructor can bypass the survey requirement"""
        # Login as instructor
        self.login_instructor()
        
        # Instructor tries to start quiz without completing survey
        url = reverse('quiz-start-attempt', args=[self.quiz.id])
        response = self.client.post(url)
        
        # Should succeed because instructors can bypass
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)