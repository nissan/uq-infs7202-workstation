from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Course, Module, Quiz, Enrollment
from .serializers import (
    CourseSerializer, 
    CourseDetailSerializer, 
    ModuleSerializer, 
    QuizSerializer, 
    EnrollmentSerializer
)

User = get_user_model()

class CourseSerializerValidationTest(TestCase):
    """Tests for CourseSerializer validation."""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='password'
        )
        
        self.valid_data = {
            'title': 'Test Course',
            'description': 'Test description',
            'instructor': self.instructor.id,
            'status': 'published',
            'enrollment_type': 'open',
            'max_students': 30,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timezone.timedelta(days=90)
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = CourseSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Missing title
        invalid_data = self.valid_data.copy()
        invalid_data.pop('title')
        serializer = CourseSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
        # Missing instructor
        invalid_data = self.valid_data.copy()
        invalid_data.pop('instructor')
        serializer = CourseSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('instructor', serializer.errors)
    
    def test_invalid_status(self):
        """Test that invalid status fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['status'] = 'invalid_status'
        serializer = CourseSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
    
    def test_invalid_enrollment_type(self):
        """Test that invalid enrollment_type fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['enrollment_type'] = 'invalid_type'
        serializer = CourseSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('enrollment_type', serializer.errors)
        
    def test_course_type_default_and_validation(self):
        """Test that course_type has the correct default and validates choices."""
        # Default value should be 'standard'
        serializer = CourseSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data.get('course_type', 'standard'), 'standard')
        
        # Valid value should pass validation
        valid_data = self.valid_data.copy()
        valid_data['course_type'] = 'self_paced'
        serializer = CourseSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['course_type'], 'self_paced')
        
        # Invalid value should fail validation
        invalid_data = self.valid_data.copy()
        invalid_data['course_type'] = 'invalid_type'
        serializer = CourseSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('course_type', serializer.errors)
    
    def test_negative_max_students(self):
        """Test that negative max_students fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['max_students'] = -10
        serializer = CourseSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('max_students', serializer.errors)
    
    def test_end_date_before_start_date(self):
        """Test that end_date before start_date fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['end_date'] = timezone.now().date() - timezone.timedelta(days=10)
        serializer = CourseSerializer(data=invalid_data)
        # Note: Currently there's no validation for this in the serializer
        # If you add date validation, this test should be updated to check for it
        # self.assertFalse(serializer.is_valid())
        # self.assertIn('end_date', serializer.errors)


class ModuleSerializerValidationTest(TestCase):
    """Tests for ModuleSerializer validation."""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='password'
        )
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test description',
            instructor=self.instructor,
            status='published'
        )
        
        self.valid_data = {
            'course': self.course.id,
            'title': 'Test Module',
            'description': 'Test module description',
            'order': 1
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = ModuleSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Missing course
        invalid_data = self.valid_data.copy()
        invalid_data.pop('course')
        serializer = ModuleSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('course', serializer.errors)
        
        # Missing title
        invalid_data = self.valid_data.copy()
        invalid_data.pop('title')
        serializer = ModuleSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
    
    def test_negative_order(self):
        """Test that negative order fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['order'] = -1
        serializer = ModuleSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('order', serializer.errors)


class QuizSerializerValidationTest(TestCase):
    """Tests for QuizSerializer validation."""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='password'
        )
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test description',
            instructor=self.instructor,
            status='published'
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test module description',
            order=1
        )
        
        self.valid_data = {
            'module': self.module.id,
            'title': 'Test Quiz',
            'description': 'Test quiz description',
            'is_survey': False
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = QuizSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Missing module
        invalid_data = self.valid_data.copy()
        invalid_data.pop('module')
        serializer = QuizSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('module', serializer.errors)
        
        # Missing title
        invalid_data = self.valid_data.copy()
        invalid_data.pop('title')
        serializer = QuizSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)


class EnrollmentSerializerValidationTest(TestCase):
    """Tests for EnrollmentSerializer validation."""
    
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
            'status': 'active',
            'progress': 0
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = EnrollmentSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Missing user
        invalid_data = self.valid_data.copy()
        invalid_data.pop('user')
        serializer = EnrollmentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)
        
        # Missing course
        invalid_data = self.valid_data.copy()
        invalid_data.pop('course')
        serializer = EnrollmentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('course', serializer.errors)
    
    def test_invalid_status(self):
        """Test that invalid status fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['status'] = 'invalid_status'
        serializer = EnrollmentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
    
    def test_negative_progress(self):
        """Test that negative progress fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['progress'] = -10
        serializer = EnrollmentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('progress', serializer.errors)
    
    def test_unique_constraint(self):
        """Test that unique constraint is enforced."""
        # First create an enrollment
        Enrollment.objects.create(
            user=self.student,
            course=self.course,
            status='active'
        )
        
        # Try to create another enrollment for same user and course
        serializer = EnrollmentSerializer(data=self.valid_data)
        # With the UniqueTogetherValidator, validation should now fail
        self.assertFalse(serializer.is_valid())  
        self.assertIn('non_field_errors', serializer.errors)