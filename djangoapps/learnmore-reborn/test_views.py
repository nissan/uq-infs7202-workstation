from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
import random
import time

from courses.models import Course, Module, Quiz, Enrollment
from courses.views import CourseCatalogView, CourseDetailView, ModuleDetailView, QuizDetailView, enroll_course, unenroll_course

User = get_user_model()

class ViewTestCase(TestCase):
    """Test case for view rendering with authentication disabled"""

    def setUp(self):
        """Setup test users and data"""
        # Call parent setUp to initialize the client and users
        super().setUp()
        
        # Generate unique usernames for each test run
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create an instructor user
        self.instructor = User.objects.create_user(
            username=f'instructor_{unique_id}',
            email=f'instructor_{unique_id}@example.com',
            password='instructorpass'
        )
        self.instructor.profile.is_instructor = True
        self.instructor.profile.save()
        
        # Create a student user
        self.student = User.objects.create_user(
            username=f'student_{unique_id}',
            email=f'student_{unique_id}@example.com',
            password='studentpass'
        )
        
        # Create courses
        self.published_course = Course.objects.create(
            title='Published Course',
            slug='published-course',
            description='Description for published course',
            instructor=self.instructor,
            status='published',
            enrollment_type='open',
            max_students=10
        )
        
        self.draft_course = Course.objects.create(
            title='Draft Course',
            slug='draft-course',
            description='Description for draft course',
            instructor=self.instructor,
            status='draft',
            enrollment_type='open',
            max_students=10
        )
        
        # Create modules
        self.module = Module.objects.create(
            course=self.published_course,
            title='Test Module',
            description='Module description',
            order=1
        )
        
        # Create quiz
        self.quiz = Quiz.objects.create(
            module=self.module,
            title='Test Quiz',
            description='Quiz description',
            is_survey=False
        )
        
        # Create enrollment for student
        self.enrollment = Enrollment.objects.create(
            user=self.student,
            course=self.published_course,
            status='active'
        )
    
    def test_course_catalog_anonymous(self):
        """Test course catalog view for anonymous user"""
        # Create a direct request to the view
        factory = RequestFactory()
        request = factory.get(reverse('course-catalog'))
        
        # For anonymous user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        # Get the response directly from the view
        response = CourseCatalogView.as_view()(request)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Since we're using the RequestFactory, we need to attach the response
        # to a test client response for template assertion
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Check template 
        self.assertIn('courses', response.context_data)
        
        # Only published courses should be visible
        self.assertEqual(len(response.context_data['courses']), 1)
        self.assertEqual(response.context_data['courses'][0].title, 'Published Course')
    
    def test_course_catalog_instructor(self):
        """Test course catalog view for instructor"""
        # Login as instructor
        self.login_api(self.instructor)
        
        # Request with status filters that instructors can see
        url = reverse('course-catalog') + '?status=draft&status=published'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Both courses should be visible with status filter
        self.assertEqual(len(response.context['courses']), 2)
        
        # Logout
        self.logout()
    
    def test_course_detail_view(self):
        """Test course detail view"""
        url = reverse('course-detail', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-detail.html')
        self.assertEqual(response.context['course'].title, 'Published Course')
        
        # Check is_enrolled is False for anonymous
        self.assertFalse(response.context['is_enrolled'])
    
    def test_course_detail_enrolled(self):
        """Test course detail view when student is enrolled"""
        # Login as student
        self.login_api(self.student)
        
        url = reverse('course-detail', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Verify student is shown as enrolled
        self.assertTrue(response.context['is_enrolled'])
        
        # Logout
        self.logout()
    
    def test_module_detail_unauthenticated(self):
        """Test module detail view redirects unauthenticated users to login"""
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_module_detail_enrolled_student(self):
        """Test module detail view for enrolled student"""
        # Login as student
        self.login_api(self.student)
        
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/module_detail.html')
        self.assertTrue(response.context['is_enrolled'])
        
        # Logout
        self.logout()
    
    def test_module_detail_instructor(self):
        """Test module detail view for instructor (not enrolled but has access)"""
        # Login as instructor
        self.login_api(self.instructor)
        
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/module_detail.html')
        
        # Logout
        self.logout()
    
    def test_quiz_detail_unauthenticated(self):
        """Test quiz detail view redirects unauthenticated users to login"""
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_quiz_detail_enrolled_student(self):
        """Test quiz detail view for enrolled student"""
        # Login as student
        self.login_api(self.student)
        
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/quiz_detail.html')
        
        # Logout
        self.logout()
    
    def test_enroll_unauthenticated(self):
        """Test enrollment redirects unauthenticated users to login"""
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_enroll_new_student(self):
        """Test successful enrollment for a new student"""
        # Create new student with unique username
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        new_student = User.objects.create_user(
            username=f'newstudent_{unique_id}',
            email=f'new_{unique_id}@example.com',
            password='newpass'
        )
        
        # Login as new student
        # Use force_authenticate directly since this user isn't set up in the base class
        self.client.force_authenticate(user=new_student)
        
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        response = self.client.post(url, follow=True)
        
        # Check final response status code (after following redirects)
        self.assertEqual(response.status_code, 200)
        
        # Verify enrollment was created
        self.assertTrue(
            Enrollment.objects.filter(
                user=new_student,
                course=self.published_course,
                status='active'
            ).exists()
        )
        
        # Logout
        self.logout()
    
    def test_enroll_already_enrolled(self):
        """Test enrollment for user already enrolled shows message"""
        # Login as student (already enrolled)
        self.login_api(self.student)
        
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        response = self.client.post(url, follow=True)
        
        # Should redirect to course detail
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-detail.html')
        
        # Check for message about already being enrolled
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already enrolled' in str(message) for message in messages))
        
        # Logout
        self.logout()
    
    def test_unenroll_enrolled_student(self):
        """Test successful unenrollment for enrolled student"""
        # Login as student (enrolled)
        self.login_api(self.student)
        
        url = reverse('course-unenroll', kwargs={'slug': self.published_course.slug})
        response = self.client.post(url, follow=True)
        
        # Should redirect to course catalog
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-catalog.html')
        
        # Verify enrollment status is updated
        enrollment = Enrollment.objects.get(
            user=self.student,
            course=self.published_course
        )
        self.assertEqual(enrollment.status, 'dropped')
        
        # Logout
        self.logout()
    
    def test_unenroll_not_enrolled(self):
        """Test unenrollment when not enrolled shows error message"""
        # Login as instructor (not enrolled)
        self.login_api(self.instructor)
        
        url = reverse('course-unenroll', kwargs={'slug': self.published_course.slug})
        response = self.client.post(url, follow=True)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('not enrolled' in str(message) for message in messages))
        
        # Logout
        self.logout()