from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import (
    CourseCategory, Course, Module, CourseContent,
    CourseEnrollment, Quiz, Question, Choice
)
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Generates test data for courses and related models'

    def create_quiz(self, content, title, description, is_pre_check=False):
        """Helper function to create a quiz with sample questions"""
        quiz = Quiz.objects.create(
            content=content,
            title=title,
            description=description,
            is_pre_check=is_pre_check,
            passing_score=70 if not is_pre_check else 0,
            time_limit=30 if is_pre_check else 60,
            attempts_allowed=3 if is_pre_check else 2,
            shuffle_questions=True,
            show_correct_answers=True
        )

        # Create questions based on quiz type
        if is_pre_check:
            # Pre-knowledge check questions
            questions_data = [
                {
                    'text': 'What is your current experience level with web development?',
                    'type': 'multiple_choice',
                    'points': 1,
                    'choices': [
                        ('Complete beginner', False),
                        ('Some basic knowledge', False),
                        ('Intermediate level', False),
                        ('Advanced level', False)
                    ]
                },
                {
                    'text': 'Have you taken any web development courses before?',
                    'type': 'true_false',
                    'points': 1,
                    'choices': [
                        ('Yes', False),
                        ('No', False)
                    ]
                },
                {
                    'text': 'What programming languages are you familiar with?',
                    'type': 'multiple_choice',
                    'points': 1,
                    'choices': [
                        ('None', False),
                        ('HTML/CSS only', False),
                        ('JavaScript', False),
                        ('Multiple languages', False)
                    ]
                },
                {
                    'text': 'What are your main learning goals for this course?',
                    'type': 'essay',
                    'points': 2,
                    'choices': []
                },
                {
                    'text': 'How much time can you dedicate to this course per week?',
                    'type': 'multiple_choice',
                    'points': 1,
                    'choices': [
                        ('Less than 5 hours', False),
                        ('5-10 hours', False),
                        ('10-15 hours', False),
                        ('More than 15 hours', False)
                    ]
                }
            ]
        else:
            # Knowledge check quiz questions
            questions_data = [
                {
                    'text': 'Which of the following is NOT a valid HTML5 semantic element?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        ('<header>', False),
                        ('<nav>', False),
                        ('<content>', True),
                        ('<footer>', False)
                    ]
                },
                {
                    'text': 'CSS Grid and Flexbox are mutually exclusive layout systems.',
                    'type': 'true_false',
                    'points': 1,
                    'choices': [
                        ('True', False),
                        ('False', True)
                    ]
                },
                {
                    'text': 'Which JavaScript framework uses a virtual DOM for efficient rendering?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        ('Angular', False),
                        ('React', True),
                        ('Vue', False),
                        ('jQuery', False)
                    ]
                },
                {
                    'text': 'REST APIs must always return data in JSON format.',
                    'type': 'true_false',
                    'points': 1,
                    'choices': [
                        ('True', False),
                        ('False', True)
                    ]
                },
                {
                    'text': 'Explain the difference between let, const, and var in JavaScript.',
                    'type': 'essay',
                    'points': 3,
                    'choices': []
                }
            ]

        # Create questions and choices
        for order, q_data in enumerate(questions_data, 1):
            question = Question.objects.create(
                quiz=quiz,
                question_text=q_data['text'],
                question_type=q_data['type'],
                points=q_data['points'],
                order=order
            )

            for choice_order, (choice_text, is_correct) in enumerate(q_data['choices'], 1):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct,
                    order=choice_order
                )

        return quiz

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
                    'title': 'Course Introduction',
                    'description': 'Get started with the course and assess your current knowledge.',
                    'estimated_time': 45,  # 15 min welcome + 30 min pre-check
                    'contents': [
                        {
                            'title': 'Welcome to the Course',
                            'content_type': 'text',
                            'content': 'Welcome to this comprehensive course! In this module, we\'ll cover the basics and set up your development environment.',
                            'estimated_time': 15
                        },
                        {
                            'title': 'Pre-Knowledge Check',
                            'content_type': 'quiz',
                            'content': 'Take this quiz to assess your current knowledge and help us personalize your learning experience.',
                            'estimated_time': 30,
                            'is_pre_check': True
                        }
                    ]
                },
                {
                    'title': 'Getting Started',
                    'description': 'Set up your development environment and learn the fundamentals.',
                    'estimated_time': 75,  # 30 min installation + 45 min first project
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
                    'estimated_time': 105,  # 60 min concepts + 45 min quiz
                    'contents': [
                        {
                            'title': 'Key Concepts',
                            'content_type': 'text',
                            'content': 'Understanding the core concepts is crucial for your success...',
                            'estimated_time': 60
                        },
                        {
                            'title': 'Core Concepts Quiz',
                            'content_type': 'quiz',
                            'content': 'Test your understanding of the core concepts covered in this module.',
                            'estimated_time': 45,
                            'is_pre_check': False
                        }
                    ]
                },
                {
                    'title': 'Advanced Topics',
                    'description': 'Dive deep into advanced concepts and techniques.',
                    'estimated_time': 150,  # 90 min techniques + 60 min final assessment
                    'contents': [
                        {
                            'title': 'Advanced Techniques',
                            'content_type': 'text',
                            'content': 'Now that you understand the basics, let\'s explore advanced techniques...',
                            'estimated_time': 90
                        },
                        {
                            'title': 'Final Assessment',
                            'content_type': 'quiz',
                            'content': 'Comprehensive quiz covering all the advanced topics in this module.',
                            'estimated_time': 60,
                            'is_pre_check': False
                        }
                    ]
                }
            ]

            # Create modules and content
            for order, module_data in enumerate(modules_data, 1):
                module = Module.objects.create(
                    course=course,
                    title=module_data['title'],
                    description=module_data['description'],
                    order=order,
                    estimated_time=module_data['estimated_time']
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

                    # Create quiz if content type is quiz
                    if content_data['content_type'] == 'quiz':
                        is_pre_check = content_data.get('is_pre_check', False)
                        quiz = self.create_quiz(
                            content=content,
                            title=content_data['title'],
                            description=content_data['content'],
                            is_pre_check=is_pre_check
                        )
                        self.stdout.write(f'Created quiz: {quiz.title}')

        self.stdout.write(self.style.SUCCESS('Successfully generated test data')) 