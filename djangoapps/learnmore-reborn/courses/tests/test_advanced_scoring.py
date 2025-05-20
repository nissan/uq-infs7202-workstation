from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import (
    Course, Module, Quiz, QuizAttempt, 
    Question, MultipleChoiceQuestion, Choice,
    QuestionResponse
)
from django.utils import timezone

User = get_user_model()

class WeightedScoringTest(TestCase):
    """Tests for weighted scoring in multiple choice questions."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        
        # Create a course, module, and quiz
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.user
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Module Description',
        )
        
        self.quiz = Quiz.objects.create(
            module=self.module,
            title='Test Quiz',
            description='Test Quiz Description',
            passing_score=70,
            is_published=True
        )
    
    def test_partial_credit_positive_only(self):
        """Test that partial credit works correctly with only positive values."""
        # Create a multiple choice question with partial credit
        question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='What is the capital of France?',
            question_type='multiple_choice',
            allow_multiple=True,
            use_partial_credit=True,
            points=10
        )
        
        # Create choices with various point values
        choice1 = Choice.objects.create(
            question=question,
            text='Paris',
            is_correct=True,
            points_value=10  # Full credit
        )
        
        choice2 = Choice.objects.create(
            question=question,
            text='Lyon',
            is_correct=False,
            points_value=3  # Partial credit (somewhat related)
        )
        
        choice3 = Choice.objects.create(
            question=question,
            text='Rome',
            is_correct=False,
            points_value=0  # No credit
        )
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress'
        )
        
        # Test case 1: Choose correct and partially correct answers
        response1 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice1.id, choice2.id]}
        )
        
        # Check the answer
        response1.check_answer()
        
        # With partial credit, points should be 10 + 3 = 13, but capped at 10
        self.assertEqual(response1.points_earned, 10)
        self.assertFalse(response1.is_correct)  # Not fully correct because of choice2
        
        # Test case 2: Choose only partially correct answer
        response2 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice2.id]}
        )
        
        # Check the answer
        response2.check_answer()
        
        # Should get partial credit
        self.assertEqual(response2.points_earned, 3)
        self.assertFalse(response2.is_correct)
    
    def test_partial_credit_with_negative_points(self):
        """Test that partial credit works correctly with negative point values."""
        # Create a multiple choice question with partial credit
        question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Select all the prime numbers:',
            question_type='multiple_choice',
            allow_multiple=True,
            use_partial_credit=True,
            minimum_score=0,  # Cannot go below 0
            points=10
        )
        
        # Create choices with various point values
        choice1 = Choice.objects.create(
            question=question,
            text='2',
            is_correct=True,
            points_value=3  # Correct choice
        )
        
        choice2 = Choice.objects.create(
            question=question,
            text='3',
            is_correct=True,
            points_value=3  # Correct choice
        )
        
        choice3 = Choice.objects.create(
            question=question,
            text='5',
            is_correct=True,
            points_value=4  # Correct choice
        )
        
        choice4 = Choice.objects.create(
            question=question,
            text='4',
            is_correct=False,
            points_value=-5  # Penalty for wrong answer
        )
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress'
        )
        
        # Test case 1: Choose correct answers only
        response1 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice1.id, choice2.id, choice3.id]}
        )
        
        # Check the answer
        response1.check_answer()
        
        # Total points = 3 + 3 + 4 = 10
        self.assertEqual(response1.points_earned, 10)
        self.assertTrue(response1.is_correct)
        
        # Test case 2: Choose some correct, some wrong
        response2 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice1.id, choice2.id, choice4.id]}
        )
        
        # Check the answer
        response2.check_answer()
        
        # Points = 3 + 3 - 5 = 1
        self.assertEqual(response2.points_earned, 1)
        self.assertFalse(response2.is_correct)
        
        # Test case 3: Choose all wrong answers
        response3 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice4.id]}
        )
        
        # Check the answer
        response3.check_answer()
        
        # Points = -5, but minimum is 0
        self.assertEqual(response3.points_earned, 0)
        self.assertFalse(response3.is_correct)
    
    def test_partial_credit_with_neutral_choices(self):
        """Test that neutral choices are correctly handled."""
        # Create a multiple choice question with partial credit
        question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Select all correctly spelled words:',
            question_type='multiple_choice',
            allow_multiple=True,
            use_partial_credit=True,
            points=6
        )
        
        # Create choices with various point values
        choice1 = Choice.objects.create(
            question=question,
            text='Separate',
            is_correct=True,
            points_value=3
        )
        
        choice2 = Choice.objects.create(
            question=question,
            text='Relevant',
            is_correct=True,
            points_value=3
        )
        
        choice3 = Choice.objects.create(
            question=question,
            text='Seperate',  # Misspelled
            is_correct=False,
            points_value=-2
        )
        
        choice4 = Choice.objects.create(
            question=question,
            text='Skip this question',
            is_correct=False,
            is_neutral=True,  # Neutral choice
            points_value=0
        )
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress'
        )
        
        # Test neutral choice + correct choice
        response = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice1.id, choice4.id]}
        )
        
        # Check the answer
        response.check_answer()
        
        # Neutral choice should be ignored, points = 3
        self.assertEqual(response.points_earned, 3)
        self.assertFalse(response.is_correct)  # Not fully correct

class NormalizationTest(TestCase):
    """Tests for score normalization in multiple choice questions."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        
        # Create a course, module, and quiz
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.user
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Module Description',
        )
        
        self.quiz = Quiz.objects.create(
            module=self.module,
            title='Test Quiz',
            description='Test Quiz Description',
            passing_score=70,
            is_published=True
        )
    
    def test_zscore_normalization(self):
        """Test Z-score normalization."""
        # Create a multiple choice question with z-score normalization
        question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Z-score normalization question',
            question_type='multiple_choice',
            use_partial_credit=True,
            points=10,
            normalization_method='zscore',
            normalization_parameters={
                'mean': 5,      # Center at 5
                'std_dev': 2    # Standard deviation of 2
            }
        )
        
        # Create choices with point values
        choice1 = Choice.objects.create(
            question=question,
            text='Excellent answer',
            is_correct=True,
            points_value=10
        )
        
        choice2 = Choice.objects.create(
            question=question,
            text='Good answer',
            is_correct=False,
            points_value=7
        )
        
        choice3 = Choice.objects.create(
            question=question,
            text='Okay answer',
            is_correct=False,
            points_value=5
        )
        
        choice4 = Choice.objects.create(
            question=question,
            text='Poor answer',
            is_correct=False,
            points_value=2
        )
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress'
        )
        
        # Test various score normalizations
        
        # Score of 7 is 1 standard deviation above mean (5)
        # Normalized: mean + 1*stddev/4 * max_points/2 = 5 + 1*2/4 * 10/2 = 5 + 0.5*5 = 7.5
        response1 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice2.id]}
        )
        response1.check_answer()
        
        # Score of 2 is 1.5 standard deviations below mean
        # Normalized: mean + (-1.5)*stddev/4 * max_points/2 = 5 + (-1.5)*2/4 * 10/2 = 5 - 0.75*5 = 1.25 (rounded to 1)
        response2 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice4.id]}
        )
        response2.check_answer()
        
        # Verify the z-score normalization applied correctly
        self.assertIn(response1.points_earned, [7, 8])  # Account for rounding differences
        self.assertIn(response2.points_earned, [1, 2])  # Account for rounding differences
    
    def test_minmax_normalization(self):
        """Test min-max scaling normalization."""
        # Create a multiple choice question with min-max normalization
        question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Min-max normalization question',
            question_type='multiple_choice',
            use_partial_credit=True,
            points=10,
            normalization_method='minmax',
            normalization_parameters={
                'input_min': 0,     # Input range min
                'input_max': 10,    # Input range max
                'output_min': 2,    # Output range min
                'output_max': 10    # Output range max
            }
        )
        
        # Create choices with point values
        choices = []
        for i in range(11):  # Create choices with scores 0-10
            choices.append(Choice.objects.create(
                question=question,
                text=f'Answer worth {i} points',
                is_correct=(i == 10),  # Only the 10-point answer is correct
                points_value=i
            ))
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress'
        )
        
        # Test various scores for min-max normalization
        
        # 0 should map to 2 (output_min)
        response0 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choices[0].id]}
        )
        response0.check_answer()
        
        # 5 should map to 6 (halfway between output_min and output_max)
        response5 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choices[5].id]}
        )
        response5.check_answer()
        
        # 10 should map to 10 (output_max)
        response10 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choices[10].id]}
        )
        response10.check_answer()
        
        # Verify the min-max normalization applied correctly
        self.assertEqual(response0.points_earned, 2)  # Maps to output_min
        self.assertEqual(response5.points_earned, 6)  # Maps to halfway point
        self.assertEqual(response10.points_earned, 10)  # Maps to output_max
    
    def test_custom_normalization(self):
        """Test custom normalization with explicit mapping."""
        # Create a multiple choice question with custom normalization
        question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Custom normalization question',
            question_type='multiple_choice',
            use_partial_credit=True,
            points=10,
            normalization_method='custom',
            normalization_parameters={
                'mapping': {
                    "1": 2,   # Map 1 to 2
                    "3": 5,   # Map 3 to 5
                    "5": 6,   # Map 5 to 6
                    "8": 9,   # Map 8 to 9
                    "10": 10  # Map 10 to 10
                }
            }
        )
        
        # Create choices with point values
        choice1 = Choice.objects.create(
            question=question,
            text='1 point answer',
            is_correct=False,
            points_value=1
        )
        
        choice3 = Choice.objects.create(
            question=question,
            text='3 point answer',
            is_correct=False,
            points_value=3
        )
        
        choice5 = Choice.objects.create(
            question=question,
            text='5 point answer',
            is_correct=False,
            points_value=5
        )
        
        choice8 = Choice.objects.create(
            question=question,
            text='8 point answer',
            is_correct=False,
            points_value=8
        )
        
        choice10 = Choice.objects.create(
            question=question,
            text='10 point answer',
            is_correct=True,
            points_value=10
        )
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress'
        )
        
        # Test that custom mapping applies correctly
        
        # 1 should map to 2
        response1 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice1.id]}
        )
        response1.check_answer()
        
        # 5 should map to 6
        response5 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice5.id]}
        )
        response5.check_answer()
        
        # 10 should map to 10
        response10 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice10.id]}
        )
        response10.check_answer()
        
        # Verify the custom normalization applied correctly
        self.assertEqual(response1.points_earned, 2)
        self.assertEqual(response5.points_earned, 6)
        self.assertEqual(response10.points_earned, 10)
    
    def test_no_normalization(self):
        """Test that 'none' normalization method doesn't change scores."""
        # Create a multiple choice question with no normalization
        question = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='No normalization question',
            question_type='multiple_choice',
            use_partial_credit=True,
            points=10,
            normalization_method='none'
        )
        
        # Create choices with point values
        choice3 = Choice.objects.create(
            question=question,
            text='3 point answer',
            is_correct=False,
            points_value=3
        )
        
        choice7 = Choice.objects.create(
            question=question,
            text='7 point answer',
            is_correct=False,
            points_value=7
        )
        
        choice10 = Choice.objects.create(
            question=question,
            text='10 point answer',
            is_correct=True,
            points_value=10
        )
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress'
        )
        
        # Test that scores aren't normalized
        
        # Should stay as 3
        response3 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice3.id]}
        )
        response3.check_answer()
        
        # Should stay as 7
        response7 = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            response_data={'selected_choices': [choice7.id]}
        )
        response7.check_answer()
        
        # Verify scores remain unchanged
        self.assertEqual(response3.points_earned, 3)
        self.assertEqual(response7.points_earned, 7)