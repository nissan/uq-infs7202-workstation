import pytest
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Module, Category

User = get_user_model()

@pytest.mark.django_db
class TestModuleModel:
    """
    Tests for the Module model CRUD operations.
    """
    
    @pytest.fixture
    def setup_course(self):
        """Set up a test course for module testing."""
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
            title="Test Course for Modules",
            slug="test-course-for-modules",
            description="Test course for module testing",
            category=category,
            coordinator=coordinator,
            status='published'
        )
        
        return course
    
    def test_create_module(self, setup_course):
        """Test creating a new module."""
        course = setup_course
        
        title = "Test Module"
        description = "Test module description"
        order = 1
        
        # Create the module
        module = Module.objects.create(
            course=course,
            title=title,
            description=description,
            order=order
        )
        
        # Assertions for creation
        assert module.id is not None
        assert module.course == course
        assert module.title == title
        assert module.description == description
        assert module.order == order
        assert module.created_at is not None
        assert module.updated_at is not None
    
    def test_read_module(self, setup_course):
        """Test retrieving a module."""
        course = setup_course
        
        # Create a module
        title = "Module for Reading"
        module = Module.objects.create(
            course=course,
            title=title,
            description="Description for retrieval testing",
            order=1
        )
        
        # Retrieve by ID
        retrieved_by_id = Module.objects.get(id=module.id)
        assert retrieved_by_id.title == title
        
        # Retrieve by course and order
        retrieved_by_course_order = Module.objects.get(course=course, order=1)
        assert retrieved_by_course_order.id == module.id
        
        # Test filtering
        course_modules = Module.objects.filter(course=course)
        assert module in course_modules
        
        # Test ordering
        Module.objects.create(
            course=course,
            title="Second Module",
            description="Second module for ordering test",
            order=2
        )
        
        ordered_modules = Module.objects.filter(course=course).order_by('order')
        assert ordered_modules[0].id == module.id
        assert ordered_modules[0].order == 1
        assert ordered_modules[1].order == 2
    
    def test_update_module(self, setup_course):
        """Test updating a module."""
        course = setup_course
        
        # Create a module
        module = Module.objects.create(
            course=course,
            title="Original Module Title",
            description="Original description",
            order=1
        )
        
        # Update the module
        new_title = "Updated Module Title"
        new_description = "Updated description"
        new_order = 3
        
        # Store original timestamps
        original_created_at = module.created_at
        original_updated_at = module.updated_at
        
        # Modify and save
        module.title = new_title
        module.description = new_description
        module.order = new_order
        module.save()
        
        # Refresh from database
        module.refresh_from_db()
        
        # Assertions
        assert module.title == new_title
        assert module.description == new_description
        assert module.order == new_order
        assert module.created_at == original_created_at  # Should not change
        assert module.updated_at > original_updated_at  # Should be updated
    
    def test_delete_module(self, setup_course):
        """Test deleting a module."""
        course = setup_course
        
        # Create a module
        module = Module.objects.create(
            course=course,
            title="Module to Delete",
            description="This module will be deleted",
            order=1
        )
        
        # Verify created
        module_id = module.id
        assert Module.objects.filter(id=module_id).exists()
        
        # Delete the module
        module.delete()
        
        # Verify deleted
        assert not Module.objects.filter(id=module_id).exists()
    
    def test_unique_constraint(self, setup_course):
        """Test the unique constraint of course and order."""
        course = setup_course
        
        # Create a module with order=1
        Module.objects.create(
            course=course,
            title="First Module",
            description="First module description",
            order=1
        )
        
        # Attempt to create another module with the same order
        # This should raise an IntegrityError due to the unique_together constraint
        with pytest.raises(Exception) as excinfo:
            Module.objects.create(
                course=course,
                title="Duplicate Order Module",
                description="This should fail",
                order=1
            )
        
        # Different order should work fine
        module2 = Module.objects.create(
            course=course,
            title="Second Module",
            description="Second module description",
            order=2
        )
        assert module2.id is not None
    
    def test_str_representation(self, setup_course):
        """Test the string representation of a module."""
        course = setup_course
        
        title = "Test String Module"
        module = Module.objects.create(
            course=course,
            title=title,
            description="Description",
            order=1
        )
        
        expected_str = f"{course.title} - {title}"
        assert str(module) == expected_str