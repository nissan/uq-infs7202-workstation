from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import (
    Course, Module, Quiz, 
    Question, MultipleChoiceQuestion, TrueFalseQuestion, 
    Choice, QuizAttempt, QuestionResponse
)
from test_auth_settings import AuthDisabledTestCase

User = get_user_model()

class QuestionScoringTest(AuthDisabledTestCase):
    """Tests for question scoring algorithms."""
    
    def setUp(self):
        """Set up test data."""
        # Create user, course, module, and quiz
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
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
            passing_score=70,
            is_published=True
        )
        
        # Create a single-answer MCQ
        self.mcq_single = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='What is 2+2?',
            points=1,
            order=1,
            allow_multiple=False,
            explanation='Basic arithmetic',
            correct_feedback='Correct! 2+2=4',
            incorrect_feedback='Incorrect! 2+2=4'
        )
        
        # Create choices for the single-answer MCQ
        self.mcq_single_choice1 = Choice.objects.create(
            question=self.mcq_single,
            text='3',
            is_correct=False,
            order=1
        )
        self.mcq_single_choice2 = Choice.objects.create(
            question=self.mcq_single,
            text='4',
            is_correct=True,
            order=2
        )
        self.mcq_single_choice3 = Choice.objects.create(
            question=self.mcq_single,
            text='5',
            is_correct=False,
            order=3
        )
        
        # Create a multiple-answer MCQ
        self.mcq_multiple = MultipleChoiceQuestion.objects.create(
            quiz=self.quiz,
            text='Select all prime numbers under 6',
            points=2,
            order=2,
            allow_multiple=True,
            explanation='Prime numbers are divisible only by 1 and themselves',
            correct_feedback='Correct! 2, 3, and 5 are prime numbers under 6',
            incorrect_feedback='Incorrect! 2, 3, and 5 are prime numbers under 6'
        )
        
        # Create choices for the multiple-answer MCQ
        self.mcq_multiple_choice1 = Choice.objects.create(
            question=self.mcq_multiple,
            text='1',
            is_correct=False,
            order=1
        )
        self.mcq_multiple_choice2 = Choice.objects.create(
            question=self.mcq_multiple,
            text='2',
            is_correct=True,
            order=2
        )
        self.mcq_multiple_choice3 = Choice.objects.create(
            question=self.mcq_multiple,
            text='3',
            is_correct=True,
            order=3
        )
        self.mcq_multiple_choice4 = Choice.objects.create(
            question=self.mcq_multiple,
            text='4',
            is_correct=False,
            order=4
        )
        self.mcq_multiple_choice5 = Choice.objects.create(
            question=self.mcq_multiple,
            text='5',
            is_correct=True,
            order=5
        )
        
        # Create a true/false question
        self.tf_question = TrueFalseQuestion.objects.create(
            quiz=self.quiz,
            text='Is 2+2=4?',
            points=1,
            order=3,
            correct_answer=True,
            explanation='Basic arithmetic truth',
            correct_feedback='Correct!',
            incorrect_feedback='Incorrect!'
        )
        
        # Create a quiz attempt
        self.quiz_attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress',
            attempt_number=1
        )

    def test_mcq_single_answer_correct(self):
        """Test scoring a correct answer for a single-answer MCQ."""
        # Test with the correct choice ID
        is_correct, points, feedback = self.mcq_single.check_answer([self.mcq_single_choice2.id])
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(feedback, 'Correct! 2+2=4')
        
        # Test with a non-list input (should still work)
        is_correct, points, feedback = self.mcq_single.check_answer(self.mcq_single_choice2.id)
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(feedback, 'Correct! 2+2=4')

    def test_mcq_single_answer_incorrect(self):
        """Test scoring an incorrect answer for a single-answer MCQ."""
        # Test with an incorrect choice ID
        is_correct, points, feedback = self.mcq_single.check_answer([self.mcq_single_choice1.id])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect! 2+2=4')
        
        # Test with multiple selections (should be incorrect for single-answer)
        is_correct, points, feedback = self.mcq_single.check_answer([
            self.mcq_single_choice1.id, 
            self.mcq_single_choice2.id
        ])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect! 2+2=4')

    def test_mcq_multiple_answer_correct(self):
        """Test scoring a completely correct answer for a multiple-answer MCQ."""
        # All correct choices and only correct choices
        is_correct, points, feedback = self.mcq_multiple.check_answer([
            self.mcq_multiple_choice2.id,  # 2 (correct)
            self.mcq_multiple_choice3.id,  # 3 (correct)
            self.mcq_multiple_choice5.id   # 5 (correct)
        ])
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 2)
        self.assertEqual(feedback, 'Correct! 2, 3, and 5 are prime numbers under 6')

    def test_mcq_multiple_answer_partial(self):
        """Test scoring a partially correct answer for a multiple-answer MCQ."""
        # Missing one correct choice
        is_correct, points, feedback = self.mcq_multiple.check_answer([
            self.mcq_multiple_choice2.id,  # 2 (correct)
            self.mcq_multiple_choice3.id   # 3 (correct)
            # Missing 5
        ])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect! 2, 3, and 5 are prime numbers under 6')
        
        # Including an incorrect choice
        is_correct, points, feedback = self.mcq_multiple.check_answer([
            self.mcq_multiple_choice2.id,  # 2 (correct)
            self.mcq_multiple_choice3.id,  # 3 (correct)
            self.mcq_multiple_choice4.id,  # 4 (incorrect)
            self.mcq_multiple_choice5.id   # 5 (correct)
        ])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect! 2, 3, and 5 are prime numbers under 6')

    def test_true_false_correct(self):
        """Test scoring a correct answer for a true/false question."""
        # Test with boolean True
        is_correct, points, feedback = self.tf_question.check_answer(True)
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(feedback, 'Correct!')
        
        # Test with string 'true'
        is_correct, points, feedback = self.tf_question.check_answer('true')
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(feedback, 'Correct!')
        
        # Test with string 'True'
        is_correct, points, feedback = self.tf_question.check_answer('True')
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(feedback, 'Correct!')
        
        # Test with integer 1
        is_correct, points, feedback = self.tf_question.check_answer(1)
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(feedback, 'Correct!')
        
        # Test with string '1'
        is_correct, points, feedback = self.tf_question.check_answer('1')
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(feedback, 'Correct!')
        
        # Test with list containing True
        is_correct, points, feedback = self.tf_question.check_answer([True])
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(feedback, 'Correct!')

    def test_true_false_incorrect(self):
        """Test scoring an incorrect answer for a true/false question."""
        # Test with boolean False
        is_correct, points, feedback = self.tf_question.check_answer(False)
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect!')
        
        # Test with string 'false'
        is_correct, points, feedback = self.tf_question.check_answer('false')
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect!')
        
        # Test with string 'False'
        is_correct, points, feedback = self.tf_question.check_answer('False')
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect!')
        
        # Test with integer 0
        is_correct, points, feedback = self.tf_question.check_answer(0)
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect!')
        
        # Test with string '0'
        is_correct, points, feedback = self.tf_question.check_answer('0')
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect!')
        
        # Test with empty list (should return None for user_answer which is not correct)
        is_correct, points, feedback = self.tf_question.check_answer([])
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(feedback, 'Incorrect!')

    def test_question_response_check_answer_mcq(self):
        """Test the QuestionResponse.check_answer method for MCQ."""
        # Create a response for a single-answer MCQ with correct answer
        mcq_response = QuestionResponse.objects.create(
            attempt=self.quiz_attempt,
            question=self.mcq_single,
            response_data={'selected_choice': self.mcq_single_choice2.id}
        )
        
        is_correct, points = mcq_response.check_answer()
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(mcq_response.feedback, 'Correct! 2+2=4')
        self.assertEqual(mcq_response.is_correct, True)
        self.assertEqual(mcq_response.points_earned, 1)
        
        # Create a response for a multiple-answer MCQ with incorrect answer
        mcq_multi_response = QuestionResponse.objects.create(
            attempt=self.quiz_attempt,
            question=self.mcq_multiple,
            response_data={'selected_choices': [
                self.mcq_multiple_choice2.id,  # 2 (correct)
                self.mcq_multiple_choice4.id   # 4 (incorrect)
            ]}
        )
        
        is_correct, points = mcq_multi_response.check_answer()
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(mcq_multi_response.feedback, 'Incorrect! 2, 3, and 5 are prime numbers under 6')
        self.assertEqual(mcq_multi_response.is_correct, False)
        self.assertEqual(mcq_multi_response.points_earned, 0)

    def test_question_response_check_answer_true_false(self):
        """Test the QuestionResponse.check_answer method for true/false questions."""
        # Create a response for a true/false question with correct answer
        tf_response = QuestionResponse.objects.create(
            attempt=self.quiz_attempt,
            question=self.tf_question,
            response_data={'selected_answer': True}
        )
        
        is_correct, points = tf_response.check_answer()
        
        self.assertTrue(is_correct)
        self.assertEqual(points, 1)
        self.assertEqual(tf_response.feedback, 'Correct!')
        self.assertEqual(tf_response.is_correct, True)
        self.assertEqual(tf_response.points_earned, 1)
        
        # Test with incorrect answer by updating the existing response
        tf_response.response_data = {'selected_answer': 'false'}
        tf_response.save()
        
        # Reset the fields that were set by the previous check_answer
        tf_response.is_correct = False
        tf_response.points_earned = 0
        tf_response.feedback = ''
        tf_response.save()
        
        is_correct, points = tf_response.check_answer()
        
        self.assertFalse(is_correct)
        self.assertEqual(points, 0)
        self.assertEqual(tf_response.feedback, 'Incorrect!')
        self.assertEqual(tf_response.is_correct, False)
        self.assertEqual(tf_response.points_earned, 0)

    def test_quiz_attempt_calculate_score(self):
        """Test the QuizAttempt.calculate_score method."""
        # Create responses for all questions
        mcq_response = QuestionResponse.objects.create(
            attempt=self.quiz_attempt,
            question=self.mcq_single,
            response_data={'selected_choice': self.mcq_single_choice2.id}
        )
        mcq_response.check_answer()
        
        # This one is incorrect
        mcq_multi_response = QuestionResponse.objects.create(
            attempt=self.quiz_attempt,
            question=self.mcq_multiple,
            response_data={'selected_choices': [
                self.mcq_multiple_choice2.id,  # Correct but incomplete
            ]}
        )
        mcq_multi_response.check_answer()
        
        tf_response = QuestionResponse.objects.create(
            attempt=self.quiz_attempt,
            question=self.tf_question,
            response_data={'selected_answer': True}
        )
        tf_response.check_answer()
        
        # Calculate score
        score, max_score = self.quiz_attempt.calculate_score()
        
        # We expect 2 points out of 4 possible points
        # MCQ single: 1/1 (correct)
        # MCQ multiple: 0/2 (incorrect - missing choices)
        # True/False: 1/1 (correct)
        self.assertEqual(score, 2)
        self.assertEqual(max_score, 4)
        self.assertEqual(self.quiz_attempt.score, 2)
        self.assertEqual(self.quiz_attempt.max_score, 4)
        
        # This should be a failing score (2/4 = 50%, passing is 70%)
        self.assertFalse(self.quiz_attempt.is_passed)
        
        # Update the multiple-choice response to be correct
        mcq_multi_response.response_data = {'selected_choices': [
            self.mcq_multiple_choice2.id,  # 2 (correct)
            self.mcq_multiple_choice3.id,  # 3 (correct)
            self.mcq_multiple_choice5.id   # 5 (correct)
        ]}
        mcq_multi_response.save()
        mcq_multi_response.check_answer()
        
        # Recalculate score
        score, max_score = self.quiz_attempt.calculate_score()
        
        # Now we expect 4 points out of 4 possible points
        self.assertEqual(score, 4)
        self.assertEqual(max_score, 4)
        
        # This should be a passing score (4/4 = 100%, passing is 70%)
        self.assertTrue(self.quiz_attempt.is_passed)

    def test_mark_completed(self):
        """Test the QuizAttempt.mark_completed method."""
        # Create a new quiz attempt to avoid conflicts with responses from other tests
        new_quiz_attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.user,
            status='in_progress',
            attempt_number=2
        )
        
        # Create responses for all questions with correct answers
        mcq_response = QuestionResponse.objects.create(
            attempt=new_quiz_attempt,
            question=self.mcq_single,
            response_data={'selected_choice': self.mcq_single_choice2.id}
        )
        mcq_response.check_answer()
        
        mcq_multi_response = QuestionResponse.objects.create(
            attempt=new_quiz_attempt,
            question=self.mcq_multiple,
            response_data={'selected_choices': [
                self.mcq_multiple_choice2.id,
                self.mcq_multiple_choice3.id,
                self.mcq_multiple_choice5.id
            ]}
        )
        mcq_multi_response.check_answer()
        
        tf_response = QuestionResponse.objects.create(
            attempt=new_quiz_attempt,
            question=self.tf_question,
            response_data={'selected_answer': True}
        )
        tf_response.check_answer()
        
        # Mark the attempt as completed
        is_passed = new_quiz_attempt.mark_completed()
        
        # Check the results
        self.assertTrue(is_passed)
        self.assertEqual(new_quiz_attempt.status, 'completed')
        self.assertIsNotNone(new_quiz_attempt.completed_at)
        self.assertEqual(new_quiz_attempt.score, 4)
        self.assertEqual(new_quiz_attempt.max_score, 4)
        self.assertTrue(new_quiz_attempt.is_passed)