from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Course, Module, Quiz, Enrollment
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase

User = get_user_model()

class ModuleQuizAPITest(APITestCaseBase):
    def setUp(self):
        # Call the parent setUp which creates self.user and self.instructor
        super().setUp()
        
        # Set the instructor as our main user
        self.main_instructor = self.instructor
        
        # Create a student user (already exists as self.user in the parent class)
        self.student = self.user
        self.student.profile.is_instructor = False
        self.student.profile.save()
        
        # Create another instructor
        self.other_instructor = User.objects.create_user(username='instructor2', password='pass')
        self.other_instructor.profile.is_instructor = True
        self.other_instructor.profile.save()

        # Create test courses
        self.course1 = Course.objects.create(
            title='Course 1', 
            description='Desc 1', 
            instructor=self.main_instructor,
            status='published'
        )
        
        self.course2 = Course.objects.create(
            title='Course 2', 
            description='Desc 2', 
            instructor=self.other_instructor,
            status='published'
        )

        # Create test modules
        self.module1 = Module.objects.create(
            course=self.course1,
            title='Module 1',
            description='Module 1 Desc',
            order=1
        )
        
        self.module2 = Module.objects.create(
            course=self.course2,
            title='Module 2',
            description='Module 2 Desc',
            order=1
        )
        
        # Create test quizzes
        self.quiz1 = Quiz.objects.create(
            module=self.module1,
            title='Quiz 1',
            description='Quiz 1 Desc',
            is_survey=False
        )
        
        self.quiz2 = Quiz.objects.create(
            module=self.module2,
            title='Quiz 2',
            description='Quiz 2 Desc',
            is_survey=True
        )
        
        # Enroll the student in course1
        Enrollment.objects.create(
            user=self.student,
            course=self.course1,
            status='active'
        )

        # Default to instructor credentials
        self.login_api(self.main_instructor)
    
    # === MODULE TESTS ===
    
    def test_list_modules_as_instructor(self):
        """Test that an instructor can see all modules"""
        url = '/api/courses/modules/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see both modules
        
    def test_list_modules_as_student(self):
        """Test that a student can only see modules from enrolled courses"""
        # Switch to student credentials
        self.login_api(self.student)
        
        url = '/api/courses/modules/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see module1
        self.assertEqual(response.data[0]['id'], self.module1.id)
        
    def test_retrieve_module(self):
        """Test retrieving a specific module"""
        url = f'/api/courses/modules/{self.module1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.module1.id)
        self.assertEqual(response.data['title'], 'Module 1')
        
    def test_create_module(self):
        """Test creating a new module for a course"""
        url = '/api/courses/modules/'
        data = {
            'course': self.course1.id,
            'title': 'New Module',
            'description': 'New module description',
            'order': 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify module was created
        self.assertTrue(Module.objects.filter(title='New Module').exists())
        
    def test_create_module_for_other_instructor_course(self):
        """Test that an instructor cannot create a module for another instructor's course"""
        url = '/api/courses/modules/'
        data = {
            'course': self.course2.id,  # Course belongs to other_instructor
            'title': 'Unauthorized Module',
            'description': 'Should not be created',
            'order': 1
        }
        response = self.client.post(url, data)
        
        # Should not be allowed to create a module for another instructor's course
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify no module was created
        self.assertFalse(Module.objects.filter(title='Unauthorized Module').exists())
        
    def test_update_module(self):
        """Test updating a module"""
        url = f'/api/courses/modules/{self.module1.id}/'
        data = {
            'course': self.course1.id,
            'title': 'Updated Module',
            'description': 'Updated description',
            'order': 1
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify module was updated
        self.module1.refresh_from_db()
        self.assertEqual(self.module1.title, 'Updated Module')
        
    def test_delete_module(self):
        """Test deleting a module"""
        url = f'/api/courses/modules/{self.module1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify module was deleted
        self.assertFalse(Module.objects.filter(id=self.module1.id).exists())
        
    def test_student_cannot_create_module(self):
        """Test that a student cannot create modules"""
        # Switch to student credentials
        self.login_api(self.student)
        
        url = '/api/courses/modules/'
        data = {
            'course': self.course1.id,
            'title': 'Student Module',
            'description': 'Should not be created',
            'order': 3
        }
        response = self.client.post(url, data)
        
        # Students should not be allowed to create modules
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        
        # Verify no module was created
        self.assertFalse(Module.objects.filter(title='Student Module').exists())
    
    # === QUIZ TESTS ===
    
    def test_list_quizzes_as_instructor(self):
        """Test that an instructor can see all quizzes"""
        url = '/api/courses/quizzes/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see both quizzes
        
    def test_list_quizzes_as_student(self):
        """Test that a student can only see quizzes from enrolled courses"""
        # Switch to student credentials
        self.login_api(self.student)
        
        url = '/api/courses/quizzes/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see quiz1
        self.assertEqual(response.data[0]['id'], self.quiz1.id)
        
    def test_retrieve_quiz(self):
        """Test retrieving a specific quiz"""
        url = f'/api/courses/quizzes/{self.quiz1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.quiz1.id)
        self.assertEqual(response.data['title'], 'Quiz 1')
        
    def test_create_quiz(self):
        """Test creating a new quiz for a module"""
        url = '/api/courses/quizzes/'
        data = {
            'module': self.module1.id,
            'title': 'New Quiz',
            'description': 'New quiz description',
            'is_survey': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify quiz was created
        self.assertTrue(Quiz.objects.filter(title='New Quiz').exists())
        
    def test_create_quiz_for_other_instructor_module(self):
        """Test that an instructor cannot create a quiz for another instructor's module"""
        url = '/api/courses/quizzes/'
        data = {
            'module': self.module2.id,  # Module belongs to a course from other_instructor
            'title': 'Unauthorized Quiz',
            'description': 'Should not be created',
            'is_survey': False
        }
        response = self.client.post(url, data)
        
        # Should not be allowed to create a quiz for another instructor's module
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify no quiz was created
        self.assertFalse(Quiz.objects.filter(title='Unauthorized Quiz').exists())
        
    def test_update_quiz(self):
        """Test updating a quiz"""
        url = f'/api/courses/quizzes/{self.quiz1.id}/'
        data = {
            'module': self.module1.id,
            'title': 'Updated Quiz',
            'description': 'Updated description',
            'is_survey': True
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify quiz was updated
        self.quiz1.refresh_from_db()
        self.assertEqual(self.quiz1.title, 'Updated Quiz')
        self.assertEqual(self.quiz1.is_survey, True)
        
    def test_delete_quiz(self):
        """Test deleting a quiz"""
        url = f'/api/courses/quizzes/{self.quiz1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify quiz was deleted
        self.assertFalse(Quiz.objects.filter(id=self.quiz1.id).exists())
        
    def test_student_cannot_create_quiz(self):
        """Test that a student cannot create quizzes"""
        # Switch to student credentials
        self.login_api(self.student)
        
        url = '/api/courses/quizzes/'
        data = {
            'module': self.module1.id,
            'title': 'Student Quiz',
            'description': 'Should not be created',
            'is_survey': False
        }
        response = self.client.post(url, data)
        
        # Students should not be allowed to create quizzes
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        
        # Verify no quiz was created
        self.assertFalse(Quiz.objects.filter(title='Student Quiz').exists())