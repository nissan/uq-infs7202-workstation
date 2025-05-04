from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.courses.models import Course, Module, Content, Enrollment
import json

User = get_user_model()


class NavigationIntegrationTestCase(TestCase):
    """Test case for navigation integration across the site."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.client = Client()
        
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword123'
        )
        
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpassword123'
        )
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@example.com',
            password='coordinatorpassword123'
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpassword123'
        )
        
        # Create groups
        self.instructor_group = Group.objects.create(name='Instructor')
        self.coordinator_group = Group.objects.create(name='Course Coordinator')
        
        # Add users to groups
        self.instructor.groups.add(self.instructor_group)
        self.coordinator.groups.add(self.coordinator_group)
    
    def test_admin_navigation(self):
        """Test admin user sees the correct navigation."""
        self.client.login(username='admin', password='adminpassword123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('courses:admin_dashboard'))
        self.assertContains(response, reverse('dashboard:home'))
    
    def test_instructor_navigation(self):
        """Test instructor user sees the correct navigation."""
        self.client.login(username='instructor', password='instructorpassword123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('courses:instructor_dashboard'))
        self.assertNotContains(response, reverse('courses:admin_dashboard'))
    
    def test_coordinator_navigation(self):
        """Test coordinator user sees the correct navigation."""
        self.client.login(username='coordinator', password='coordinatorpassword123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('courses:coordinator_dashboard'))
        self.assertNotContains(response, reverse('courses:admin_dashboard'))
    
    def test_student_navigation(self):
        """Test student user sees the correct navigation."""
        self.client.login(username='student', password='studentpassword123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('courses:student_dashboard'))
        self.assertNotContains(response, reverse('courses:admin_dashboard'))


class AtomicTemplateIntegrationTestCase(TestCase):
    """Test case for atomic template integration across the site."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.client = Client()
    
    def test_home_template_integration(self):
        """Test the home template integrates with other site components."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check base template elements are included
        self.assertContains(response, 'LearnMore Plus')  # Site title
        self.assertContains(response, 'Log In')          # Login link
        self.assertContains(response, 'Sign Up')         # Signup link
        
        # Check specific atomic sections exist
        self.assertContains(response, 'Choose Your Path')
        self.assertContains(response, 'Powerful Features')
        self.assertContains(response, 'How It Works')
        self.assertContains(response, 'What Our Users Say')
    
    def test_about_template_integration(self):
        """Test the about template integrates with other site components."""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        
        # Check base template elements are included
        self.assertContains(response, 'LearnMore Plus')  # Site title
        self.assertContains(response, 'Log In')          # Login link
        self.assertContains(response, 'Sign Up')         # Signup link
        
        # Check specific atomic sections exist
        self.assertContains(response, 'Our Story')
        self.assertContains(response, 'Our Values')
        self.assertContains(response, 'Our Team')
        self.assertContains(response, 'What People Say About Us')