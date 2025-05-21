from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from users.models import UserProfile
from io import StringIO
import sys

class CreateDemoAccountsCommandTest(TestCase):
    """Test the create_demo_accounts management command."""
    
    def test_create_demo_accounts(self):
        """Test that the command creates the expected demo accounts."""
        
        # Capture command output
        out = StringIO()
        sys.stdout = out
        
        # Run the command
        call_command('create_demo_accounts')
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        
        # Verify admin account
        admin_user = User.objects.get(username='demo_admin')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertEqual(admin_user.first_name, 'Demo')
        self.assertEqual(admin_user.last_name, 'Admin')
        self.assertTrue(admin_user.check_password('demopass123'))
        
        # Verify instructor account
        instructor_user = User.objects.get(username='demo_instructor')
        self.assertEqual(instructor_user.email, 'instructor@example.com')
        self.assertEqual(instructor_user.first_name, 'Demo')
        self.assertEqual(instructor_user.last_name, 'Instructor')
        self.assertTrue(instructor_user.check_password('demopass123'))
        
        instructor_profile = instructor_user.profile
        self.assertTrue(instructor_profile.is_instructor)
        self.assertEqual(instructor_profile.department, 'Computer Science')
        
        # Verify student account
        student_user = User.objects.get(username='demo_student')
        self.assertEqual(student_user.email, 'student@example.com')
        self.assertEqual(student_user.first_name, 'Demo')
        self.assertEqual(student_user.last_name, 'Student')
        self.assertTrue(student_user.check_password('demopass123'))
        
        student_profile = student_user.profile
        self.assertFalse(student_profile.is_instructor)
        self.assertEqual(student_profile.student_id, 's123456')
        self.assertEqual(student_profile.department, 'Information Technology')
        
        # Verify the output contains success messages
        output = out.getvalue()
        self.assertIn('Demo accounts created successfully', output)
        self.assertIn('Admin Account:', output)
        self.assertIn('Username: demo_admin', output)
        self.assertIn('Instructor Account:', output)
        self.assertIn('Username: demo_instructor', output)
        self.assertIn('Student Account:', output)
        self.assertIn('Username: demo_student', output)
        
    def test_idempotent_creation(self):
        """Test that the command can be run multiple times without error."""
        
        # Create accounts first time
        call_command('create_demo_accounts')
        
        # Get the user count
        user_count_first = User.objects.count()
        
        # Run the command again
        call_command('create_demo_accounts')
        
        # Verify that no new users were created
        user_count_second = User.objects.count()
        self.assertEqual(user_count_first, user_count_second)
        
        # Verify the accounts still exist with correct properties
        admin_user = User.objects.get(username='demo_admin')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.check_password('demopass123'))
        
        instructor_profile = User.objects.get(username='demo_instructor').profile
        self.assertTrue(instructor_profile.is_instructor)
        
        student_profile = User.objects.get(username='demo_student').profile
        self.assertEqual(student_profile.student_id, 's123456')