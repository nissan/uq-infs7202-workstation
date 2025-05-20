from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from courses.models import Course, Module, Enrollment
from progress.models import Progress, ModuleProgress

User = get_user_model()

class ProgressModelTestCase(TestCase):
    """Test cases for the Progress model"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # Create a test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            password='instructorpassword',
            email='instructor@example.com'
        )
        
        # Create a test course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            instructor=self.instructor
        )
        
        # Create test modules
        self.module1 = Module.objects.create(
            course=self.course,
            title='Module 1',
            description='First Module',
            order=0,
            content_type='text',
            estimated_time_minutes=30,
            content='Module 1 Content'
        )
        
        self.module2 = Module.objects.create(
            course=self.course,
            title='Module 2',
            description='Second Module',
            order=1,
            content_type='text',
            estimated_time_minutes=45,
            content='Module 2 Content'
        )
        
        # Create an enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Create a progress record
        self.progress = Progress.objects.create(
            user=self.user,
            course=self.course
        )
        
        # Create module progress records
        self.module_progress1 = ModuleProgress.objects.create(
            progress=self.progress,
            module=self.module1,
            status='completed',
            duration_seconds=1200  # 20 minutes
        )
        
        self.module_progress2 = ModuleProgress.objects.create(
            progress=self.progress,
            module=self.module2,
            status='not_started',
            duration_seconds=0
        )
    
    def test_progress_model_creation(self):
        """Test creating a Progress instance"""
        self.assertEqual(self.progress.user, self.user)
        self.assertEqual(self.progress.course, self.course)
        self.assertEqual(self.progress.completed_lessons, 0)  # Default value
        self.assertEqual(self.progress.total_lessons, 0)  # Default value
    
    def test_progress_update_completion_percentage(self):
        """Test update_completion_percentage method"""
        # Initially progress should be 0
        self.assertEqual(self.progress.completion_percentage, 0.0)
        
        # Update completion percentage
        self.progress.update_completion_percentage()
        
        # After update, completion should be 50% (1 of 2 modules completed)
        self.assertEqual(self.progress.completed_lessons, 1)
        self.assertEqual(self.progress.total_lessons, 2)
        self.assertEqual(self.progress.completion_percentage, 50.0)
    
    def test_module_progress_mark_completed(self):
        """Test marking a module as completed"""
        # Module2 starts as not_started
        self.assertEqual(self.module_progress2.status, 'not_started')
        
        # Mark module2 as completed
        self.module_progress2.mark_completed()
        
        # Verify module2 is now completed
        self.assertEqual(self.module_progress2.status, 'completed')
        self.assertIsNotNone(self.module_progress2.completed_at)
        
        # Refresh progress from DB
        self.progress.refresh_from_db()
        
        # Progress should now be 100% (2 of 2 modules completed)
        self.assertEqual(self.progress.completed_lessons, 2)
        self.assertEqual(self.progress.total_lessons, 2)
        self.assertEqual(self.progress.completion_percentage, 100.0)
        self.assertTrue(self.progress.is_completed)


from progress.tests.test_settings import progress_test_settings

@progress_test_settings
class ProgressAPITestCase(APITestCase):
    """Test cases for the Progress API"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # Create a test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            password='instructorpassword',
            email='instructor@example.com'
        )
        
        # Set up API client with authentication
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Configure API url prefix
        self.api_prefix = '/api/progress'
        
        # Create a test course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            instructor=self.instructor
        )
        
        # Create test modules
        self.module1 = Module.objects.create(
            course=self.course,
            title='Module 1',
            description='First Module',
            order=0,
            content_type='text',
            estimated_time_minutes=30,
            content='Module 1 Content'
        )
        
        self.module2 = Module.objects.create(
            course=self.course,
            title='Module 2',
            description='Second Module',
            order=1,
            content_type='text',
            estimated_time_minutes=45,
            content='Module 2 Content'
        )
        
        # Create an enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Create a progress record
        self.progress = Progress.objects.create(
            user=self.user,
            course=self.course
        )
        
        # Create module progress records
        self.module_progress1 = ModuleProgress.objects.create(
            progress=self.progress,
            module=self.module1,
            status='completed',
            duration_seconds=1200  # 20 minutes
        )
        
        self.module_progress2 = ModuleProgress.objects.create(
            progress=self.progress,
            module=self.module2,
            status='not_started',
            duration_seconds=0
        )
        
        # Set up the client
        self.client = APIClient()
        
        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_get_progress_list(self):
        """Test getting a list of user's progress records"""
        url = f'{self.api_prefix}/progress/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should have one progress record
        self.assertEqual(response.data[0]['course'], self.course.id)
    
    def test_get_module_progress_list(self):
        """Test getting a list of user's module progress records"""
        url = f'{self.api_prefix}/module-progress/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should have two module progress records
    
    def test_mark_module_as_completed(self):
        """Test marking a module as completed"""
        url = f'{self.api_prefix}/module-progress/{self.module_progress2.id}/complete/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify module is now completed
        self.module_progress2.refresh_from_db()
        self.assertEqual(self.module_progress2.status, 'completed')
        
        # Verify course completion is updated
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.completion_percentage, 100.0)
    
    def test_add_module_time(self):
        """Test adding time spent on a module"""
        # First, manually set the progress total_duration_seconds to match existing module
        self.progress.total_duration_seconds = 1200  # Match the module_progress1 duration
        self.progress.save()
        
        url = f'{self.api_prefix}/module-progress/{self.module_progress2.id}/add_time/'
        data = {'seconds': 300}  # 5 minutes
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify module duration is updated
        self.module_progress2.refresh_from_db()
        self.assertEqual(self.module_progress2.duration_seconds, 300)
        
        # Verify course total duration is updated
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.total_duration_seconds, 1500)  # 1200 + 300
    
    def test_get_learning_statistics(self):
        """Test getting learning statistics"""
        url = f'{self.api_prefix}/progress/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['courses']['total'], 1)
        self.assertEqual(response.data['modules']['total'], 2)
        self.assertEqual(response.data['modules']['completed'], 1)
    
    def test_get_continue_learning(self):
        """Test getting continue learning information"""
        url = f'{self.api_prefix}/progress/continue_learning/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['next_module']['id'], self.module2.id)


