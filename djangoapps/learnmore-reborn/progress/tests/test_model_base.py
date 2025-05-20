from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course
from progress.models import Progress

User = get_user_model()

class ProgressModelTest(TestCase):
    """Tests for Progress model CRUD operations."""
    
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
        
        # Progress data
        self.progress_data = {
            'user': self.student,
            'course': self.course,
            'completed_lessons': 2,
            'total_lessons': 10,
        }
    
    def test_create_progress(self):
        """Test creating a new progress record."""
        progress = Progress.objects.create(**self.progress_data)
        
        # Assertions for creation
        self.assertIsNotNone(progress.id)
        self.assertEqual(progress.user, self.student)
        self.assertEqual(progress.course, self.course)
        self.assertEqual(progress.completed_lessons, 2)
        self.assertEqual(progress.total_lessons, 10)
        self.assertIsNotNone(progress.last_accessed)
    
    def test_read_progress(self):
        """Test retrieving a progress record."""
        # Create the progress first
        original = Progress.objects.create(**self.progress_data)
        
        # Retrieve by ID
        retrieved_by_id = Progress.objects.get(id=original.id)
        self.assertEqual(retrieved_by_id.user, self.student)
        self.assertEqual(retrieved_by_id.course, self.course)
        
        # Retrieve by user and course
        retrieved_by_user_course = Progress.objects.get(user=self.student, course=self.course)
        self.assertEqual(retrieved_by_user_course.id, original.id)
        
        # Test filtering
        user_progress = Progress.objects.filter(user=self.student)
        self.assertIn(original, user_progress)
        
        course_progress = Progress.objects.filter(course=self.course)
        self.assertIn(original, course_progress)
    
    def test_update_progress(self):
        """Test updating a progress record."""
        # Create the progress first
        progress = Progress.objects.create(**self.progress_data)
        
        # Store original last_accessed
        original_last_accessed = progress.last_accessed
        
        # Update progress
        progress.completed_lessons = 5
        progress.save()
        
        # Refresh from database
        progress.refresh_from_db()
        
        # Assertions for update
        self.assertEqual(progress.completed_lessons, 5)
        self.assertGreater(progress.last_accessed, original_last_accessed)  # last_accessed should update
    
    def test_delete_progress(self):
        """Test deleting a progress record."""
        # Create the progress first
        progress = Progress.objects.create(**self.progress_data)
        progress_id = progress.id
        
        # Verify created
        self.assertTrue(Progress.objects.filter(id=progress_id).exists())
        
        # Delete the progress
        progress.delete()
        
        # Verify deleted
        self.assertFalse(Progress.objects.filter(id=progress_id).exists())
    
    def test_unique_constraint(self):
        """Test unique constraint between user and course."""
        # Create first progress
        Progress.objects.create(**self.progress_data)
        
        # Try to create a duplicate progress
        with self.assertRaises(Exception):
            Progress.objects.create(**self.progress_data)
    
    def test_multiple_progress_different_users(self):
        """Test creating progress records for multiple users."""
        # Create first progress
        progress1 = Progress.objects.create(**self.progress_data)
        
        # Create second student
        student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='testpass123'
        )
        
        # Create second progress for the same course but different student
        progress2 = Progress.objects.create(
            user=student2,
            course=self.course,
            completed_lessons=3,
            total_lessons=10
        )
        
        # Verify both progress records exist
        self.assertEqual(Progress.objects.filter(course=self.course).count(), 2)
        self.assertEqual(Progress.objects.filter(user=self.student).count(), 1)
        self.assertEqual(Progress.objects.filter(user=student2).count(), 1)
    
    def test_str_representation(self):
        """Test string representation of Progress."""
        progress = Progress.objects.create(**self.progress_data)
        expected_str = f"{self.student.username} progress in {self.course.title}"
        self.assertEqual(str(progress), expected_str)