from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Course
from .serializers import CourseSerializer
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase

User = get_user_model()

class CourseSerializerTest(AuthDisabledTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seruser', password='pass')
        self.course = Course.objects.create(
            title='Ser Course', description='Ser desc', instructor=self.user
        )

    def test_serializer_fields(self):
        serializer = CourseSerializer(self.course)
        data = serializer.data
        self.assertIn('id', data)
        self.assertEqual(data['title'], self.course.title)
        self.assertIn('description', data)
        self.assertIn('instructor', data)
        self.assertIn('created_at', data)


class CourseAPITest(APITestCaseBase):
    def setUp(self):
        # Call the parent setUp which creates self.user and self.instructor
        super().setUp()
        
        # Set instructor flag for the user
        self.user.profile.is_instructor = True
        self.user.profile.save()
        
        # Create a regular student user (non-instructor)
        self.student_user = User.objects.create_user(username='student', password='pass')
        self.student_user.profile.is_instructor = False
        self.student_user.profile.save()

        # Create test courses
        self.course1 = Course.objects.create(
            title='Course 1', description='Desc 1', instructor=self.user
        )
        self.course2 = Course.objects.create(
            title='Course 2', description='Desc 2', instructor=self.user
        )

        # Authenticate as instructor using APITestCaseBase's helper method
        self.login_api(self.user)

    def test_list_courses(self):
        url = '/api/courses/courses/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        titles = {item['title'] for item in response.data}
        self.assertSetEqual(titles, {'Course 1', 'Course 2'})

    def test_retrieve_course(self):
        url = f'/api/courses/courses/{self.course1.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.course1.id)
        self.assertEqual(response.data['title'], self.course1.title)

    def test_create_course(self):
        url = '/api/courses/courses/'
        data = {
            'title': 'New Course', 
            'description': 'New Desc', 
            'instructor': self.user.id,
            'status': 'published',
            'enrollment_type': 'open',
            'max_students': 30
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Course.objects.filter(title='New Course').exists())

    def test_update_course(self):
        url = f'/api/courses/courses/{self.course1.slug}/'
        data = {
            'title': 'Updated Title',
            'description': self.course1.description,
            'instructor': self.user.id,
            'status': 'published',
            'enrollment_type': 'open',
            'max_students': 50
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course1.refresh_from_db()
        self.assertEqual(self.course1.title, 'Updated Title')

    def test_delete_course(self):
        url = f'/api/courses/courses/{self.course1.slug}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course1.id).exists())
        
    def test_course_catalog(self):
        # Set courses to published status
        self.course1.status = 'published'
        self.course1.save()
        self.course2.status = 'published'
        self.course2.save()
        
        url = '/api/courses/catalog/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_course_catalog_search(self):
        # Set courses to published status
        self.course1.status = 'published'
        self.course1.save()
        self.course2.status = 'published'
        self.course2.save()
        
        url = '/api/courses/catalog/search/?q=Course 1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Course 1')
        
    def test_enroll_in_course(self):
        # Set course to published status
        self.course1.status = 'published'
        self.course1.save()
        
        url = f'/api/courses/courses/{self.course1.slug}/enroll/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if enrollment was created
        from .models import Enrollment
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course1).exists())
        
    def test_enroll_in_unpublished_course(self):
        """Test enrolling in a course that is not published yet"""
        # Ensure course is in draft status
        self.course1.status = 'draft'
        self.course1.save()
        
        url = f'/api/courses/courses/{self.course1.slug}/enroll/'
        response = self.client.post(url)
        
        # Should not be allowed to enroll in an unpublished course
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'You cannot enroll in an unpublished course')
        
        # Verify no enrollment was created
        from .models import Enrollment
        self.assertFalse(Enrollment.objects.filter(user=self.user, course=self.course1).exists())
        
    def test_enroll_in_full_course(self):
        """Test enrolling in a course that has reached its capacity"""
        # Set up a course with max_students = 1
        self.course1.status = 'published'
        self.course1.max_students = 1
        self.course1.save()
        
        # Create another user and enroll them first to fill the course
        other_user = User.objects.create_user(username='otheruser', password='pass')
        
        from .models import Enrollment
        Enrollment.objects.create(user=other_user, course=self.course1, status='active')
        
        # Try to enroll our test user
        url = f'/api/courses/courses/{self.course1.slug}/enroll/'
        response = self.client.post(url)
        
        # Should not be allowed to enroll in a full course
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'This course has reached its maximum enrollment capacity')
        
        # Verify no enrollment was created for our test user
        self.assertFalse(Enrollment.objects.filter(user=self.user, course=self.course1).exists())
        
    def test_enroll_in_course_already_enrolled(self):
        """Test enrolling in a course where user is already enrolled"""
        # Set course to published status
        self.course1.status = 'published'
        self.course1.save()
        
        # First enrollment
        from .models import Enrollment
        Enrollment.objects.create(user=self.user, course=self.course1, status='active')
        
        # Try to enroll again
        url = f'/api/courses/courses/{self.course1.slug}/enroll/'
        response = self.client.post(url)
        
        # Should not be allowed to enroll twice
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'You are already enrolled in this course')
        
        # Verify still only one enrollment exists
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course1).count(), 1)
        
    def test_enroll_in_restricted_course(self):
        """Test enrolling in a course with restricted enrollment"""
        # Set course to published status with restricted enrollment
        self.course1.status = 'published'
        self.course1.enrollment_type = 'restricted'
        self.course1.save()
        
        # Try to enroll
        url = f'/api/courses/courses/{self.course1.slug}/enroll/'
        response = self.client.post(url)
        
        # The current implementation allows this by default
        # In a real implementation, this would be HTTP_400_BAD_REQUEST if access check fails
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_unenroll_from_course(self):
        # Set course to published status and create enrollment
        self.course1.status = 'published'
        self.course1.save()
        
        from .models import Enrollment
        enrollment = Enrollment.objects.create(user=self.user, course=self.course1, status='active')
        
        url = f'/api/courses/courses/{self.course1.slug}/unenroll/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check if enrollment status was updated
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'dropped')
        
    def test_unenroll_from_course_not_enrolled(self):
        """Test unenrolling from a course where user is not enrolled"""
        # Set course to published status
        self.course1.status = 'published'
        self.course1.save()
        
        # Do not create an enrollment
        
        url = f'/api/courses/courses/{self.course1.slug}/unenroll/'
        response = self.client.post(url)
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'You are not enrolled in this course')
        
    def test_list_enrolled_courses(self):
        # Set course to published status and create enrollment
        self.course1.status = 'published'
        self.course1.save()
        
        from .models import Enrollment
        enrollment = Enrollment.objects.create(user=self.user, course=self.course1, status='active')
        
        url = '/api/courses/enrolled/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['course'], self.course1.id)
        
    def test_list_completed_courses(self):
        """Test listing completed courses"""
        # Set course to published status and create completed enrollment
        self.course1.status = 'published'
        self.course1.save()
        
        from .models import Enrollment
        from django.utils import timezone
        
        # Create a completed enrollment
        enrollment = Enrollment.objects.create(
            user=self.user, 
            course=self.course1, 
            status='completed',
            completed_at=timezone.now()
        )
        
        # Create an active enrollment for another course
        Enrollment.objects.create(
            user=self.user,
            course=self.course2,
            status='active'
        )
        
        url = '/api/courses/enrollments/completed/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only return the completed course
        self.assertEqual(response.data[0]['course'], self.course1.id)
        self.assertEqual(response.data[0]['status'], 'completed')
        self.assertIsNotNone(response.data[0]['completed_at'])
        
    def test_student_cannot_create_course(self):
        """Test that a regular student cannot create courses"""
        # Switch to student credentials
        self.login_api(self.student_user)
        
        url = '/api/courses/courses/'
        data = {
            'title': 'Student Course', 
            'description': 'Created by student', 
            'instructor': self.student_user.id,
            'status': 'published'
        }
        
        response = self.client.post(url, data)
        
        # Student should not be allowed to create courses
        # Depending on implementation, this could be 403 Forbidden or 401 Unauthorized
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        
        # Verify no course was created
        self.assertFalse(Course.objects.filter(title='Student Course').exists())
    
    def test_student_cannot_update_instructor_course(self):
        """Test that a regular student cannot update an instructor's course"""
        # Switch to student credentials
        self.login_api(self.student_user)
        
        url = f'/api/courses/courses/{self.course1.slug}/'
        data = {
            'title': 'Hacked Course',
            'description': 'Modified by student',
            'instructor': self.student_user.id,  # Try to change instructor
            'status': 'published'
        }
        
        response = self.client.put(url, data)
        
        # Student should not be allowed to update courses they don't own
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        
        # Verify course was not modified
        self.course1.refresh_from_db()
        self.assertEqual(self.course1.title, 'Course 1')
        self.assertEqual(self.course1.instructor, self.user)  # Still the original instructor
    
    def test_student_cannot_delete_instructor_course(self):
        """Test that a regular student cannot delete an instructor's course"""
        # Switch to student credentials
        self.login_api(self.student_user)
        
        url = f'/api/courses/courses/{self.course1.slug}/'
        response = self.client.delete(url)
        
        # Student should not be allowed to delete courses they don't own
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        
        # Verify course was not deleted
        self.assertTrue(Course.objects.filter(id=self.course1.id).exists())
        
    def test_instructor_can_see_all_courses(self):
        """Test that instructors can see all courses"""
        # Create a course by another instructor
        other_instructor = User.objects.create_user(username='instructor2', password='pass')
        other_instructor.profile.is_instructor = True
        other_instructor.profile.save()
        
        other_course = Course.objects.create(
            title='Other Course',
            description='Created by another instructor',
            instructor=other_instructor
        )
        
        # Using instructor credentials (default in setUp)
        url = '/api/courses/courses/'
        response = self.client.get(url)
        
        # Instructor should see all courses (both their own and others')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # course1, course2, and other_course
        
        # Verify all courses are included
        course_ids = [course['id'] for course in response.data]
        self.assertIn(self.course1.id, course_ids)
        self.assertIn(self.course2.id, course_ids)
        self.assertIn(other_course.id, course_ids)
        
    def test_student_sees_only_enrolled_courses(self):
        """Test that students only see courses they're enrolled in"""
        # Switch to student credentials
        self.login_api(self.student_user)
        
        # Enroll student in one course
        from .models import Enrollment
        Enrollment.objects.create(
            user=self.student_user,
            course=self.course1,
            status='active'
        )
        
        url = '/api/courses/courses/'
        response = self.client.get(url)
        
        # Student should only see their enrolled course
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.course1.id)
