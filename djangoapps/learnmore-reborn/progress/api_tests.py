from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from courses.models import Course
from .models import Progress
from .serializers import ProgressSerializer

User = get_user_model()


class ProgressSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='proguser', password='pass')
        self.course = Course.objects.create(
            title='Prog Course', description='Prog desc', instructor=self.user
        )
        self.progress = Progress.objects.create(
            user=self.user,
            course=self.course,
            completed_lessons=1,
            total_lessons=5,
        )

    def test_serializer_fields(self):
        serializer = ProgressSerializer(self.progress)
        data = serializer.data
        self.assertIn('id', data)
        self.assertEqual(data['completed_lessons'], self.progress.completed_lessons)
        self.assertIn('user', data)
        self.assertIn('course', data)
        self.assertIn('last_accessed', data)


class ProgressAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='proguser2', password='pass')
        self.user.profile.is_instructor = True
        self.user.profile.save()

        # Create test courses
        self.course1 = Course.objects.create(
            title='Prog Course1', description='Prog1', instructor=self.user
        )
        self.course2 = Course.objects.create(
            title='Prog Course2', description='Prog2', instructor=self.user
        )

        # Create test progress records
        self.progress1 = Progress.objects.create(
            user=self.user, course=self.course1, completed_lessons=2, total_lessons=5
        )
        self.progress2 = Progress.objects.create(
            user=self.user, course=self.course2, completed_lessons=3, total_lessons=5
        )

        # Login and get token
        response = self.client.post('/api/users/login/', {
            'username': 'proguser2',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_list_progress(self):
        url = '/api/progress/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_progress(self):
        url = f'/api/progress/{self.progress1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.progress1.id)

    def test_create_progress(self):
        url = '/api/progress/'
        data = {
            'user': self.user.id,
            'course': self.course1.id,  # Using course1 since it already has a progress record
            'completed_lessons': 0,
            'total_lessons': 10,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Should fail due to unique constraint
        self.assertFalse(
            Progress.objects.filter(
                user=self.user, course=self.course1, completed_lessons=0
            ).exists()
        )

    def test_update_progress(self):
        url = f'/api/progress/{self.progress1.id}/'
        data = {
            'user': self.user.id,
            'course': self.course1.id,
            'completed_lessons': 4,
            'total_lessons': 5,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.progress1.refresh_from_db()
        self.assertEqual(self.progress1.completed_lessons, 4)

    def test_delete_progress(self):
        url = f'/api/progress/{self.progress1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Progress.objects.filter(id=self.progress1.id).exists())