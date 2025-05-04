from django.core.management.base import BaseCommand
from django.core.management import call_command
from rest_framework.test import APIClient
from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse
from django.db import connection, connections
import os
import time
import sqlite3

class Command(BaseCommand):
    help = 'Fully resets the database, runs migrations, sets up groups/permissions, and seeds demo data via API.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Resetting database...'))
        
        # Get the database file path
        db_path = connection.settings_dict['NAME']
        
        # Close all database connections
        for conn in connections.all():
            conn.close()
        
        # Wait a moment to ensure all connections are closed
        time.sleep(1)
        
        # Delete the database file if it exists
        if os.path.exists(db_path):
            try:
                # Try to connect to the database to ensure it's not locked
                try:
                    conn = sqlite3.connect(db_path)
                    conn.close()
                except sqlite3.Error:
                    self.stdout.write(self.style.WARNING('Database is locked, waiting...'))
                    time.sleep(2)  # Wait longer if database is locked
                
                os.remove(db_path)
                self.stdout.write(self.style.SUCCESS(f'Deleted database file: {db_path}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error deleting database file: {str(e)}'))
                return
        
        # Wait a moment to ensure the file is deleted
        time.sleep(1)
        
        self.stdout.write(self.style.WARNING('Running migrations...'))
        call_command('migrate')

        # Create API client
        client = APIClient()

        self.stdout.write(self.style.WARNING('Setting up groups and permissions...'))
        
        # Create groups first
        groups_data = [
            {
                'name': 'Administrator',
                'permissions': []
            },
            {
                'name': 'Course Coordinator',
                'permissions': ['Can manage courses', 'Can manage enrollments']
            },
            {
                'name': 'Instructor',
                'permissions': ['Can create courses', 'Can manage modules']
            },
            {
                'name': 'Student',
                'permissions': ['Can view courses', 'Can take quizzes']
            }
        ]

        for group_data in groups_data:
            group, created = Group.objects.get_or_create(name=group_data['name'])
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_data["name"]}'))
                # Add permissions if specified
                for perm_name in group_data['permissions']:
                    try:
                        perm = Permission.objects.get(name=perm_name)
                        group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'Permission not found: {perm_name}'))

        self.stdout.write(self.style.SUCCESS('Groups and permissions set up.'))

        self.stdout.write(self.style.WARNING('Seeding enhanced demo data...'))
        try:
            call_command('enhanced_seed_data')
            self.stdout.write(self.style.SUCCESS('Enhanced demo data successfully seeded!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding enhanced demo data: {str(e)}'))
            
            # Fallback to original seed methods
            self.stdout.write(self.style.WARNING('Falling back to original seed methods...'))
            self.stdout.write(self.style.WARNING('Seeding demo data via API...'))
            call_command('seed_demo_data_api')

        self.stdout.write(self.style.WARNING('Seeding activity data...'))
        call_command('seed_activity_data')
        
        self.stdout.write(self.style.WARNING('Seeding AI Tutor demo data...'))
        try:
            call_command('seed_ai_tutor_demo')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding AI Tutor demo data: {str(e)}'))
            self.stdout.write(self.style.WARNING('AI Tutor demo data seeding skipped. You can run it manually with:'))
            self.stdout.write('python manage.py seed_ai_tutor_demo')

        self.stdout.write(self.style.SUCCESS('System reset complete!'))
        self.stdout.write('')
        self.stdout.write('Test users created:')
        self.stdout.write('------------------')
        self.stdout.write('Admin:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('')
        self.stdout.write('Course Coordinator:')
        self.stdout.write('  Username: coordinator')
        self.stdout.write('  Password: coordinator123')
        self.stdout.write('')
        self.stdout.write('Instructors:')
        self.stdout.write('  Username: dr.smith')
        self.stdout.write('  Password: dr.smith123')
        self.stdout.write('  Username: dr.johnson')
        self.stdout.write('  Password: dr.johnson123')
        self.stdout.write('  Username: prof.williams')
        self.stdout.write('  Password: prof.williams123')
        self.stdout.write('')
        self.stdout.write('Students:')
        self.stdout.write('  Username: john.doe')
        self.stdout.write('  Password: john.doe123')
        self.stdout.write('  Username: jane.smith')
        self.stdout.write('  Password: jane.smith123')
        self.stdout.write('  Username: bob.wilson')
        self.stdout.write('  Password: bob.wilson123')
        self.stdout.write('  Username: alice.johnson')
        self.stdout.write('  Password: alice.johnson123')
        self.stdout.write('')
        self.stdout.write('Run the development server with:')
        self.stdout.write('python manage.py runserver') 