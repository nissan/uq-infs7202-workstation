from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Course
from .serializers import CourseSerializer

User = get_user_model()

class CourseSerializerTest(TestCase):
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


class CourseAPITest(APITestCase):
    def setUp(self):
        # Create a test user with instructor profile
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.user.profile.is_instructor = True
        self.user.profile.save()

        # Create test courses
        self.course1 = Course.objects.create(
            title='Course 1', description='Desc 1', instructor=self.user
        )
        self.course2 = Course.objects.create(
            title='Course 2', description='Desc 2', instructor=self.user
        )

        # Login and get token
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

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
