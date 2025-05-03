from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db import transaction
from django.urls import reverse
from apps.courses.models import Category, Course, Module, Content
from apps.qr_codes.services import QRCodeService
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with demo data using Django ORM'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed demo data...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create coordinator user
        coordinator_user, created = User.objects.get_or_create(
            username='coordinator',
            defaults={
                'email': 'coordinator@example.com',
                'is_staff': True
            }
        )
        if created:
            coordinator_user.set_password('coordinator123')
            coordinator_user.save()
            self.stdout.write(self.style.SUCCESS('Created coordinator user'))
        
        # Create instructor users
        instructors = [
            {
                'username': 'dr.smith',
                'email': 'dr.smith@example.com',
                'password': 'dr.smith123',
                'first_name': 'John',
                'last_name': 'Smith'
            },
            {
                'username': 'dr.johnson',
                'email': 'dr.johnson@example.com',
                'password': 'dr.johnson123',
                'first_name': 'Sarah',
                'last_name': 'Johnson'
            },
            {
                'username': 'prof.williams',
                'email': 'prof.williams@example.com',
                'password': 'prof.williams123',
                'first_name': 'Michael',
                'last_name': 'Williams'
            }
        ]
        
        for instructor_data in instructors:
            instructor, created = User.objects.get_or_create(
                username=instructor_data['username'],
                defaults={
                    'email': instructor_data['email'],
                    'first_name': instructor_data['first_name'],
                    'last_name': instructor_data['last_name']
                }
            )
            if created:
                instructor.set_password(instructor_data['password'])
                instructor.save()
                self.stdout.write(self.style.SUCCESS(f'Created instructor: {instructor.get_full_name()}'))
        
        # Create student users
        students = [
            {
                'username': 'john.doe',
                'email': 'john@example.com',
                'password': 'john.doe123',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'username': 'jane.smith',
                'email': 'jane@example.com',
                'password': 'jane.smith123',
                'first_name': 'Jane',
                'last_name': 'Smith'
            },
            {
                'username': 'bob.wilson',
                'email': 'bob@example.com',
                'password': 'bob.wilson123',
                'first_name': 'Bob',
                'last_name': 'Wilson'
            },
            {
                'username': 'alice.johnson',
                'email': 'alice@example.com',
                'password': 'alice.johnson123',
                'first_name': 'Alice',
                'last_name': 'Johnson'
            }
        ]
        
        for student_data in students:
            student, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name']
                }
            )
            if created:
                student.set_password(student_data['password'])
                student.save()
                self.stdout.write(self.style.SUCCESS(f'Created student: {student.get_full_name()}'))
        
        # Create categories
        categories_data = [
            {
                'name': 'Programming',
                'description': 'Learn programming languages and software development',
            },
            {
                'name': 'Data Science',
                'description': 'Explore data analysis, machine learning, and statistics',
            },
            {
                'name': 'Web Development',
                'description': 'Build modern web applications and websites',
            },
            {
                'name': 'Mobile Development',
                'description': 'Create mobile applications for iOS and Android',
            },
            {
                'name': 'Database Management',
                'description': 'Learn database design, implementation, and management',
            },
        ]
        
        categories = {}
        for category_data in categories_data:
            self.stdout.write(f'Attempting to create category: {category_data["name"]}')
            try:
                with transaction.atomic():
                    # Generate a unique slug
                    base_slug = slugify(category_data['name'])
                    slug = base_slug
                    counter = 1
                    max_attempts = 5
                    
                    while counter <= max_attempts:
                        try:
                            category = Category.objects.create(
                                name=category_data['name'],
                                description=category_data['description'],
                                slug=slug
                            )
                            categories[category_data['name']] = category.id
                            self.stdout.write(self.style.SUCCESS(f'Created category: {category_data["name"]}'))
                            break
                        except Exception as e:
                            if 'UNIQUE constraint failed' in str(e) or 'already exists' in str(e):
                                self.stdout.write(f'Slug {slug} already exists, trying with counter {counter}')
                                slug = f"{base_slug}-{counter}"
                                counter += 1
                            else:
                                raise
                    
                    if counter > max_attempts:
                        self.stdout.write(self.style.ERROR(f'Failed to create category {category_data["name"]} after {max_attempts} attempts'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating category {category_data["name"]}: {str(e)}'))
        
        # Verify all categories were created
        if len(categories) != len(categories_data):
            self.stdout.write(self.style.ERROR(f'Not all categories were created successfully. Created {len(categories)} out of {len(categories_data)} categories.'))
            return
        
        self.stdout.write(self.style.SUCCESS('All categories created successfully'))
        
        # Create courses
        courses_data = [
            {
                'title': 'Introduction to Python Programming',
                'description': 'Learn Python from scratch. This course covers basic syntax, data structures, and object-oriented programming.',
                'category': 'Programming',
                'status': 'published',
                'max_students': 50,
                'modules': [
                    {
                        'title': 'Getting Started with Python',
                        'description': 'Introduction to Python programming language',
                        'order': 1,
                        'contents': [
                            {
                                'title': 'Python Installation',
                                'content_type': 'text',
                                'content': 'Learn how to install Python on your system',
                                'estimated_time': 15,
                                'order': 1,
                            },
                            {
                                'title': 'First Python Program',
                                'content_type': 'text',
                                'content': 'Write your first Python program',
                                'estimated_time': 30,
                                'order': 2,
                            },
                            {
                                'title': 'Python Basics Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your understanding of Python basics',
                                'estimated_time': 20,
                                'order': 3,
                                'is_prerequisite': True,
                                'is_pre_check': True,
                            },
                        ]
                    },
                    {
                        'title': 'Python Data Structures',
                        'description': 'Learn about Python data structures and algorithms',
                        'order': 2,
                        'contents': [
                            {
                                'title': 'Lists and Tuples',
                                'content_type': 'text',
                                'content': 'Understanding Python lists and tuples',
                                'estimated_time': 45,
                                'order': 1,
                            },
                            {
                                'title': 'Data Structures Video',
                                'content_type': 'video',
                                'content': 'https://example.com/videos/python-data-structures',
                                'estimated_time': 60,
                                'order': 2,
                            },
                            {
                                'title': 'Data Structures Assignment',
                                'content_type': 'assignment',
                                'content': 'Implement a custom data structure in Python',
                                'estimated_time': 120,
                                'order': 3,
                            },
                        ]
                    }
                ]
            },
            {
                'title': 'Web Development with Django',
                'description': 'Build web applications using Django framework',
                'category': 'Web Development',
                'status': 'published',
                'max_students': 30,
                'modules': [
                    {
                        'title': 'Introduction to Django',
                        'description': 'Learn the basics of Django framework',
                        'order': 1,
                        'contents': [
                            {
                                'title': 'Django Installation',
                                'content_type': 'text',
                                'content': 'Set up your Django development environment',
                                'estimated_time': 20,
                                'order': 1,
                            },
                            {
                                'title': 'Creating Your First Django Project',
                                'content_type': 'text',
                                'content': 'Learn how to create and structure a Django project',
                                'estimated_time': 45,
                                'order': 2,
                            },
                            {
                                'title': 'Django Basics Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your understanding of Django basics',
                                'estimated_time': 30,
                                'order': 3,
                                'is_prerequisite': True,
                            },
                        ]
                    }
                ]
            },
            {
                'title': 'Advanced Data Science',
                'description': 'Advanced topics in data science and machine learning',
                'category': 'Data Science',
                'status': 'draft',
                'max_students': 20,
                'modules': [
                    {
                        'title': 'Machine Learning Fundamentals',
                        'description': 'Introduction to machine learning concepts',
                        'order': 1,
                        'contents': [
                            {
                                'title': 'ML Concepts',
                                'content_type': 'text',
                                'content': 'Understanding basic machine learning concepts',
                                'estimated_time': 60,
                                'order': 1,
                            },
                            {
                                'title': 'ML Video Lecture',
                                'content_type': 'video',
                                'content': 'https://example.com/videos/ml-fundamentals',
                                'estimated_time': 90,
                                'order': 2,
                            },
                            {
                                'title': 'ML Assignment',
                                'content_type': 'assignment',
                                'content': 'Implement a simple ML algorithm',
                                'estimated_time': 180,
                                'order': 3,
                            },
                        ]
                    }
                ]
            },
            {
                'title': 'Mobile App Development',
                'description': 'Learn to build mobile applications for iOS and Android',
                'category': 'Mobile Development',
                'status': 'archived',
                'max_students': 25,
                'modules': [
                    {
                        'title': 'Mobile Development Basics',
                        'description': 'Introduction to mobile app development',
                        'order': 1,
                        'contents': [
                            {
                                'title': 'Mobile Platforms',
                                'content_type': 'text',
                                'content': 'Overview of iOS and Android platforms',
                                'estimated_time': 30,
                                'order': 1,
                            },
                            {
                                'title': 'Development Tools',
                                'content_type': 'text',
                                'content': 'Setting up your mobile development environment',
                                'estimated_time': 45,
                                'order': 2,
                            },
                            {
                                'title': 'Mobile Development Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your knowledge of mobile development basics',
                                'estimated_time': 20,
                                'order': 3,
                                'is_pre_check': True,
                            },
                        ]
                    }
                ]
            }
        ]
        
        for course_data in courses_data:
            try:
                with transaction.atomic():
                    # Generate a unique slug
                    base_slug = slugify(course_data['title'])
                    slug = base_slug
                    counter = 1
                    max_attempts = 5
                    
                    while counter <= max_attempts:
                        try:
                            course = Course.objects.create(
                                title=course_data['title'],
                                description=course_data['description'],
                                category_id=categories[course_data['category']],
                                status=course_data['status'],
                                max_students=course_data['max_students'],
                                slug=slug,
                                start_date=timezone.now().date(),
                                end_date=(timezone.now() + timedelta(days=90)).date(),
                            )
                            self.stdout.write(self.style.SUCCESS(f'Created course: {course_data["title"]}'))
                            
                            # Create modules and contents
                            for module_data in course_data['modules']:
                                module = Module.objects.create(
                                    course=course,
                                    title=module_data['title'],
                                    description=module_data['description'],
                                    order=module_data['order']
                                )
                                self.stdout.write(self.style.SUCCESS(f'Created module: {module_data["title"]}'))
                                
                                for content_data in module_data['contents']:
                                    content = Content.objects.create(
                                        module=module,
                                        title=content_data['title'],
                                        content_type=content_data['content_type'],
                                        content=content_data['content'],
                                        estimated_time=content_data['estimated_time'],
                                        order=content_data['order']
                                    )
                                    self.stdout.write(self.style.SUCCESS(f'Created content: {content_data["title"]}'))
                            break
                        except Exception as e:
                            if 'UNIQUE constraint failed' in str(e) or 'already exists' in str(e):
                                self.stdout.write(f'Slug {slug} already exists, trying with counter {counter}')
                                slug = f"{base_slug}-{counter}"
                                counter += 1
                            else:
                                raise
                    
                    if counter > max_attempts:
                        self.stdout.write(self.style.ERROR(f'Failed to create course {course_data["title"]} after {max_attempts} attempts'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating course {course_data["title"]}: {str(e)}'))

        # Generate QR codes for all courses and modules
        self.stdout.write(self.style.WARNING('Generating QR codes for courses and modules...'))
        
        for course in Course.objects.all():
            # Generate course QR code
            course_url = f'/courses/course/{course.slug}/'
            QRCodeService.get_or_create_qr_code(course, course_url)
            self.stdout.write(f'Generated QR code for course: {course.title}')
            
            # Generate module QR codes
            for module in course.modules.all():
                module_url = f'/courses/course/{course.slug}/module/{module.order}/'
                QRCodeService.get_or_create_qr_code(module, module_url)
                self.stdout.write(f'Generated QR code for module: {module.title}')
        
        self.stdout.write(self.style.SUCCESS('QR codes generated successfully'))

        self.stdout.write(self.style.SUCCESS('Demo data seeding completed!')) 