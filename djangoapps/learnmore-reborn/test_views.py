from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from courses.models import Course, Module, Quiz, Enrollment
from test_auth_settings import test_settings_override

User = get_user_model()

@test_settings_override
class ViewTestCase(TestCase):
    """Test case for view rendering with authentication disabled"""

    def setUp(self):
        """Setup test users and data"""
        # Create a client
        self.client = Client()
        
        # Create an instructor user
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpass'
        )
        self.instructor.profile.is_instructor = True
        self.instructor.profile.save()
        
        # Create a student user
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
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
        url = reverse('course-catalog')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-catalog.html')
        
        # Only published courses should be visible
        self.assertEqual(len(response.context['courses']), 1)
        self.assertEqual(response.context['courses'][0].title, 'Published Course')
    
    def test_course_catalog_instructor(self):
        """Test course catalog view for instructor"""
        # Login as instructor
        self.client.login(username='instructor', password='instructorpass')
        
        # Request with status filters that instructors can see
        url = reverse('course-catalog') + '?status=draft&status=published'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Both courses should be visible with status filter
        self.assertEqual(len(response.context['courses']), 2)
        
        # Logout
        self.client.logout()
    
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
        self.client.login(username='student', password='studentpass')
        
        url = reverse('course-detail', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Verify student is shown as enrolled
        self.assertTrue(response.context['is_enrolled'])
        
        # Logout
        self.client.logout()
    
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
        self.client.login(username='student', password='studentpass')
        
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/module_detail.html')
        self.assertTrue(response.context['is_enrolled'])
        
        # Logout
        self.client.logout()
    
    def test_module_detail_instructor(self):
        """Test module detail view for instructor (not enrolled but has access)"""
        # Login as instructor
        self.client.login(username='instructor', password='instructorpass')
        
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/module_detail.html')
        
        # Logout
        self.client.logout()
    
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
        self.client.login(username='student', password='studentpass')
        
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/quiz_detail.html')
        
        # Logout
        self.client.logout()
    
    def test_enroll_unauthenticated(self):
        """Test enrollment redirects unauthenticated users to login"""
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_enroll_new_student(self):
        """Test successful enrollment for a new student"""
        # Create new student
        new_student = User.objects.create_user(
            username='newstudent',
            email='new@example.com',
            password='newpass'
        )
        
        # Login as new student
        self.client.login(username='newstudent', password='newpass')
        
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
        self.client.logout()
    
    def test_enroll_already_enrolled(self):
        """Test enrollment for user already enrolled shows message"""
        # Login as student (already enrolled)
        self.client.login(username='student', password='studentpass')
        
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        response = self.client.post(url, follow=True)
        
        # Should redirect to course detail
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-detail.html')
        
        # Check for message about already being enrolled
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already enrolled' in str(message) for message in messages))
        
        # Logout
        self.client.logout()
    
    def test_unenroll_enrolled_student(self):
        """Test successful unenrollment for enrolled student"""
        # Login as student (enrolled)
        self.client.login(username='student', password='studentpass')
        
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
        self.client.logout()
    
    def test_unenroll_not_enrolled(self):
        """Test unenrollment when not enrolled shows error message"""
        # Login as instructor (not enrolled)
        self.client.login(username='instructor', password='instructorpass')
        
        url = reverse('course-unenroll', kwargs={'slug': self.published_course.slug})
        response = self.client.post(url, follow=True)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('not enrolled' in str(message) for message in messages))
        
        # Logout
        self.client.logout()