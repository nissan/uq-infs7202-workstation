from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Quiz
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase

User = get_user_model()

class QuizModelTest(AuthDisabledTestCase):
    """Tests for Quiz model CRUD operations."""
    
    def setUp(self):
        """Set up test data."""
        # Create an instructor, course, and module for the quizzes
        self.instructor = User.objects.create_user(
            username='instructor1',
            email='instructor1@example.com',
            password='testpass123'
        )
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
        
        self.quiz_data = {
            'module': self.module,
            'title': 'Test Quiz',
            'description': 'Test quiz description',
            'is_survey': False
        }
    
    def test_create_quiz(self):
        """Test creating a new quiz."""
        quiz = Quiz.objects.create(**self.quiz_data)
        
        # Assertions for creation
        self.assertIsNotNone(quiz.id)
        self.assertEqual(quiz.module, self.module)
        self.assertEqual(quiz.title, self.quiz_data['title'])
        self.assertEqual(quiz.description, self.quiz_data['description'])
        self.assertEqual(quiz.is_survey, False)
    
    def test_read_quiz(self):
        """Test retrieving a quiz."""
        # Create the quiz first
        original = Quiz.objects.create(**self.quiz_data)
        
        # Retrieve by ID
        retrieved_by_id = Quiz.objects.get(id=original.id)
        self.assertEqual(retrieved_by_id.title, self.quiz_data['title'])
        
        # Retrieve by module
        retrieved_by_module = Quiz.objects.filter(module=self.module).first()
        self.assertEqual(retrieved_by_module.id, original.id)
        
        # Test filtering by is_survey
        non_survey_quizzes = Quiz.objects.filter(is_survey=False)
        self.assertIn(original, non_survey_quizzes)
        
        # Create a survey quiz and test filtering
        survey_quiz = Quiz.objects.create(
            module=self.module,
            title='Survey Quiz',
            description='Survey quiz description',
            is_survey=True
        )
        survey_quizzes = Quiz.objects.filter(is_survey=True)
        self.assertIn(survey_quiz, survey_quizzes)
        self.assertNotIn(original, survey_quizzes)
    
    def test_update_quiz(self):
        """Test updating a quiz."""
        # Create the quiz first
        quiz = Quiz.objects.create(**self.quiz_data)
        
        # Update the quiz
        new_title = 'Updated Quiz Title'
        new_description = 'Updated quiz description'
        
        quiz.title = new_title
        quiz.description = new_description
        quiz.is_survey = True
        quiz.save()
        
        # Refresh from database
        quiz.refresh_from_db()
        
        # Assertions for update
        self.assertEqual(quiz.title, new_title)
        self.assertEqual(quiz.description, new_description)
        self.assertEqual(quiz.is_survey, True)
    
    def test_delete_quiz(self):
        """Test deleting a quiz."""
        # Create the quiz first
        quiz = Quiz.objects.create(**self.quiz_data)
        quiz_id = quiz.id
        
        # Verify created
        self.assertTrue(Quiz.objects.filter(id=quiz_id).exists())
        
        # Delete the quiz
        quiz.delete()
        
        # Verify deleted
        self.assertFalse(Quiz.objects.filter(id=quiz_id).exists())
    
    def test_multiple_quizzes_per_module(self):
        """Test creating multiple quizzes for a module."""
        # Create first quiz
        quiz1 = Quiz.objects.create(**self.quiz_data)
        
        # Create second quiz
        quiz2 = Quiz.objects.create(
            module=self.module,
            title='Second Quiz',
            description='Second quiz description',
            is_survey=False
        )
        
        # Create third quiz (a survey)
        quiz3 = Quiz.objects.create(
            module=self.module,
            title='Survey Quiz',
            description='Survey quiz description',
            is_survey=True
        )
        
        # Verify all quizzes exist
        quizzes = Quiz.objects.filter(module=self.module)
        self.assertEqual(quizzes.count(), 3)
        
        # Verify filtering works
        self.assertEqual(Quiz.objects.filter(module=self.module, is_survey=False).count(), 2)
        self.assertEqual(Quiz.objects.filter(module=self.module, is_survey=True).count(), 1)
    
    def test_str_representation(self):
        """Test string representation of Quiz."""
        quiz = Quiz.objects.create(**self.quiz_data)
        expected_str = f"{self.module.title} - {self.quiz_data['title']}"
        self.assertEqual(str(quiz), expected_str)