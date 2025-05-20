import pytest
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.courses.models import (
    Course, Module, Content, Category, Quiz, Question, Choice
)

User = get_user_model()

@pytest.mark.django_db
class TestQuestionModel:
    """
    Tests for the Question and Choice models CRUD operations.
    """
    
    @pytest.fixture
    def setup_quiz(self):
        """Set up test quiz for question testing."""
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
            title="Test Course for Questions",
            slug="test-course-for-questions",
            description="Test course for question testing",
            category=category,
            coordinator=coordinator,
            status='published'
        )
        
        # Create a module
        module = Module.objects.create(
            course=course,
            title="Test Module for Questions",
            description="Test module for question testing",
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
            title="Test Quiz for Questions",
            description="Quiz for question testing",
            passing_score=70
        )
        
        return quiz
    
    def test_create_question(self, setup_quiz):
        """Test creating a new question."""
        quiz = setup_quiz
        
        question_text = "What is the answer to this test question?"
        
        # Create the question
        question = Question.objects.create(
            quiz=quiz,
            question_text=question_text,
            question_type='multiple_choice',
            points=2
        )
        
        # Assertions for creation
        assert question.id is not None
        assert question.quiz == quiz
        assert question.question_text == question_text
        assert question.question_type == 'multiple_choice'
        assert question.points == 2
        assert question.created_at is not None
        assert question.updated_at is not None
    
    def test_read_question(self, setup_quiz):
        """Test retrieving a question."""
        quiz = setup_quiz
        
        # Create a question
        question_text = "Question for Reading"
        question = Question.objects.create(
            quiz=quiz,
            question_text=question_text,
            question_type='multiple_choice',
            points=1
        )
        
        # Retrieve by ID
        retrieved_by_id = Question.objects.get(id=question.id)
        assert retrieved_by_id.question_text == question_text
        
        # Retrieve by quiz
        quiz_questions = Question.objects.filter(quiz=quiz)
        assert question in quiz_questions
        
        # Test filtering by question type
        Question.objects.create(
            quiz=quiz,
            question_text="True/False question",
            question_type='true_false',
            points=1
        )
        
        multiple_choice_questions = Question.objects.filter(question_type='multiple_choice')
        true_false_questions = Question.objects.filter(question_type='true_false')
        
        assert question in multiple_choice_questions
        assert question not in true_false_questions
        assert multiple_choice_questions.count() == 1
        assert true_false_questions.count() == 1
    
    def test_update_question(self, setup_quiz):
        """Test updating a question."""
        quiz = setup_quiz
        
        # Create a question
        question = Question.objects.create(
            quiz=quiz,
            question_text="Original question text",
            question_type='multiple_choice',
            points=1
        )
        
        # Update the question
        new_question_text = "Updated question text"
        new_question_type = 'short_answer'
        new_points = 3
        
        # Store original timestamps
        original_created_at = question.created_at
        original_updated_at = question.updated_at
        
        # Modify and save
        question.question_text = new_question_text
        question.question_type = new_question_type
        question.points = new_points
        question.save()
        
        # Refresh from database
        question.refresh_from_db()
        
        # Assertions
        assert question.question_text == new_question_text
        assert question.question_type == new_question_type
        assert question.points == new_points
        assert question.created_at == original_created_at  # Should not change
        assert question.updated_at > original_updated_at  # Should be updated
    
    def test_delete_question(self, setup_quiz):
        """Test deleting a question."""
        quiz = setup_quiz
        
        # Create a question
        question = Question.objects.create(
            quiz=quiz,
            question_text="Question to Delete",
            question_type='multiple_choice',
            points=1
        )
        
        # Verify created
        question_id = question.id
        assert Question.objects.filter(id=question_id).exists()
        
        # Delete the question
        question.delete()
        
        # Verify deleted
        assert not Question.objects.filter(id=question_id).exists()
    
    def test_str_representation(self, setup_quiz):
        """Test the string representation of a question."""
        quiz = setup_quiz
        
        question_text = "This is a test question"
        question = Question.objects.create(
            quiz=quiz,
            question_text=question_text,
            question_type='multiple_choice',
            points=1
        )
        
        expected_str = f"{quiz.title} - {question_text[:50]}"
        assert str(question) == expected_str
    
    def test_create_choice(self, setup_quiz):
        """Test creating choices for a question."""
        quiz = setup_quiz
        
        # Create a multiple choice question
        question = Question.objects.create(
            quiz=quiz,
            question_text="What is the capital of France?",
            question_type='multiple_choice',
            points=1
        )
        
        # Create choices
        choice1 = Choice.objects.create(
            question=question,
            choice_text="Paris",
            is_correct=True
        )
        
        choice2 = Choice.objects.create(
            question=question,
            choice_text="London",
            is_correct=False
        )
        
        choice3 = Choice.objects.create(
            question=question,
            choice_text="Berlin",
            is_correct=False
        )
        
        # Assertions for creation
        assert choice1.id is not None
        assert choice1.question == question
        assert choice1.choice_text == "Paris"
        assert choice1.is_correct is True
        assert choice1.created_at is not None
        assert choice1.updated_at is not None
        
        assert choice2.is_correct is False
        assert choice3.is_correct is False
        
        # Verify choices are related to the question
        question_choices = question.choices.all()
        assert choice1 in question_choices
        assert choice2 in question_choices
        assert choice3 in question_choices
        assert question_choices.count() == 3
    
    def test_read_choice(self, setup_quiz):
        """Test retrieving choices."""
        quiz = setup_quiz
        
        # Create a question
        question = Question.objects.create(
            quiz=quiz,
            question_text="What is the capital of Germany?",
            question_type='multiple_choice',
            points=1
        )
        
        # Create choices
        choice = Choice.objects.create(
            question=question,
            choice_text="Berlin",
            is_correct=True
        )
        
        # Retrieve by ID
        retrieved_by_id = Choice.objects.get(id=choice.id)
        assert retrieved_by_id.choice_text == "Berlin"
        
        # Retrieve by question
        question_choices = Choice.objects.filter(question=question)
        assert choice in question_choices
        
        # Test filtering by correctness
        correct_choices = Choice.objects.filter(is_correct=True)
        incorrect_choices = Choice.objects.filter(is_correct=False)
        
        assert choice in correct_choices
        assert choice not in incorrect_choices
    
    def test_update_choice(self, setup_quiz):
        """Test updating a choice."""
        quiz = setup_quiz
        
        # Create a question
        question = Question.objects.create(
            quiz=quiz,
            question_text="What is the capital of Spain?",
            question_type='multiple_choice',
            points=1
        )
        
        # Create a choice
        choice = Choice.objects.create(
            question=question,
            choice_text="Barcelona",
            is_correct=False
        )
        
        # Update the choice
        new_choice_text = "Madrid"
        
        # Store original timestamps
        original_created_at = choice.created_at
        original_updated_at = choice.updated_at
        
        # Modify and save
        choice.choice_text = new_choice_text
        choice.is_correct = True
        choice.save()
        
        # Refresh from database
        choice.refresh_from_db()
        
        # Assertions
        assert choice.choice_text == new_choice_text
        assert choice.is_correct is True
        assert choice.created_at == original_created_at  # Should not change
        assert choice.updated_at > original_updated_at  # Should be updated
    
    def test_delete_choice(self, setup_quiz):
        """Test deleting a choice."""
        quiz = setup_quiz
        
        # Create a question
        question = Question.objects.create(
            quiz=quiz,
            question_text="What is the capital of Italy?",
            question_type='multiple_choice',
            points=1
        )
        
        # Create a choice
        choice = Choice.objects.create(
            question=question,
            choice_text="Rome",
            is_correct=True
        )
        
        # Verify created
        choice_id = choice.id
        assert Choice.objects.filter(id=choice_id).exists()
        
        # Delete the choice
        choice.delete()
        
        # Verify deleted
        assert not Choice.objects.filter(id=choice_id).exists()
    
    def test_different_question_types(self, setup_quiz):
        """Test creating different types of questions."""
        quiz = setup_quiz
        
        # Multiple choice question
        mc_question = Question.objects.create(
            quiz=quiz,
            question_text="What is the capital of France?",
            question_type='multiple_choice',
            points=1
        )
        assert mc_question.question_type == 'multiple_choice'
        
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
        
        # True/False question
        tf_question = Question.objects.create(
            quiz=quiz,
            question_text="Paris is the capital of France.",
            question_type='true_false',
            points=1
        )
        assert tf_question.question_type == 'true_false'
        
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
        
        # Short answer question
        sa_question = Question.objects.create(
            quiz=quiz,
            question_text="What is the capital of France?",
            question_type='short_answer',
            points=1
        )
        assert sa_question.question_type == 'short_answer'
        
        # Verify all questions are in the database
        assert Question.objects.filter(quiz=quiz).count() == 3