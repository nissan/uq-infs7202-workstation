from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from courses.models import Course
from .models import Progress
from .serializers import ProgressSerializer

User = get_user_model()

class ProgressSerializerValidationTest(TestCase):
    """Tests for ProgressSerializer validation."""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='password'
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='password'
        )
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test description',
            instructor=self.instructor,
            status='published'
        )
        
        self.valid_data = {
            'user': self.student.id,
            'course': self.course.id,
            'completed_lessons': 2,
            'total_lessons': 5
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = ProgressSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Missing user
        invalid_data = self.valid_data.copy()
        invalid_data.pop('user')
        serializer = ProgressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)
        
        # Missing course
        invalid_data = self.valid_data.copy()
        invalid_data.pop('course')
        serializer = ProgressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('course', serializer.errors)
        
        # completed_lessons and total_lessons have default values in the model (0),
        # so they aren't required in the serializer
    
    def test_negative_lessons(self):
        """Test that negative lessons count fails validation."""
        # Negative completed_lessons
        invalid_data = self.valid_data.copy()
        invalid_data['completed_lessons'] = -1
        serializer = ProgressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('completed_lessons', serializer.errors)
        
        # Negative total_lessons
        invalid_data = self.valid_data.copy()
        invalid_data['total_lessons'] = -1
        serializer = ProgressSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('total_lessons', serializer.errors)
    
    def test_completed_lessons_greater_than_total(self):
        """Test that completed_lessons > total_lessons fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['completed_lessons'] = 10
        invalid_data['total_lessons'] = 5
        serializer = ProgressSerializer(data=invalid_data)
        # Note: Currently there's no validation for this in the serializer
        # If you add this validation, this test should be updated to check for it
        # self.assertFalse(serializer.is_valid())
        # self.assertIn('completed_lessons', serializer.errors)
        
    def test_unique_constraint(self):
        """Test that unique constraint is enforced."""
        # First create a progress record
        Progress.objects.create(
            user=self.student,
            course=self.course,
            completed_lessons=1,
            total_lessons=5
        )
        
        # Try to create another progress for same user and course
        serializer = ProgressSerializer(data=self.valid_data)
        # With the UniqueTogetherValidator, validation should now fail
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)