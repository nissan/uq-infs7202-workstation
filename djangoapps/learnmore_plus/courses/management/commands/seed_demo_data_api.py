from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from django.urls import reverse
import json
import random
from datetime import datetime, timedelta
from django.utils.text import slugify
from random import randint, choice

class Command(BaseCommand):
    help = 'Seeds the database with demo data using the API endpoints'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed demo data via API...')
        
        # Create API client
        client = APIClient()
        
        # Create admin user and get token
        admin_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User'
        }
        response = client.post('/api/users/', admin_data, format='json')
        if response.status_code == 201:
            admin_user = User.objects.get(username='admin')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            client.force_authenticate(user=admin_user)
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            error_detail = getattr(response, 'data', response.content)
            self.stdout.write(self.style.ERROR(f'Failed to create admin user: {error_detail}'))
            return

        # Create groups
        groups = {
            'Course Coordinator': ['Can manage courses', 'Can manage enrollments'],
            'Instructor': ['Can create courses', 'Can manage modules'],
            'Student': ['Can view courses', 'Can take quizzes']
        }

        for group_name, permissions in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for perm_name in permissions:
                perm = Permission.objects.get(name=perm_name)
                group.permissions.add(perm)
            self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))

        # Expanded test users with realistic names
        users_data = [
            # Admins
            {
                'username': 'amorgan', 'email': 'alice.morgan@example.com', 'password': 'admin123', 'first_name': 'Alice', 'last_name': 'Morgan', 'groups': ['Admin']
            },
            {
                'username': 'blee', 'email': 'brian.lee@example.com', 'password': 'admin123', 'first_name': 'Brian', 'last_name': 'Lee', 'groups': ['Admin']
            },
            # Coordinators
            {'username': 'ebrown', 'email': 'emily.brown@example.com', 'password': 'coord123', 'first_name': 'Emily', 'last_name': 'Brown', 'groups': ['Course Coordinator']},
            {'username': 'mgreen', 'email': 'michael.green@example.com', 'password': 'coord123', 'first_name': 'Michael', 'last_name': 'Green', 'groups': ['Course Coordinator']},
            # Instructors
            {'username': 'jsmith', 'email': 'john.smith@example.com', 'password': 'inst123', 'first_name': 'John', 'last_name': 'Smith', 'groups': ['Instructor']},
            {'username': 'sjohnson', 'email': 'sarah.johnson@example.com', 'password': 'inst123', 'first_name': 'Sarah', 'last_name': 'Johnson', 'groups': ['Instructor']},
            {'username': 'lwhite', 'email': 'lisa.white@example.com', 'password': 'inst123', 'first_name': 'Lisa', 'last_name': 'White', 'groups': ['Instructor']},
            {'username': 'dkim', 'email': 'david.kim@example.com', 'password': 'inst123', 'first_name': 'David', 'last_name': 'Kim', 'groups': ['Instructor']},
            # Students
            {'username': 'jsmith2', 'email': 'jane.smith@example.com', 'password': 'stud123', 'first_name': 'Jane', 'last_name': 'Smith', 'groups': ['Student']},
            {'username': 'bwilson', 'email': 'bob.wilson@example.com', 'password': 'stud123', 'first_name': 'Bob', 'last_name': 'Wilson', 'groups': ['Student']},
            {'username': 'ajohnson', 'email': 'alice.johnson@example.com', 'password': 'stud123', 'first_name': 'Alice', 'last_name': 'Johnson', 'groups': ['Student']},
            {'username': 'jdoe', 'email': 'john.doe@example.com', 'password': 'stud123', 'first_name': 'John', 'last_name': 'Doe', 'groups': ['Student']},
            {'username': 'mgarcia', 'email': 'maria.garcia@example.com', 'password': 'stud123', 'first_name': 'Maria', 'last_name': 'Garcia', 'groups': ['Student']},
            {'username': 'dlee', 'email': 'david.lee@example.com', 'password': 'stud123', 'first_name': 'David', 'last_name': 'Lee', 'groups': ['Student']},
            {'username': 'emartinez', 'email': 'emma.martinez@example.com', 'password': 'stud123', 'first_name': 'Emma', 'last_name': 'Martinez', 'groups': ['Student']},
            {'username': 'wbrown', 'email': 'william.brown@example.com', 'password': 'stud123', 'first_name': 'William', 'last_name': 'Brown', 'groups': ['Student']},
        ]

        for user_data in users_data:
            groups = user_data.pop('groups')
            response = client.post('/api/users/', user_data, format='json')
            if response.status_code == 201:
                user = User.objects.get(username=user_data['username'])
                for group_name in groups:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                self.stdout.write(self.style.SUCCESS(f'Created user: {user_data["username"]}'))
            else:
                error_detail = getattr(response, 'data', response.content)
                self.stdout.write(self.style.ERROR(f'Failed to create user {user_data["username"]}: {error_detail}'))

        # Print all existing categories before seeding
        all_categories = []
        url = '/api/categories/'
        while url:
            get_response = client.get(url)
            if get_response.status_code == 200:
                data = get_response.data['results'] if isinstance(get_response.data, dict) and 'results' in get_response.data else get_response.data
                all_categories.extend(data)
                url = get_response.data.get('next') if isinstance(get_response.data, dict) else None
            else:
                break
        if all_categories:
            self.stdout.write(self.style.WARNING('Existing categories before seeding:'))
            for cat in all_categories:
                self.stdout.write(f"- {cat['name']} (slug: {cat['slug']})")

        # Create categories
        categories_data = [
            {
                'name': 'Programming',
                'description': 'Programming and software development courses'
            },
            {
                'name': 'Web Development',
                'description': 'Web development and design courses'
            },
            {
                'name': 'Data Science',
                'description': 'Data science and analytics courses'
            }
        ]

        # Fetch all categories once for existence check
        all_categories = []
        url = '/api/categories/'
        while url:
            get_response = client.get(url)
            if get_response.status_code == 200:
                data = get_response.data['results'] if isinstance(get_response.data, dict) and 'results' in get_response.data else get_response.data
                all_categories.extend(data)
                url = get_response.data.get('next') if isinstance(get_response.data, dict) else None
            else:
                break
        existing_names = {cat['name'].lower() for cat in all_categories}
        existing_slugs = {cat['slug'] for cat in all_categories}

        for category_data in categories_data:
            slug = slugify(category_data['name'])
            category_data['slug'] = slug
            if category_data['name'].lower() in existing_names or slug in existing_slugs:
                self.stdout.write(self.style.WARNING(f"Category already exists (name or slug): {category_data['name']} / {slug}"))
                continue
            response = client.post('/api/categories/', category_data, format='json')
            if response.status_code == 201:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_data["name"]}'))
                existing_names.add(category_data['name'].lower())
                existing_slugs.add(slug)
            else:
                error_detail = getattr(response, 'data', response.content)
                if isinstance(error_detail, dict) and 'detail' in error_detail and 'UNIQUE constraint failed: courses_category.slug' in str(error_detail['detail']):
                    self.stdout.write(self.style.WARNING(f"Category already exists (slug): {category_data['name']} / {slug}"))
                    continue
                self.stdout.write(self.style.ERROR(f'Failed to create category {category_data["name"]}: {error_detail}'))

        # Expanded courses (at least 10)
        courses_data = [
            {'title': 'Python for Beginners', 'description': 'Learn Python from scratch.', 'category': 1, 'instructor': 5, 'status': 'published'},
            {'title': 'Advanced Java', 'description': 'Deep dive into Java programming.', 'category': 1, 'instructor': 6, 'status': 'published'},
            {'title': 'C++ Fundamentals', 'description': 'Master the basics of C++.', 'category': 1, 'instructor': 7, 'status': 'published'},
            {'title': 'Full Stack Web Dev', 'description': 'Become a full stack web developer.', 'category': 2, 'instructor': 8, 'status': 'published'},
            {'title': 'React & Redux', 'description': 'Modern frontend with React and Redux.', 'category': 2, 'instructor': 5, 'status': 'published'},
            {'title': 'Django Deep Dive', 'description': 'Advanced Django techniques.', 'category': 2, 'instructor': 6, 'status': 'published'},
            {'title': 'Intro to Data Science', 'description': 'Data science for beginners.', 'category': 3, 'instructor': 7, 'status': 'published'},
            {'title': 'Machine Learning 101', 'description': 'Introduction to machine learning.', 'category': 3, 'instructor': 8, 'status': 'published'},
            {'title': 'Data Visualization with Python', 'description': 'Visualize data using Python.', 'category': 3, 'instructor': 5, 'status': 'published'},
            {'title': 'SQL & Databases', 'description': 'Learn SQL and database design.', 'category': 3, 'instructor': 6, 'status': 'published'},
            {'title': 'Cloud Computing Basics', 'description': 'Introduction to cloud computing.', 'category': 1, 'instructor': 7, 'status': 'published'},
            {'title': 'DevOps Essentials', 'description': 'Core DevOps concepts and tools.', 'category': 2, 'instructor': 8, 'status': 'published'},
        ]

        # Assign coordinators to courses (round robin)
        coordinator_ids = [3, 4]  # ebrown, mgreen
        for i, course in enumerate(courses_data):
            course['coordinator'] = coordinator_ids[i % len(coordinator_ids)]

        # Expanded modules and content for each course
        modules_template = [
            {
                'title': 'Introduction',
                'description': 'Overview and basics.',
                'order': 1,
                'contents': [
                    {'title': 'Welcome', 'content_type': 'text', 'content': 'Welcome to the course!', 'order': 1},
                    {'title': 'Course Overview', 'content_type': 'video', 'content': 'https://example.com/intro.mp4', 'order': 2},
                ]
            },
            {
                'title': 'Core Concepts',
                'description': 'Key concepts and skills.',
                'order': 2,
                'contents': [
                    {'title': 'Core Reading', 'content_type': 'file', 'content': 'core_concepts.pdf', 'order': 1},
                    {'title': 'Knowledge Check', 'content_type': 'quiz', 'content': 'Quiz placeholder', 'order': 2, 'is_pre_check': False, 'questions': [
                        {'text': 'What is a core concept?', 'question_type': 'multiple_choice', 'choices': [
                            {'text': 'A main idea', 'is_correct': True},
                            {'text': 'A minor detail', 'is_correct': False},
                            {'text': 'A quiz', 'is_correct': False},
                        ]},
                        {'text': 'True or False: Core concepts are optional.', 'question_type': 'true_false', 'choices': [
                            {'text': 'True', 'is_correct': False},
                            {'text': 'False', 'is_correct': True},
                        ]},
                    ]},
                ]
            },
            {
                'title': 'Survey & Feedback',
                'description': 'Pre-course survey and feedback.',
                'order': 3,
                'contents': [
                    {'title': 'Pre-course Survey', 'content_type': 'quiz', 'content': 'Quiz placeholder', 'order': 1, 'is_pre_check': True, 'questions': [
                        {'text': 'Have you studied this topic before?', 'question_type': 'multiple_choice', 'choices': [
                            {'text': 'Yes', 'is_correct': False},
                            {'text': 'No', 'is_correct': False},
                        ]},
                        {'text': 'What is your main goal?', 'question_type': 'short_answer', 'choices': []},
                    ]},
                ]
            }
        ]
        # Assign modules to each course
        for course in courses_data:
            course['modules'] = modules_template

        # Assign students to courses (all students enrolled in all courses, with varied statuses)
        student_ids = list(range(9, 17))  # jsmith2, bwilson, ajohnson, jdoe, mgarcia, dlee, emartinez, wbrown
        enrollment_statuses = ['active', 'completed', 'dropped']
        enrollments_data = []
        for i, course in enumerate(courses_data, 1):
            for j, student_id in enumerate(student_ids):
                status = enrollment_statuses[(i + j) % len(enrollment_statuses)]
                enrollments_data.append({'student': student_id, 'course': i, 'status': status})

        for course_data in courses_data:
            modules = course_data.pop('modules')
            response = client.post('/api/courses/', course_data, format='json')
            if response.status_code == 201:
                course_id = response.data['id']
                self.stdout.write(self.style.SUCCESS(f'Created course: {course_data["title"]}'))
                
                # Create modules
                for module_data in modules:
                    contents = module_data.pop('contents')
                    module_data['course'] = course_id
                    response = client.post('/api/modules/', module_data, format='json')
                    if response.status_code == 201:
                        module_id = response.data['id']
                        self.stdout.write(self.style.SUCCESS(f'Created module: {module_data["title"]}'))
                        
                        # Create contents
                        for content_data in contents:
                            content_data['module'] = module_id
                            if 'content' not in content_data:
                                content_data['content'] = ''  # Always provide content field
                            if content_data['content_type'] == 'quiz':
                                questions = content_data.pop('questions')
                                content_data['content'] = 'Quiz placeholder'
                                content_data['quiz_data'] = {
                                    'passing_score': 70,
                                    'max_attempts': 3,
                                    'is_published': True
                                }
                                response = client.post('/api/contents/', content_data, format='json')
                                if response.status_code == 201:
                                    content_id = response.data['id']
                                    self.stdout.write(self.style.SUCCESS(f'Created quiz content: {content_data["title"]}'))
                                    self.stdout.write(f'Quiz content creation response: {response.data}')
                                    # Explicitly create the Quiz object
                                    quiz_payload = {
                                        'content': content_id,
                                        'title': content_data['title'],
                                        'description': '',
                                        'passing_score': 70,
                                        'attempts_allowed': 3,
                                        'shuffle_questions': True,
                                        'show_correct_answers': True,
                                        'is_prerequisite': False,
                                        'is_pre_check': content_data.get('is_pre_check', False)
                                    }
                                    quiz_create_response = client.post('/api/quizzes/', quiz_payload, format='json')
                                    if quiz_create_response.status_code == 201:
                                        quiz_id = quiz_create_response.data['id']
                                        self.stdout.write(self.style.SUCCESS(f'Created quiz object: {quiz_create_response.data}'))
                                        # Create questions
                                        for question_data in questions:
                                            choices = question_data.pop('choices')
                                            question_data['question_text'] = question_data.pop('text')
                                            question_data['question_type'] = 'multiple_choice'
                                            question_data['quiz'] = quiz_id
                                            response = client.post('/api/questions/', question_data, format='json')
                                            if response.status_code == 201:
                                                question_id = response.data['id']
                                                self.stdout.write(self.style.SUCCESS(f'Created question: {question_data["question_text"]}'))
                                                
                                                # Create choices
                                                for choice_data in choices:
                                                    choice_data['question'] = question_id
                                                    choice_data['choice_text'] = choice_data.pop('text')
                                                    response = client.post('/api/choices/', choice_data, format='json')
                                                    if response.status_code == 201:
                                                        self.stdout.write(self.style.SUCCESS(f'Created choice: {choice_data["choice_text"]}'))
                                                    else:
                                                        error_detail = getattr(response, 'data', response.content)
                                                        self.stdout.write(self.style.ERROR(f'Failed to create choice: {error_detail}'))
                                            else:
                                                error_detail = getattr(response, 'data', response.content)
                                                self.stdout.write(self.style.ERROR(f'Failed to create question: {error_detail}'))
                                    else:
                                        error_detail = getattr(quiz_create_response, 'data', quiz_create_response.content)
                                        self.stdout.write(self.style.ERROR(f'Failed to create quiz object for content_id {content_id}: {error_detail}'))
                                else:
                                    error_detail = getattr(response, 'data', response.content)
                                    self.stdout.write(self.style.ERROR(f'Failed to create quiz content: {error_detail}'))
                            else:
                                # Handle text content
                                text_content = content_data.pop('content', '')
                                content_data['content'] = text_content  # Keep the content field at the top level
                                content_data['text_data'] = {
                                    'is_published': True
                                }
                                response = client.post('/api/contents/', content_data, format='json')
                                if response.status_code == 201:
                                    self.stdout.write(self.style.SUCCESS(f'Created content: {content_data["title"]}'))
                                else:
                                    error_detail = getattr(response, 'data', response.content)
                                    self.stdout.write(self.style.ERROR(f'Failed to create text content: {error_detail}'))
                    else:
                        error_detail = getattr(response, 'data', response.content)
                        self.stdout.write(self.style.ERROR(f'Failed to create module: {error_detail}'))
            else:
                error_detail = getattr(response, 'data', response.content)
                self.stdout.write(self.style.ERROR(f'Failed to create course: {error_detail}'))

        for enrollment_data in enrollments_data:
            response = client.post('/api/enrollments/', enrollment_data, format='json')
            if response.status_code == 201:
                self.stdout.write(self.style.SUCCESS(f'Created enrollment for student {enrollment_data["student"]}'))
            else:
                error_detail = getattr(response, 'data', response.content)
                self.stdout.write(self.style.ERROR(f'Failed to create enrollment: {error_detail}'))

        # After creating enrollments, simulate module progress and quiz attempts
        # Fetch all modules and quizzes for each course
        module_progress_statuses = ['not_started', 'in_progress', 'completed']
        quiz_attempt_statuses = ['in_progress', 'submitted', 'graded']
        for enrollment in enrollments_data:
            # For each enrollment, fetch modules for the course
            course_id = enrollment['course']
            student_id = enrollment['student']
            # Get modules for this course
            modules_response = client.get(f'/api/modules/?course_id={course_id}')
            if modules_response.status_code == 200:
                modules = modules_response.data['results'] if isinstance(modules_response.data, dict) and 'results' in modules_response.data else modules_response.data
                for module in modules:
                    # Create module progress
                    mp_payload = {
                        'enrollment': f'{student_id}-{course_id}',  # You may need to adjust this if your API expects a PK
                        'module': module['id'],
                        'status': choice(module_progress_statuses),
                        'progress': randint(0, 100)
                    }
                    client.post('/api/module-progress/', mp_payload, format='json')
                    # For each content in the module, if it's a quiz, create a quiz attempt
                    contents_response = client.get(f'/api/contents/?module_id={module["id"]}')
                    if contents_response.status_code == 200:
                        contents = contents_response.data['results'] if isinstance(contents_response.data, dict) and 'results' in contents_response.data else contents_response.data
                        for content in contents:
                            if content['content_type'] == 'quiz':
                                # Fetch the quiz object
                                quiz_response = client.get(f'/api/quizzes/?content_id={content["id"]}')
                                if quiz_response.status_code == 200 and quiz_response.data:
                                    quiz_obj = quiz_response.data[0] if isinstance(quiz_response.data, list) else quiz_response.data['results'][0]
                                    quiz_id = quiz_obj['id']
                                    qa_payload = {
                                        'student': student_id,
                                        'quiz': quiz_id,
                                        'status': choice(quiz_attempt_statuses),
                                        'score': randint(0, 100)
                                    }
                                    client.post('/api/quiz-attempts/', qa_payload, format='json')

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data via API'))

        # Update final user output to match actual demo users created
        self.stdout.write(self.style.SUCCESS('Test users created:'))
        self.stdout.write('------------------')
        self.stdout.write('Admin:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('')
        self.stdout.write('Course Coordinators:')
        self.stdout.write('  Username: coordinator1')
        self.stdout.write('  Password: coord123')
        self.stdout.write('  Username: coordinator2')
        self.stdout.write('  Password: password123')
        self.stdout.write('')
        self.stdout.write('Instructors:')
        self.stdout.write('  Username: instructor1')
        self.stdout.write('  Password: inst123')
        self.stdout.write('  Username: instructor2')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: instructor3')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: instructor4')
        self.stdout.write('  Password: password123')
        self.stdout.write('')
        self.stdout.write('Students:')
        self.stdout.write('  Username: student1')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: student2')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: student3')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: student4')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: student5')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: student6')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: student7')
        self.stdout.write('  Password: password123')
        self.stdout.write('  Username: student8')
        self.stdout.write('  Password: password123') 