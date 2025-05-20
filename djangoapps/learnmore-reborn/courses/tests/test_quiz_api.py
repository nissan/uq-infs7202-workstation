from django.urls import reverse
from rest_framework import status
from courses.models import (
    Course, Module, Quiz, MultipleChoiceQuestion, TrueFalseQuestion,
    Choice, QuizAttempt, QuestionResponse, Enrollment
)
from api_test_utils import APITestCaseBase

class QuizAPITest(APITestCaseBase):
    """Test the quiz API endpoints."""
    
    def setUp(self):
        super().setUp()
        
        # Create a course and module
        self.course = Course.objects.create(
            title='API Test Course',
            description='Course for API testing',
            instructor=self.instructor,
            status='published'
        )
        
        self.module = Module.objects.create(
            title='API Test Module',
            course=self.course,
            description='Module for API testing',
            order=1
        )
        
        # Create a quiz
        self.quiz = Quiz.objects.create(
            title='API Test Quiz',
            module=self.module,
            description='A test quiz for API testing',
            instructions='Answer all questions to the best of your ability',
            time_limit_minutes=15,
            passing_score=70,
            is_published=True
        )
        
        # Create questions
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
        
        self.tf_question = TrueFalseQuestion.objects.create(
            quiz=self.quiz,
            text='Python is a programming language.',
            order=2,
            points=1,
            correct_answer=True
        )
        
        # Create another course for the unpublished quiz
        self.course2 = Course.objects.create(
            title='API Test Course 2',
            description='Course for API testing',
            instructor=self.instructor,
            status='published'
        )
        
        self.module2 = Module.objects.create(
            title='API Test Module 2',
            course=self.course2,
            description='Module for API testing',
            order=1
        )
        
        # Create another quiz (unpublished)
        self.unpublished_quiz = Quiz.objects.create(
            title='Unpublished Quiz',
            module=self.module2,
            description='An unpublished quiz',
            is_published=False
        )
        
        # Enroll the user in the course
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
    
    def test_quiz_list_as_instructor(self):
        """Test that instructors can see all quizzes."""
        self.client.force_authenticate(user=self.instructor)
        
        url = reverse('quiz-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see both published and unpublished
    
    def test_quiz_list_as_student(self):
        """Test that students can only see published quizzes."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('quiz-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see published quiz
        self.assertEqual(response.data[0]['title'], 'API Test Quiz')
    
    def test_quiz_detail_as_instructor(self):
        """Test that instructors can see quiz details with correct answers."""
        self.client.force_authenticate(user=self.instructor)
        
        url = reverse('quiz-detail', args=[self.quiz.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Quiz')
        
        # Check that it includes questions with correct answers
        self.assertTrue('questions' in response.data)
        self.assertEqual(len(response.data['questions']), 2)
        
        # For multiple choice, check if choices are included
        mcq_data = None
        for q in response.data['questions']:
            if q['question_type'] == 'multiple_choice':
                mcq_data = q
                break
                
        self.assertIsNotNone(mcq_data)
        self.assertTrue('choices' in mcq_data)
    
    def test_quiz_create_as_instructor(self):
        """Test creating a quiz as an instructor."""
        self.client.force_authenticate(user=self.instructor)
        
        url = reverse('quiz-list')
        data = {
            'title': 'New API Quiz',
            'description': 'A new quiz created via API',
            'module': self.module.id,
            'instructions': 'Complete all questions',
            'time_limit_minutes': 20,
            'passing_score': 80,
            'is_published': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New API Quiz')
        
        # Verify in database
        quiz = Quiz.objects.get(id=response.data['id'])
        self.assertEqual(quiz.title, 'New API Quiz')
        self.assertEqual(quiz.passing_score, 80)
    
    def test_quiz_create_as_student_should_fail(self):
        """Test that students cannot create quizzes."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('quiz-list')
        data = {
            'title': 'Student Quiz',
            'description': 'A quiz created by a student',
            'module': self.module.id,
            'is_published': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_start_quiz_attempt(self):
        """Test starting a quiz attempt."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('quiz-start-attempt', args=[self.quiz.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in response.data)
        
        # Verify attempt was created
        attempt_id = response.data['id']
        attempt = QuizAttempt.objects.get(id=attempt_id)
        
        self.assertEqual(attempt.quiz, self.quiz)
        self.assertEqual(attempt.user, self.user)
        self.assertEqual(attempt.status, 'in_progress')
        self.assertEqual(attempt.attempt_number, 1)
    
    def test_submit_response(self):
        """Test submitting an answer to a question."""
        self.client.force_authenticate(user=self.user)
        
        # First create an attempt
        url = reverse('quiz-start-attempt', args=[self.quiz.id])
        response = self.client.post(url)
        attempt_id = response.data['id']
        
        # Submit a response to the multiple choice question
        url = reverse('quiz-attempt-submit-response', args=[attempt_id])
        response_data = {
            'question': self.mcq.id,
            'response_data': {'selected_choice': self.correct_choice.id},
            'time_spent_seconds': 30
        }
        
        response = self.client.post(url, response_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_correct'])
        self.assertEqual(response.data['points_earned'], 1)
    
    def test_complete_quiz(self):
        """Test completing a quiz and getting results."""
        self.client.force_authenticate(user=self.user)
        
        # First create an attempt
        url = reverse('quiz-start-attempt', args=[self.quiz.id])
        response = self.client.post(url)
        attempt_id = response.data['id']
        
        # Submit responses to both questions
        url = reverse('quiz-attempt-submit-response', args=[attempt_id])
        
        # Answer MCQ correctly
        self.client.post(url, {
            'question': self.mcq.id,
            'response_data': {'selected_choice': self.correct_choice.id},
            'time_spent_seconds': 30
        }, format='json')
        
        # Answer TF correctly
        self.client.post(url, {
            'question': self.tf_question.id,
            'response_data': {'selected_answer': 'true'},
            'time_spent_seconds': 15
        }, format='json')
        
        # Complete the quiz
        url = reverse('quiz-attempt-complete', args=[attempt_id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['score'], 2)
        self.assertEqual(response.data['max_score'], 2)
        self.assertTrue(response.data['is_passed'])
        
        # Check that responses are included
        self.assertTrue('responses' in response.data)
        self.assertEqual(len(response.data['responses']), 2)
    
    def test_quiz_attempt_as_other_user_should_fail(self):
        """Test that a user cannot access another user's quiz attempt."""
        # Create an attempt for the student
        self.client.force_authenticate(user=self.user)
        url = reverse('quiz-start-attempt', args=[self.quiz.id])
        response = self.client.post(url)
        attempt_id = response.data['id']
        
        # Try to access as another user
        self.client.force_authenticate(user=self.instructor)
        url = reverse('quiz-attempt-detail', args=[attempt_id])
        response = self.client.get(url)
        
        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)