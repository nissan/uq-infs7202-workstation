import pytest
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Module, Content, Category, Quiz

User = get_user_model()

@pytest.mark.django_db
class TestQuizModel:
    """
    Tests for the Quiz model CRUD operations.
    """
    
    @pytest.fixture
    def setup_content(self):
        """Set up test content for quiz testing."""
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
            title="Test Course for Quiz",
            slug="test-course-for-quiz",
            description="Test course for quiz testing",
            category=category,
            coordinator=coordinator,
            status='published'
        )
        
        # Create a module
        module = Module.objects.create(
            course=course,
            title="Test Module for Quiz",
            description="Test module for quiz testing",
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
        
        return content
    
    def test_create_quiz(self, setup_content):
        """Test creating a new quiz."""
        content = setup_content
        
        title = "Test Quiz"
        description = "Test quiz description"
        
        # Create the quiz
        quiz = Quiz.objects.create(
            content=content,
            title=title,
            description=description,
            passing_score=70,
            time_limit=30,  # 30 minutes
            attempts_allowed=3,
            shuffle_questions=True,
            show_correct_answers=True
        )
        
        # Assertions for creation
        assert quiz.id is not None
        assert quiz.content == content
        assert quiz.title == title
        assert quiz.description == description
        assert quiz.passing_score == 70
        assert quiz.time_limit == 30
        assert quiz.attempts_allowed == 3
        assert quiz.shuffle_questions is True
        assert quiz.show_correct_answers is True
        assert quiz.is_prerequisite is False
        assert quiz.is_pre_check is False
        assert quiz.created_at is not None
        assert quiz.updated_at is not None
    
    def test_read_quiz(self, setup_content):
        """Test retrieving a quiz."""
        content = setup_content
        
        # Create a quiz
        title = "Quiz for Reading"
        quiz = Quiz.objects.create(
            content=content,
            title=title,
            description="Quiz for retrieval testing",
            passing_score=70,
            time_limit=45
        )
        
        # Retrieve by ID
        retrieved_by_id = Quiz.objects.get(id=quiz.id)
        assert retrieved_by_id.title == title
        
        # Retrieve by content
        retrieved_by_content = Quiz.objects.get(content=content)
        assert retrieved_by_content.id == quiz.id
        
        # Test filtering
        time_limited_quizzes = Quiz.objects.filter(time_limit__gt=0)
        assert quiz in time_limited_quizzes
        
        prerequisite_quizzes = Quiz.objects.filter(is_prerequisite=True)
        assert quiz not in prerequisite_quizzes
    
    def test_update_quiz(self, setup_content):
        """Test updating a quiz."""
        content = setup_content
        
        # Create a quiz
        quiz = Quiz.objects.create(
            content=content,
            title="Original Quiz Title",
            description="Original description",
            passing_score=70,
            time_limit=30,
            attempts_allowed=3,
            shuffle_questions=True,
            show_correct_answers=True
        )
        
        # Update the quiz
        new_title = "Updated Quiz Title"
        new_description = "Updated description"
        new_passing_score = 80
        new_time_limit = 45
        
        # Store original timestamps
        original_created_at = quiz.created_at
        original_updated_at = quiz.updated_at
        
        # Modify and save
        quiz.title = new_title
        quiz.description = new_description
        quiz.passing_score = new_passing_score
        quiz.time_limit = new_time_limit
        quiz.shuffle_questions = False
        quiz.is_prerequisite = True
        quiz.save()
        
        # Refresh from database
        quiz.refresh_from_db()
        
        # Assertions
        assert quiz.title == new_title
        assert quiz.description == new_description
        assert quiz.passing_score == new_passing_score
        assert quiz.time_limit == new_time_limit
        assert quiz.shuffle_questions is False
        assert quiz.is_prerequisite is True
        assert quiz.created_at == original_created_at  # Should not change
        assert quiz.updated_at > original_updated_at  # Should be updated
    
    def test_delete_quiz(self, setup_content):
        """Test deleting a quiz."""
        content = setup_content
        
        # Create a quiz
        quiz = Quiz.objects.create(
            content=content,
            title="Quiz to Delete",
            description="This quiz will be deleted",
            passing_score=70
        )
        
        # Verify created
        quiz_id = quiz.id
        assert Quiz.objects.filter(id=quiz_id).exists()
        
        # Delete the quiz
        quiz.delete()
        
        # Verify deleted
        assert not Quiz.objects.filter(id=quiz_id).exists()
    
    def test_one_to_one_constraint(self, setup_content):
        """Test the one-to-one constraint with content."""
        content = setup_content
        
        # Create a quiz
        Quiz.objects.create(
            content=content,
            title="First Quiz",
            description="First quiz description",
            passing_score=70
        )
        
        # Attempt to create another quiz for the same content
        # This should raise an IntegrityError due to the one-to-one constraint
        with pytest.raises(Exception) as excinfo:
            Quiz.objects.create(
                content=content,
                title="Second Quiz",
                description="Should fail",
                passing_score=70
            )
    
    def test_str_representation(self, setup_content):
        """Test the string representation of a quiz."""
        content = setup_content
        
        title = "Test String Quiz"
        quiz = Quiz.objects.create(
            content=content,
            title=title,
            description="Description",
            passing_score=70
        )
        
        assert str(quiz) == title