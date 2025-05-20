from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .test_utils import get_authenticated_client, force_authenticate_client
from courses.models import Course, Module, Enrollment
from .models import Progress, ModuleProgress

User = get_user_model()

class ProgressIntegrationTestCase(TestCase):
    """Integration tests for progress tracking functionality"""
    
    def setUp(self):
        # Create test user
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
        self.modules = []
        for i in range(3):
            module = Module.objects.create(
                course=self.course,
                title=f'Module {i+1}',
                description=f'Module {i+1} Description',
                order=i,
                content_type='text',
                estimated_time_minutes=30 * (i+1),
                content=f'Content for Module {i+1}'
            )
            self.modules.append(module)
        
        # Create prerequisites
        self.modules[1].prerequisites.add(self.modules[0])
        self.modules[2].prerequisites.add(self.modules[1])
        
        # Create an enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Set up an authenticated client
        self.api_client, _ = get_authenticated_client(self.user)
        
        # Set up a session client
        self.client = self.client_class()
        self.client.login(username='testuser', password='testpassword')
    
    def test_complete_module_flow(self):
        """
        Test the complete flow of using the learning interface and tracking progress:
        1. Access the first module to start learning
        2. Mark it as completed via API
        3. Access the second module (which required the first as a prerequisite)
        4. View learning statistics
        """
        # 1. Access the first module to start learning
        module_url = f'/progress/learning/{self.modules[0].id}/'
        response = self.client.get(module_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify module progress was created
        progress = Progress.objects.get(user=self.user, course=self.course)
        module_progress = ModuleProgress.objects.get(
            progress=progress, 
            module=self.modules[0]
        )
        self.assertEqual(module_progress.status, 'in_progress')
        
        # 2. Mark it as completed via API
        complete_url = f'/api/progress/module-progress/{module_progress.id}/complete/'
        response = self.api_client.post(complete_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify module is marked as completed
        module_progress.refresh_from_db()
        self.assertEqual(module_progress.status, 'completed')
        
        # Verify progress is updated
        progress.refresh_from_db()
        self.assertEqual(progress.completed_lessons, 1)
        self.assertEqual(progress.completion_percentage, 33.33)  # 1/3 * 100
        
        # 3. Access the second module
        module_url = f'/progress/learning/{self.modules[1].id}/'
        response = self.client.get(module_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify the second module is now accessible
        context = response.context
        self.assertTrue(context['module_accessible_map'][self.modules[1].id])
        
        # Get module progress for second module
        module_progress = ModuleProgress.objects.get(
            progress=progress, 
            module=self.modules[1]
        )
        
        # Add some time spent on the module
        time_url = f'/api/progress/module-progress/{module_progress.id}/add_time/'
        response = self.api_client.post(time_url, {'seconds': 600})  # 10 minutes
        self.assertEqual(response.status_code, 200)
        
        # Verify time is tracked
        module_progress.refresh_from_db()
        self.assertEqual(module_progress.duration_seconds, 600)
        
        # 4. View learning statistics
        stats_url = '/progress/statistics/'
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify stats contain correct information
        self.assertIn('stats', response.context)
        stats = response.context['stats']
        self.assertEqual(stats['modules']['completed'], 1)
        self.assertEqual(stats['modules']['total'], 3)
        
        # 5. Try API for continue learning
        continue_url = '/api/progress/progress/continue_learning/'
        response = self.api_client.get(continue_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify next module is module 2
        self.assertEqual(response.data['next_module']['id'], self.modules[1].id)
    
    def test_course_progress_access_control(self):
        """Test that users can only see their own progress"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpassword',
            email='other@example.com'
        )
        
        # Enroll other user in the course
        Enrollment.objects.create(
            user=other_user,
            course=self.course,
            status='active'
        )
        
        # Access first module to create progress for both users
        self.client.get(f'/progress/learning/{self.modules[0].id}/')
        
        # Log in as other user
        other_client = self.client_class()
        other_client.login(username='otheruser', password='otherpassword')
        other_client.get(f'/progress/learning/{self.modules[0].id}/')
        
        # Get API client for other user
        other_api, _ = get_authenticated_client(other_user)
        
        # First user marks module as completed
        progress = Progress.objects.get(user=self.user, course=self.course)
        module_progress = ModuleProgress.objects.get(
            progress=progress,
            module=self.modules[0]
        )
        complete_url = f'/api/progress/module-progress/{module_progress.id}/complete/'
        self.api_client.post(complete_url)
        
        # Other user should not be able to access first user's module progress
        response = other_api.get(f'/api/progress/module-progress/{module_progress.id}/')
        self.assertEqual(response.status_code, 404)
        
        # Other user should only see their own progress
        response = other_api.get('/api/progress/progress/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        
        # First user's progress should show completion
        response = self.api_client.get('/api/progress/progress/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['completed_lessons'], 1)
        
        # Other user's progress should not show completion
        progress = Progress.objects.get(user=other_user, course=self.course)
        self.assertEqual(progress.completed_lessons, 0)