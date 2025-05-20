from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import Course, Enrollment

User = get_user_model()

class EnrollmentModelTest(TestCase):
    """Tests for Enrollment model CRUD operations."""
    
    def setUp(self):
        """Set up test data."""
        # Create an instructor and a student
        self.instructor = User.objects.create_user(
            username='instructor1',
            email='instructor1@example.com',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass123'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test course description',
            instructor=self.instructor,
            status='published'
        )
        
        # Enrollment data
        self.enrollment_data = {
            'user': self.student,
            'course': self.course,
            'status': 'active',
            'progress': 0
        }
    
    def test_create_enrollment(self):
        """Test creating a new enrollment."""
        enrollment = Enrollment.objects.create(**self.enrollment_data)
        
        # Assertions for creation
        self.assertIsNotNone(enrollment.id)
        self.assertEqual(enrollment.user, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.status, 'active')
        self.assertEqual(enrollment.progress, 0)
        self.assertIsNotNone(enrollment.enrolled_at)
        self.assertIsNone(enrollment.completed_at)
    
    def test_read_enrollment(self):
        """Test retrieving an enrollment."""
        # Create the enrollment first
        original = Enrollment.objects.create(**self.enrollment_data)
        
        # Retrieve by ID
        retrieved_by_id = Enrollment.objects.get(id=original.id)
        self.assertEqual(retrieved_by_id.user, self.student)
        self.assertEqual(retrieved_by_id.course, self.course)
        
        # Retrieve by user and course
        retrieved_by_user_course = Enrollment.objects.get(user=self.student, course=self.course)
        self.assertEqual(retrieved_by_user_course.id, original.id)
        
        # Test filtering by status
        active_enrollments = Enrollment.objects.filter(status='active')
        self.assertIn(original, active_enrollments)
        
        # Test student and course relationships
        student_enrollments = Enrollment.objects.filter(user=self.student)
        self.assertIn(original, student_enrollments)
        
        course_enrollments = Enrollment.objects.filter(course=self.course)
        self.assertIn(original, course_enrollments)
    
    def test_update_enrollment(self):
        """Test updating an enrollment."""
        # Create the enrollment first
        enrollment = Enrollment.objects.create(**self.enrollment_data)
        
        # Update progress
        enrollment.progress = 50
        enrollment.save()
        
        # Refresh from database
        enrollment.refresh_from_db()
        
        # Assertions for update
        self.assertEqual(enrollment.progress, 50)
        
        # Update status to completed
        enrollment.mark_completed()
        
        # Refresh from database
        enrollment.refresh_from_db()
        
        # Assertions for completion
        self.assertEqual(enrollment.status, 'completed')
        self.assertIsNotNone(enrollment.completed_at)
    
    def test_delete_enrollment(self):
        """Test deleting an enrollment."""
        # Create the enrollment first
        enrollment = Enrollment.objects.create(**self.enrollment_data)
        enrollment_id = enrollment.id
        
        # Verify created
        self.assertTrue(Enrollment.objects.filter(id=enrollment_id).exists())
        
        # Delete the enrollment
        enrollment.delete()
        
        # Verify deleted
        self.assertFalse(Enrollment.objects.filter(id=enrollment_id).exists())
    
    def test_unique_constraint(self):
        """Test unique constraint between user and course."""
        # Create first enrollment
        Enrollment.objects.create(**self.enrollment_data)
        
        # Try to create a duplicate enrollment
        with self.assertRaises(Exception):
            Enrollment.objects.create(**self.enrollment_data)
    
    def test_multiple_enrollments_different_students(self):
        """Test creating enrollments for multiple students."""
        # Create first enrollment
        enrollment1 = Enrollment.objects.create(**self.enrollment_data)
        
        # Create second student
        student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='testpass123'
        )
        
        # Create second enrollment for the same course but different student
        enrollment2 = Enrollment.objects.create(
            user=student2,
            course=self.course,
            status='active',
            progress=0
        )
        
        # Verify both enrollments exist
        self.assertEqual(Enrollment.objects.filter(course=self.course).count(), 2)
        self.assertEqual(Enrollment.objects.filter(user=self.student).count(), 1)
        self.assertEqual(Enrollment.objects.filter(user=student2).count(), 1)
    
    def test_enrollment_status_changes(self):
        """Test changing enrollment status."""
        enrollment = Enrollment.objects.create(**self.enrollment_data)
        
        # Test initial status
        self.assertEqual(enrollment.status, 'active')
        
        # Change to completed
        enrollment.status = 'completed'
        enrollment.completed_at = timezone.now()
        enrollment.save()
        
        # Refresh from database
        enrollment.refresh_from_db()
        
        # Verify status change
        self.assertEqual(enrollment.status, 'completed')
        self.assertIsNotNone(enrollment.completed_at)
        
        # Change to dropped
        enrollment.status = 'dropped'
        enrollment.save()
        
        # Refresh from database
        enrollment.refresh_from_db()
        
        # Verify status change
        self.assertEqual(enrollment.status, 'dropped')
    
    def test_str_representation(self):
        """Test string representation of Enrollment."""
        enrollment = Enrollment.objects.create(**self.enrollment_data)
        expected_str = f"{self.student.username} - {self.course.title}"
        self.assertEqual(str(enrollment), expected_str)