import pytest
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Category, CourseEnrollment

User = get_user_model()

@pytest.mark.django_db
class TestCourseEnrollmentModel:
    """
    Tests for the CourseEnrollment model CRUD operations.
    """
    
    @pytest.fixture
    def setup_data(self):
        """Set up test data for enrollment testing."""
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
            title="Test Course for Enrollment",
            slug="test-course-for-enrollment",
            description="Test course for enrollment testing",
            category=category,
            coordinator=coordinator,
            status='published'
        )
        
        # Create a student
        student = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='password123'
        )
        
        return {'course': course, 'student': student}
    
    def test_create_enrollment(self, setup_data):
        """Test creating a new enrollment."""
        data = setup_data
        course = data['course']
        student = data['student']
        
        # Create the enrollment
        enrollment = CourseEnrollment.objects.create(
            student=student,
            course=course,
            status='active',
            progress=0,
            enrolled_at=timezone.now()
        )
        
        # Assertions for creation
        assert enrollment.id is not None
        assert enrollment.student == student
        assert enrollment.course == course
        assert enrollment.status == 'active'
        assert enrollment.progress == 0
        assert enrollment.enrolled_at is not None
        assert enrollment.completed_at is None
    
    def test_read_enrollment(self, setup_data):
        """Test retrieving an enrollment."""
        data = setup_data
        course = data['course']
        student = data['student']
        
        # Create an enrollment
        enrollment = CourseEnrollment.objects.create(
            student=student,
            course=course,
            status='active',
            progress=10
        )
        
        # Retrieve by ID
        retrieved_by_id = CourseEnrollment.objects.get(id=enrollment.id)
        assert retrieved_by_id.student == student
        assert retrieved_by_id.course == course
        
        # Retrieve by student and course
        retrieved_by_student_course = CourseEnrollment.objects.get(student=student, course=course)
        assert retrieved_by_student_course.id == enrollment.id
        
        # Test filtering
        student_enrollments = CourseEnrollment.objects.filter(student=student)
        assert enrollment in student_enrollments
        
        course_enrollments = CourseEnrollment.objects.filter(course=course)
        assert enrollment in course_enrollments
        
        active_enrollments = CourseEnrollment.objects.filter(status='active')
        assert enrollment in active_enrollments
    
    def test_update_enrollment(self, setup_data):
        """Test updating an enrollment."""
        data = setup_data
        course = data['course']
        student = data['student']
        
        # Create an enrollment
        enrollment = CourseEnrollment.objects.create(
            student=student,
            course=course,
            status='active',
            progress=0
        )
        
        # Update the enrollment
        enrollment.status = 'completed'
        enrollment.progress = 100
        enrollment.completed_at = timezone.now()
        enrollment.save()
        
        # Refresh from database
        enrollment.refresh_from_db()
        
        # Assertions
        assert enrollment.status == 'completed'
        assert enrollment.progress == 100
        assert enrollment.completed_at is not None
    
    def test_delete_enrollment(self, setup_data):
        """Test deleting an enrollment."""
        data = setup_data
        course = data['course']
        student = data['student']
        
        # Create an enrollment
        enrollment = CourseEnrollment.objects.create(
            student=student,
            course=course,
            status='active',
            progress=0
        )
        
        # Verify created
        enrollment_id = enrollment.id
        assert CourseEnrollment.objects.filter(id=enrollment_id).exists()
        
        # Delete the enrollment
        enrollment.delete()
        
        # Verify deleted
        assert not CourseEnrollment.objects.filter(id=enrollment_id).exists()
    
    def test_unique_constraint(self, setup_data):
        """Test the unique constraint of student and course."""
        data = setup_data
        course = data['course']
        student = data['student']
        
        # Create an enrollment
        CourseEnrollment.objects.create(
            student=student,
            course=course,
            status='active',
            progress=0
        )
        
        # Attempt to create another enrollment for the same student and course
        # This should raise an IntegrityError due to the unique_together constraint
        with pytest.raises(Exception) as excinfo:
            CourseEnrollment.objects.create(
                student=student,
                course=course,
                status='dropped',
                progress=0
            )
    
    def test_str_representation(self, setup_data):
        """Test the string representation of an enrollment."""
        data = setup_data
        course = data['course']
        student = data['student']
        
        enrollment = CourseEnrollment.objects.create(
            student=student,
            course=course,
            status='active',
            progress=0
        )
        
        expected_str = f"{student.username} - {course.title}"
        assert str(enrollment) == expected_str