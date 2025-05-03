from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.courses.models import Course, CourseCategory, CourseModule, CourseContent
from django.utils.text import slugify
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample course data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding course data...')

        # Create categories
        categories = [
            'Web Development',
            'Data Science',
            'Mobile Development',
            'Design',
            'Business',
            'Marketing',
        ]

        created_categories = []
        for category_name in categories:
            category, created = CourseCategory.objects.get_or_create(
                name=category_name,
                defaults={
                    'description': f'Learn everything about {category_name}',
                }
            )
            created_categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category_name}')

        # Create an instructor if none exists
        instructor, created = User.objects.get_or_create(
            username='instructor',
            defaults={
                'email': 'instructor@example.com',
                'is_staff': True,
            }
        )
        if created:
            instructor.set_password('instructor123')
            instructor.save()
            self.stdout.write('Created instructor user')

        # Sample course data
        courses_data = [
            {
                'title': 'Introduction to Python Programming',
                'description': 'Learn Python from scratch. This course covers basic syntax, data structures, and object-oriented programming.',
                'price': 49.99,
                'level': 'beginner',
                'category': 'Web Development',
            },
            {
                'title': 'Advanced Data Analysis with Python',
                'description': 'Master data analysis using Python. Learn pandas, numpy, and data visualization techniques.',
                'price': 79.99,
                'level': 'intermediate',
                'category': 'Data Science',
            },
            {
                'title': 'Mobile App Development with React Native',
                'description': 'Build cross-platform mobile apps using React Native. Learn to create iOS and Android apps with one codebase.',
                'price': 69.99,
                'level': 'intermediate',
                'category': 'Mobile Development',
            },
            {
                'title': 'UI/UX Design Fundamentals',
                'description': 'Learn the principles of user interface and user experience design. Create beautiful and functional designs.',
                'price': 59.99,
                'level': 'beginner',
                'category': 'Design',
            },
            {
                'title': 'Digital Marketing Masterclass',
                'description': 'Comprehensive guide to digital marketing. Learn SEO, social media marketing, and content strategy.',
                'price': 89.99,
                'level': 'intermediate',
                'category': 'Marketing',
            },
            {
                'title': 'Business Analytics Essentials',
                'description': 'Learn to make data-driven business decisions. Master Excel, SQL, and basic statistics.',
                'price': 0,
                'level': 'beginner',
                'category': 'Business',
            },
        ]

        # Create courses
        for course_data in courses_data:
            category = CourseCategory.objects.get(name=course_data['category'])
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    'slug': slugify(course_data['title']),
                    'description': course_data['description'],
                    'price': course_data['price'],
                    'level': course_data['level'],
                    'category': category,
                    'instructor': instructor,
                    'status': 'published',
                }
            )
            
            if created:
                self.stdout.write(f'Created course: {course.title}')
                
                # Create modules and content for each course
                modules = [
                    {
                        'title': 'Getting Started',
                        'description': 'Introduction to the course and setup instructions',
                        'order': 1,
                        'contents': [
                            {
                                'title': 'Welcome to the Course',
                                'content_type': 'video',
                                'estimated_time': 10,
                                'order': 1,
                            },
                            {
                                'title': 'Course Overview',
                                'content_type': 'text',
                                'estimated_time': 15,
                                'order': 2,
                            },
                        ]
                    },
                    {
                        'title': 'Core Concepts',
                        'description': 'Learn the fundamental concepts',
                        'order': 2,
                        'contents': [
                            {
                                'title': 'Key Concepts Explained',
                                'content_type': 'video',
                                'estimated_time': 20,
                                'order': 1,
                            },
                            {
                                'title': 'Practice Exercise',
                                'content_type': 'quiz',
                                'estimated_time': 30,
                                'order': 2,
                            },
                        ]
                    },
                ]

                for module_data in modules:
                    module = CourseModule.objects.create(
                        course=course,
                        title=module_data['title'],
                        description=module_data['description'],
                        order=module_data['order']
                    )
                    
                    for content_data in module_data['contents']:
                        CourseContent.objects.create(
                            module=module,
                            title=content_data['title'],
                            content_type=content_data['content_type'],
                            estimated_time=content_data['estimated_time'],
                            order=content_data['order']
                        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded course data')) 