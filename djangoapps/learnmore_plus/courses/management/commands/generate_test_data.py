from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import Category, Course, Module, Content, Quiz, Question, Choice, CourseEnrollment
from django.contrib.auth.models import Group
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate test data for courses'

    def create_quiz(self, content, title, description, is_prerequisite=False):
        quiz = Quiz.objects.create(
            content=content,
            title=title,
            description=description,
            passing_score=70,
            time_limit=30,
            is_prerequisite=is_prerequisite
        )
        self.stdout.write(f'Created quiz: {quiz.title}')

        # Create questions
        questions = [
            {
                'text': 'What is the main purpose of this topic?',
                'type': 'multiple_choice',
                'choices': [
                    {'text': 'Correct answer', 'is_correct': True},
                    {'text': 'Wrong answer 1', 'is_correct': False},
                    {'text': 'Wrong answer 2', 'is_correct': False},
                    {'text': 'Wrong answer 3', 'is_correct': False},
                ]
            },
            {
                'text': 'Which of these is NOT a key concept?',
                'type': 'multiple_choice',
                'choices': [
                    {'text': 'Wrong answer 1', 'is_correct': False},
                    {'text': 'Correct answer', 'is_correct': True},
                    {'text': 'Wrong answer 2', 'is_correct': False},
                    {'text': 'Wrong answer 3', 'is_correct': False},
                ]
            },
            {
                'text': 'What is the correct sequence of steps?',
                'type': 'multiple_choice',
                'choices': [
                    {'text': 'Correct sequence', 'is_correct': True},
                    {'text': 'Wrong sequence 1', 'is_correct': False},
                    {'text': 'Wrong sequence 2', 'is_correct': False},
                    {'text': 'Wrong sequence 3', 'is_correct': False},
                ]
            },
        ]

        for question_data in questions:
            question = Question.objects.create(
                quiz=quiz,
                question_text=question_data['text'],
                question_type=question_data['type'],
                points=1,
            )
            self.stdout.write(f'Created question: {question.question_text}')

            # Create choices
            for choice_data in question_data['choices']:
                Choice.objects.create(
                    question=question,
                    choice_text=choice_data['text'],
                    is_correct=choice_data['is_correct'],
                )
                self.stdout.write(f'Created choice: {choice_data["text"]}')

        return quiz

    def handle(self, *args, **kwargs):
        # Create test users
        test_users = [
            {"username": "admin", "email": "admin@example.com", "password": "admin123", "group": "Administrator"},
            {"username": "coordinator", "email": "coordinator@example.com", "password": "coordinator123", "group": "Course Coordinator"},
            {"username": "instructor", "email": "instructor@example.com", "password": "instructor123", "group": "Instructor"},
            {"username": "student", "email": "student@example.com", "password": "student123", "group": "Student"},
        ]

        for user_info in test_users:
            user, created = User.objects.get_or_create(username=user_info["username"], defaults={
                "email": user_info["email"]
            })
            if created:
                user.set_password(user_info["password"])
                user.save()
            group, _ = Group.objects.get_or_create(name=user_info["group"])
            user.groups.add(group)
            user.save()

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

        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'slug': category_data['name'].lower().replace(' ', '-'),
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Get instructor user for course creation
        instructor = User.objects.get(username='instructor')
        student = User.objects.get(username='student')

        # Create courses
        courses_data = [
            {
                'title': 'Python Programming',
                'description': 'Learn Python programming from scratch. This course covers basic syntax, data structures, and object-oriented programming.',
                'category': 'Programming',
                'status': 'published',
                'max_students': 50,
                'modules': [
                    {
                        'title': 'Getting Started with Python',
                        'description': 'Introduction to Python and basic concepts',
                        'contents': [
                            {
                                'title': 'Prerequisite Knowledge Check',
                                'content_type': 'quiz',
                                'content': 'Test your basic programming knowledge',
                                'estimated_time': 20,
                                'is_prerequisite': True,
                            },
                            {
                                'title': 'Introduction to Python',
                                'content_type': 'text',
                                'content': 'Python is a high-level, interpreted programming language...',
                                'estimated_time': 30,
                            },
                            {
                                'title': 'Setting Up Your Environment',
                                'content_type': 'video',
                                'content': 'Learn how to set up Python and your development environment...',
                                'estimated_time': 45,
                            },
                            {
                                'title': 'Basic Syntax Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your understanding of Python basics',
                                'estimated_time': 20,
                                'is_prerequisite': False,
                            },
                        ]
                    },
                    {
                        'title': 'Data Structures',
                        'description': 'Learn about Python data structures',
                        'contents': [
                            {
                                'title': 'Lists and Tuples',
                                'content_type': 'text',
                                'content': 'Understanding Python lists and tuples...',
                                'estimated_time': 40,
                            },
                            {
                                'title': 'Dictionaries and Sets',
                                'content_type': 'video',
                                'content': 'Working with dictionaries and sets in Python...',
                                'estimated_time': 35,
                            },
                            {
                                'title': 'Data Structures Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your knowledge of Python data structures',
                                'estimated_time': 25,
                                'is_prerequisite': False,
                            },
                        ]
                    },
                    {
                        'title': 'Object-Oriented Programming',
                        'description': 'Learn OOP concepts in Python',
                        'contents': [
                            {
                                'title': 'Classes and Objects',
                                'content_type': 'text',
                                'content': 'Understanding classes and objects in Python...',
                                'estimated_time': 45,
                            },
                            {
                                'title': 'Inheritance and Polymorphism',
                                'content_type': 'video',
                                'content': 'Advanced OOP concepts in Python...',
                                'estimated_time': 50,
                            },
                            {
                                'title': 'OOP Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your OOP knowledge',
                                'estimated_time': 30,
                                'is_prerequisite': False,
                            },
                        ]
                    },
                ]
            },
            {
                'title': 'Full Stack Development',
                'description': 'Build web applications with modern technologies. Learn frontend and backend development.',
                'category': 'Web Development',
                'status': 'published',
                'max_students': 30,
                'modules': [
                    {
                        'title': 'Frontend Fundamentals',
                        'description': 'Learn HTML, CSS, and JavaScript basics',
                        'contents': [
                            {
                                'title': 'Prerequisite Knowledge Check',
                                'content_type': 'quiz',
                                'content': 'Test your basic web knowledge',
                                'estimated_time': 20,
                                'is_prerequisite': True,
                            },
                            {
                                'title': 'HTML5 Essentials',
                                'content_type': 'text',
                                'content': 'Learn the fundamentals of HTML5...',
                                'estimated_time': 45,
                            },
                            {
                                'title': 'CSS Styling',
                                'content_type': 'video',
                                'content': 'Master CSS styling and layouts...',
                                'estimated_time': 60,
                            },
                            {
                                'title': 'JavaScript Basics',
                                'content_type': 'text',
                                'content': 'Introduction to JavaScript programming...',
                                'estimated_time': 50,
                            },
                            {
                                'title': 'Frontend Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your frontend knowledge',
                                'estimated_time': 30,
                                'is_prerequisite': False,
                            },
                        ]
                    },
                    {
                        'title': 'Backend Development',
                        'description': 'Learn server-side programming',
                        'contents': [
                            {
                                'title': 'Introduction to Django',
                                'content_type': 'text',
                                'content': 'Learn Django framework basics...',
                                'estimated_time': 55,
                            },
                            {
                                'title': 'Database Design',
                                'content_type': 'video',
                                'content': 'Understanding database design and relationships...',
                                'estimated_time': 40,
                            },
                            {
                                'title': 'API Development',
                                'content_type': 'text',
                                'content': 'Building RESTful APIs with Django...',
                                'estimated_time': 45,
                            },
                            {
                                'title': 'Backend Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your backend knowledge',
                                'estimated_time': 35,
                                'is_prerequisite': False,
                            },
                        ]
                    },
                    {
                        'title': 'Full Stack Integration',
                        'description': 'Combine frontend and backend technologies',
                        'contents': [
                            {
                                'title': 'API Integration',
                                'content_type': 'text',
                                'content': 'Connecting frontend with backend APIs...',
                                'estimated_time': 50,
                            },
                            {
                                'title': 'Authentication and Authorization',
                                'content_type': 'video',
                                'content': 'Implementing secure user authentication...',
                                'estimated_time': 45,
                            },
                            {
                                'title': 'Final Project Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your full stack knowledge',
                                'estimated_time': 40,
                                'is_prerequisite': False,
                            },
                        ]
                    },
                ]
            },
            {
                'title': 'Machine Learning Fundamentals',
                'description': 'Introduction to machine learning concepts and algorithms.',
                'category': 'Data Science',
                'status': 'published',
                'max_students': 40,
                'modules': [
                    {
                        'title': 'Introduction to Machine Learning',
                        'description': 'Basic concepts and terminology',
                        'contents': [
                            {
                                'title': 'Prerequisite Knowledge Check',
                                'content_type': 'quiz',
                                'content': 'Test your basic statistics and programming knowledge',
                                'estimated_time': 25,
                                'is_prerequisite': True,
                            },
                            {
                                'title': 'What is Machine Learning?',
                                'content_type': 'text',
                                'content': 'Understanding the basics of machine learning...',
                                'estimated_time': 40,
                            },
                            {
                                'title': 'Types of Machine Learning',
                                'content_type': 'video',
                                'content': 'Supervised, unsupervised, and reinforcement learning...',
                                'estimated_time': 50,
                            },
                            {
                                'title': 'ML Basics Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your understanding of ML concepts',
                                'estimated_time': 30,
                                'is_prerequisite': False,
                            },
                        ]
                    },
                    {
                        'title': 'Data Preprocessing',
                        'description': 'Prepare data for machine learning',
                        'contents': [
                            {
                                'title': 'Data Cleaning',
                                'content_type': 'text',
                                'content': 'Techniques for cleaning and preparing data...',
                                'estimated_time': 45,
                            },
                            {
                                'title': 'Feature Engineering',
                                'content_type': 'video',
                                'content': 'Creating and selecting features for ML models...',
                                'estimated_time': 55,
                            },
                            {
                                'title': 'Data Preprocessing Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your data preprocessing knowledge',
                                'estimated_time': 35,
                                'is_prerequisite': False,
                            },
                        ]
                    },
                ]
            },
        ]

        for course_data in courses_data:
            category = Category.objects.get(name=course_data['category'])
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    'description': course_data['description'],
                    'category': category,
                    'status': course_data['status'],
                    'max_students': course_data['max_students'],
                    'slug': course_data['title'].lower().replace(' ', '-'),
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + timedelta(days=90)).date(),
                }
            )
            
            if created:
                course.instructors.add(instructor)
                self.stdout.write(f'Created course: {course.title}')

                # Create modules and content
                for module_index, module_data in enumerate(course_data['modules'], 1):
                    module = Module.objects.create(
                        course=course,
                        title=module_data['title'],
                        description=module_data['description'],
                        order=module_index,
                    )
                    self.stdout.write(f'Created module: {module.title}')

                    # Create content
                    for content_index, content_data in enumerate(module_data['contents'], 1):
                        content = Content.objects.create(
                            module=module,
                            title=content_data['title'],
                            content_type=content_data['content_type'],
                            content=content_data['content'],
                            estimated_time=content_data['estimated_time'],
                            order=content_index,
                        )
                        self.stdout.write(f'Created content: {content.title}')

                        # Create quiz if content type is quiz
                        if content_data['content_type'] == 'quiz':
                            quiz_title = f"{'Prerequisite: ' if content_data.get('is_prerequisite', False) else ''}{content.title}"
                            quiz_description = f"{'Prerequisite knowledge check: ' if content_data.get('is_prerequisite', False) else 'Knowledge check: '}{content_data['content']}"
                            self.create_quiz(
                                content=content,
                                title=quiz_title,
                                description=quiz_description,
                                is_prerequisite=content_data.get('is_prerequisite', False)
                            )

                # Create some enrollments for the student
                if random.random() < 0.7:  # 70% chance to enroll in each course
                    enrollment = CourseEnrollment.objects.create(
                        student=student,
                        course=course,
                        status='active',
                        enrolled_at=timezone.now()
                    )
                    self.stdout.write(f'Enrolled student in course: {course.title}')

        self.stdout.write(self.style.SUCCESS('Successfully generated test data')) 