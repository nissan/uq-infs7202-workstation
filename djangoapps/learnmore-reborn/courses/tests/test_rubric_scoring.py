import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from courses.models import (
    Quiz, Module, Course, Question, EssayQuestion, QuizAttempt, QuestionResponse,
    ScoringRubric, RubricCriterion, RubricFeedback
)

User = get_user_model()

class RubricScoringModelTests(TestCase):
    """Test cases for rubric scoring models."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
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
        
        # Create course structure
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
        
        self.quiz = Quiz.objects.create(
            module=self.module,
            title="Test Quiz",
            description="Test quiz description",
            passing_score=70
        )
        
        # Create a rubric
        self.rubric = ScoringRubric.objects.create(
            name="Essay Evaluation Rubric",
            description="A rubric for evaluating essay responses",
            created_by=self.instructor
        )
        
        # Create criteria for the rubric
        self.criterion1 = RubricCriterion.objects.create(
            rubric=self.rubric,
            name="Content",
            description="Depth and relevance of content",
            max_points=10,
            weight=1.0,
            order=1
        )
        
        self.criterion2 = RubricCriterion.objects.create(
            rubric=self.rubric,
            name="Organization",
            description="Structure and flow of the essay",
            max_points=5,
            weight=1.0,
            order=2
        )
        
        self.criterion3 = RubricCriterion.objects.create(
            rubric=self.rubric,
            name="Clarity",
            description="Clarity of writing and expression",
            max_points=5,
            weight=1.0,
            order=3
        )
        
        # Create an essay question with the rubric
        self.essay_question = EssayQuestion.objects.create(
            quiz=self.quiz,
            text="Explain the importance of testing in software development.",
            order=1,
            points=20,
            min_word_count=50,
            max_word_count=500,
            use_detailed_rubric=True,
            scoring_rubric=self.rubric
        )
        
        # Create a quiz attempt and response
        self.attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='completed',
            score=0,
            max_score=20
        )
        
        self.response = QuestionResponse.objects.create(
            attempt=self.attempt,
            question=self.essay_question,
            response_data={'essay_text': "This is a test essay response for testing rubric scoring." * 10},
            is_correct=False,
            points_earned=0
        )
    
    def test_rubric_total_points(self):
        """Test that rubric total points are calculated correctly."""
        # Total should be sum of all criterion max points
        expected_total = self.criterion1.max_points + self.criterion2.max_points + self.criterion3.max_points
        self.assertEqual(self.rubric.total_points, expected_total)
        
        # Update a criterion's max points
        self.criterion1.max_points = 15
        self.criterion1.save()
        
        # Refresh rubric from database
        self.rubric.refresh_from_db()
        
        # Check that total was updated
        expected_total = 15 + self.criterion2.max_points + self.criterion3.max_points
        self.assertEqual(self.rubric.total_points, expected_total)
    
    def test_criterion_performance_levels(self):
        """Test that default performance levels are created for criteria."""
        # Check that performance levels were auto-created
        self.assertIn("Excellent", self.criterion1.performance_levels)
        self.assertIn("Good", self.criterion1.performance_levels)
        self.assertIn("Satisfactory", self.criterion1.performance_levels)
        self.assertIn("Needs Improvement", self.criterion1.performance_levels)
        self.assertIn("Unsatisfactory", self.criterion1.performance_levels)
        
        # Check point values for levels
        self.assertEqual(self.criterion1.performance_levels["Excellent"]["points"], 10)
        self.assertEqual(self.criterion1.performance_levels["Good"]["points"], 7)  # 75% of 10
        self.assertEqual(self.criterion1.performance_levels["Satisfactory"]["points"], 5)  # 50% of 10
        
        # Test custom performance levels
        custom_levels = {
            "Outstanding": {"points": 10, "description": "Exceptional work"},
            "Proficient": {"points": 7, "description": "Solid work"},
            "Basic": {"points": 4, "description": "Meets basic requirements"},
            "Inadequate": {"points": 0, "description": "Does not meet requirements"}
        }
        
        self.criterion1.performance_levels = custom_levels
        self.criterion1.save()
        
        # Refresh from database
        self.criterion1.refresh_from_db()
        
        # Check custom levels were saved
        self.assertIn("Outstanding", self.criterion1.performance_levels)
        self.assertIn("Proficient", self.criterion1.performance_levels)
        self.assertEqual(self.criterion1.performance_levels["Outstanding"]["points"], 10)
    
    def test_calculate_score_method(self):
        """Test the calculate_score method on the ScoringRubric model."""
        # Create a dictionary of criterion scores
        criterion_scores = {
            self.criterion1.id: 8,  # Content: 8/10
            self.criterion2.id: 4,  # Organization: 4/5
            self.criterion3.id: 3   # Clarity: 3/5
        }
        
        # Calculate the score
        total_score, max_score, percentage = self.rubric.calculate_score(criterion_scores)
        
        # Check results
        self.assertEqual(total_score, 15)  # 8 + 4 + 3
        self.assertEqual(max_score, 20)    # 10 + 5 + 5
        self.assertEqual(percentage, 75.0)  # 15/20 = 75%
        
        # Test with partial criteria
        partial_scores = {
            self.criterion1.id: 6,  # Only score the first criterion
        }
        
        total_score, max_score, percentage = self.rubric.calculate_score(partial_scores)
        
        # Should only count the first criterion in the calculation
        self.assertEqual(total_score, 6)
        self.assertEqual(max_score, 20)  # Still the total max score
        self.assertEqual(percentage, 30.0)  # 6/20 = 30%
        
        # Test with scores exceeding max points
        over_scores = {
            self.criterion1.id: 15,  # More than the max 10
            self.criterion2.id: 8,   # More than the max 5
            self.criterion3.id: 7    # More than the max 5
        }
        
        total_score, max_score, percentage = self.rubric.calculate_score(over_scores)
        
        # Should cap at maximum for each criterion
        self.assertEqual(total_score, 20)  # 10 + 5 + 5 (capped at max)
        self.assertEqual(max_score, 20)
        self.assertEqual(percentage, 100.0)

class RubricGradingFunctionalityTests(TestCase):
    """Test cases for the rubric-based grading functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
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
        
        # Create course structure
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
        
        self.quiz = Quiz.objects.create(
            module=self.module,
            title="Test Quiz",
            description="Test quiz description",
            passing_score=70
        )
        
        # Create a rubric
        self.rubric = ScoringRubric.objects.create(
            name="Essay Evaluation Rubric",
            description="A rubric for evaluating essay responses",
            created_by=self.instructor
        )
        
        # Create criteria for the rubric
        self.criterion1 = RubricCriterion.objects.create(
            rubric=self.rubric,
            name="Content",
            description="Depth and relevance of content",
            max_points=10,
            weight=1.0,
            order=1
        )
        
        self.criterion2 = RubricCriterion.objects.create(
            rubric=self.rubric,
            name="Organization",
            description="Structure and flow of the essay",
            max_points=5,
            weight=1.0,
            order=2
        )
        
        self.criterion3 = RubricCriterion.objects.create(
            rubric=self.rubric,
            name="Clarity",
            description="Clarity of writing and expression",
            max_points=5,
            weight=1.0,
            order=3
        )
        
        # Create an essay question with the rubric
        self.essay_question = EssayQuestion.objects.create(
            quiz=self.quiz,
            text="Explain the importance of testing in software development.",
            order=1,
            points=20,
            min_word_count=50,
            max_word_count=500,
            use_detailed_rubric=True,
            scoring_rubric=self.rubric
        )
        
        # Create a quiz attempt and response
        self.attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            user=self.student,
            status='completed',
            score=0,
            max_score=20
        )
        
        self.response = QuestionResponse.objects.create(
            attempt=self.attempt,
            question=self.essay_question,
            response_data={'essay_text': "This is a test essay response for testing rubric scoring." * 10},
            is_correct=False,
            points_earned=0
        )
    
    def test_grade_response_with_rubric(self):
        """Test grading an essay response using a rubric."""
        # Create criterion scores
        criterion_scores = {
            str(self.criterion1.id): {
                'points': 8,
                'comments': 'Good coverage of key concepts',
                'level': 'Good'
            },
            str(self.criterion2.id): {
                'points': 4,
                'comments': 'Well structured essay',
                'level': 'Excellent'
            },
            str(self.criterion3.id): {
                'points': 3,
                'comments': 'Clear writing but some grammar issues',
                'level': 'Satisfactory'
            }
        }
        
        # Grade the response
        self.essay_question.grade_response(
            response=self.response,
            points=0,  # Should be calculated from criteria
            feedback="Overall good work",
            graded_by=self.instructor,
            criterion_scores=criterion_scores
        )
        
        # Refresh the response
        self.response.refresh_from_db()
        
        # Check that the response was graded
        self.assertIsNotNone(self.response.graded_at)
        self.assertEqual(self.response.points_earned, 15)  # 8 + 4 + 3 = 15
        self.assertEqual(self.response.instructor_comment, "Overall good work")
        self.assertEqual(self.response.graded_by, self.instructor)
        
        # Check that criterion feedback was created
        criterion_feedback = self.response.criterion_feedback.all()
        self.assertEqual(criterion_feedback.count(), 3)
        
        # Check specific criterion feedback
        content_feedback = self.response.criterion_feedback.get(criterion=self.criterion1)
        self.assertEqual(content_feedback.points_earned, 8)
        self.assertEqual(content_feedback.comments, 'Good coverage of key concepts')
        self.assertEqual(content_feedback.performance_level, 'Good')
        
        # Check that the attempt score was updated
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.score, 15)
        self.assertEqual(self.attempt.max_score, 20)
        self.assertTrue(self.attempt.is_passed)  # 15/20 = 75% > 70% passing score
    
    def test_grade_response_simple_vs_rubric(self):
        """Test difference between simple grading and rubric-based grading."""
        # First test simple grading (without rubric)
        self.essay_question.use_detailed_rubric = False
        self.essay_question.save()
        
        self.essay_question.grade_response(
            response=self.response,
            points=16,
            feedback="Good essay",
            graded_by=self.instructor
        )
        
        # Refresh the response and attempt
        self.response.refresh_from_db()
        self.attempt.refresh_from_db()
        
        # Check simple grading results
        self.assertEqual(self.response.points_earned, 16)
        self.assertEqual(self.attempt.score, 16)
        
        # Now test rubric-based grading
        self.essay_question.use_detailed_rubric = True
        self.essay_question.save()
        
        # Create a new essay question for the same quiz
        second_essay_question = EssayQuestion.objects.create(
            quiz=self.quiz,
            text="Describe the software development lifecycle.",
            order=2,
            points=20,
            min_word_count=50,
            max_word_count=500,
            use_detailed_rubric=True,
            scoring_rubric=self.rubric
        )
        
        # Create a new response for the second question
        new_response = QuestionResponse.objects.create(
            attempt=self.attempt,
            question=second_essay_question,
            response_data={'essay_text': "Another response for testing." * 10},
            is_correct=False,
            points_earned=0
        )
        
        # Grade with rubric
        criterion_scores = {
            str(self.criterion1.id): {'points': 7, 'comments': '', 'level': 'Good'},
            str(self.criterion2.id): {'points': 4, 'comments': '', 'level': 'Good'},
            str(self.criterion3.id): {'points': 4, 'comments': '', 'level': 'Good'}
        }
        
        second_essay_question.grade_response(
            response=new_response,
            points=0,
            feedback="Rubric-based feedback",
            graded_by=self.instructor,
            criterion_scores=criterion_scores
        )
        
        # Refresh objects
        new_response.refresh_from_db()
        self.attempt.refresh_from_db()
        
        # Check rubric grading results
        self.assertEqual(new_response.points_earned, 15)  # 7 + 4 + 4 = 15
        
        # Check that criterion feedback is created
        self.assertEqual(new_response.criterion_feedback.count(), 3)
    
    def test_scaling_to_question_points(self):
        """Test that rubric scores are properly scaled to question points."""
        # Test lower point scale
        essay1 = EssayQuestion.objects.create(
            quiz=self.quiz,
            text="First scaling test question",
            order=3,
            points=10,  # Lower than rubric total (20)
            min_word_count=50,
            max_word_count=500,
            use_detailed_rubric=True,
            scoring_rubric=self.rubric
        )
        
        response1 = QuestionResponse.objects.create(
            attempt=self.attempt,
            question=essay1,
            response_data={'essay_text': "Response for lower point scaling test." * 10},
            is_correct=False,
            points_earned=0
        )
        
        # Grade with full points on rubric
        criterion_scores = {
            str(self.criterion1.id): {'points': 10, 'comments': '', 'level': 'Excellent'},
            str(self.criterion2.id): {'points': 5, 'comments': '', 'level': 'Excellent'},
            str(self.criterion3.id): {'points': 5, 'comments': '', 'level': 'Excellent'}
        }
        
        essay1.grade_response(
            response=response1,
            points=0,
            feedback="Perfect score on rubric - lower scale",
            graded_by=self.instructor,
            criterion_scores=criterion_scores
        )
        
        # Refresh the response
        response1.refresh_from_db()
        
        # Check scaling: 20/20 on rubric = 10/10 on question
        self.assertEqual(response1.points_earned, 10)
        
        # Test higher point scale
        essay2 = EssayQuestion.objects.create(
            quiz=self.quiz,
            text="Second scaling test question",
            order=4,
            points=40,  # Higher than rubric total (20)
            min_word_count=50,
            max_word_count=500,
            use_detailed_rubric=True,
            scoring_rubric=self.rubric
        )
        
        response2 = QuestionResponse.objects.create(
            attempt=self.attempt,
            question=essay2,
            response_data={'essay_text': "Response for higher point scaling test." * 10},
            is_correct=False,
            points_earned=0
        )
        
        # Grade with half points on rubric
        half_criterion_scores = {
            str(self.criterion1.id): {'points': 5, 'comments': '', 'level': 'Satisfactory'},
            str(self.criterion2.id): {'points': 2, 'comments': '', 'level': 'Needs Improvement'},
            str(self.criterion3.id): {'points': 3, 'comments': '', 'level': 'Satisfactory'}
        }
        
        essay2.grade_response(
            response=response2,
            points=0,
            feedback="Half score on rubric - higher scale",
            graded_by=self.instructor,
            criterion_scores=half_criterion_scores
        )
        
        # Refresh the response
        response2.refresh_from_db()
        
        # Check scaling: 10/20 on rubric = 20/40 on question
        self.assertEqual(response2.points_earned, 20)