import pytest
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.courses.models import Course, Category

User = get_user_model()

@pytest.mark.django_db
class TestCourseModel:
    """
    Tests for the Course model CRUD operations.
    """
    
    @pytest.fixture
    def setup_users(self):
        """Setup instructor and coordinator users."""
        # Create instructor user
        instructor_group, _ = Group.objects.get_or_create(name='Instructor')
        instructor = User.objects.create_user(
            username='test_instructor',
            email='instructor@test.com',
            password='password123'
        )
        instructor.groups.add(instructor_group)
        
        # Create coordinator user
        coordinator_group, _ = Group.objects.get_or_create(name='Course Coordinator')
        coordinator = User.objects.create_user(
            username='test_coordinator',
            email='coordinator@test.com',
            password='password123'
        )
        coordinator.groups.add(coordinator_group)
        
        return {'instructor': instructor, 'coordinator': coordinator}
    
    @pytest.fixture
    def category(self):
        """Create a test category."""
        return Category.objects.create(
            name="Test Category",
            slug="test-category",
            description="Test category description"
        )
    
    def test_create_course(self, setup_users, category):
        """Test creating a new course."""
        users = setup_users
        
        title = "Test Course"
        description = "Test course description"
        
        # Create the course
        course = Course.objects.create(
            title=title,
            slug=slugify(title),
            description=description,
            category=category,
            coordinator=users['coordinator'],
            status='published',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=90),
        )
        
        # Add instructors
        course.instructors.add(users['instructor'])
        
        # Assertions for creation
        assert course.id is not None
        assert course.title == title
        assert course.slug == slugify(title)
        assert course.description == description
        assert course.category == category
        assert course.coordinator == users['coordinator']
        assert course.instructors.count() == 1
        assert course.instructors.first() == users['instructor']
        assert course.status == 'published'
        assert course.created_at is not None
        assert course.updated_at is not None
        
        # Test property methods
        assert course.is_active is True  # Using date fields
        assert course.enrollment_count == 0
        assert course.is_full is False
    
    def test_read_course(self, setup_users, category):
        """Test retrieving a course."""
        users = setup_users
        
        # Create a course
        title = "Course for Reading"
        course = Course.objects.create(
            title=title,
            slug=slugify(title),
            description="Description for retrieval testing",
            category=category,
            coordinator=users['coordinator'],
            status='published'
        )
        course.instructors.add(users['instructor'])
        
        # Retrieve by ID
        retrieved_by_id = Course.objects.get(id=course.id)
        assert retrieved_by_id.title == title
        
        # Retrieve by slug
        retrieved_by_slug = Course.objects.get(slug=slugify(title))
        assert retrieved_by_slug.id == course.id
        
        # Test filtering
        published_courses = Course.objects.filter(status='published')
        assert course in published_courses
        
        # Test filtering by instructor
        instructor_courses = Course.objects.filter(instructors=users['instructor'])
        assert course in instructor_courses
        
        # Test filtering by coordinator
        coordinator_courses = Course.objects.filter(coordinator=users['coordinator'])
        assert course in coordinator_courses
    
    def test_update_course(self, setup_users, category):
        """Test updating a course."""
        users = setup_users
        
        # Create a course
        course = Course.objects.create(
            title="Original Course Title",
            slug="original-course-title",
            description="Original description",
            category=category,
            coordinator=users['coordinator'],
            status='draft'
        )
        
        # Update the course
        new_title = "Updated Course Title"
        new_description = "Updated description"
        
        # Store original timestamps
        original_created_at = course.created_at
        original_updated_at = course.updated_at
        
        # Modify and save
        course.title = new_title
        course.slug = slugify(new_title)
        course.description = new_description
        course.status = 'published'
        course.save()
        
        # Refresh from database
        course.refresh_from_db()
        
        # Assertions
        assert course.title == new_title
        assert course.slug == slugify(new_title)
        assert course.description == new_description
        assert course.status == 'published'
        assert course.created_at == original_created_at  # Should not change
        assert course.updated_at > original_updated_at  # Should be updated
    
    def test_delete_course(self, setup_users, category):
        """Test deleting a course."""
        users = setup_users
        
        # Create a course
        course = Course.objects.create(
            title="Course to Delete",
            slug="course-to-delete",
            description="This course will be deleted",
            category=category,
            coordinator=users['coordinator']
        )
        
        # Verify created
        course_id = course.id
        assert Course.objects.filter(id=course_id).exists()
        
        # Delete the course
        course.delete()
        
        # Verify deleted
        assert not Course.objects.filter(id=course_id).exists()
    
    def test_str_representation(self, setup_users, category):
        """Test the string representation of a course."""
        users = setup_users
        
        title = "Test String Course"
        course = Course.objects.create(
            title=title,
            slug=slugify(title),
            description="Description",
            category=category,
            coordinator=users['coordinator']
        )
        
        assert str(course) == title