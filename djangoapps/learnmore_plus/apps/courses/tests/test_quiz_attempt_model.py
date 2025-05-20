import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.courses.models import (
    Course, Module, Content, Category, Quiz, Question, Choice,
    QuizAttempt, Answer
)

User = get_user_model()

@pytest.mark.django_db
class TestQuizAttemptModel:
    """
    Tests for the QuizAttempt and Answer models CRUD operations.
    """
    
    @pytest.fixture
    def setup_quiz_data(self):
        """Set up test data for quiz attempt testing."""
        # Create a category
        category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            description="Test category description"
        )
        
        # Create a coordinator
        coordinator = User.objects.create_user(
            username='test_coordinator',
            email='coordinator@test.com',
            password='password123'
        )
        
        # Create a course
        course = Course.objects.create(
            title="Test Course for Quiz Attempts",
            slug="test-course-for-quiz-attempts",
            description="Test course for quiz attempt testing",
            category=category,
            coordinator=coordinator,
            status='published'
        )
        
        # Create a module
        module = Module.objects.create(
            course=course,
            title="Test Module for Quiz Attempts",
            description="Test module for quiz attempt testing",
            order=1
        )
        
        # Create quiz content
        content = Content.objects.create(
            module=module,
            title="Test Quiz Content",
            content_type='quiz',
            content="This is a quiz placeholder",
            order=1
        )
        
        # Create a quiz
        quiz = Quiz.objects.create(
            content=content,
            title="Test Quiz for Attempts",
            description="Quiz for attempt testing",
            passing_score=70,
            time_limit=30,
            attempts_allowed=3
        )
        
        # Create a multiple choice question
        mc_question = Question.objects.create(
            quiz=quiz,
            question_text="What is the capital of France?",
            question_type='multiple_choice',
            points=2
        )
        
        # Add choices to multiple choice question
        Choice.objects.create(
            question=mc_question,
            choice_text="Paris",
            is_correct=True
        )
        Choice.objects.create(
            question=mc_question,
            choice_text="London",
            is_correct=False
        )
        Choice.objects.create(
            question=mc_question,
            choice_text="Berlin",
            is_correct=False
        )
        
        # Create a true/false question
        tf_question = Question.objects.create(
            quiz=quiz,
            question_text="Paris is the capital of France.",
            question_type='true_false',
            points=1
        )
        
        # Add choices to true/false question
        Choice.objects.create(
            question=tf_question,
            choice_text="True",
            is_correct=True
        )
        Choice.objects.create(
            question=tf_question,
            choice_text="False",
            is_correct=False
        )
        
        # Create a student
        student = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='password123'
        )
        
        return {
            'quiz': quiz,
            'student': student,
            'mc_question': mc_question,
            'tf_question': tf_question
        }
    
    def test_create_quiz_attempt(self, setup_quiz_data):
        """Test creating a new quiz attempt."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        
        # Create the quiz attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress',
            started_at=timezone.now()
        )
        
        # Assertions for creation
        assert attempt.id is not None
        assert attempt.student == student
        assert attempt.quiz == quiz
        assert attempt.status == 'in_progress'
        assert attempt.score is None
        assert attempt.started_at is not None
        assert attempt.submitted_at is None
        assert attempt.graded_at is None
        assert attempt.time_spent == 0
    
    def test_read_quiz_attempt(self, setup_quiz_data):
        """Test retrieving a quiz attempt."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress'
        )
        
        # Retrieve by ID
        retrieved_by_id = QuizAttempt.objects.get(id=attempt.id)
        assert retrieved_by_id.student == student
        assert retrieved_by_id.quiz == quiz
        
        # Test filtering by student
        student_attempts = QuizAttempt.objects.filter(student=student)
        assert attempt in student_attempts
        
        # Test filtering by quiz
        quiz_attempts = QuizAttempt.objects.filter(quiz=quiz)
        assert attempt in quiz_attempts
        
        # Test filtering by status
        in_progress_attempts = QuizAttempt.objects.filter(status='in_progress')
        assert attempt in in_progress_attempts
    
    def test_update_quiz_attempt(self, setup_quiz_data):
        """Test updating a quiz attempt."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress',
            started_at=timezone.now()
        )
        
        # Update the attempt to submitted
        now = timezone.now()
        attempt.status = 'submitted'
        attempt.score = 75.0
        attempt.submitted_at = now
        attempt.time_spent = 600  # 10 minutes in seconds
        attempt.save()
        
        # Refresh from database
        attempt.refresh_from_db()
        
        # Assertions
        assert attempt.status == 'submitted'
        assert attempt.score == 75.0
        assert attempt.submitted_at is not None
        assert attempt.time_spent == 600
        
        # Update to graded
        attempt.status = 'graded'
        attempt.graded_at = timezone.now()
        attempt.save()
        
        # Refresh from database
        attempt.refresh_from_db()
        
        # Assertions
        assert attempt.status == 'graded'
        assert attempt.graded_at is not None
    
    def test_delete_quiz_attempt(self, setup_quiz_data):
        """Test deleting a quiz attempt."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress'
        )
        
        # Verify created
        attempt_id = attempt.id
        assert QuizAttempt.objects.filter(id=attempt_id).exists()
        
        # Delete the attempt
        attempt.delete()
        
        # Verify deleted
        assert not QuizAttempt.objects.filter(id=attempt_id).exists()
    
    def test_create_answer(self, setup_quiz_data):
        """Test creating answers for a quiz attempt."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        mc_question = data['mc_question']
        tf_question = data['tf_question']
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress'
        )
        
        # Create answers
        mc_answer = Answer.objects.create(
            attempt=attempt,
            question=mc_question,
            answer_text="Paris",
            is_correct=True,
            points_earned=mc_question.points,
            time_spent=15
        )
        
        tf_answer = Answer.objects.create(
            attempt=attempt,
            question=tf_question,
            answer_text="True",
            is_correct=True,
            points_earned=tf_question.points,
            time_spent=10
        )
        
        # Assertions for creation
        assert mc_answer.id is not None
        assert mc_answer.attempt == attempt
        assert mc_answer.question == mc_question
        assert mc_answer.answer_text == "Paris"
        assert mc_answer.is_correct is True
        assert mc_answer.points_earned == mc_question.points
        assert mc_answer.time_spent == 15
        assert mc_answer.created_at is not None
        assert mc_answer.updated_at is not None
        
        assert tf_answer.id is not None
        assert tf_answer.attempt == attempt
        assert tf_answer.question == tf_question
        assert tf_answer.answer_text == "True"
        assert tf_answer.is_correct is True
        assert tf_answer.points_earned == tf_question.points
        
        # Verify answers are related to the attempt
        attempt_answers = attempt.answers.all()
        assert mc_answer in attempt_answers
        assert tf_answer in attempt_answers
        assert attempt_answers.count() == 2
    
    def test_read_answer(self, setup_quiz_data):
        """Test retrieving answers."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        mc_question = data['mc_question']
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress'
        )
        
        # Create an answer
        answer = Answer.objects.create(
            attempt=attempt,
            question=mc_question,
            answer_text="Paris",
            is_correct=True,
            points_earned=mc_question.points
        )
        
        # Retrieve by ID
        retrieved_by_id = Answer.objects.get(id=answer.id)
        assert retrieved_by_id.answer_text == "Paris"
        
        # Retrieve by attempt and question
        retrieved_by_attempt_question = Answer.objects.get(
            attempt=attempt, 
            question=mc_question
        )
        assert retrieved_by_attempt_question.id == answer.id
        
        # Test filtering
        correct_answers = Answer.objects.filter(is_correct=True)
        assert answer in correct_answers
        
        # Test filtering by points
        full_points_answers = Answer.objects.filter(points_earned=mc_question.points)
        assert answer in full_points_answers
    
    def test_update_answer(self, setup_quiz_data):
        """Test updating an answer."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        mc_question = data['mc_question']
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress'
        )
        
        # Create an answer
        answer = Answer.objects.create(
            attempt=attempt,
            question=mc_question,
            answer_text="Berlin",  # Incorrect answer
            is_correct=False,
            points_earned=0
        )
        
        # Update the answer
        new_answer_text = "Paris"  # Correct answer
        
        # Store original timestamps
        original_created_at = answer.created_at
        original_updated_at = answer.updated_at
        
        # Modify and save
        answer.answer_text = new_answer_text
        answer.is_correct = True
        answer.points_earned = mc_question.points
        answer.time_spent = 30
        answer.save()
        
        # Refresh from database
        answer.refresh_from_db()
        
        # Assertions
        assert answer.answer_text == new_answer_text
        assert answer.is_correct is True
        assert answer.points_earned == mc_question.points
        assert answer.time_spent == 30
        assert answer.created_at == original_created_at  # Should not change
        assert answer.updated_at > original_updated_at  # Should be updated
    
    def test_delete_answer(self, setup_quiz_data):
        """Test deleting an answer."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        mc_question = data['mc_question']
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress'
        )
        
        # Create an answer
        answer = Answer.objects.create(
            attempt=attempt,
            question=mc_question,
            answer_text="Paris",
            is_correct=True,
            points_earned=mc_question.points
        )
        
        # Verify created
        answer_id = answer.id
        assert Answer.objects.filter(id=answer_id).exists()
        
        # Delete the answer
        answer.delete()
        
        # Verify deleted
        assert not Answer.objects.filter(id=answer_id).exists()
    
    def test_unique_constraint(self, setup_quiz_data):
        """Test the unique constraint of attempt and question for answers."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        mc_question = data['mc_question']
        
        # Create an attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress'
        )
        
        # Create an answer
        Answer.objects.create(
            attempt=attempt,
            question=mc_question,
            answer_text="Paris",
            is_correct=True,
            points_earned=mc_question.points
        )
        
        # Attempt to create another answer for the same attempt and question
        # This should raise an IntegrityError due to the unique_together constraint
        with pytest.raises(Exception) as excinfo:
            Answer.objects.create(
                attempt=attempt,
                question=mc_question,
                answer_text="London",
                is_correct=False,
                points_earned=0
            )
    
    def test_quiz_workflow(self, setup_quiz_data):
        """Test a complete quiz workflow."""
        data = setup_quiz_data
        quiz = data['quiz']
        student = data['student']
        mc_question = data['mc_question']
        tf_question = data['tf_question']
        
        # Create a quiz attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status='in_progress',
            started_at=timezone.now()
        )
        
        # Answer questions
        Answer.objects.create(
            attempt=attempt,
            question=mc_question,
            answer_text="Paris",  # Correct
            is_correct=True,
            points_earned=mc_question.points,
            time_spent=20
        )
        
        Answer.objects.create(
            attempt=attempt,
            question=tf_question,
            answer_text="True",  # Correct
            is_correct=True,
            points_earned=tf_question.points,
            time_spent=10
        )
        
        # Calculate total points
        total_points = mc_question.points + tf_question.points
        earned_points = mc_question.points + tf_question.points
        
        # Submit the attempt
        attempt.status = 'submitted'
        attempt.score = (earned_points / total_points) * 100
        attempt.submitted_at = timezone.now()
        attempt.time_spent = 30  # Total time in seconds
        attempt.save()
        
        # Refresh from database
        attempt.refresh_from_db()
        
        # Assertions for submission
        assert attempt.status == 'submitted'
        assert attempt.score == 100.0  # Both answers correct
        assert attempt.submitted_at is not None
        assert attempt.time_spent == 30
        
        # Grade the attempt
        attempt.status = 'graded'
        attempt.graded_at = timezone.now()
        attempt.save()
        
        # Refresh from database
        attempt.refresh_from_db()
        
        # Assertions for grading
        assert attempt.status == 'graded'
        assert attempt.graded_at is not None