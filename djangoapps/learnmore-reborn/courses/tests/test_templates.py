from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Quiz, Enrollment

User = get_user_model()

class CourseTemplateTests(TestCase):
    """Test case for course-related templates"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpass'
        )
        # Setup instructor profile if it exists
        if hasattr(self.instructor, 'profile'):
            self.instructor.profile.is_instructor = True
            self.instructor.profile.save()
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='A test course',
            status='published',
            enrollment_type='open',
            instructor=self.instructor
        )
        
        # Create test module
        self.module = Module.objects.create(
            title='Test Module',
            course=self.course,
            order=1
        )
        
        # Create test quiz - removed time_limit field
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            module=self.module,
            description='Test quiz description'
        )

    def test_course_catalog_renders(self):
        """Test course catalog page renders correctly"""
        # Get the response
        response = self.client.get(reverse('course-catalog'))
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check template used
        self.assertTemplateUsed(response, 'courses/course-catalog.html')
        
        # Check context
        self.assertIn('courses', response.context)
        self.assertEqual(list(response.context['courses']), [self.course])

    def test_course_detail_renders(self):
        """Test course detail page renders correctly"""
        # Get the response
        response = self.client.get(
            reverse('course-detail', kwargs={'slug': self.course.slug})
        )
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check template used
        self.assertTemplateUsed(response, 'courses/course-detail.html')
        
        # Check context
        self.assertEqual(response.context['course'], self.course)
        self.assertFalse(response.context['is_enrolled'])

    def test_module_detail_requires_login(self):
        """Test module detail page requires login"""
        # Get the response
        response = self.client.get(
            reverse('module-detail', kwargs={'pk': self.module.pk})
        )
        
        # Check redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_module_detail_requires_enrollment(self):
        """Test module detail page requires enrollment"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Get the response
        response = self.client.get(
            reverse('module-detail', kwargs={'pk': self.module.pk})
        )
        
        # Check redirect to course detail
        self.assertEqual(response.status_code, 302)
        
    def test_module_detail_renders_when_enrolled(self):
        """Test module detail page renders when enrolled"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Create enrollment
        Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Get the response
        response = self.client.get(
            reverse('module-detail', kwargs={'pk': self.module.pk})
        )
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check template used
        self.assertTemplateUsed(response, 'courses/module_detail.html')
        
        # Check context
        self.assertEqual(response.context['module'], self.module)
        self.assertTrue(response.context['is_enrolled'])

    def test_quiz_detail_requires_login(self):
        """Test quiz detail page requires login"""
        # Get the response
        response = self.client.get(
            reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        )
        
        # Check redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_enrollment_functionality(self):
        """Test enrollment and unenrollment functionality"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Test enrollment
        response = self.client.get(
            reverse('course-enroll', kwargs={'slug': self.course.slug})
        )
        
        # Check redirect to course detail
        self.assertEqual(response.status_code, 302)
        
        # Check enrollment was created
        self.assertTrue(
            Enrollment.objects.filter(
                user=self.user,
                course=self.course,
                status='active'
            ).exists()
        )
        
        # Test unenrollment
        response = self.client.get(
            reverse('course-unenroll', kwargs={'slug': self.course.slug})
        )
        
        # Check redirect to catalog
        self.assertEqual(response.status_code, 302)
        
        # Check enrollment was updated
        self.assertTrue(
            Enrollment.objects.filter(
                user=self.user,
                course=self.course,
                status='dropped'
            ).exists()
        )