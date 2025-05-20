from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from courses.models import Course, Module, Quiz, Enrollment
from api_test_utils import APITestCaseBase

User = get_user_model()

class DjangoViewsTestCase(APITestCaseBase):
    """Tests for Django template views with DRF authentication disabled"""
    
    def setUp(self):
        # Call parent setUp
        super().setUp()
        
        import random
        # Generate unique usernames for each test run
        unique_id = random.randint(10000, 99999)
        
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
        """Test course catalog view as anonymous user"""
        url = reverse('course-catalog')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-catalog.html')
        
        # Only published courses should be visible
        self.assertEqual(len(response.context['courses']), 1)
        self.assertEqual(response.context['courses'][0].title, 'Published Course')
    
    def test_course_catalog_instructor(self):
        """Test course catalog view as instructor with status filter"""
        # Login as instructor
        self.login_api(self.instructor)
        
        # Request with status filters that instructors can see
        url = reverse('course-catalog') + '?status=draft&status=published'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Both courses should be visible with status filter
        self.assertEqual(len(response.context['courses']), 2)
        
        # Logout
        self.client.logout()
    
    def test_course_detail_published(self):
        """Test course detail view for published course"""
        url = reverse('course-detail', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-detail.html')
        self.assertEqual(response.context['course'].title, 'Published Course')
    
    def test_course_detail_draft(self):
        """Test course detail view for draft course"""
        url = reverse('course-detail', kwargs={'slug': self.draft_course.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-detail.html')
    
    def test_course_detail_enrolled(self):
        """Test course detail view when user is enrolled"""
        # Login as student who is enrolled
        self.login_api(self.student)
        
        url = reverse('course-detail', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_enrolled'])
        
        # Logout
        self.client.logout()
    
    def test_module_detail_unauthenticated(self):
        """Test module detail view redirects unauthenticated users to login"""
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertRedirects(
            response, 
            f'/accounts/login/?next={url}',
            fetch_redirect_response=False
        )
    
    def test_module_detail_instructor(self):
        """Test module detail view for instructor"""
        # Login as instructor
        self.login_api(self.instructor)
        
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/module_detail.html')
        
        # Logout
        self.client.logout()
    
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
        self.client.logout()
    
    def test_quiz_detail_unauthenticated(self):
        """Test quiz detail view redirects unauthenticated users to login"""
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertRedirects(
            response, 
            f'/accounts/login/?next={url}',
            fetch_redirect_response=False
        )
    
    def test_quiz_detail_instructor(self):
        """Test quiz detail view for instructor"""
        # Login as instructor
        self.login_api(self.instructor)
        
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/quiz_detail.html')
        
        # Logout
        self.client.logout()
    
    def test_quiz_detail_enrolled_student(self):
        """Test quiz detail view for enrolled student"""
        # Login as student
        self.login_api(self.student)
        
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
        self.assertRedirects(
            response, 
            f'/accounts/login/?next={url}',
            fetch_redirect_response=False
        )
    
    def test_enroll_new_student(self):
        """Test successful enrollment for a new student"""
        # Create a new student with unique username
        import time
        import random
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        username = f'newstudent_{unique_id}'
        
        new_student = User.objects.create_user(
            username=username,
            email=f'new_{unique_id}@example.com',
            password='newpass'
        )
        
        # Login as new student
        self.client.login(username=username, password='newpass')
        
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url, follow=True)
        
        # Should redirect to course detail
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
        """Test enrollment when student is already enrolled"""
        # Login as student (already enrolled)
        self.login_api(self.student)
        
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url, follow=True)
        
        # Should redirect to course detail with message
        self.assertEqual(response.status_code, 200)
        
        # Check for message about already being enrolled
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already enrolled' in str(message) for message in messages))
        
        # Logout
        self.client.logout()
    
    def test_enroll_draft_course(self):
        """Test enrollment in a draft course is prevented"""
        # Login as student
        self.login_api(self.student)
        
        url = reverse('course-enroll', kwargs={'slug': self.draft_course.slug})
        response = self.client.get(url, follow=True)
        
        # Should redirect to catalog with error message
        self.assertEqual(response.status_code, 200)
        
        # Check for error message about unpublished course
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('unpublished' in str(message) for message in messages))
        
        # Verify no enrollment was created
        self.assertFalse(
            Enrollment.objects.filter(
                user=self.student,
                course=self.draft_course
            ).exists()
        )
        
        # Logout
        self.client.logout()
    
    def test_unenroll_unauthenticated(self):
        """Test unenrollment redirects unauthenticated users to login"""
        url = reverse('course-unenroll', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertRedirects(
            response, 
            f'/accounts/login/?next={url}',
            fetch_redirect_response=False
        )
    
    def test_unenroll_enrolled_student(self):
        """Test successful unenrollment for an enrolled student"""
        # Login as student (already enrolled)
        self.login_api(self.student)
        
        url = reverse('course-unenroll', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url, follow=True)
        
        # Should redirect to course catalog
        self.assertEqual(response.status_code, 200)
        
        # Verify enrollment status was updated
        enrollment = Enrollment.objects.get(
            user=self.student,
            course=self.published_course
        )
        self.assertEqual(enrollment.status, 'dropped')
        
        # Logout
        self.client.logout()
    
    def test_unenroll_not_enrolled(self):
        """Test unenrollment when student is not enrolled"""
        # Login as instructor (not enrolled)
        self.login_api(self.instructor)
        
        url = reverse('course-unenroll', kwargs={'slug': self.published_course.slug})
        response = self.client.get(url, follow=True)
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 200)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('not enrolled' in str(message) for message in messages))
        
        # Logout
        self.client.logout()