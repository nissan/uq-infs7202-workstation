from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Module
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase

User = get_user_model()

class ModuleModelTest(AuthDisabledTestCase):
    """Tests for Module model CRUD operations."""
    
    def setUp(self):
        """Set up test data."""
        # Create an instructor and course for the modules
        self.instructor = User.objects.create_user(
            username='instructor1',
            email='instructor1@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test course description',
            instructor=self.instructor,
            status='published'
        )
        
        self.module_data = {
            'course': self.course,
            'title': 'Test Module',
            'description': 'Test module description',
            'order': 1
        }
    
    def test_create_module(self):
        """Test creating a new module."""
        module = Module.objects.create(**self.module_data)
        
        # Assertions for creation
        self.assertIsNotNone(module.id)
        self.assertEqual(module.course, self.course)
        self.assertEqual(module.title, self.module_data['title'])
        self.assertEqual(module.description, self.module_data['description'])
        self.assertEqual(module.order, 1)
    
    def test_read_module(self):
        """Test retrieving a module."""
        # Create the module first
        original = Module.objects.create(**self.module_data)
        
        # Retrieve by ID
        retrieved_by_id = Module.objects.get(id=original.id)
        self.assertEqual(retrieved_by_id.title, self.module_data['title'])
        
        # Retrieve by course and order
        retrieved_by_course_order = Module.objects.get(course=self.course, order=1)
        self.assertEqual(retrieved_by_course_order.id, original.id)
        
        # Test filtering by course
        course_modules = Module.objects.filter(course=self.course)
        self.assertIn(original, course_modules)
        
        # Test ordering
        Module.objects.create(
            course=self.course,
            title='Second Module',
            description='Second module description',
            order=2
        )
        ordered_modules = Module.objects.filter(course=self.course).order_by('order')
        self.assertEqual(ordered_modules[0].id, original.id)
        self.assertEqual(ordered_modules[0].order, 1)
        self.assertEqual(ordered_modules[1].order, 2)
    
    def test_update_module(self):
        """Test updating a module."""
        # Create the module first
        module = Module.objects.create(**self.module_data)
        
        # Update the module
        new_title = 'Updated Module Title'
        new_description = 'Updated module description'
        new_order = 3
        
        module.title = new_title
        module.description = new_description
        module.order = new_order
        module.save()
        
        # Refresh from database
        module.refresh_from_db()
        
        # Assertions for update
        self.assertEqual(module.title, new_title)
        self.assertEqual(module.description, new_description)
        self.assertEqual(module.order, new_order)
    
    def test_delete_module(self):
        """Test deleting a module."""
        # Create the module first
        module = Module.objects.create(**self.module_data)
        module_id = module.id
        
        # Verify created
        self.assertTrue(Module.objects.filter(id=module_id).exists())
        
        # Delete the module
        module.delete()
        
        # Verify deleted
        self.assertFalse(Module.objects.filter(id=module_id).exists())
    
    def test_multiple_modules_per_course(self):
        """Test creating multiple modules for a course."""
        # Create first module
        module1 = Module.objects.create(**self.module_data)
        
        # Create second module
        module2 = Module.objects.create(
            course=self.course,
            title='Second Module',
            description='Second module description',
            order=2
        )
        
        # Create third module
        module3 = Module.objects.create(
            course=self.course,
            title='Third Module',
            description='Third module description',
            order=3
        )
        
        # Verify all modules exist
        modules = Module.objects.filter(course=self.course).order_by('order')
        self.assertEqual(modules.count(), 3)
        self.assertEqual(modules[0].id, module1.id)
        self.assertEqual(modules[1].id, module2.id)
        self.assertEqual(modules[2].id, module3.id)
    
    def test_str_representation(self):
        """Test string representation of Module."""
        module = Module.objects.create(**self.module_data)
        expected_str = f"{self.course.title} - {self.module_data['title']}"
        self.assertEqual(str(module), expected_str)