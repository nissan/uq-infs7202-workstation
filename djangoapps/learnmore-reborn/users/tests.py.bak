from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile

class UserAPITests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile = self.user.profile
        self.profile.student_id = '12345'
        self.profile.department = 'Computer Science'
        self.profile.save()

        # URLs
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        self.google_auth_url = reverse('google-auth')

        # Test data
        self.valid_registration_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        self.valid_login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        self.valid_profile_data = {
            'bio': 'Test bio',
            'student_id': '54321',
            'department': 'Mathematics',
            'is_instructor': True
        }

        self.valid_google_auth_data = {
            'google_id': '123456789',
            'email': 'google@example.com',
            'first_name': 'Google',
            'last_name': 'User',
            'profile_picture': 'https://example.com/photo.jpg'
        }

        # Initialize tokens
        self.access_token = None
        self.refresh_token = None

    def authenticate(self):
        """Helper method to authenticate and get tokens"""
        response = self.client.post(self.login_url, self.valid_login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']
        self.refresh_token = response.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post(self.register_url, self.valid_registration_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_registration_invalid_data(self):
        """Test user registration with invalid data"""
        invalid_data = self.valid_registration_data.copy()
        invalid_data['password2'] = 'differentpass'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login endpoint"""
        response = self.client.post(self.login_url, self.valid_login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        invalid_data = self.valid_login_data.copy()
        invalid_data['password'] = 'wrongpass'
        response = self.client.post(self.login_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout(self):
        """Test user logout endpoint"""
        # First login to get tokens
        self.authenticate()
        
        # Then logout
        response = self.client.post(self.logout_url, {'refresh': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_profile_retrieve(self):
        """Test retrieving user profile"""
        # Login and set authentication
        self.authenticate()
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], '12345')
        self.assertEqual(response.data['department'], 'Computer Science')

    def test_profile_update(self):
        """Test updating user profile"""
        # Login and set authentication
        self.authenticate()
        
        response = self.client.put(self.profile_url, self.valid_profile_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.student_id, '54321')
        self.assertEqual(self.profile.department, 'Mathematics')
        self.assertTrue(self.profile.is_instructor)

    def test_google_auth_new_user(self):
        """Test Google authentication for new user"""
        response = self.client.post(self.google_auth_url, self.valid_google_auth_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user was created
        user = User.objects.get(email='google@example.com')
        self.assertEqual(user.profile.google_id, '123456789')

    def test_google_auth_existing_user(self):
        """Test Google authentication for existing user"""
        # Create a user with the same email
        existing_user = User.objects.create_user(
            username='existing',
            email='google@example.com',
            password='pass123',
            first_name='Existing',
            last_name='User'
        )

        response = self.client.post(self.google_auth_url, self.valid_google_auth_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify google_id was updated
        existing_user.refresh_from_db()
        self.assertEqual(existing_user.profile.google_id, '123456789')
