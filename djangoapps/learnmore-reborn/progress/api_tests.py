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
        # Create instructor user
        self.instructor = User.objects.create_user(username='instructor', password='pass')
        self.instructor.profile.is_instructor = True
        self.instructor.profile.save()
        
        # Create student user
        self.student = User.objects.create_user(username='student', password='pass')
        self.student.profile.is_instructor = False
        self.student.profile.save()
        
        # Create another student user
        self.other_student = User.objects.create_user(username='otherstudent', password='pass')
        self.other_student.profile.is_instructor = False
        self.other_student.profile.save()

        # Create test courses
        self.course1 = Course.objects.create(
            title='Course1', description='Desc1', instructor=self.instructor,
            status='published'
        )
        self.course2 = Course.objects.create(
            title='Course2', description='Desc2', instructor=self.instructor,
            status='published'
        )

        # Create test progress records for the instructor
        self.instructor_progress1 = Progress.objects.create(
            user=self.instructor, course=self.course1, completed_lessons=2, total_lessons=5
        )
        self.instructor_progress2 = Progress.objects.create(
            user=self.instructor, course=self.course2, completed_lessons=3, total_lessons=5
        )
        
        # Create test progress records for the student
        self.student_progress = Progress.objects.create(
            user=self.student, course=self.course1, completed_lessons=1, total_lessons=5
        )
        
        # Create test progress records for the other student
        self.other_student_progress = Progress.objects.create(
            user=self.other_student, course=self.course2, completed_lessons=4, total_lessons=5
        )

        # Login as instructor and get token
        response = self.client.post('/api/users/login/', {
            'username': 'instructor',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.instructor_token = response.data['access']
        
        # Login as student and get token
        response = self.client.post('/api/users/login/', {
            'username': 'student',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_token = response.data['access']
        
        # Login as other student and get token
        response = self.client.post('/api/users/login/', {
            'username': 'otherstudent',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.other_student_token = response.data['access']
        
        # Default to instructor credentials
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')

    def test_instructor_list_own_progress(self):
        """Test instructor listing their own progress"""
        url = '/api/progress/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see both their progress records
        
        # Verify correct progress records are returned
        progress_ids = [prog['id'] for prog in response.data]
        self.assertIn(self.instructor_progress1.id, progress_ids)
        self.assertIn(self.instructor_progress2.id, progress_ids)

    def test_student_list_own_progress(self):
        """Test student listing their own progress"""
        # Switch to student credentials
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        url = '/api/progress/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see their own progress
        self.assertEqual(response.data[0]['id'], self.student_progress.id)
        
    def test_student_cannot_see_other_student_progress(self):
        """Test student cannot see another student's progress"""
        # Switch to student credentials
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        url = f'/api/progress/{self.other_student_progress.id}/'
        response = self.client.get(url)
        
        # Should not be able to access another student's progress
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_retrieve_own_progress(self):
        """Test retrieving your own progress"""
        url = f'/api/progress/{self.instructor_progress1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.instructor_progress1.id)

    def test_create_progress_duplicate_check(self):
        """Test creating a duplicate progress (should fail)"""
        url = '/api/progress/'
        data = {
            'user': self.instructor.id,
            'course': self.course1.id,  # Course that already has a progress record
            'completed_lessons': 0,
            'total_lessons': 10,
        }
        response = self.client.post(url, data)
        
        # Should fail due to unique constraint
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no new progress was created
        self.assertFalse(
            Progress.objects.filter(
                user=self.instructor, 
                course=self.course1, 
                completed_lessons=0
            ).exists()
        )
        
    def test_create_progress_for_new_course(self):
        """Test creating a new progress record for a course"""
        # Create a new course
        new_course = Course.objects.create(
            title='New Course', 
            description='New Desc', 
            instructor=self.instructor,
            status='published'
        )
        
        url = '/api/progress/'
        data = {
            'user': self.instructor.id,
            'course': new_course.id,
            'completed_lessons': 1,
            'total_lessons': 10,
        }
        response = self.client.post(url, data)
        
        # Should succeed for a new course
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify progress was created
        self.assertTrue(
            Progress.objects.filter(
                user=self.instructor, 
                course=new_course
            ).exists()
        )

    def test_update_own_progress(self):
        """Test updating your own progress"""
        url = f'/api/progress/{self.instructor_progress1.id}/'
        data = {
            'user': self.instructor.id,
            'course': self.course1.id,
            'completed_lessons': 4,
            'total_lessons': 5,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify progress was updated
        self.instructor_progress1.refresh_from_db()
        self.assertEqual(self.instructor_progress1.completed_lessons, 4)
        
    def test_student_cannot_update_other_student_progress(self):
        """Test student cannot update another student's progress"""
        # Switch to student credentials
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        url = f'/api/progress/{self.other_student_progress.id}/'
        data = {
            'user': self.other_student.id,
            'course': self.course2.id,
            'completed_lessons': 5,  # Try to update completed lessons
            'total_lessons': 5,
        }
        response = self.client.put(url, data)
        
        # Should not be able to update another student's progress
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify progress was not updated
        self.other_student_progress.refresh_from_db()
        self.assertEqual(self.other_student_progress.completed_lessons, 4)  # Still the original value

    def test_delete_own_progress(self):
        """Test deleting your own progress"""
        url = f'/api/progress/{self.instructor_progress1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify progress was deleted
        self.assertFalse(Progress.objects.filter(id=self.instructor_progress1.id).exists())
        
    def test_student_cannot_delete_other_student_progress(self):
        """Test student cannot delete another student's progress"""
        # Switch to student credentials
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
        
        url = f'/api/progress/{self.other_student_progress.id}/'
        response = self.client.delete(url)
        
        # Should not be able to delete another student's progress
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify progress was not deleted
        self.assertTrue(Progress.objects.filter(id=self.other_student_progress.id).exists())