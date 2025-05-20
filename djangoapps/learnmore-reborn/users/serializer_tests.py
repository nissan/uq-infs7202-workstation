from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from .models import UserProfile
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    LoginSerializer, 
    GoogleAuthSerializer
)

class UserSerializerValidationTest(TestCase):
    """Tests for UserSerializer validation."""
    
    def setUp(self):
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = UserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Missing username
        invalid_data = self.valid_data.copy()
        invalid_data.pop('username')
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        
        # Missing email
        invalid_data = self.valid_data.copy()
        invalid_data.pop('email')
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        
        # Missing password
        invalid_data = self.valid_data.copy()
        invalid_data.pop('password')
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        
        # Missing password2
        invalid_data = self.valid_data.copy()
        invalid_data.pop('password2')
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)
        
        # Missing first_name
        invalid_data = self.valid_data.copy()
        invalid_data.pop('first_name')
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)
        
        # Missing last_name
        invalid_data = self.valid_data.copy()
        invalid_data.pop('last_name')
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)
    
    def test_password_mismatch(self):
        """Test that password mismatch fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'differentpass'
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_username_exists(self):
        """Test that existing username fails validation."""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='pass123'
        )
        
        # Try to create another user with the same username
        serializer = UserSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)


class UserProfileSerializerValidationTest(TestCase):
    """Tests for UserProfileSerializer validation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = self.user.profile
        
        self.valid_data = {
            'bio': 'Test bio',
            'student_id': '12345',
            'department': 'Computer Science',
            'is_instructor': True
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = UserProfileSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_empty_fields(self):
        """Test that empty fields are allowed."""
        valid_data = {
            'bio': '',
            'student_id': '',
            'department': '',
            'is_instructor': False
        }
        serializer = UserProfileSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())


class LoginSerializerValidationTest(TestCase):
    """Tests for LoginSerializer validation."""
    
    def setUp(self):
        self.valid_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = LoginSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Missing username
        invalid_data = self.valid_data.copy()
        invalid_data.pop('username')
        serializer = LoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        
        # Missing password
        invalid_data = self.valid_data.copy()
        invalid_data.pop('password')
        serializer = LoginSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class GoogleAuthSerializerValidationTest(TestCase):
    """Tests for GoogleAuthSerializer validation."""
    
    def setUp(self):
        self.valid_data = {
            'google_id': '12345',
            'email': 'google@example.com',
            'first_name': 'Google',
            'last_name': 'User',
            'profile_picture': 'https://example.com/photo.jpg'
        }
    
    def test_valid_data(self):
        """Test that valid data passes validation."""
        serializer = GoogleAuthSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Missing google_id
        invalid_data = self.valid_data.copy()
        invalid_data.pop('google_id')
        serializer = GoogleAuthSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('google_id', serializer.errors)
        
        # Missing email
        invalid_data = self.valid_data.copy()
        invalid_data.pop('email')
        serializer = GoogleAuthSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        
        # Missing first_name
        invalid_data = self.valid_data.copy()
        invalid_data.pop('first_name')
        serializer = GoogleAuthSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)
        
        # Missing last_name
        invalid_data = self.valid_data.copy()
        invalid_data.pop('last_name')
        serializer = GoogleAuthSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)
    
    def test_optional_profile_picture(self):
        """Test that profile_picture is optional."""
        valid_data = self.valid_data.copy()
        valid_data.pop('profile_picture')
        serializer = GoogleAuthSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_email(self):
        """Test that invalid email fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'not-an-email'
        serializer = GoogleAuthSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_invalid_url(self):
        """Test that invalid profile_picture URL fails validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['profile_picture'] = 'not-a-url'
        serializer = GoogleAuthSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('profile_picture', serializer.errors)