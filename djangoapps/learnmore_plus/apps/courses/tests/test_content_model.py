import pytest
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Module, Content, Category

User = get_user_model()

@pytest.mark.django_db
class TestContentModel:
    """
    Tests for the Content model CRUD operations.
    """
    
    @pytest.fixture
    def setup_module(self):
        """Set up a test module for content testing."""
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
            title="Test Course for Content",
            slug="test-course-for-content",
            description="Test course for content testing",
            category=category,
            coordinator=coordinator,
            status='published'
        )
        
        # Create a module
        module = Module.objects.create(
            course=course,
            title="Test Module for Content",
            description="Test module for content testing",
            order=1
        )
        
        return module
    
    def test_create_content(self, setup_module):
        """Test creating new content."""
        module = setup_module
        
        title = "Test Content"
        content_text = "This is test content text."
        
        # Create the content
        content = Content.objects.create(
            module=module,
            title=title,
            content_type='text',
            content=content_text,
            order=1,
            estimated_time=30  # 30 minutes
        )
        
        # Assertions for creation
        assert content.id is not None
        assert content.module == module
        assert content.title == title
        assert content.content_type == 'text'
        assert content.content == content_text
        assert content.order == 1
        assert content.estimated_time == 30
        assert content.created_at is not None
        assert content.updated_at is not None
    
    def test_read_content(self, setup_module):
        """Test retrieving content."""
        module = setup_module
        
        # Create content
        title = "Content for Reading"
        content = Content.objects.create(
            module=module,
            title=title,
            content_type='text',
            content="Content for retrieval testing",
            order=1
        )
        
        # Retrieve by ID
        retrieved_by_id = Content.objects.get(id=content.id)
        assert retrieved_by_id.title == title
        
        # Retrieve by module and order
        retrieved_by_module_order = Content.objects.get(module=module, order=1)
        assert retrieved_by_module_order.id == content.id
        
        # Test filtering by content type
        Content.objects.create(
            module=module,
            title="Video Content",
            content_type='video',
            content="https://example.com/video",
            order=2
        )
        
        text_contents = Content.objects.filter(content_type='text')
        video_contents = Content.objects.filter(content_type='video')
        
        assert content in text_contents
        assert content not in video_contents
        assert text_contents.count() == 1
        assert video_contents.count() == 1
    
    def test_update_content(self, setup_module):
        """Test updating content."""
        module = setup_module
        
        # Create content
        content = Content.objects.create(
            module=module,
            title="Original Content Title",
            content_type='text',
            content="Original content text",
            order=1,
            estimated_time=15
        )
        
        # Update the content
        new_title = "Updated Content Title"
        new_content_text = "Updated content text"
        new_content_type = 'file'
        new_estimated_time = 45
        
        # Store original timestamps
        original_created_at = content.created_at
        original_updated_at = content.updated_at
        
        # Modify and save
        content.title = new_title
        content.content = new_content_text
        content.content_type = new_content_type
        content.estimated_time = new_estimated_time
        content.save()
        
        # Refresh from database
        content.refresh_from_db()
        
        # Assertions
        assert content.title == new_title
        assert content.content == new_content_text
        assert content.content_type == new_content_type
        assert content.estimated_time == new_estimated_time
        assert content.created_at == original_created_at  # Should not change
        assert content.updated_at > original_updated_at  # Should be updated
    
    def test_delete_content(self, setup_module):
        """Test deleting content."""
        module = setup_module
        
        # Create content
        content = Content.objects.create(
            module=module,
            title="Content to Delete",
            content_type='text',
            content="This content will be deleted",
            order=1
        )
        
        # Verify created
        content_id = content.id
        assert Content.objects.filter(id=content_id).exists()
        
        # Delete the content
        content.delete()
        
        # Verify deleted
        assert not Content.objects.filter(id=content_id).exists()
    
    def test_unique_constraint(self, setup_module):
        """Test the unique constraint of module and order."""
        module = setup_module
        
        # Create content with order=1
        Content.objects.create(
            module=module,
            title="First Content",
            content_type='text',
            content="First content text",
            order=1
        )
        
        # Attempt to create another content with the same order
        # This should raise an IntegrityError due to the unique_together constraint
        with pytest.raises(Exception) as excinfo:
            Content.objects.create(
                module=module,
                title="Duplicate Order Content",
                content_type='text',
                content="This should fail",
                order=1
            )
        
        # Different order should work fine
        content2 = Content.objects.create(
            module=module,
            title="Second Content",
            content_type='text',
            content="Second content text",
            order=2
        )
        assert content2.id is not None
    
    def test_str_representation(self, setup_module):
        """Test the string representation of content."""
        module = setup_module
        
        title = "Test String Content"
        content = Content.objects.create(
            module=module,
            title=title,
            content_type='text',
            content="Test content text",
            order=1
        )
        
        expected_str = f"{module.title} - {title}"
        assert str(content) == expected_str
    
    def test_different_content_types(self, setup_module):
        """Test creating content with different content types."""
        module = setup_module
        
        # Test text content
        text_content = Content.objects.create(
            module=module,
            title="Text Content",
            content_type='text',
            content="This is text content",
            order=1
        )
        assert text_content.content_type == 'text'
        
        # Test video content
        video_content = Content.objects.create(
            module=module,
            title="Video Content",
            content_type='video',
            content="https://example.com/video.mp4",
            order=2
        )
        assert video_content.content_type == 'video'
        
        # Test file content
        file_content = Content.objects.create(
            module=module,
            title="File Content",
            content_type='file',
            content="/path/to/file.pdf",
            order=3
        )
        assert file_content.content_type == 'file'
        
        # Test quiz content
        quiz_content = Content.objects.create(
            module=module,
            title="Quiz Content",
            content_type='quiz',
            content="Quiz placeholder",
            order=4
        )
        assert quiz_content.content_type == 'quiz'