"""
Script to create test users for the LearnMore platform.
Creates users with different roles: admin, instructor, student.

Usage:
    python manage.py shell < create_test_users.py
"""

from django.contrib.auth.models import User
from users.models import UserProfile
from django.db import transaction
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

# Create test users
test_users = [
    {
        'username': 'student1',
        'email': 'student1@example.com',
        'password': 'studentpass123',
        'first_name': 'Student',
        'last_name': 'One',
        'is_staff': False,
        'is_superuser': False,
        'profile': {
            'student_id': '12345678',
            'department': 'Computer Science',
            'is_instructor': False,
            'bio': 'I am a computer science student.'
        }
    },
    {
        'username': 'student2',
        'email': 'student2@example.com',
        'password': 'studentpass123',
        'first_name': 'Student',
        'last_name': 'Two',
        'is_staff': False,
        'is_superuser': False,
        'profile': {
            'student_id': '87654321',
            'department': 'Mathematics',
            'is_instructor': False,
            'bio': 'I am a mathematics student.'
        }
    },
    {
        'username': 'instructor1',
        'email': 'instructor1@example.com',
        'password': 'instructorpass123',
        'first_name': 'Instructor',
        'last_name': 'One',
        'is_staff': True,
        'is_superuser': False,
        'profile': {
            'department': 'Computer Science',
            'is_instructor': True,
            'bio': 'I am a computer science instructor.'
        }
    },
    {
        'username': 'instructor2',
        'email': 'instructor2@example.com',
        'password': 'instructorpass123',
        'first_name': 'Instructor',
        'last_name': 'Two',
        'is_staff': True,
        'is_superuser': False,
        'profile': {
            'department': 'Mathematics',
            'is_instructor': True,
            'bio': 'I am a mathematics instructor.'
        }
    },
    {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'adminpass123',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True,
        'profile': {
            'department': 'Administration',
            'is_instructor': True,
            'bio': 'I am the system administrator.'
        }
    }
]

created_count = 0
updated_count = 0

with transaction.atomic():
    for user_data in test_users:
        profile_data = user_data.pop('profile')
        password = user_data.pop('password')
        user, created = User.objects.update_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        user.set_password(password)
        user.save()
        # Ensure profile exists
        profile, _ = UserProfile.objects.get_or_create(user=user)
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.save()
        print(f"Updated profile for: {user.username}")
        
        if created:
            created_count += 1
        else:
            updated_count += 1

print(f"Created {created_count} new users and updated {updated_count} existing users.")
print("Test users have been successfully created.")