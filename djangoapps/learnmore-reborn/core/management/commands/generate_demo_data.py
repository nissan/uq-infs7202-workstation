#!/usr/bin/env python
import os
import django
import random
import uuid
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from courses.models import (
    Course, Module, Quiz, Question, MultipleChoiceQuestion, 
    TrueFalseQuestion, EssayQuestion, Choice, Enrollment, 
    QuizAttempt, QuestionResponse, ScoringRubric, RubricCriterion,
    QuizPrerequisite
)
from users.models import UserProfile
from progress.models import Progress, ModuleProgress
from analytics.models import (
    UserActivity, CourseAnalytics, UserAnalytics,
    LearnerAnalytics, ModuleEngagement
)
from qr_codes.models import QRCode, QRCodeBatch

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate comprehensive demo data showing all platform features'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of student users to create'
        )
        parser.add_argument(
            '--instructors',
            type=int,
            default=5,
            help='Number of instructor users to create'
        )
        parser.add_argument(
            '--courses',
            type=int,
            default=8,
            help='Number of courses to create'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing data before creating new demo data'
        )
        parser.add_argument(
            '--no-progress',
            action='store_true',
            help='Skip generating user progress data'
        )
        parser.add_argument(
            '--no-analytics',
            action='store_true',
            help='Skip generating analytics data'
        )

    def handle(self, *args, **options):
        num_students = options['users']
        num_instructors = options['instructors']
        num_courses = options['courses']
        clean_data = options['clean']
        skip_progress = options['no_progress']
        skip_analytics = options['no_analytics']
        
        if clean_data:
            self.clean_existing_data()
            
        self.stdout.write(self.style.SUCCESS(f"Starting demo data generation with {num_students} students, {num_instructors} instructors, and {num_courses} courses"))
        
        # Create users first
        admin_user = self.create_admin_user()
        instructors = self.create_instructors(num_instructors)
        students = self.create_students(num_students)
        
        # Create courses and related content
        courses = self.create_courses(num_courses, instructors)
        
        # Create enrollments
        self.create_enrollments(students, courses)
        
        # Generate user progress if not skipped
        if not skip_progress:
            self.generate_user_progress(students, courses)
        
        # Generate analytics data if not skipped
        if not skip_analytics:
            self.generate_analytics_data(students, courses)
        
        # Generate QR codes for courses and modules
        self.generate_qr_codes(courses, admin_user)
        
        self.stdout.write(self.style.SUCCESS('Demo data generation complete!'))
        
        # Print summary
        self.print_summary(students, instructors, courses)

    def clean_existing_data(self):
        """Clean existing demo data before creating new data"""
        self.stdout.write(self.style.WARNING('Cleaning existing demo data...'))
        
        # Get users with demo emails
        demo_users = User.objects.filter(email__contains='demo@')
        user_ids = list(demo_users.values_list('id', flat=True))
        
        # Delete related data 
        Progress.objects.filter(user_id__in=user_ids).delete()
        Enrollment.objects.filter(user_id__in=user_ids).delete()
        QuizAttempt.objects.filter(user_id__in=user_ids).delete()
        UserActivity.objects.filter(user_id__in=user_ids).delete()
        ModuleEngagement.objects.filter(user_id__in=user_ids).delete()
        
        # Delete the demo users
        demo_users.delete()
        
        # Delete demo courses (containing 'Demo' in the title)
        demo_courses = Course.objects.filter(title__contains='Demo')
        demo_courses.delete()
        
        # Delete demo QR code batches
        QRCodeBatch.objects.filter(name__contains='Demo').delete()
        
        self.stdout.write(self.style.SUCCESS('Existing demo data cleaned successfully'))

    def create_admin_user(self):
        """Create or get admin user"""
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword'
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_user.username}"))
        else:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(self.style.SUCCESS(f"Using existing admin user: {admin_user.username}"))
        return admin_user

    def create_instructors(self, num_instructors):
        """Create instructor users"""
        instructors = []
        for i in range(1, num_instructors + 1):
            username = f'instructor{i}'
            if not User.objects.filter(username=username).exists():
                instructor = User.objects.create_user(
                    username=username,
                    email=f'instructor{i}@demo.com',
                    password='instructorpassword',
                    first_name=f'Instructor{i}',
                    last_name=f'Demo'
                )
                # Set instructor flag
                instructor.profile.is_instructor = True
                instructor.profile.bio = f"Demo instructor {i} with expertise in various subjects."
                instructor.profile.department = random.choice(['Computer Science', 'Engineering', 'Business', 'Arts', 'Sciences'])
                instructor.profile.save()
                
                instructors.append(instructor)
                self.stdout.write(self.style.SUCCESS(f"Created instructor: {instructor.username}"))
            else:
                instructor = User.objects.get(username=username)
                instructors.append(instructor)
                self.stdout.write(self.style.SUCCESS(f"Using existing instructor: {instructor.username}"))
        return instructors

    def create_students(self, num_students):
        """Create student users"""
        students = []
        
        # Generate random student names for more realism
        first_names = ['Alex', 'Bailey', 'Casey', 'Dakota', 'Emerson', 
                      'Finley', 'Gale', 'Harper', 'Indiana', 'Jordan', 
                      'Kennedy', 'Logan', 'Morgan', 'Nico', 'Olivia', 
                      'Parker', 'Quinn', 'Riley', 'Skyler', 'Taylor', 
                      'Uriah', 'Val', 'Winter', 'Xander', 'Yara', 'Zion']
        last_names = ['Adams', 'Brown', 'Chen', 'Davis', 'Edwards', 
                     'Fisher', 'Garcia', 'Hayes', 'Ibrahim', 'Jones', 
                     'Kim', 'Lopez', 'Miller', 'Nguyen', 'Ortiz', 
                     'Patel', 'Quinn', 'Rodriguez', 'Smith', 'Thompson', 
                     'Uematsu', 'Vasquez', 'Williams', 'Xu', 'Young', 'Zhang']
        
        for i in range(1, num_students + 1):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'student{i}'
            
            if not User.objects.filter(username=username).exists():
                student = User.objects.create_user(
                    username=username,
                    email=f'student{i}@demo.com',
                    password='studentpassword',
                    first_name=first_name,
                    last_name=last_name
                )
                # Add profile info
                student.profile.bio = f"Demo student {i} interested in learning new skills."
                student.profile.student_id = f"S{100000 + i}"
                student.profile.department = random.choice(['Computer Science', 'Engineering', 'Business', 'Arts', 'Sciences'])
                student.profile.save()
                
                students.append(student)
                self.stdout.write(self.style.SUCCESS(f"Created student: {student.username} ({first_name} {last_name})"))
            else:
                student = User.objects.get(username=username)
                students.append(student)
                self.stdout.write(self.style.SUCCESS(f"Using existing student: {student.username}"))
        
        return students

    def create_courses(self, num_courses, instructors):
        """Create courses with modules, quizzes, and questions"""
        # Sample course data with different subjects and levels
        course_templates = [
            {
                'title': 'Introduction to Programming with Python',
                'description': 'Learn the basics of Python programming language. This course covers variables, data types, control flow, functions, and more.',
                'status': 'published',
                'enrollment_type': 'open',
                'course_type': 'standard',
                'max_students': 50,
                'duration_days': 90,
                'modules': [
                    {'title': 'Python Basics', 'order': 1, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Control Flow', 'order': 2, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Functions', 'order': 3, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Data Structures', 'order': 4, 'lessons': 6, 'content_type': 'mixed'},
                    {'title': 'File Handling', 'order': 5, 'lessons': 4, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'Web Development with Django',
                'description': 'Master web development using Django framework. Build robust and scalable web applications with Python and Django.',
                'status': 'published',
                'enrollment_type': 'open',
                'course_type': 'intensive',
                'max_students': 30,
                'duration_days': 120,
                'modules': [
                    {'title': 'Django Overview', 'order': 1, 'lessons': 3, 'content_type': 'mixed'},
                    {'title': 'Models & Databases', 'order': 2, 'lessons': 6, 'content_type': 'mixed'},
                    {'title': 'Views & Templates', 'order': 3, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Forms & User Input', 'order': 4, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Authentication & Authorization', 'order': 5, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'RESTful APIs', 'order': 6, 'lessons': 5, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'Data Science Fundamentals',
                'description': 'Explore the world of data science using Python libraries like NumPy, Pandas, and Matplotlib. Learn data manipulation, visualization, and basic machine learning concepts.',
                'status': 'published',
                'enrollment_type': 'restricted',
                'course_type': 'standard',
                'max_students': 25,
                'duration_days': 150,
                'modules': [
                    {'title': 'Introduction to Data Science', 'order': 1, 'lessons': 3, 'content_type': 'mixed'},
                    {'title': 'NumPy Basics', 'order': 2, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Data Manipulation with Pandas', 'order': 3, 'lessons': 6, 'content_type': 'mixed'},
                    {'title': 'Data Visualization', 'order': 4, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Introduction to Machine Learning', 'order': 5, 'lessons': 7, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'Advanced JavaScript',
                'description': 'Take your JavaScript skills to the next level with advanced concepts like closures, prototypes, async/await, and modern ES6+ features.',
                'status': 'published',
                'enrollment_type': 'open',
                'course_type': 'self_paced',
                'max_students': 0,  # Unlimited
                'duration_days': 60,
                'modules': [
                    {'title': 'Modern JavaScript Syntax', 'order': 1, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Closures & Scope', 'order': 2, 'lessons': 3, 'content_type': 'mixed'},
                    {'title': 'Prototypes & Object-Oriented JS', 'order': 3, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Asynchronous JavaScript', 'order': 4, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'ES6+ Features', 'order': 5, 'lessons': 6, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'Machine Learning with TensorFlow',
                'description': 'Learn to build and deploy machine learning models using TensorFlow. This course covers neural networks, deep learning, and model deployment.',
                'status': 'published',
                'enrollment_type': 'restricted',
                'course_type': 'intensive',
                'max_students': 20,
                'duration_days': 180,
                'modules': [
                    {'title': 'TensorFlow Basics', 'order': 1, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Neural Networks Fundamentals', 'order': 2, 'lessons': 6, 'content_type': 'mixed'},
                    {'title': 'Convolutional Neural Networks', 'order': 3, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Recurrent Neural Networks', 'order': 4, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Model Deployment', 'order': 5, 'lessons': 3, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'UI/UX Design Principles',
                'description': 'Learn the core principles of UI/UX design. This course covers user research, wireframing, prototyping, and usability testing.',
                'status': 'published',
                'enrollment_type': 'open',
                'course_type': 'standard',
                'max_students': 40,
                'duration_days': 90,
                'modules': [
                    {'title': 'Intro to UX Design', 'order': 1, 'lessons': 3, 'content_type': 'mixed'},
                    {'title': 'User Research Methods', 'order': 2, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Wireframing & Prototyping', 'order': 3, 'lessons': 6, 'content_type': 'mixed'},
                    {'title': 'UI Design Fundamentals', 'order': 4, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Usability Testing', 'order': 5, 'lessons': 4, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'Cloud Computing with AWS',
                'description': 'Master cloud computing concepts and services with Amazon Web Services (AWS). Learn about EC2, S3, Lambda, and more.',
                'status': 'published',
                'enrollment_type': 'open',
                'course_type': 'intensive',
                'max_students': 35,
                'duration_days': 120,
                'modules': [
                    {'title': 'Cloud Computing Basics', 'order': 1, 'lessons': 3, 'content_type': 'mixed'},
                    {'title': 'EC2 & Virtual Servers', 'order': 2, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'S3 & Storage Solutions', 'order': 3, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Databases in AWS', 'order': 4, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Serverless with Lambda', 'order': 5, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Security & Best Practices', 'order': 6, 'lessons': 5, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'Cybersecurity Essentials',
                'description': 'Learn fundamental cybersecurity concepts and practices. This course covers threat detection, risk assessment, security policies, and more.',
                'status': 'published',
                'enrollment_type': 'open',
                'course_type': 'standard',
                'max_students': 30,
                'duration_days': 90,
                'modules': [
                    {'title': 'Introduction to Cybersecurity', 'order': 1, 'lessons': 3, 'content_type': 'mixed'},
                    {'title': 'Network Security', 'order': 2, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Web Security', 'order': 3, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Cryptography Basics', 'order': 4, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Security Policies & Compliance', 'order': 5, 'lessons': 3, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'Mobile App Development with React Native',
                'description': 'Build cross-platform mobile applications with React Native. Learn to create apps that work on both iOS and Android platforms.',
                'status': 'published',
                'enrollment_type': 'open',
                'course_type': 'intensive',
                'max_students': 25,
                'duration_days': 120,
                'modules': [
                    {'title': 'React Native Fundamentals', 'order': 1, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'UI Components & Styling', 'order': 2, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Navigation & Routing', 'order': 3, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'State Management', 'order': 4, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Native Modules & APIs', 'order': 5, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Publishing Your App', 'order': 6, 'lessons': 3, 'content_type': 'mixed'},
                ],
            },
            {
                'title': 'Project Management Fundamentals',
                'description': 'Learn essential project management skills, methodologies, and tools. This course covers project planning, execution, monitoring, and closing.',
                'status': 'published',
                'enrollment_type': 'open',
                'course_type': 'self_paced',
                'max_students': 50,
                'duration_days': 90,
                'modules': [
                    {'title': 'Project Management Overview', 'order': 1, 'lessons': 3, 'content_type': 'mixed'},
                    {'title': 'Project Initiation & Planning', 'order': 2, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Project Execution', 'order': 3, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Risk & Change Management', 'order': 4, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'Project Monitoring & Control', 'order': 5, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Project Closing', 'order': 6, 'lessons': 3, 'content_type': 'mixed'},
                ],
            },
            # Add a course explicitly marked as a draft
            {
                'title': 'Advanced Artificial Intelligence Concepts',
                'description': 'Explore cutting-edge AI concepts including reinforcement learning, generative models, and practical applications.',
                'status': 'draft',
                'enrollment_type': 'restricted',
                'course_type': 'intensive',
                'max_students': 15,
                'duration_days': 180,
                'modules': [
                    {'title': 'Reinforcement Learning', 'order': 1, 'lessons': 6, 'content_type': 'mixed'},
                    {'title': 'Generative Adversarial Networks', 'order': 2, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'Transformer Models', 'order': 3, 'lessons': 5, 'content_type': 'mixed'},
                    {'title': 'AI Ethics', 'order': 4, 'lessons': 4, 'content_type': 'mixed'},
                    {'title': 'AI for Business Applications', 'order': 5, 'lessons': 5, 'content_type': 'mixed'},
                ],
            },
        ]
        
        created_courses = []
        
        # Use a subset of course templates based on the requested number
        templates_to_use = course_templates[:num_courses]
        
        for i, template in enumerate(templates_to_use):
            # Prefix with "Demo" to identify generated courses
            course_title = f"Demo: {template['title']}"
            
            # Check if course already exists
            if Course.objects.filter(title=course_title).exists():
                course = Course.objects.get(title=course_title)
                self.stdout.write(self.style.SUCCESS(f"Using existing course: {course.title}"))
                created_courses.append(course)
                continue
                
            # Randomly select an instructor
            instructor = random.choice(instructors)
            
            # Create the course
            course = Course.objects.create(
                title=course_title,
                description=template['description'],
                status=template['status'],
                enrollment_type=template['enrollment_type'],
                course_type=template['course_type'],
                max_students=template['max_students'],
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=template['duration_days']),
                instructor=instructor,
                qr_enabled=random.choice([True, False])
            )
            
            created_courses.append(course)
            self.stdout.write(self.style.SUCCESS(f"Created course: {course.title}"))
            
            # Create modules for this course
            self.create_modules_for_course(course, template['modules'])
        
        return created_courses

    def create_modules_for_course(self, course, module_templates):
        """Create modules with learning content and quizzes for a course"""
        all_modules = []
        
        # First, create all modules
        for module_template in module_templates:
            module = Module.objects.create(
                course=course,
                title=module_template['title'],
                description=f"This module covers essential concepts of {module_template['title']}.",
                order=module_template['order'],
                content_type=module_template['content_type'],
                estimated_time_minutes=module_template['lessons'] * 15,  # 15 mins per lesson as estimation
                content=self.generate_module_content(module_template['title'], module_template['lessons']),
                qr_access=random.choice(['disabled', 'public', 'enrolled'])
            )
            all_modules.append(module)
            self.stdout.write(self.style.SUCCESS(f"  Created module: {module.title} for course: {course.title}"))
            
            # Create a quiz for this module 
            # Not all modules have quizzes to make it more realistic
            if random.random() < 0.8:  # 80% chance of having a quiz
                self.create_quiz_for_module(module)
        
        # Set prerequisites for some modules
        self.set_module_prerequisites(all_modules)
    
    def generate_module_content(self, module_title, num_lessons):
        """Generate dummy content for a module"""
        content = f"# {module_title}\n\n"
        
        for i in range(1, num_lessons + 1):
            content += f"## Lesson {i}: {module_title} - Topic {i}\n\n"
            content += "### Overview\n\n"
            content += f"This lesson covers important concepts related to {module_title.lower()}.\n\n"
            content += "### Key Concepts\n\n"
            content += "- Concept 1: Description and explanation\n"
            content += "- Concept 2: Description and explanation\n"
            content += "- Concept 3: Description and explanation\n\n"
            content += "### Examples\n\n"
            content += "```\n# Sample code or example\nprint('Hello, world!')\n```\n\n"
            content += "### Summary\n\n"
            content += f"In this lesson, you learned about key aspects of {module_title.lower()}. "
            content += "Continue to the next lesson to build on these concepts.\n\n"
            
        return content

    def create_quiz_for_module(self, module):
        """Create a quiz with questions for a module"""
        # Determine if this will be a regular quiz or a survey
        is_survey = random.random() < 0.2  # 20% chance of being a survey
        
        quiz = Quiz.objects.create(
            module=module,
            title=f"{module.title} {'Survey' if is_survey else 'Quiz'}",
            description=f"{'Gather feedback about' if is_survey else 'Test your knowledge of'} {module.title}.",
            instructions=f"{'Please provide your feedback by answering the following questions.' if is_survey else 'Answer the following questions to test your understanding.'} {'Take your time and good luck!' if not is_survey else ''}",
            time_limit_minutes=0 if is_survey else random.choice([10, 15, 20, 30]),
            grace_period_minutes=2,
            allow_time_extension=random.choice([True, False]),
            passing_score=70,
            randomize_questions=random.choice([True, False]),
            randomize_choices=random.choice([True, False]),
            qr_tracking=module.qr_access != 'disabled',
            allow_multiple_attempts=random.choice([True, False]),
            max_attempts=random.choice([0, 2, 3, 5]) if is_survey else random.choice([1, 2, 3]),
            show_feedback_after=random.choice(['each_question', 'completion']),
            general_feedback="Thank you for completing this quiz. Review your results and study any areas where you need improvement.",
            conditional_feedback={
                "0-59": "You need more practice. Consider reviewing the module content again.",
                "60-79": "Good job! You have a solid understanding, but there's room for improvement.",
                "80-100": "Excellent work! You've demonstrated a strong understanding of the material."
            },
            access_code="" if random.random() < 0.7 else f"ACCESS{random.randint(1000, 9999)}",
            available_from=timezone.now() - timedelta(days=5),
            available_until=timezone.now() + timedelta(days=30),
            is_published=True,
            is_survey=is_survey
        )
        
        self.stdout.write(self.style.SUCCESS(f"    Created {quiz.title}"))
        
        # Create questions for this quiz
        if is_survey:
            self.create_survey_questions(quiz)
        else:
            self.create_regular_questions(quiz)
            
        return quiz
        
    def create_regular_questions(self, quiz):
        """Create a mix of regular question types for a quiz"""
        # Determine number of questions (between 5 and 10)
        num_questions = random.randint(5, 10)
        
        # Question order tracking
        order = 1
        
        # Create multiple choice questions (60% of questions)
        num_mc_questions = int(num_questions * 0.6)
        for i in range(num_mc_questions):
            # Determine if it allows multiple answers
            allow_multiple = random.random() < 0.3  # 30% chance of allowing multiple answers
            
            # Create the question
            mc_question = MultipleChoiceQuestion.objects.create(
                quiz=quiz,
                text=f"Multiple choice question {i+1} about {quiz.module.title}?",
                question_type='multiple_choice',
                order=order,
                points=random.choice([1, 2, 3]),
                explanation=f"Explanation for question {i+1}",
                correct_feedback="Great job! That's correct.",
                incorrect_feedback="Not quite right. Review the material and try again.",
                allow_multiple=allow_multiple,
                use_partial_credit=random.choice([True, False]) if allow_multiple else False
            )
            
            # Create choices
            num_choices = random.randint(3, 5)
            for j in range(num_choices):
                # For multiple answer questions, have multiple correct choices
                is_correct = False
                if allow_multiple:
                    # For multiple answer questions, distribute correct answers
                    if j < 2:  # Make first couple choices correct
                        is_correct = True
                    else:
                        is_correct = random.random() < 0.2  # 20% chance of being correct
                else:
                    # For single answer questions, exactly one correct choice
                    is_correct = (j == 0)  # First option is correct
                
                Choice.objects.create(
                    question=mc_question,
                    text=f"Choice {j+1} for question {i+1}",
                    is_correct=is_correct,
                    feedback=f"{'Correct!' if is_correct else 'Incorrect.'} This explains why choice {j+1} is {'correct' if is_correct else 'incorrect'}.",
                    order=j+1,
                    points_value=2 if is_correct else -1 if mc_question.use_partial_credit else 0
                )
            
            order += 1
        
        # Create true/false questions (30% of questions)
        num_tf_questions = int(num_questions * 0.3)
        for i in range(num_tf_questions):
            TrueFalseQuestion.objects.create(
                quiz=quiz,
                text=f"True or false: Statement {i+1} about {quiz.module.title} is correct.",
                question_type='true_false',
                order=order,
                points=1,
                explanation=f"Explanation for true/false question {i+1}",
                correct_feedback="Great job! That's correct.",
                incorrect_feedback="Not quite right. Review the material and try again.",
                correct_answer=random.choice([True, False])
            )
            order += 1
        
        # Create essay questions (10% of questions or at least 1)
        num_essay_questions = max(1, int(num_questions * 0.1))
        for i in range(num_essay_questions):
            # Create a rubric for some essay questions
            use_detailed_rubric = random.choice([True, False])
            
            if use_detailed_rubric:
                # Create a rubric first
                rubric = ScoringRubric.objects.create(
                    name=f"Rubric for {quiz.module.title} Essay {i+1}",
                    description=f"Evaluation criteria for essay on {quiz.module.title}"
                )
                
                # Add criteria to the rubric
                criterion_types = [
                    "Content Knowledge", 
                    "Organization", 
                    "Critical Thinking", 
                    "Communication Skills",
                    "References and Evidence"
                ]
                
                for j, criterion_type in enumerate(criterion_types[:3]):  # Use first 3 criteria types
                    RubricCriterion.objects.create(
                        rubric=rubric,
                        name=criterion_type,
                        description=f"Evaluates the student's {criterion_type.lower()}",
                        max_points=5,
                        weight=1.0,
                        order=j+1
                    )
                
                essay_question = EssayQuestion.objects.create(
                    quiz=quiz,
                    text=f"Write an essay discussing {quiz.module.title}. Include key concepts and examples.",
                    question_type='essay',
                    order=order,
                    points=10,
                    explanation="This essay evaluates your understanding of the concepts presented in this module.",
                    min_word_count=100,
                    max_word_count=500,
                    rubric="Please provide thorough explanations and examples to support your points.",
                    scoring_rubric=rubric,
                    example_answer=f"Example answer for essay about {quiz.module.title}...",
                    allow_attachments=random.choice([True, False]),
                    use_detailed_rubric=True
                )
            else:
                # Simple essay question without detailed rubric
                essay_question = EssayQuestion.objects.create(
                    quiz=quiz,
                    text=f"Write a short response about {quiz.module.title}. Include your thoughts on the key concepts.",
                    question_type='essay',
                    order=order,
                    points=5,
                    explanation="This response evaluates your understanding of the concepts presented in this module.",
                    min_word_count=50,
                    max_word_count=250,
                    rubric="Graded based on accuracy, completeness, and clarity.",
                    example_answer=f"Example answer for essay about {quiz.module.title}...",
                    allow_attachments=False,
                    use_detailed_rubric=False
                )
            
            order += 1

    def create_survey_questions(self, quiz):
        """Create questions specifically for a survey"""
        # Survey questions are mostly multiple choice with rating scales
        # Determine number of questions (between 5 and 8)
        num_questions = random.randint(5, 8)
        
        # Question categories for surveys
        survey_categories = [
            "Content Quality",
            "Learning Experience",
            "Difficulty Level",
            "Pace of Learning",
            "Instructor Effectiveness",
            "Materials Quality",
            "Overall Satisfaction"
        ]
        
        # Question order tracking
        order = 1
        
        # Create multiple choice rating questions
        for i in range(min(num_questions-1, len(survey_categories))):
            category = survey_categories[i]
            
            mc_question = MultipleChoiceQuestion.objects.create(
                quiz=quiz,
                text=f"How would you rate the {category.lower()} of this module?",
                question_type='multiple_choice',
                order=order,
                points=1,
                explanation="Your feedback helps us improve the course.",
                allow_multiple=False
            )
            
            # Create 5-point Likert scale choices
            ratings = ["Very Poor", "Poor", "Average", "Good", "Excellent"]
            for j, rating in enumerate(ratings):
                Choice.objects.create(
                    question=mc_question,
                    text=rating,
                    is_correct=True,  # All choices are "correct" in a survey
                    is_neutral=True,  # Neutral for scoring
                    order=j+1
                )
            
            order += 1
        
        # Add one essay question for general feedback
        EssayQuestion.objects.create(
            quiz=quiz,
            text="Please provide any additional feedback or suggestions for improving this module.",
            question_type='essay',
            order=order,
            points=1,
            min_word_count=0,
            max_word_count=500,
            allow_attachments=False,
            use_detailed_rubric=False
        )

    def set_module_prerequisites(self, modules):
        """Set prerequisites for modules to create a learning path"""
        if len(modules) <= 1:
            return
            
        # Skip the first module (it has no prerequisites)
        for i in range(1, len(modules)):
            # 70% chance of having the previous module as prerequisite
            if random.random() < 0.7:
                modules[i].prerequisites.add(modules[i-1])
                self.stdout.write(self.style.SUCCESS(f"  Set {modules[i-1].title} as prerequisite for {modules[i].title}"))
        
        # Occasionally set quiz prerequisites
        quizzes = []
        for module in modules:
            quiz_set = module.quizzes.all()
            if quiz_set.exists():
                quizzes.append(quiz_set.first())
        
        if len(quizzes) >= 2:
            # Set some quiz prerequisites
            for i in range(1, len(quizzes)):
                # 40% chance of having a quiz prerequisite
                if random.random() < 0.4:
                    QuizPrerequisite.objects.create(
                        quiz=quizzes[i],
                        prerequisite_quiz=quizzes[i-1],
                        required_passing=random.choice([True, False]),
                        bypass_for_instructors=True
                    )
                    self.stdout.write(self.style.SUCCESS(f"  Set {quizzes[i-1].title} as prerequisite for {quizzes[i].title}"))

    def create_enrollments(self, students, courses):
        """Create student enrollments in courses"""
        self.stdout.write(self.style.SUCCESS("Creating enrollments..."))
        
        enrollment_count = 0
        
        for student in students:
            # Determine how many courses this student enrolls in (1-4)
            num_enrollments = random.randint(1, min(4, len(courses)))
            
            # Randomly select courses
            selected_courses = random.sample(courses, num_enrollments)
            
            for course in selected_courses:
                # Skip if course is draft (unless random chance to simulate a tester)
                if course.status == 'draft' and random.random() < 0.9:
                    continue
                    
                # Skip if already enrolled
                if Enrollment.objects.filter(user=student, course=course).exists():
                    continue
                
                # Create enrollment with random progress
                enrollment = Enrollment.objects.create(
                    user=student,
                    course=course,
                    status='active',
                    # Random progress percentages
                    progress=random.randint(0, 100)
                )
                enrollment_count += 1
                
                # Mark some enrollments as completed
                if random.random() < 0.2:  # 20% chance
                    enrollment.status = 'completed'
                    enrollment.completed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                    enrollment.save()
        
        self.stdout.write(self.style.SUCCESS(f"Created {enrollment_count} enrollments"))

    def generate_user_progress(self, students, courses):
        """Generate progress records for enrolled students"""
        self.stdout.write(self.style.SUCCESS("Generating user progress data..."))
        
        # For each enrolled student
        for student in students:
            # Get all enrollments for this student
            enrollments = Enrollment.objects.filter(user=student)
            
            for enrollment in enrollments:
                course = enrollment.course
                
                # Create or get progress record
                progress, created = Progress.objects.get_or_create(
                    user=student,
                    course=course,
                    defaults={
                        'total_lessons': course.modules.count(),
                        'total_duration_seconds': 0
                    }
                )
                
                # Get all modules for this course
                modules = course.modules.all().order_by('order')
                
                # Determine how far the student has progressed (based on enrollment progress %)
                completion_threshold = enrollment.progress / 100.0
                total_modules = len(modules)
                modules_to_complete = int(total_modules * completion_threshold)
                
                # Generate progress for each module
                for i, module in enumerate(modules):
                    status = 'not_started'
                    completed_at = None
                    duration = 0
                    
                    if i < modules_to_complete:
                        # This module is completed
                        status = 'completed'
                        completed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                        duration = random.randint(10, 60) * 60  # 10-60 minutes in seconds
                    elif i == modules_to_complete and completion_threshold > 0:
                        # This module is in progress
                        status = 'in_progress'
                        duration = random.randint(5, 30) * 60  # 5-30 minutes in seconds
                    
                    # Create module progress
                    module_progress, created = ModuleProgress.objects.get_or_create(
                        progress=progress,
                        module=module,
                        defaults={
                            'status': status,
                            'duration_seconds': duration,
                            'completed_at': completed_at,
                            'content_position': {'page': random.randint(1, 5)} if status == 'in_progress' else {}
                        }
                    )
                    
                    # Generate quiz attempts for completed modules
                    if status == 'completed':
                        self.generate_quiz_attempts(student, module)
                
                # Update overall progress record
                progress.update_completion_percentage()
                
                # Add random study duration
                total_duration = sum(mp.duration_seconds for mp in ModuleProgress.objects.filter(progress=progress))
                progress.total_duration_seconds = total_duration
                progress.save()
        
        self.stdout.write(self.style.SUCCESS("User progress data generated"))

    def generate_quiz_attempts(self, student, module):
        """Generate quiz attempts for a student on completed modules"""
        # Get all quizzes for this module
        quizzes = module.quizzes.filter(is_published=True)
        
        if not quizzes.exists():
            return
            
        for quiz in quizzes:
            # Check if student already has attempts
            existing_attempts = QuizAttempt.objects.filter(user=student, quiz=quiz)
            if existing_attempts.exists():
                continue
                
            # Determine number of attempts (1-3)
            num_attempts = 1
            if quiz.allow_multiple_attempts:
                if quiz.max_attempts > 0:
                    num_attempts = random.randint(1, min(3, quiz.max_attempts))
                else:
                    num_attempts = random.randint(1, 3)
            
            # Create each attempt
            for attempt_number in range(1, num_attempts + 1):
                is_final_attempt = (attempt_number == num_attempts)
                score_factor = 0.6 if attempt_number == 1 else 0.8 if attempt_number == 2 else 0.9
                
                # For surveys, always have one successful attempt
                if quiz.is_survey:
                    score_factor = 1.0
                    num_attempts = 1
                
                # Create the attempt
                with transaction.atomic():
                    attempt = QuizAttempt.objects.create(
                        quiz=quiz,
                        user=student,
                        started_at=timezone.now() - timedelta(days=random.randint(1, 20)),
                        status='completed',
                        attempt_number=attempt_number
                    )
                    
                    # Set completed time (10-30 minutes after start)
                    attempt.completed_at = attempt.started_at + timedelta(minutes=random.randint(10, 30))
                    attempt.time_spent_seconds = (attempt.completed_at - attempt.started_at).total_seconds()
                    attempt.last_activity_at = attempt.completed_at
                    
                    # Get questions for this quiz
                    questions = list(quiz.questions.all().order_by('order'))
                    if not questions:
                        attempt.delete()
                        continue
                    
                    # Generate responses for each question
                    earned_points = 0
                    max_points = 0
                    
                    for question in questions:
                        points = question.points
                        max_points += points
                        
                        # Determine if this answer is correct based on score factor
                        is_correct = random.random() < score_factor
                        
                        if question.question_type == 'multiple_choice':
                            if question.multiplechoicequestion.allow_multiple:
                                # Handle multiple choice with multiple answers
                                all_choices = list(question.multiplechoicequestion.choices.all())
                                correct_choices = [c.id for c in all_choices if c.is_correct]
                                
                                if is_correct:
                                    # Select all correct choices with maybe one mistake
                                    selected = correct_choices.copy()
                                    if random.random() < 0.2 and len(selected) > 1:
                                        selected.pop(random.randrange(len(selected)))
                                else:
                                    # Select some but not all correct choices
                                    selected = random.sample(correct_choices, 
                                                           max(1, len(correct_choices) - random.randint(1, len(correct_choices))))
                                    
                                    # Maybe add an incorrect choice
                                    incorrect_choices = [c.id for c in all_choices if not c.is_correct]
                                    if incorrect_choices and random.random() < 0.5:
                                        selected.append(random.choice(incorrect_choices))
                                
                                # Create the response
                                response = QuestionResponse.objects.create(
                                    attempt=attempt,
                                    question=question,
                                    response_data={'selected_choices': selected},
                                    time_spent_seconds=random.randint(10, 60)
                                )
                            else:
                                # Handle multiple choice with single answer
                                all_choices = list(question.multiplechoicequestion.choices.all())
                                correct_choice = next((c for c in all_choices if c.is_correct), None)
                                
                                if is_correct and correct_choice:
                                    selected_choice = correct_choice.id
                                else:
                                    # Select random choice (might be correct by chance)
                                    selected_choice = random.choice(all_choices).id
                                
                                # Create the response
                                response = QuestionResponse.objects.create(
                                    attempt=attempt,
                                    question=question,
                                    response_data={'selected_choice': selected_choice},
                                    time_spent_seconds=random.randint(10, 60)
                                )
                        
                        elif question.question_type == 'true_false':
                            correct_answer = question.truefalsequestion.correct_answer
                            
                            if is_correct:
                                selected_answer = correct_answer
                            else:
                                selected_answer = not correct_answer
                            
                            # Create the response
                            response = QuestionResponse.objects.create(
                                attempt=attempt,
                                question=question,
                                response_data={'selected_answer': selected_answer},
                                time_spent_seconds=random.randint(5, 30)
                            )
                        
                        elif question.question_type == 'essay':
                            # For essays, create a dummy response
                            word_count = random.randint(
                                min(50, question.essayquestion.min_word_count or 50),
                                min(250, question.essayquestion.max_word_count or 250)
                            )
                            
                            essay_text = f"This is a sample essay response with approximately {word_count} words. "
                            essay_text += "It discusses the key concepts from the module and provides examples. " * 8
                            
                            # Create the response
                            response = QuestionResponse.objects.create(
                                attempt=attempt,
                                question=question,
                                response_data={'essay_text': essay_text},
                                time_spent_seconds=random.randint(120, 600),
                            )
                            
                            # For final attempts, simulate instructor grading for essays
                            if is_final_attempt:
                                instructor = quiz.module.course.instructor
                                response.instructor_comment = "Good effort on this response. You covered the main points well."
                                response.graded_at = timezone.now() - timedelta(days=random.randint(1, 5))
                                response.graded_by = instructor
                                
                                # Assign points based on score factor
                                essay_points = int(points * score_factor)
                                response.points_earned = essay_points
                                response.is_correct = essay_points > (points * 0.6)
                                response.save()
                                
                                earned_points += essay_points
                                continue
                        
                        # Check the answer and update response
                        response.check_answer()
                        earned_points += response.points_earned
                    
                    # Update the attempt score
                    attempt.score = earned_points
                    attempt.max_score = max_points
                    
                    # Set passing based on score percentage
                    if max_points > 0:
                        percentage = (earned_points / max_points) * 100
                        attempt.is_passed = percentage >= quiz.passing_score
                    else:
                        attempt.is_passed = True
                        
                    attempt.save()

    def generate_analytics_data(self, students, courses):
        """Generate analytics data for students and courses"""
        self.stdout.write(self.style.SUCCESS("Generating analytics data..."))
        
        # Generate user activity records
        self.generate_user_activity(students, courses)
        
        # Generate learner analytics
        self.generate_learner_analytics(students)
        
        # Generate course analytics
        self.generate_course_analytics(courses)
        
        # Generate module engagement data
        self.generate_module_engagement(students, courses)
        
        self.stdout.write(self.style.SUCCESS("Analytics data generated"))

    def generate_user_activity(self, students, courses):
        """Generate user activity records"""
        activity_types = ['login', 'view_course', 'view_module', 'start_quiz', 'complete_quiz']
        
        # Create a random number of activities for each student
        for student in students:
            # Get student enrollments
            enrollments = Enrollment.objects.filter(user=student)
            enrolled_courses = [e.course for e in enrollments]
            
            if not enrolled_courses:
                continue
                
            # Generate 10-30 activities per student
            num_activities = random.randint(10, 30)
            
            for _ in range(num_activities):
                # Select random activity type
                activity_type = random.choice(activity_types)
                
                # Create appropriate details based on activity type
                details = {}
                
                if activity_type == 'login':
                    details = {}
                elif activity_type in ['view_course', 'view_module', 'start_quiz', 'complete_quiz']:
                    # Select a random enrolled course
                    course = random.choice(enrolled_courses)
                    details['course_id'] = course.id
                    details['course_title'] = course.title
                    
                    if activity_type in ['view_module', 'start_quiz', 'complete_quiz']:
                        # Select a random module
                        modules = list(course.modules.all())
                        if modules:
                            module = random.choice(modules)
                            details['module_id'] = module.id
                            details['module_title'] = module.title
                            
                            if activity_type in ['start_quiz', 'complete_quiz']:
                                # Select a random quiz
                                quizzes = list(module.quizzes.all())
                                if quizzes:
                                    quiz = random.choice(quizzes)
                                    details['quiz_id'] = quiz.id
                                    details['quiz_title'] = quiz.title
                                    
                                    if activity_type == 'complete_quiz':
                                        details['score'] = random.randint(50, 100)
                
                # Create the activity record
                activity_time = timezone.now() - timedelta(days=random.randint(1, 30))
                
                UserActivity.objects.create(
                    user=student,
                    activity_type=activity_type,
                    timestamp=activity_time,
                    ip_address=f"192.168.1.{random.randint(1, 255)}",
                    user_agent="Mozilla/5.0 (Demo Data Generator)",
                    session_id=str(uuid.uuid4()),
                    details=details
                )

    def generate_learner_analytics(self, students):
        """Generate learner analytics for students"""
        for student in students:
            # Check if student has quiz attempts
            attempts = QuizAttempt.objects.filter(user=student)
            
            if not attempts.exists():
                continue
                
            # Create or get learner analytics
            learner_analytics, created = LearnerAnalytics.objects.get_or_create(user=student)
            
            # Calculate metrics
            try:
                learner_analytics.calculate_overall_metrics()
                learner_analytics.calculate_performance_by_category()
                learner_analytics.identify_strengths_and_weaknesses()
                learner_analytics.calculate_progress_over_time()
                learner_analytics.calculate_percentile_ranking()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error calculating learner analytics for {student.username}: {e}"))

    def generate_course_analytics(self, courses):
        """Generate course analytics"""
        for course in courses:
            # Check if course has enrollments
            enrollments = Enrollment.objects.filter(course=course)
            
            if not enrollments.exists():
                continue
                
            # Create or get course analytics
            course_analytics, created = CourseAnalytics.objects.get_or_create(course=course)
            
            # Generate some dummy analytics data
            analytics_data = {
                'total_enrollments': enrollments.count(),
                'active_enrollments': enrollments.filter(status='active').count(),
                'new_enrollments': random.randint(5, 20),
                'completion_rate': random.randint(30, 90),
                'average_score': random.randint(65, 95),
                'engagement_score': random.uniform(3.0, 5.0),
                'active_users': random.randint(5, 15)
            }
            
            # Set data
            for key, value in analytics_data.items():
                if hasattr(course_analytics, key):
                    setattr(course_analytics, key, value)
            
            # Add some trend data
            course_analytics.enrollment_trend = {
                'weeks': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'values': [random.randint(5, 20) for _ in range(4)]
            }
            
            course_analytics.score_distribution = {
                '0-59': random.randint(0, 5),
                '60-69': random.randint(2, 8),
                '70-79': random.randint(5, 15),
                '80-89': random.randint(10, 20),
                '90-100': random.randint(5, 15)
            }
            
            # Save the analytics
            course_analytics.last_calculated = timezone.now()
            course_analytics.save()

    def generate_module_engagement(self, students, courses):
        """Generate module engagement data"""
        for student in students:
            # Get student enrollments
            enrollments = Enrollment.objects.filter(user=student)
            
            for enrollment in enrollments:
                course = enrollment.course
                modules = course.modules.all()
                
                for module in modules:
                    # Check if there's progress for this module
                    try:
                        progress = Progress.objects.get(user=student, course=course)
                        module_progress = ModuleProgress.objects.get(progress=progress, module=module)
                        
                        # Only create engagement for modules with some progress
                        if module_progress.status != 'not_started':
                            # Create module engagement
                            engagement, created = ModuleEngagement.objects.get_or_create(
                                module=module,
                                user=student,
                                defaults={
                                    'view_count': random.randint(1, 10),
                                    'time_spent': timedelta(seconds=module_progress.duration_seconds),
                                    'last_viewed': timezone.now() - timedelta(days=random.randint(1, 14)),
                                    'completion_date': module_progress.completed_at,
                                    'interaction_data': {
                                        'scroll_depth': random.randint(60, 100),
                                        'clicks': random.randint(5, 30),
                                        'highlights': random.randint(0, 5),
                                        'notes': random.randint(0, 3)
                                    }
                                }
                            )
                    except (Progress.DoesNotExist, ModuleProgress.DoesNotExist):
                        continue

    def generate_qr_codes(self, courses, admin_user):
        """Generate QR codes for courses and modules"""
        self.stdout.write(self.style.SUCCESS("Generating QR codes..."))
        
        # Create a QR code batch for courses
        course_batch = QRCodeBatch.objects.create(
            name="Demo Course QR Codes",
            description="QR codes for accessing demo courses",
            created_by=admin_user,
            target_type="course",
            access_level="public",
            max_scans_per_code=100,
            is_active=True
        )
        
        # Create a QR code batch for modules
        module_batch = QRCodeBatch.objects.create(
            name="Demo Module QR Codes",
            description="QR codes for accessing demo modules",
            created_by=admin_user,
            target_type="module",
            access_level="enrolled",
            max_scans_per_code=50,
            is_active=True
        )
        
        # Generate QR codes for courses that have QR enabled
        for course in courses:
            if course.qr_enabled:
                # Get content type for course
                course_content_type = ContentType.objects.get_for_model(Course)
                
                # Create QR code for this course
                QRCode.objects.create(
                    content_type=course_content_type,
                    object_id=course.id,
                    max_scans=100,
                    current_scans=random.randint(0, 50),
                    is_active=True,
                    access_level="public",
                    payload={
                        "title": course.title,
                        "type": "course_access"
                    },
                    batch=course_batch
                )
                
                # Increment batch counter
                course_batch.codes_count += 1
                
                # Generate QR codes for modules with QR access enabled
                for module in course.modules.all():
                    if module.qr_access != 'disabled':
                        # Get content type for module
                        module_content_type = ContentType.objects.get_for_model(Module)
                        
                        # Create QR code for this module
                        QRCode.objects.create(
                            content_type=module_content_type,
                            object_id=module.id,
                            max_scans=50,
                            current_scans=random.randint(0, 30),
                            is_active=True,
                            access_level=module.qr_access,
                            payload={
                                "title": module.title,
                                "type": "module_access",
                                "course_id": course.id
                            },
                            batch=module_batch
                        )
                        
                        # Increment batch counter
                        module_batch.codes_count += 1
        
        # Update batch counters
        course_batch.save()
        module_batch.save()
        
        self.stdout.write(self.style.SUCCESS(f"Generated {course_batch.codes_count} course QR codes and {module_batch.codes_count} module QR codes"))

    def print_summary(self, students, instructors, courses):
        """Print a summary of generated data"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("DEMO DATA GENERATION SUMMARY"))
        self.stdout.write("="*50)
        
        # User counts
        self.stdout.write(f"Users created:")
        self.stdout.write(f"  - Admin: 1")
        self.stdout.write(f"  - Instructors: {len(instructors)}")
        self.stdout.write(f"  - Students: {len(students)}")
        
        # Course counts
        self.stdout.write(f"\nCourses created: {len(courses)}")
        published_courses = sum(1 for c in courses if c.status == 'published')
        draft_courses = sum(1 for c in courses if c.status == 'draft')
        self.stdout.write(f"  - Published: {published_courses}")
        self.stdout.write(f"  - Draft: {draft_courses}")
        
        # Module counts
        module_count = sum(c.modules.count() for c in courses)
        self.stdout.write(f"\nModules created: {module_count}")
        
        # Quiz counts
        quiz_count = Quiz.objects.filter(module__course__in=courses).count()
        question_count = Question.objects.filter(quiz__module__course__in=courses).count()
        self.stdout.write(f"\nQuizzes created: {quiz_count}")
        self.stdout.write(f"Questions created: {question_count}")
        
        # QR code counts
        qr_code_count = QRCode.objects.count()
        self.stdout.write(f"\nQR codes created: {qr_code_count}")
        
        # Enrollment and progress counts
        enrollment_count = Enrollment.objects.filter(course__in=courses).count()
        active_enrollments = Enrollment.objects.filter(course__in=courses, status='active').count()
        completed_enrollments = Enrollment.objects.filter(course__in=courses, status='completed').count()
        self.stdout.write(f"\nEnrollments created: {enrollment_count}")
        self.stdout.write(f"  - Active: {active_enrollments}")
        self.stdout.write(f"  - Completed: {completed_enrollments}")
        
        # Quiz attempt counts
        attempt_count = QuizAttempt.objects.filter(quiz__module__course__in=courses).count()
        passed_attempts = QuizAttempt.objects.filter(quiz__module__course__in=courses, is_passed=True).count()
        self.stdout.write(f"\nQuiz attempts created: {attempt_count}")
        self.stdout.write(f"  - Passed: {passed_attempts}")
        
        # Login info
        self.stdout.write("\n" + "-"*50)
        self.stdout.write("ACCESS INFORMATION:")
        self.stdout.write("-"*50)
        self.stdout.write("Admin login:")
        self.stdout.write("  - Username: admin")
        self.stdout.write("  - Password: adminpassword")
        self.stdout.write("\nInstructor login (example):")
        self.stdout.write("  - Username: instructor1")
        self.stdout.write("  - Password: instructorpassword")
        self.stdout.write("\nStudent login (example):")
        self.stdout.write("  - Username: student1")
        self.stdout.write("  - Password: studentpassword")
        
        self.stdout.write("\n" + "="*50)