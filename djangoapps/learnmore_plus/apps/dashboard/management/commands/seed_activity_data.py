from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with user activity data via API'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding user activity data via API...')

        # Create API client
        client = APIClient()

        # Get admin user for authentication
        try:
            admin_user = User.objects.get(username='admin')
            client.force_authenticate(user=admin_user)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found. Please run reset_db first.'))
            return

        # Get all users
        users = User.objects.all()
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please run reset_db first.'))
            return

        # Generate activity data for the last 30 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        # Action types available in the API
        action_types = [
            'login',
            'logout',
            'course_view',
            'quiz_attempt',
            'content_access',
            'profile_update',
            'settings_change'
        ]

        # Create activities for each user
        for user in users:
            # Generate 5-20 activities per user
            num_activities = random.randint(5, 20)
            
            for _ in range(num_activities):
                # Random timestamp within the last 30 days
                timestamp = start_date + timedelta(
                    seconds=random.randint(0, int((end_date - start_date).total_seconds()))
                )
                
                # Random action type
                action = random.choice(action_types)
                
                # Generate random IP address
                ip_address = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
                
                # Generate random user agent
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                ]
                user_agent = random.choice(user_agents)
                
                # Generate random details based on action type
                details = {}
                if action == 'course_view':
                    details = {
                        'course_id': random.randint(1, 10),
                        'course_title': f'Course {random.randint(1, 10)}',
                        'duration': random.randint(30, 300)
                    }
                elif action == 'quiz_attempt':
                    details = {
                        'quiz_id': random.randint(1, 20),
                        'quiz_title': f'Quiz {random.randint(1, 20)}',
                        'score': random.randint(0, 100),
                        'time_spent': random.randint(300, 1800)
                    }
                elif action == 'content_access':
                    details = {
                        'content_id': random.randint(1, 50),
                        'content_type': random.choice(['text', 'video', 'file']),
                        'duration': random.randint(60, 600)
                    }
                elif action == 'profile_update':
                    details = {
                        'fields_updated': random.choice(['email', 'password', 'preferences', 'all']),
                        'timestamp': timestamp.isoformat()
                    }
                elif action == 'settings_change':
                    details = {
                        'setting': random.choice(['notifications', 'privacy', 'display', 'language']),
                        'old_value': 'default',
                        'new_value': 'custom'
                    }

                # Create activity via API
                activity_data = {
                    'user': user.id,
                    'action': action,
                    'timestamp': timestamp.isoformat(),
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'details': details
                }

                response = client.post('/api/activities/', activity_data, format='json')
                if response.status_code == 201:
                    self.stdout.write(self.style.SUCCESS(f'Created activity for user {user.username}: {action}'))
                else:
                    error_detail = getattr(response, 'data', response.content)
                    self.stdout.write(self.style.ERROR(f'Failed to create activity: {error_detail}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded user activities via API')) 