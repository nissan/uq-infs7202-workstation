from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

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
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.course1 = Course.objects.create(
            title='Course 1', description='Desc 1', instructor=self.user
        )
        self.course2 = Course.objects.create(
            title='Course 2', description='Desc 2', instructor=self.user
        )

    def test_list_courses(self):
        url = '/api/courses/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        titles = {item['title'] for item in response.data}
        self.assertSetEqual(titles, {'Course 1', 'Course 2'})

    def test_retrieve_course(self):
        url = f'/api/courses/{self.course1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.course1.id)
        self.assertEqual(response.data['title'], self.course1.title)

    def test_create_course(self):
        url = '/api/courses/'
        data = {'title': 'New Course', 'description': 'New Desc', 'instructor': self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Course.objects.filter(title='New Course').exists())

    def test_update_course(self):
        url = f'/api/courses/{self.course1.id}/'
        data = {
            'title': 'Updated Title',
            'description': self.course1.description,
            'instructor': self.user.id,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.course1.refresh_from_db()
        self.assertEqual(self.course1.title, 'Updated Title')

    def test_delete_course(self):
        url = f'/api/courses/{self.course1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Course.objects.filter(id=self.course1.id).exists())
