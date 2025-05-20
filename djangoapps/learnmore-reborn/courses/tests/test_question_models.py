from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import (
    Course, Module, Quiz, 
    Question, MultipleChoiceQuestion, TrueFalseQuestion, 
    Choice, QuizAttempt, QuestionResponse
)
from test_auth_settings import AuthDisabledTestCase

User = get_user_model()

class QuestionModelTest(AuthDisabledTestCase):
    """Tests for Question models and their functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create an instructor, course, module, and quiz
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
        self.quiz = Quiz.objects.create(
            module=self.module,
            title='Test Quiz',
            description='Test quiz description',
            instructions='Test quiz instructions',
            time_limit_minutes=15,
            passing_score=70,
            is_published=True
        )
        
        # Base data for multiple choice questions
        self.mcq_data = {
            'quiz': self.quiz,
            'text': 'What is 2+2?',
            'points': 1,
            'order': 1,
            'allow_multiple': False,
            'explanation': 'Basic arithmetic'
        }
        
        # Base data for true/false questions
        self.tf_data = {
            'quiz': self.quiz,
            'text': 'Is 2+2=4?',
            'points': 1,
            'order': 2,
            'correct_answer': True,
            'explanation': 'Basic arithmetic truth'
        }
    
    def test_multiple_choice_question_creation(self):
        """Test creating a multiple choice question."""
        mcq = MultipleChoiceQuestion.objects.create(**self.mcq_data)
        
        # Test the question was created correctly
        self.assertIsNotNone(mcq.id)
        self.assertEqual(mcq.quiz, self.quiz)
        self.assertEqual(mcq.text, self.mcq_data['text'])
        self.assertEqual(mcq.points, self.mcq_data['points'])
        self.assertEqual(mcq.order, self.mcq_data['order'])
        self.assertEqual(mcq.allow_multiple, self.mcq_data['allow_multiple'])
        self.assertEqual(mcq.explanation, self.mcq_data['explanation'])
        
        # Test the question type was set correctly
        self.assertEqual(mcq.question_type, 'multiple_choice')
        
        # Test the base question exists
        base_question = Question.objects.get(id=mcq.id)
        self.assertEqual(base_question.text, self.mcq_data['text'])
    
    def test_true_false_question_creation(self):
        """Test creating a true/false question."""
        tf = TrueFalseQuestion.objects.create(**self.tf_data)
        
        # Test the question was created correctly
        self.assertIsNotNone(tf.id)
        self.assertEqual(tf.quiz, self.quiz)
        self.assertEqual(tf.text, self.tf_data['text'])
        self.assertEqual(tf.points, self.tf_data['points'])
        self.assertEqual(tf.order, self.tf_data['order'])
        self.assertEqual(tf.correct_answer, self.tf_data['correct_answer'])
        self.assertEqual(tf.explanation, self.tf_data['explanation'])
        
        # Test the question type was set correctly
        self.assertEqual(tf.question_type, 'true_false')
        
        # Test the base question exists
        base_question = Question.objects.get(id=tf.id)
        self.assertEqual(base_question.text, self.tf_data['text'])
    
    def test_choice_creation(self):
        """Test creating choices for a multiple choice question."""
        # Create the question first
        mcq = MultipleChoiceQuestion.objects.create(**self.mcq_data)
        
        # Create choices
        choice1 = Choice.objects.create(
            question=mcq,
            text='4',
            is_correct=True,
            order=1
        )
        
        choice2 = Choice.objects.create(
            question=mcq,
            text='3',
            is_correct=False,
            order=2
        )
        
        choice3 = Choice.objects.create(
            question=mcq,
            text='5',
            is_correct=False,
            order=3
        )
        
        # Test the choices were created correctly
        self.assertEqual(Choice.objects.filter(question=mcq).count(), 3)
        
        # Test retrieving the choices from the question
        choices = mcq.choices.all().order_by('order')
        self.assertEqual(choices[0].text, '4')
        self.assertEqual(choices[0].is_correct, True)
        self.assertEqual(choices[1].text, '3')
        self.assertEqual(choices[1].is_correct, False)
        self.assertEqual(choices[2].text, '5')
        self.assertEqual(choices[2].is_correct, False)
    
    def test_question_deletion_cascades_to_choices(self):
        """Test that deleting a question cascades to its choices."""
        # Create the question first
        mcq = MultipleChoiceQuestion.objects.create(**self.mcq_data)
        
        # Create choices
        Choice.objects.create(
            question=mcq,
            text='4',
            is_correct=True,
            order=1
        )
        
        Choice.objects.create(
            question=mcq,
            text='3',
            is_correct=False,
            order=2
        )
        
        # Verify choices exist
        self.assertEqual(Choice.objects.filter(question=mcq).count(), 2)
        
        # Delete the question
        mcq_id = mcq.id
        mcq.delete()
        
        # Verify question is deleted
        self.assertFalse(MultipleChoiceQuestion.objects.filter(id=mcq_id).exists())
        
        # Verify choices are deleted
        self.assertEqual(Choice.objects.filter(question_id=mcq_id).count(), 0)
    
    def test_quiz_deletion_cascades_to_questions(self):
        """Test that deleting a quiz cascades to its questions."""
        # Create the questions
        mcq = MultipleChoiceQuestion.objects.create(**self.mcq_data)
        tf = TrueFalseQuestion.objects.create(**self.tf_data)
        
        # Verify questions exist
        self.assertEqual(Question.objects.filter(quiz=self.quiz).count(), 2)
        
        # Delete the quiz
        quiz_id = self.quiz.id
        self.quiz.delete()
        
        # Verify questions are deleted
        self.assertEqual(Question.objects.filter(quiz_id=quiz_id).count(), 0)
        self.assertFalse(MultipleChoiceQuestion.objects.filter(id=mcq.id).exists())
        self.assertFalse(TrueFalseQuestion.objects.filter(id=tf.id).exists())
    
    def test_choice_validation(self):
        """Test validation for choices in multiple choice questions."""
        # Create the question with multiple correct answers allowed
        mcq_multi = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Select all prime numbers under 10',
            points=1,
            order=3,
            allow_multiple=True
        )
        
        # Create choices
        Choice.objects.create(
            question=mcq_multi,
            text='2',
            is_correct=True,
            order=1
        )
        
        Choice.objects.create(
            question=mcq_multi,
            text='3',
            is_correct=True,
            order=2
        )
        
        Choice.objects.create(
            question=mcq_multi,
            text='4',
            is_correct=False,
            order=3
        )
        
        # Test retrieving correct choices
        correct_choices = Choice.objects.filter(question=mcq_multi, is_correct=True)
        self.assertEqual(correct_choices.count(), 2)
        self.assertEqual(set(correct_choices.values_list('text', flat=True)), {'2', '3'})
        
        # Test retrieving incorrect choices
        incorrect_choices = Choice.objects.filter(question=mcq_multi, is_correct=False)
        self.assertEqual(incorrect_choices.count(), 1)
        self.assertEqual(incorrect_choices.first().text, '4')
    
    def test_get_questions_ordering(self):
        """Test that questions are returned in the correct order."""
        # Create questions with different orders
        MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Question 3',
            points=1,
            order=3
        )
        
        MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Question 1',
            points=1,
            order=1
        )
        
        MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Question 2',
            points=1,
            order=2
        )
        
        # Retrieve questions and test ordering
        questions = self.quiz.questions.all().order_by('order')
        self.assertEqual(questions.count(), 3)
        self.assertEqual(questions[0].text, 'Question 1')
        self.assertEqual(questions[1].text, 'Question 2')
        self.assertEqual(questions[2].text, 'Question 3')
    
    def test_str_representation(self):
        """Test string representation of questions."""
        mcq = MultipleChoiceQuestion.objects.create(**self.mcq_data)
        tf = TrueFalseQuestion.objects.create(**self.tf_data)
        
        # Test MCQ string representation
        expected_mcq_str = f"{self.quiz.title} - Q{self.mcq_data['order']}: {self.mcq_data['text'][:50]}..."
        self.assertEqual(str(mcq), expected_mcq_str)
        
        # Test TF string representation
        expected_tf_str = f"{self.quiz.title} - Q{self.tf_data['order']}: {self.tf_data['text'][:50]}..."
        self.assertEqual(str(tf), expected_tf_str)
        
    def test_question_explanation(self):
        """Test explanation field for questions."""
        mcq = MultipleChoiceQuestion.objects.create(**self.mcq_data)
        tf = TrueFalseQuestion.objects.create(**self.tf_data)
        
        # Test explanations
        self.assertEqual(mcq.explanation, self.mcq_data['explanation'])
        self.assertEqual(tf.explanation, self.tf_data['explanation'])
        
        # Update explanation
        new_explanation = 'Updated explanation'
        mcq.explanation = new_explanation
        mcq.save()
        
        # Refresh from DB
        mcq.refresh_from_db()
        self.assertEqual(mcq.explanation, new_explanation)