from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from apps.courses.models import (
    Category, Course, Module, Content, Quiz, Question, Choice,
    CourseEnrollment, ModuleProgress, QuizAttempt, Answer
)
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive demo data'

    def create_quiz(self, content, title, description, is_prerequisite=False, is_pre_check=False):
        quiz = Quiz.objects.create(
            content=content,
            title=title,
            description=description,
            passing_score=70 if not is_pre_check else 0,
            time_limit=30,
            attempts_allowed=3,
            is_prerequisite=is_prerequisite,
            is_pre_check=is_pre_check,
            shuffle_questions=True,
            show_correct_answers=True
        )
        self.stdout.write(f'Created quiz: {quiz.title}')

        # Create questions with varying difficulty and time requirements
        questions = [
            {
                'text': 'What is the main purpose of this topic?',
                'type': 'multiple_choice',
                'points': 2,
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
                'points': 3,
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
                'points': 4,
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
                points=question_data['points'],
            )

            for choice_data in question_data['choices']:
                Choice.objects.create(
                    question=question,
                    choice_text=choice_data['text'],
                    is_correct=choice_data['is_correct'],
                )

        return quiz

    def create_course_content(self, module, content_data):
        content = Content.objects.create(
            module=module,
            title=content_data['title'],
            content_type=content_data['content_type'],
            content=content_data['content'],
            estimated_time=content_data['estimated_time'],
            order=content_data['order'],
        )

        if content_data['content_type'] == 'quiz':
            quiz_title = f"{'Pre-check: ' if content_data.get('is_pre_check', False) else ''}{content.title}"
            quiz_description = f"{'Pre-check survey: ' if content_data.get('is_pre_check', False) else 'Knowledge check: '}{content_data['content']}"
            self.create_quiz(
                content=content,
                title=quiz_title,
                description=quiz_description,
                is_prerequisite=content_data.get('is_prerequisite', False),
                is_pre_check=content_data.get('is_pre_check', False)
            )

        return content

    def create_module_progress(self, enrollment, module, status='not_started', progress=0):
        return ModuleProgress.objects.create(
            enrollment=enrollment,
            module=module,
            status=status,
            progress=progress,
            started_at=timezone.now() if status != 'not_started' else None,
            completed_at=timezone.now() if status == 'completed' else None
        )

    def create_quiz_attempt(self, student, quiz, status='submitted', score=None):
        # Generate realistic time spent data
        time_spent = random.randint(quiz.time_limit * 30, quiz.time_limit * 60)  # 30-60% of time limit
        if status == 'timeout':
            time_spent = quiz.time_limit * 60  # Full time limit
        elif status == 'in_progress':
            time_spent = random.randint(0, quiz.time_limit * 30)  # Less than 30% of time limit

        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status=status,
            score=score,
            time_spent=time_spent,
            started_at=timezone.now() - timedelta(minutes=random.randint(5, 30)),
            submitted_at=timezone.now() if status != 'in_progress' else None,
            graded_at=timezone.now() if status == 'graded' else None,
            last_activity=timezone.now()
        )

        # Create answers with time spent data
        for question in quiz.questions.all():
            time_spent = random.randint(30, 180)  # 30 seconds to 3 minutes per question
            is_correct = random.choice([True, False])
            points_earned = question.points if is_correct else 0
            
            Answer.objects.create(
                attempt=attempt,
                question=question,
                answer_text=random.choice(['A', 'B', 'C', 'D']) if question.question_type == 'multiple_choice' else str(is_correct),
                is_correct=is_correct,
                points_earned=points_earned,
                time_spent=time_spent,
                last_modified=timezone.now()
            )

        return attempt

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo data...')

        # Create groups if they don't exist
        groups = {
            'Administrator': Group.objects.get_or_create(name='Administrator')[0],
            'Course Coordinator': Group.objects.get_or_create(name='Course Coordinator')[0],
            'Instructor': Group.objects.get_or_create(name='Instructor')[0],
            'Student': Group.objects.get_or_create(name='Student')[0],
        }

        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        admin.groups.add(groups['Administrator'])
        self.stdout.write('Created admin user')

        # Create coordinator
        coordinator, created = User.objects.get_or_create(
            username='coordinator',
            defaults={
                'email': 'coordinator@example.com',
                'is_staff': True
            }
        )
        if created:
            coordinator.set_password('coordinator123')
            coordinator.save()
        coordinator.groups.add(groups['Course Coordinator'])
        self.stdout.write('Created coordinator user')

        # Create instructors
        instructors = []
        instructor_data = [
            {
                'username': 'dr.smith',
                'email': 'dr.smith@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'password': 'dr.smith123',
                'title': 'Dr.'
            },
            {
                'username': 'dr.johnson',
                'email': 'dr.johnson@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'password': 'dr.johnson123',
                'title': 'Dr.'
            },
            {
                'username': 'prof.williams',
                'email': 'prof.williams@example.com',
                'first_name': 'Michael',
                'last_name': 'Williams',
                'password': 'prof.williams123',
                'title': 'Prof.'
            }
        ]

        for data in instructor_data:
            instructor, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_staff': True
                }
            )
            if created:
                instructor.set_password(data['password'])
                instructor.save()
            instructor.groups.add(groups['Instructor'])
            instructors.append(instructor)
            self.stdout.write(f'Created instructor: {instructor.get_full_name()}')

        # Create students
        students = []
        student_data = [
            {
                'username': 'john.doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'username': 'jane.smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith'
            },
            {
                'username': 'bob.wilson',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson'
            },
            {
                'username': 'alice.johnson',
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson'
            }
        ]

        for data in student_data:
            student, created = User.objects.get_or_create(
                username=data['username'],
                defaults=data
            )
            if created:
                student.set_password(f"{data['username']}123")
                student.save()
            student.groups.add(groups['Student'])
            students.append(student)
            self.stdout.write(f'Created student: {student.get_full_name()}')

        # Create categories
        categories = []
        category_data = [
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

        for data in category_data:
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'slug': data['name'].lower().replace(' ', '-'),
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create courses
        courses = []
        course_data = [
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
                                'title': 'Pre-check Survey',
                                'content_type': 'quiz',
                                'content': 'Test your basic programming knowledge',
                                'estimated_time': 20,
                                'is_pre_check': True,
                                'order': 1,
                            },
                            {
                                'title': 'Introduction to Python',
                                'content_type': 'text',
                                'content': 'Python is a high-level, interpreted programming language...',
                                'estimated_time': 30,
                                'order': 2,
                            },
                            {
                                'title': 'Setting Up Your Environment',
                                'content_type': 'video',
                                'content': 'Learn how to set up Python and your development environment...',
                                'estimated_time': 45,
                                'order': 3,
                            },
                            {
                                'title': 'Basic Syntax Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your understanding of Python basics',
                                'estimated_time': 20,
                                'order': 4,
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
                                'order': 1,
                            },
                            {
                                'title': 'Dictionaries and Sets',
                                'content_type': 'video',
                                'content': 'Working with dictionaries and sets in Python...',
                                'estimated_time': 35,
                                'order': 2,
                            },
                            {
                                'title': 'Data Structures Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your knowledge of Python data structures',
                                'estimated_time': 25,
                                'order': 3,
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
                                'title': 'Pre-check Survey',
                                'content_type': 'quiz',
                                'content': 'Test your basic web knowledge',
                                'estimated_time': 20,
                                'is_pre_check': True,
                                'order': 1,
                            },
                            {
                                'title': 'HTML5 Essentials',
                                'content_type': 'text',
                                'content': 'Learn the fundamentals of HTML5...',
                                'estimated_time': 45,
                                'order': 2,
                            },
                            {
                                'title': 'CSS Styling',
                                'content_type': 'video',
                                'content': 'Master CSS styling and layouts...',
                                'estimated_time': 60,
                                'order': 3,
                            },
                            {
                                'title': 'JavaScript Basics',
                                'content_type': 'text',
                                'content': 'Introduction to JavaScript programming...',
                                'estimated_time': 50,
                                'order': 4,
                            },
                            {
                                'title': 'Frontend Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your frontend knowledge',
                                'estimated_time': 30,
                                'order': 5,
                            },
                        ]
                    },
                ]
            },
        ]

        for course_info in course_data:
            category = Category.objects.get(name=course_info['category'])
            course, created = Course.objects.get_or_create(
                title=course_info['title'],
                defaults={
                    'description': course_info['description'],
                    'category': category,
                    'status': course_info['status'],
                    'max_students': course_info['max_students'],
                    'slug': course_info['title'].lower().replace(' ', '-'),
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + timedelta(days=90)).date(),
                }
            )
            
            if created:
                # Assign random instructor
                course.instructors.add(random.choice(instructors))
                courses.append(course)
                self.stdout.write(f'Created course: {course.title}')

                # Create modules and content
                for module_index, module_data in enumerate(course_info['modules'], 1):
                    module = Module.objects.create(
                        course=course,
                        title=module_data['title'],
                        description=module_data['description'],
                        order=module_index,
                    )
                    self.stdout.write(f'Created module: {module.title}')

                    # Create content
                    for content_data in module_data['contents']:
                        self.create_course_content(module, content_data)

                # Create enrollments and progress
                for student in students:
                    if random.random() < 0.7:  # 70% chance to enroll
                        enrollment = CourseEnrollment.objects.create(
                            student=student,
                            course=course,
                            status=random.choice(['active', 'completed', 'dropped']),
                            enrolled_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                            completed_at=timezone.now() if random.random() < 0.3 else None,
                            progress=random.randint(0, 100)
                        )
                        self.stdout.write(f'Created enrollment: {enrollment}')

                        # Create module progress
                        for module in course.modules.all():
                            status = random.choice(['not_started', 'in_progress', 'completed'])
                            progress = random.randint(0, 100)
                            self.create_module_progress(enrollment, module, status, progress)

                        # Create quiz attempts
                        for module in course.modules.all():
                            for content in module.contents.filter(content_type='quiz'):
                                if content.quiz:
                                    # Create 1-2 attempts per quiz
                                    for _ in range(random.randint(1, 2)):
                                        status = random.choice(['submitted', 'graded'])
                                        score = random.randint(60, 100) if status == 'graded' else None
                                        self.create_quiz_attempt(student, content.quiz, status, score)

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data')) 