from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import (
    Quiz, Module, Course,
    MultipleChoiceQuestion, Choice
)

User = get_user_model()

class PartialCreditModelTest(TestCase):
    """Test model-level behavior of partial credit scoring."""
    
    def setUp(self):
        """Set up test data."""
        # Create an instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123'
        )
        
        # Create course, module, and quiz
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
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
            title='Partial Credit Quiz',
            description='Testing partial credit',
            passing_score=70,
            is_published=True
        )
        
        # Create partial credit multiple choice question
        self.partial_mcq = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Select your knowledge level of programming languages:',
            order=1,
            points=10,
            allow_multiple=True,
            use_partial_credit=True,
            minimum_score=0
        )
        
        # Create choices with different point values
        self.choice1 = Choice.objects.create(
            question=self.partial_mcq,
            text='Expert in Python',
            is_correct=True,
            points_value=5,
            order=0
        )
        
        self.choice2 = Choice.objects.create(
            question=self.partial_mcq,
            text='Proficient in Java',
            is_correct=True,
            points_value=4,
            order=1
        )
        
        self.choice3 = Choice.objects.create(
            question=self.partial_mcq,
            text='Beginner in C++',
            is_correct=True,
            points_value=2,
            order=2
        )
        
        self.choice4 = Choice.objects.create(
            question=self.partial_mcq,
            text='Unfamiliar with Ruby',
            is_correct=False,
            points_value=-3,
            order=3
        )
        
        self.choice5 = Choice.objects.create(
            question=self.partial_mcq,
            text='Not applicable',
            is_correct=False,
            is_neutral=True,
            points_value=0,
            order=4
        )
        
        # Create another MCQ with minimum score
        self.minimum_mcq = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Select your preferred programming paradigms:',
            order=2,
            points=10,
            allow_multiple=True,
            use_partial_credit=True,
            minimum_score=3
        )
        
        # Create choices for minimum score MCQ
        self.min_choice1 = Choice.objects.create(
            question=self.minimum_mcq,
            text='Functional Programming',
            is_correct=True,
            points_value=4,
            order=0
        )
        
        self.min_choice2 = Choice.objects.create(
            question=self.minimum_mcq,
            text='Object-Oriented Programming',
            is_correct=True,
            points_value=4,
            order=1
        )
        
        self.min_choice3 = Choice.objects.create(
            question=self.minimum_mcq,
            text='Procedural Programming',
            is_correct=True,
            points_value=3,
            order=2
        )
        
        self.min_choice4 = Choice.objects.create(
            question=self.minimum_mcq,
            text='I prefer not to code',
            is_correct=False,
            points_value=-6,
            order=3
        )
        
    def test_check_answer_with_positive_points(self):
        """Test check_answer with only positive point choices."""
        # Select two positive point choices (5 + 4 = 9 points)
        is_correct, points, feedback = self.partial_mcq.check_answer([self.choice1.id, self.choice2.id])
        
        # Not completely correct (missing choice3) but partial credit awarded
        self.assertFalse(is_correct)
        self.assertEqual(points, 9)
        
    def test_check_answer_with_mixed_points(self):
        """Test check_answer with mixed positive and negative point choices."""
        # Select mixed points (5 + 4 - 3 = 6 points)
        is_correct, points, feedback = self.partial_mcq.check_answer([
            self.choice1.id, self.choice2.id, self.choice4.id
        ])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 6)
        
    def test_check_answer_with_neutral_choice(self):
        """Test check_answer with a neutral choice that shouldn't affect score."""
        # Select one positive and one neutral (5 + 0 = 5 points)
        is_correct, points, feedback = self.partial_mcq.check_answer([
            self.choice1.id, self.choice5.id
        ])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 5)
        
    def test_check_answer_below_minimum(self):
        """Test that scores below minimum are raised to the minimum score."""
        # Select only negative points for the minimum_mcq (-6 points, but minimum is 3)
        is_correct, points, feedback = self.minimum_mcq.check_answer([self.min_choice4.id])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 3)  # Should be raised to minimum
        
    def test_check_answer_above_maximum(self):
        """Test that scores above maximum are capped at the maximum."""
        # Select all positive choices (4 + 4 + 3 = 11 points, but max is 10)
        is_correct, points, feedback = self.minimum_mcq.check_answer([
            self.min_choice1.id, self.min_choice2.id, self.min_choice3.id
        ])
        
        # All correct choices are selected, so it should be marked as correct
        # even though we're using partial credit
        self.assertTrue(is_correct)
        self.assertEqual(points, 10)  # Should be capped at maximum
        
    def test_check_answer_is_correct_logic(self):
        """Test the logic for determining if an answer is completely correct."""
        # For partial credit questions, is_correct should be True only when
        # all correct choices are selected and no incorrect choices are selected
        
        # Select all correct choices and no incorrect ones
        is_correct, points, feedback = self.partial_mcq.check_answer([
            self.choice1.id, self.choice2.id, self.choice3.id
        ])
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 10)  # Capped at maximum
        
        # Select all correct choices plus a negative one
        is_correct, points, feedback = self.partial_mcq.check_answer([
            self.choice1.id, self.choice2.id, self.choice3.id, self.choice4.id
        ])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 8)  # 5 + 4 + 2 - 3 = 8
        
        # Select all correct choices plus a neutral one
        is_correct, points, feedback = self.partial_mcq.check_answer([
            self.choice1.id, self.choice2.id, self.choice3.id, self.choice5.id
        ])
        
        # In the model implementation, even neutral choices affect the is_correct
        # logic when use_partial_credit is enabled
        self.assertFalse(is_correct)
        self.assertEqual(points, 10)  # Capped at maximum