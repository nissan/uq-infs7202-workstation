from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import CourseCategory, Course, CourseModule, CourseContent, CourseEnrollment
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Generates test data for courses and related models'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating test data...')

        # Create categories
        categories = [
            ('Web Development', 'Learn modern web development technologies and frameworks'),
            ('Data Science', 'Master data analysis, machine learning, and AI'),
            ('Mobile Development', 'Build mobile applications for iOS and Android'),
            ('DevOps', 'Learn about deployment, automation, and infrastructure'),
            ('Design', 'Master UI/UX design and graphic design principles'),
        ]

        created_categories = []
        for name, description in categories:
            category, created = CourseCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            created_categories.append(category)
            self.stdout.write(f'Created category: {name}')

        # Create instructor
        instructor, created = User.objects.get_or_create(
            username='instructor',
            defaults={
                'email': 'instructor@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_staff': True
            }
        )
        if created:
            instructor.set_password('instructor123')
            instructor.save()
            self.stdout.write('Created instructor account')

        # Create sample courses
        courses_data = [
            {
                'title': 'Complete Web Development Bootcamp',
                'description': 'Learn HTML, CSS, JavaScript, React, Node.js, and more in this comprehensive web development course.',
                'category': 'Web Development',
                'level': 'beginner',
                'price': 99.99,
                'max_students': 100,
                'is_featured': True,
            },
            {
                'title': 'Data Science with Python',
                'description': 'Master data analysis, visualization, and machine learning using Python and popular data science libraries.',
                'category': 'Data Science',
                'level': 'intermediate',
                'price': 149.99,
                'max_students': 50,
                'is_featured': True,
            },
            {
                'title': 'iOS App Development with Swift',
                'description': 'Learn to build professional iOS applications using Swift and SwiftUI.',
                'category': 'Mobile Development',
                'level': 'intermediate',
                'price': 129.99,
                'max_students': 75,
                'is_featured': False,
            },
            {
                'title': 'DevOps Engineering',
                'description': 'Master CI/CD, Docker, Kubernetes, and cloud infrastructure.',
                'category': 'DevOps',
                'level': 'advanced',
                'price': 199.99,
                'max_students': 30,
                'is_featured': True,
            },
            {
                'title': 'UI/UX Design Masterclass',
                'description': 'Learn modern UI/UX design principles, tools, and best practices.',
                'category': 'Design',
                'level': 'beginner',
                'price': 79.99,
                'max_students': 0,
                'is_featured': False,
            },
        ]

        # Create courses with modules and content
        for course_data in courses_data:
            category = CourseCategory.objects.get(name=course_data['category'])
            course = Course.objects.create(
                title=course_data['title'],
                description=course_data['description'],
                category=category,
                instructor=instructor,
                level=course_data['level'],
                price=course_data['price'],
                max_students=course_data['max_students'],
                is_featured=course_data['is_featured'],
                status='published',
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=365)
            )
            self.stdout.write(f'Created course: {course.title}')

            # Create modules for each course
            modules_data = [
                {
                    'title': 'Introduction',
                    'description': 'Get started with the course and learn the basics.',
                    'contents': [
                        {
                            'title': 'Welcome to the Course',
                            'content_type': 'text',
                            'content': 'Welcome to this comprehensive course! In this module, we\'ll cover the basics and set up your development environment.',
                            'estimated_time': 15
                        },
                        {
                            'title': 'Course Overview',
                            'content_type': 'text',
                            'content': 'This course will take you from beginner to professional. Here\'s what you\'ll learn...',
                            'estimated_time': 20
                        }
                    ]
                },
                {
                    'title': 'Getting Started',
                    'description': 'Set up your development environment and learn the fundamentals.',
                    'contents': [
                        {
                            'title': 'Installation Guide',
                            'content_type': 'text',
                            'content': 'Follow these steps to set up your development environment...',
                            'estimated_time': 30
                        },
                        {
                            'title': 'First Project',
                            'content_type': 'text',
                            'content': 'Let\'s create your first project and understand the basic concepts...',
                            'estimated_time': 45
                        }
                    ]
                },
                {
                    'title': 'Core Concepts',
                    'description': 'Learn the essential concepts and techniques.',
                    'contents': [
                        {
                            'title': 'Key Concepts',
                            'content_type': 'text',
                            'content': 'Understanding the core concepts is crucial for your success...',
                            'estimated_time': 60
                        },
                        {
                            'title': 'Best Practices',
                            'content_type': 'text',
                            'content': 'Learn the industry best practices and standards...',
                            'estimated_time': 45
                        }
                    ]
                },
                {
                    'title': 'Advanced Topics',
                    'description': 'Dive deep into advanced concepts and techniques.',
                    'contents': [
                        {
                            'title': 'Advanced Techniques',
                            'content_type': 'text',
                            'content': 'Now that you understand the basics, let\'s explore advanced techniques...',
                            'estimated_time': 90
                        },
                        {
                            'title': 'Real-world Applications',
                            'content_type': 'text',
                            'content': 'See how these concepts are applied in real-world scenarios...',
                            'estimated_time': 75
                        }
                    ]
                }
            ]

            # Create modules and content
            for order, module_data in enumerate(modules_data, 1):
                module = CourseModule.objects.create(
                    course=course,
                    title=module_data['title'],
                    description=module_data['description'],
                    order=order
                )
                self.stdout.write(f'Created module: {module.title}')

                # Create content for each module
                for content_order, content_data in enumerate(module_data['contents'], 1):
                    content = CourseContent.objects.create(
                        module=module,
                        title=content_data['title'],
                        content_type=content_data['content_type'],
                        content=content_data['content'],
                        order=content_order,
                        estimated_time=content_data['estimated_time']
                    )
                    self.stdout.write(f'Created content: {content.title}')

        self.stdout.write(self.style.SUCCESS('Successfully generated test data')) 