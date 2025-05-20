from django.test import TestCase
from django.contrib.auth.models import User
from users.models import UserProfile

class UserProfileTest(TestCase):
    """Tests for UserProfile model CRUD operations."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Profile is automatically created by the signal
        self.profile = self.user.profile
    
    def test_profile_created_automatically(self):
        """Test that a profile is created automatically when a user is created."""
        # Assert that profile was created
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)
        
        # Assert default values
        self.assertEqual(self.profile.bio, '')
        self.assertEqual(self.profile.student_id, '')
        self.assertEqual(self.profile.department, '')
        self.assertFalse(self.profile.is_instructor)
        self.assertEqual(self.profile.google_id, '')
        self.assertIsNotNone(self.profile.created_at)
        self.assertIsNotNone(self.profile.updated_at)
    
    def test_update_profile(self):
        """Test updating a user profile."""
        # Update profile fields
        self.profile.bio = 'Test bio'
        self.profile.student_id = '12345'
        self.profile.department = 'Computer Science'
        self.profile.is_instructor = True
        self.profile.google_id = 'google123'
        self.profile.save()
        
        # Refresh from database
        self.profile.refresh_from_db()
        
        # Assert updated values
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.student_id, '12345')
        self.assertEqual(self.profile.department, 'Computer Science')
        self.assertTrue(self.profile.is_instructor)
        self.assertEqual(self.profile.google_id, 'google123')
    
    def test_delete_user_deletes_profile(self):
        """Test that deleting a user deletes the profile."""
        profile_id = self.profile.id
        user_id = self.user.id
        
        # Delete the user
        self.user.delete()
        
        # Verify user and profile are deleted
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())
    
    def test_update_user_updates_profile(self):
        """Test that the signal updates the profile when the user is updated."""
        # Store original timestamps
        original_updated_at = self.profile.updated_at
        
        # Update user
        self.user.first_name = 'Updated'
        self.user.save()
        
        # Refresh profile from database
        self.profile.refresh_from_db()
        
        # Assert profile updated_at has changed
        self.assertGreater(self.profile.updated_at, original_updated_at)
    
    def test_create_profile_for_existing_user(self):
        """Test creating a profile for an existing user without one."""
        # Create a new user and delete their auto-created profile
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        user2.profile.delete()
        
        # Verify profile is deleted
        user2 = User.objects.get(id=user2.id)  # Refresh user
        with self.assertRaises(UserProfile.DoesNotExist):
            profile = user2.profile
        
        # Create a new profile
        profile = UserProfile.objects.create(
            user=user2,
            bio='New bio',
            student_id='54321',
            department='Mathematics',
            is_instructor=True
        )
        
        # Verify profile is created with correct values
        self.assertEqual(profile.user, user2)
        self.assertEqual(profile.bio, 'New bio')
        self.assertEqual(profile.student_id, '54321')
        self.assertEqual(profile.department, 'Mathematics')
        self.assertTrue(profile.is_instructor)
    
    def test_str_representation(self):
        """Test string representation of UserProfile."""
        expected_str = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.profile), expected_str)