class LearningInterfaceViewTestCase(TestCase):
    """Test cases for the learning interface views"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # Create a test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            password='instructorpassword',
            email='instructor@example.com'
        )
        
        # Create a test course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            instructor=self.instructor
        )
        
        # Create test modules
        self.module1 = Module.objects.create(
            course=self.course,
            title='Module 1',
            description='First Module',
            order=0,
            content_type='text',
            estimated_time_minutes=30,
            content='Module 1 Content'
        )
        
        self.module2 = Module.objects.create(
            course=self.course,
            title='Module 2',
            description='Second Module',
            order=1,
            content_type='text',
            estimated_time_minutes=45,
            content='Module 2 Content'
        )
        
        # Create prerequisites relationship
        self.module2.prerequisites.add(self.module1)
        
        # Create an enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Set up the client
        self.client = self.client_class()
        
        # Log in the user
        self.client.login(username='testuser', password='testpassword')
    
    def test_learning_interface_view(self):
        """Test accessing the learning interface view"""
        url = f'/progress/learning/{self.module1.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'progress/learning-interface.html')
        
        # Verify a progress record was created
        progress_exists = Progress.objects.filter(
            user=self.user,
            course=self.course
        ).exists()
        self.assertTrue(progress_exists)
        
        # Verify a module progress record was created
        module_progress_exists = ModuleProgress.objects.filter(
            module=self.module1
        ).exists()
        self.assertTrue(module_progress_exists)
    
    def test_module_prerequisites(self):
        """Test module prerequisites functionality"""
        # First, access module1 to create module progress
        url = f'/progress/learning/{self.module1.id}/'
        self.client.get(url)
        
        # Get the module progress for module1
        progress = Progress.objects.get(user=self.user, course=self.course)
        module1_progress = ModuleProgress.objects.get(
            progress=progress, 
            module=self.module1
        )
        
        # Now access module2, which requires module1 to be completed
        url = f'/progress/learning/{self.module2.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify module1 is a prerequisite for module2 and is not completed
        self.assertNotEqual(module1_progress.status, 'completed')
        
        # Get the accessibility map from context
        module_accessible_map = response.context.get('module_accessible_map')
        
        # Verify module2 is not accessible because module1 is not completed
        self.assertFalse(module_accessible_map.get(self.module2.id))
        
        # Now mark module1 as completed
        module1_progress.mark_completed()
        
        # Access module2 again
        response = self.client.get(url)
        
        # Verify module2 is now accessible
        module_accessible_map = response.context.get('module_accessible_map')
        self.assertTrue(module_accessible_map.get(self.module2.id))
    
    def test_learning_statistics_view(self):
        """Test accessing the learning statistics view"""
        url = '/progress/statistics/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'progress/learning-statistics.html')
        
        # Verify context contains stats
        self.assertIn('stats', response.context)
        self.assertIn('overall_completion', response.context)
    
    def test_unenrolled_access(self):
        """Test accessing module without being enrolled"""
        # Create another user who is not enrolled
        unenrolled_user = User.objects.create_user(
            username='unenrolled',
            password='unenrolledpass',
            email='unenrolled@example.com'
        )
        
        # Log in the unenrolled user
        self.client.logout()
        self.client.login(username='unenrolled', password='unenrolledpass')
        
        # Try to access the module
        url = f'/progress/learning/{self.module1.id}/'
        response = self.client.get(url)
        
        # Should redirect to course detail page
        self.assertEqual(response.status_code, 302)
        # Only verify that it redirects, not the exact URL
        redirect_url = response.url
        self.assertTrue(redirect_url.startswith('/courses/'))