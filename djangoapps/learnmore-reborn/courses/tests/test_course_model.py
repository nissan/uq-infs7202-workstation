from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from courses.models import Course
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase

User = get_user_model()

class CourseModelTest(AuthDisabledTestCase):
    """Tests for Course model CRUD operations."""
    
    def setUp(self):
        """Set up test data."""
        self.instructor = User.objects.create_user(
            username='instructor1',
            email='instructor1@example.com',
            password='testpass123'
        )
        
        self.course_data = {
            'title': 'Test Course',
            'description': 'Test course description',
            'instructor': self.instructor,
            'status': 'published',
            'enrollment_type': 'open',
            'max_students': 100,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timezone.timedelta(days=90),
        }
        
    def test_create_course(self):
        """Test creating a new course."""
        course = Course.objects.create(**self.course_data)
        
        # Assertions for creation
        self.assertIsNotNone(course.id)
        self.assertEqual(course.title, self.course_data['title'])
        self.assertEqual(course.slug, slugify(self.course_data['title']))
        self.assertEqual(course.description, self.course_data['description'])
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(course.status, 'published')
        self.assertEqual(course.enrollment_type, 'open')
        self.assertEqual(course.max_students, 100)
        self.assertIsNotNone(course.created_at)
        self.assertIsNotNone(course.updated_at)
        
        # Test property methods
        self.assertTrue(course.is_active)
        self.assertEqual(course.enrollment_count, 0)
        self.assertFalse(course.is_full)
    
    def test_read_course(self):
        """Test retrieving a course."""
        # Create the course first
        original = Course.objects.create(**self.course_data)
        
        # Retrieve by ID
        retrieved_by_id = Course.objects.get(id=original.id)
        self.assertEqual(retrieved_by_id.title, self.course_data['title'])
        
        # Retrieve by slug
        retrieved_by_slug = Course.objects.get(slug=original.slug)
        self.assertEqual(retrieved_by_slug.id, original.id)
        
        # Test filtering
        published_courses = Course.objects.filter(status='published')
        self.assertIn(original, published_courses)
        
        # Test filtering by instructor
        instructor_courses = Course.objects.filter(instructor=self.instructor)
        self.assertIn(original, instructor_courses)
    
    def test_update_course(self):
        """Test updating a course."""
        # Create the course first
        course = Course.objects.create(**self.course_data)
        
        # Store original timestamps
        original_created_at = course.created_at
        original_updated_at = course.updated_at
        
        # Update the course
        new_title = 'Updated Course Title'
        new_description = 'Updated course description'
        
        course.title = new_title
        course.description = new_description
        course.max_students = 50
        course.save()
        
        # Refresh from database
        course.refresh_from_db()
        
        # Assertions for update
        self.assertEqual(course.title, new_title)
        self.assertEqual(course.slug, slugify(new_title))  # Slug should be updated
        self.assertEqual(course.description, new_description)
        self.assertEqual(course.max_students, 50)
        self.assertEqual(course.created_at, original_created_at)  # Should not change
        self.assertGreater(course.updated_at, original_updated_at)  # Should be updated
    
    def test_delete_course(self):
        """Test deleting a course."""
        # Create the course first
        course = Course.objects.create(**self.course_data)
        course_id = course.id
        
        # Verify created
        self.assertTrue(Course.objects.filter(id=course_id).exists())
        
        # Delete the course
        course.delete()
        
        # Verify deleted
        self.assertFalse(Course.objects.filter(id=course_id).exists())
    
    def test_course_inactive_when_draft(self):
        """Test that a course is inactive when in draft status."""
        course_data = self.course_data.copy()
        course_data['status'] = 'draft'
        course = Course.objects.create(**course_data)
        
        self.assertFalse(course.is_active)
    
    def test_course_inactive_when_archived(self):
        """Test that a course is inactive when archived."""
        course_data = self.course_data.copy()
        course_data['status'] = 'archived'
        course = Course.objects.create(**course_data)
        
        self.assertFalse(course.is_active)
    
    def test_course_active_when_published_and_in_date_range(self):
        """Test that a course is active when published and within date range."""
        course = Course.objects.create(**self.course_data)
        
        self.assertTrue(course.is_active)
    
    def test_course_inactive_when_outside_date_range(self):
        """Test that a course is inactive when outside date range."""
        course_data = self.course_data.copy()
        course_data['start_date'] = timezone.now().date() - timezone.timedelta(days=100)  
        course_data['end_date'] = timezone.now().date() - timezone.timedelta(days=10)  # Past end date
        course = Course.objects.create(**course_data)
        
        self.assertFalse(course.is_active)
    
    def test_course_full_logic(self):
        """Test the is_full property."""
        # Create a course with max_students = 1
        course_data = self.course_data.copy()
        course_data['max_students'] = 1
        course = Course.objects.create(**course_data)
        
        self.assertFalse(course.is_full)  # No enrollments yet
        
        # Create an enrollment
        student = User.objects.create_user(username='student1', password='pass')
        from courses.models import Enrollment
        Enrollment.objects.create(
            user=student,
            course=course,
            status='active'
        )
        
        # Now the course should be full
        self.assertTrue(course.is_full)
    
    def test_str_representation(self):
        """Test string representation of Course."""
        course = Course.objects.create(**self.course_data)
        self.assertEqual(str(course), self.course_data['title'])
        
    def test_course_type_field(self):
        """Test that course_type field has the correct default and choices."""
        course = Course.objects.create(**self.course_data)
        
        # Test default value
        self.assertEqual(course.course_type, 'standard')
        
        # Test changing to other valid value
        course.course_type = 'self_paced'
        course.save()
        course.refresh_from_db()
        self.assertEqual(course.course_type, 'self_paced')
        
        # Test changing to another valid value
        course.course_type = 'intensive'
        course.save()
        course.refresh_from_db()
        self.assertEqual(course.course_type, 'intensive')