from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.text import slugify
from apps.courses.models import (
    Category, Course, Module, Content, Quiz, Question, Choice,
    CourseEnrollment, ModuleProgress, QuizAttempt, Answer
)
from datetime import timedelta
import random

# Define paragraph generation function at module level so it's available throughout the file
def generate_paragraph():
    paragraphs = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisi id efficitur tincidunt, nisl nunc tincidunt urna, id lacinia nunc nisl id nisi.",
        "Mauris volutpat, odio non efficitur tincidunt, elit erat tincidunt urna, id lacinia nunc nisl id nisi. Nullam auctor, nisi id efficitur tincidunt.",
        "Sed euismod, nisl nec tincidunt tincidunt, nisl nunc tincidunt urna, id lacinia nunc nisl id nisi. Nullam auctor, nisi id efficitur tincidunt.",
    ]
    return "\n\n".join(random.sample(paragraphs, k=min(3, len(paragraphs))))

# Try to import lorem, but provide a fallback if not available
try:
    import lorem
    HAS_LOREM = True
except ImportError:
    HAS_LOREM = False
    
    # Mock the paragraph function from lorem to return our generator
    class LoremMock:
        @staticmethod
        def paragraph():
            paragraphs = [
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Nullam auctor, nisi id efficitur tincidunt.",
                "Mauris volutpat, odio non efficitur tincidunt.",
                "Sed euismod, nisl nec tincidunt tincidunt."
            ]
            return random.choice(paragraphs)
    
    lorem = LoremMock()

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive enhanced demo data'

    def create_survey_quiz(self, content, title, description):
        """Creates a pre-check survey quiz with no right/wrong answers"""
        quiz = Quiz.objects.create(
            content=content,
            title=title,
            description=description,
            passing_score=0,
            time_limit=15,
            attempts_allowed=1,
            is_prerequisite=False,
            is_pre_check=True,
            shuffle_questions=False,
            show_correct_answers=False
        )
        self.stdout.write(f'Created survey quiz: {quiz.title}')

        # Create survey questions
        questions = [
            {
                'text': 'How would you rate your experience with this subject?',
                'type': 'multiple_choice',
                'points': 0,
                'choices': [
                    {'text': 'No experience', 'is_correct': True},
                    {'text': 'Beginner', 'is_correct': True},
                    {'text': 'Intermediate', 'is_correct': True},
                    {'text': 'Advanced', 'is_correct': True},
                ]
            },
            {
                'text': 'What do you hope to gain from this course?',
                'type': 'multiple_choice',
                'points': 0,
                'choices': [
                    {'text': 'Professional skills for work', 'is_correct': True},
                    {'text': 'Academic knowledge', 'is_correct': True},
                    {'text': 'Personal interest', 'is_correct': True},
                    {'text': 'Other', 'is_correct': True},
                ]
            },
            {
                'text': 'How much time can you dedicate to this course weekly?',
                'type': 'multiple_choice',
                'points': 0,
                'choices': [
                    {'text': 'Less than 2 hours', 'is_correct': True},
                    {'text': '2-5 hours', 'is_correct': True},
                    {'text': '5-10 hours', 'is_correct': True},
                    {'text': 'More than 10 hours', 'is_correct': True},
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

    def create_knowledge_quiz(self, content, title, description, is_prerequisite=False):
        """Creates a knowledge check quiz with correct/incorrect answers"""
        quiz = Quiz.objects.create(
            content=content,
            title=title,
            description=description,
            passing_score=70,
            time_limit=30,
            attempts_allowed=3,
            is_prerequisite=is_prerequisite,
            is_pre_check=False,
            shuffle_questions=True,
            show_correct_answers=True
        )
        self.stdout.write(f'Created knowledge quiz: {quiz.title}')

        # Generate questions based on the content's module subject
        module_title = content.module.title.lower()
        
        if 'python' in title.lower() or 'python' in module_title:
            questions = [
                {
                    'text': 'Which of the following is NOT a Python data type?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': 'var', 'is_correct': True},
                        {'text': 'list', 'is_correct': False},
                        {'text': 'tuple', 'is_correct': False},
                        {'text': 'dictionary', 'is_correct': False},
                    ]
                },
                {
                    'text': 'How do you create a list in Python?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': 'x = []', 'is_correct': True},
                        {'text': 'x = ()', 'is_correct': False},
                        {'text': 'x = {}', 'is_correct': False},
                        {'text': 'x = list', 'is_correct': False},
                    ]
                },
                {
                    'text': 'Which operator is used for exponentiation in Python?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': '**', 'is_correct': True},
                        {'text': '^', 'is_correct': False},
                        {'text': '//', 'is_correct': False},
                        {'text': '%%', 'is_correct': False},
                    ]
                },
                {
                    'text': 'Python is a statically typed language.',
                    'type': 'true_false',
                    'points': 1,
                    'choices': [
                        {'text': 'True', 'is_correct': False},
                        {'text': 'False', 'is_correct': True},
                    ]
                }
            ]
        elif 'web' in title.lower() or 'web' in module_title or 'html' in module_title or 'css' in module_title:
            questions = [
                {
                    'text': 'Which HTML tag is used to define an unordered list?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': '<ul>', 'is_correct': True},
                        {'text': '<ol>', 'is_correct': False},
                        {'text': '<list>', 'is_correct': False},
                        {'text': '<dl>', 'is_correct': False},
                    ]
                },
                {
                    'text': 'Which CSS property is used to change the text color?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': 'color', 'is_correct': True},
                        {'text': 'text-color', 'is_correct': False},
                        {'text': 'font-color', 'is_correct': False},
                        {'text': 'text-style', 'is_correct': False},
                    ]
                },
                {
                    'text': 'JavaScript is a server-side programming language.',
                    'type': 'true_false',
                    'points': 1,
                    'choices': [
                        {'text': 'True', 'is_correct': False},
                        {'text': 'False', 'is_correct': True},
                    ]
                }
            ]
        elif 'data' in title.lower() or 'data' in module_title:
            questions = [
                {
                    'text': 'Which of the following is NOT a common data visualization library in Python?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': 'DataViz', 'is_correct': True},
                        {'text': 'Matplotlib', 'is_correct': False},
                        {'text': 'Seaborn', 'is_correct': False},
                        {'text': 'Plotly', 'is_correct': False},
                    ]
                },
                {
                    'text': 'What does SQL stand for?',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': 'Structured Query Language', 'is_correct': True},
                        {'text': 'Simple Query Language', 'is_correct': False},
                        {'text': 'Standard Query Language', 'is_correct': False},
                        {'text': 'System Query Language', 'is_correct': False},
                    ]
                },
                {
                    'text': 'Pandas is a Python library used for data analysis.',
                    'type': 'true_false',
                    'points': 1,
                    'choices': [
                        {'text': 'True', 'is_correct': True},
                        {'text': 'False', 'is_correct': False},
                    ]
                }
            ]
        else:
            # Generic questions
            questions = [
                {
                    'text': f'Question 1 about {content.module.title}',
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
                    'text': f'Question 2 about {content.module.title}',
                    'type': 'multiple_choice',
                    'points': 2,
                    'choices': [
                        {'text': 'Wrong answer 1', 'is_correct': False},
                        {'text': 'Correct answer', 'is_correct': True},
                        {'text': 'Wrong answer 2', 'is_correct': False},
                        {'text': 'Wrong answer 3', 'is_correct': False},
                    ]
                },
                {
                    'text': f'True or false: This is a fact about {content.module.title}',
                    'type': 'true_false',
                    'points': 1,
                    'choices': [
                        {'text': 'True', 'is_correct': True},
                        {'text': 'False', 'is_correct': False},
                    ]
                }
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
        """Creates course content with appropriate quiz types if specified"""
        content = Content.objects.create(
            module=module,
            title=content_data['title'],
            content_type=content_data['content_type'],
            content=content_data.get('content', ''),
            estimated_time=content_data.get('estimated_time', 30),
            order=content_data['order'],
        )
        
        self.stdout.write(f'Created content: {content.title}')

        if content_data['content_type'] == 'quiz':
            if content_data.get('is_pre_check', False):
                self.create_survey_quiz(
                    content=content,
                    title=f"Pre-check: {content.title}",
                    description=f"Pre-course survey: {content_data.get('content', 'Please complete this survey')}"
                )
            else:
                self.create_knowledge_quiz(
                    content=content,
                    title=f"Quiz: {content.title}",
                    description=f"Knowledge check: {content_data.get('content', 'Test your knowledge')}",
                    is_prerequisite=content_data.get('is_prerequisite', False)
                )

        return content

    def create_module_progress(self, enrollment, module, status='not_started', progress=0):
        """Creates module progress records"""
        return ModuleProgress.objects.create(
            enrollment=enrollment,
            module=module,
            status=status,
            progress=progress,
            started_at=timezone.now() if status != 'not_started' else None,
            completed_at=timezone.now() if status == 'completed' else None
        )

    def create_quiz_attempt(self, student, quiz, status='submitted', score=None):
        """Creates quiz attempt records with realistic data"""
        # Generate realistic time spent data
        time_limit_seconds = (quiz.time_limit or 30) * 60
        
        if status == 'in_progress':
            time_spent = random.randint(30, time_limit_seconds // 3)
        elif status == 'submitted' or status == 'graded':
            time_spent = random.randint(time_limit_seconds // 3, time_limit_seconds)
        else:
            time_spent = time_limit_seconds  # Full time for timeout
            
        started_at = timezone.now() - timedelta(minutes=random.randint(5, 60))
        
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            status=status,
            score=score,
            time_spent=time_spent,
            started_at=started_at,
            submitted_at=None if status == 'in_progress' else started_at + timedelta(seconds=time_spent),
            graded_at=None if status != 'graded' else started_at + timedelta(seconds=time_spent, minutes=1),
            last_activity=timezone.now()
        )

        # Create answers with time spent data
        for question in quiz.questions.all():
            # Time spent per question varies
            question_time = random.randint(5, 120)  # 5 seconds to 2 minutes per question
            
            # For survey quizzes (pre-check), all answers are considered correct
            if quiz.is_pre_check:
                is_correct = True
                choice_index = random.randint(0, question.choices.count() - 1)
                choice = question.choices.all()[choice_index]
                answer_text = choice.choice_text
            else:
                # For knowledge quizzes
                if question.question_type == 'true_false':
                    is_correct = random.random() > 0.3  # 70% chance of correct
                    choice = question.choices.filter(is_correct=is_correct).first()
                    answer_text = choice.choice_text if choice else ("True" if is_correct else "False")
                else:  # multiple_choice
                    is_correct = random.random() > 0.3  # 70% chance of correct
                    if is_correct:
                        choice = question.choices.filter(is_correct=True).first()
                    else:
                        choice = question.choices.filter(is_correct=False).first()
                    answer_text = choice.choice_text if choice else "No answer"
            
            points_earned = question.points if is_correct else 0
            
            Answer.objects.create(
                attempt=attempt,
                question=question,
                answer_text=answer_text,
                is_correct=is_correct,
                points_earned=points_earned,
                time_spent=question_time,
                last_modified=timezone.now()
            )

        return attempt

    def generate_content(self, content_type, subject):
        """Generate appropriate content based on content type and subject"""
        if content_type == 'text':
            if HAS_LOREM:
                # When using actual lorem package
                try:
                    return lorem.paragraph() + "\n\n" + lorem.paragraph() + "\n\n" + lorem.paragraph()
                except (TypeError, AttributeError):
                    # Fallback if the package doesn't work as expected
                    return generate_paragraph()
            else:
                return generate_paragraph()
        elif content_type == 'video':
            return f"https://example.com/videos/{subject.lower().replace(' ', '-')}.mp4"
        elif content_type == 'file':
            return f"https://example.com/files/{subject.lower().replace(' ', '-')}.pdf"
        elif content_type == 'quiz':
            return f"Quiz about {subject}"
        else:
            return "Content placeholder"

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding enhanced demo data...')

        # Create user groups if they don't exist
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
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        admin.groups.add(groups['Administrator'])
        self.stdout.write('Admin user ready')

        # Create coordinator
        coordinator, created = User.objects.get_or_create(
            username='coordinator',
            defaults={
                'email': 'coordinator@example.com',
                'first_name': 'Course',
                'last_name': 'Coordinator',
                'is_staff': True
            }
        )
        if created:
            coordinator.set_password('coordinator123')
            coordinator.save()
        coordinator.groups.add(groups['Course Coordinator'])
        self.stdout.write('Coordinator user ready')

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
            self.stdout.write(f'Instructor ready: {instructor.get_full_name()}')

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
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name']
                }
            )
            if created:
                student.set_password(f"{data['username']}123")
                student.save()
            student.groups.add(groups['Student'])
            students.append(student)
            self.stdout.write(f'Student ready: {student.get_full_name()}')

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
            {
                'name': 'Cybersecurity',
                'description': 'Protect systems and data from security threats',
            },
            {
                'name': 'Cloud Computing',
                'description': 'Deploy and manage applications in the cloud',
            },
        ]

        for data in category_data:
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'slug': slugify(data['name']),
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create comprehensive course data with a variety of types
        course_data = [
            # PUBLISHED COURSES WITH CONTENT
            {
                'title': 'Python Programming Fundamentals',
                'description': 'A comprehensive introduction to Python programming language covering syntax, data types, control structures, functions, and more.',
                'category': 'Programming',
                'status': 'published',
                'max_students': 50,
                'modules': [
                    {
                        'title': 'Getting Started with Python',
                        'description': 'An introduction to Python and its environment',
                        'contents': [
                            {
                                'title': 'Pre-Course Knowledge Check',
                                'content_type': 'quiz',
                                'content': 'Check your existing Python knowledge',
                                'estimated_time': 15,
                                'is_pre_check': True,
                                'order': 1,
                            },
                            {
                                'title': 'Introduction to Python',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'Python Introduction'),
                                'estimated_time': 30,
                                'order': 2,
                            },
                            {
                                'title': 'Setting Up Your Environment',
                                'content_type': 'video',
                                'content': self.generate_content('video', 'Python Setup'),
                                'estimated_time': 20,
                                'order': 3,
                            },
                            {
                                'title': 'Your First Python Program',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'First Python Program'),
                                'estimated_time': 30,
                                'order': 4,
                            },
                            {
                                'title': 'Module 1 Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your understanding of Python basics',
                                'estimated_time': 20,
                                'order': 5,
                            },
                        ]
                    },
                    {
                        'title': 'Python Data Structures',
                        'description': 'Learn about Python\'s core data structures',
                        'contents': [
                            {
                                'title': 'Lists and Tuples',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'Python Lists and Tuples'),
                                'estimated_time': 35,
                                'order': 1,
                            },
                            {
                                'title': 'Working with Lists - Demo',
                                'content_type': 'video',
                                'content': self.generate_content('video', 'Python Lists Demo'),
                                'estimated_time': 25,
                                'order': 2,
                            },
                            {
                                'title': 'Dictionaries and Sets',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'Python Dictionaries'),
                                'estimated_time': 40,
                                'order': 3,
                            },
                            {
                                'title': 'Practice Exercises',
                                'content_type': 'file',
                                'content': self.generate_content('file', 'Python Exercises'),
                                'estimated_time': 60,
                                'order': 4,
                            },
                            {
                                'title': 'Data Structures Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your understanding of Python data structures',
                                'estimated_time': 25,
                                'order': 5,
                            },
                        ]
                    },
                ]
            },
            {
                'title': 'Web Development with HTML, CSS, and JavaScript',
                'description': 'Learn to build responsive websites using modern web technologies including HTML5, CSS3, and JavaScript.',
                'category': 'Web Development',
                'status': 'published',
                'max_students': 40,
                'modules': [
                    {
                        'title': 'HTML Fundamentals',
                        'description': 'Learn the basics of HTML markup',
                        'contents': [
                            {
                                'title': 'Pre-Course Survey',
                                'content_type': 'quiz',
                                'content': 'Tell us about your experience with web development',
                                'estimated_time': 10,
                                'is_pre_check': True,
                                'order': 1,
                            },
                            {
                                'title': 'Introduction to HTML',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'HTML Basics'),
                                'estimated_time': 30,
                                'order': 2,
                            },
                            {
                                'title': 'HTML Tags and Elements',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'HTML Elements'),
                                'estimated_time': 45,
                                'order': 3,
                            },
                            {
                                'title': 'Creating Your First Web Page',
                                'content_type': 'video',
                                'content': self.generate_content('video', 'First Web Page'),
                                'estimated_time': 25,
                                'order': 4,
                            },
                            {
                                'title': 'HTML Knowledge Check',
                                'content_type': 'quiz',
                                'content': 'Test your HTML knowledge',
                                'estimated_time': 20,
                                'order': 5,
                                'is_prerequisite': True,
                            },
                        ]
                    },
                ]
            },
            {
                'title': 'Data Analysis with Python',
                'description': 'Master data analysis using Python libraries like Pandas, NumPy, and Matplotlib to extract insights from data.',
                'category': 'Data Science',
                'status': 'published',
                'max_students': 35,
                'modules': [
                    {
                        'title': 'Introduction to Data Analysis',
                        'description': 'Learn the fundamentals of data analysis',
                        'contents': [
                            {
                                'title': 'What is Data Analysis?',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'Data Analysis Introduction'),
                                'estimated_time': 25,
                                'order': 1,
                            },
                            {
                                'title': 'Data Analysis Process',
                                'content_type': 'video',
                                'content': self.generate_content('video', 'Data Analysis Process'),
                                'estimated_time': 30,
                                'order': 2,
                            },
                        ]
                    },
                    {
                        'title': 'NumPy and Pandas',
                        'description': 'Learn to use NumPy and Pandas for data manipulation',
                        'contents': [
                            {
                                'title': 'Introduction to NumPy',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'NumPy Basics'),
                                'estimated_time': 40,
                                'order': 1,
                            },
                            {
                                'title': 'Pandas DataFrames',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'Pandas DataFrames'),
                                'estimated_time': 45,
                                'order': 2,
                            },
                            {
                                'title': 'Data Manipulation with Pandas',
                                'content_type': 'video',
                                'content': self.generate_content('video', 'Pandas Demo'),
                                'estimated_time': 35,
                                'order': 3,
                            },
                            {
                                'title': 'NumPy and Pandas Quiz',
                                'content_type': 'quiz',
                                'content': 'Test your NumPy and Pandas knowledge',
                                'estimated_time': 30,
                                'order': 4,
                            },
                        ]
                    },
                ]
            },
            
            # DRAFT COURSES
            {
                'title': 'Mobile App Development with React Native',
                'description': 'Build cross-platform mobile applications using React Native for iOS and Android.',
                'category': 'Mobile Development',
                'status': 'draft',
                'max_students': 30,
                'modules': [
                    {
                        'title': 'Introduction to React Native',
                        'description': 'Learn the basics of React Native framework',
                        'contents': [
                            {
                                'title': 'What is React Native?',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'React Native Intro'),
                                'estimated_time': 20,
                                'order': 1,
                            },
                        ]
                    },
                ]
            },
            
            # EMPTY COURSES FOR SIGN-UP
            {
                'title': 'Cloud Computing with AWS',
                'description': 'Learn to deploy and manage applications in the Amazon Web Services cloud.',
                'category': 'Cloud Computing',
                'status': 'published',
                'max_students': 40,
                'modules': [
                    {
                        'title': 'Introduction to AWS',
                        'description': 'Getting started with Amazon Web Services',
                        'contents': []
                    },
                ]
            },
            {
                'title': 'Introduction to SQL and Database Design',
                'description': 'Learn database design principles and SQL query language from scratch.',
                'category': 'Database Management',
                'status': 'published',
                'max_students': 50,
                'modules': [
                    {
                        'title': 'Database Fundamentals',
                        'description': 'Introduction to database concepts',
                        'contents': []
                    },
                ]
            },
            {
                'title': 'Cybersecurity Fundamentals',
                'description': 'Learn the basics of cybersecurity and how to protect digital assets.',
                'category': 'Cybersecurity',
                'status': 'published',
                'max_students': 45,
                'modules': [
                    {
                        'title': 'Security Principles',
                        'description': 'Introduction to core security principles',
                        'contents': []
                    },
                ]
            },
            
            # ARCHIVED COURSE
            {
                'title': 'Legacy Web Development with PHP',
                'description': 'Learn PHP for server-side web development (archived course).',
                'category': 'Web Development',
                'status': 'archived',
                'max_students': 0,
                'modules': [
                    {
                        'title': 'PHP Basics',
                        'description': 'Introduction to PHP syntax',
                        'contents': [
                            {
                                'title': 'Introduction to PHP',
                                'content_type': 'text',
                                'content': self.generate_content('text', 'PHP Introduction'),
                                'estimated_time': 30,
                                'order': 1,
                            },
                        ]
                    },
                ]
            },
        ]

        # Create courses with their modules and content
        courses = []
        for course_info in course_data:
            category = Category.objects.get(name=course_info['category'])
            course, created = Course.objects.get_or_create(
                title=course_info['title'],
                defaults={
                    'description': course_info['description'],
                    'category': category,
                    'status': course_info['status'],
                    'max_students': course_info['max_students'],
                    'slug': slugify(course_info['title']),
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + timedelta(days=90)).date(),
                }
            )
            
            if created:
                # Assign instructor
                if course_info['status'] == 'published' or course_info['status'] == 'draft':
                    course.instructors.add(random.choice(instructors))
                
                # Assign coordinator
                if random.random() > 0.5:  # 50% chance to have a coordinator
                    course.coordinator = coordinator
                    course.save()
                
                courses.append(course)
                self.stdout.write(f'Created course: {course.title} ({course.status})')

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

        # Create enrollments with varying states
        for student in students:
            # Enroll in several published courses
            published_courses = Course.objects.filter(status='published')
            
            # Student enrolls in 3-5 courses
            enrollment_count = min(random.randint(3, 5), published_courses.count())
            courses_to_enroll = random.sample(list(published_courses), enrollment_count)
            
            for course in courses_to_enroll:
                # Determine enrollment status
                if course.modules.count() == 0:
                    # For empty courses, always active
                    status = 'active'
                    progress = 0
                    completed_at = None
                else:
                    # For courses with content, vary the status
                    status_choice = random.random()
                    if status_choice < 0.6:  # 60% active
                        status = 'active'
                        progress = random.randint(0, 80)
                        completed_at = None
                    elif status_choice < 0.8:  # 20% completed
                        status = 'completed'
                        progress = 100
                        completed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                    else:  # 20% dropped
                        status = 'dropped'
                        progress = random.randint(0, 50)
                        completed_at = None
                
                enrollment = CourseEnrollment.objects.create(
                    student=student,
                    course=course,
                    status=status,
                    enrolled_at=timezone.now() - timedelta(days=random.randint(30, 90)),
                    completed_at=completed_at,
                    progress=progress
                )
                self.stdout.write(f'Created enrollment: {student.username} - {course.title} ({status})')
                
                # Create module progress for non-empty courses
                if course.modules.count() > 0:
                    for module in course.modules.all():
                        # Determine module status based on enrollment status
                        if status == 'completed':
                            module_status = 'completed'
                            module_progress = 100
                        elif status == 'dropped':
                            # Random status for dropped courses
                            module_status = random.choice(['not_started', 'in_progress'])
                            module_progress = random.randint(0, 50) if module_status == 'in_progress' else 0
                        else:  # active
                            # For active courses, earlier modules are more likely to be completed
                            module_order_factor = (module.order / course.modules.count())
                            completion_probability = 1 - module_order_factor
                            
                            if random.random() < completion_probability:
                                module_status = 'completed'
                                module_progress = 100
                            elif random.random() < 0.5:
                                module_status = 'in_progress'
                                module_progress = random.randint(10, 90)
                            else:
                                module_status = 'not_started'
                                module_progress = 0
                        
                        self.create_module_progress(enrollment, module, module_status, module_progress)
                
                        # Create quiz attempts for modules with quizzes
                        if module_status != 'not_started':
                            for content in module.contents.filter(content_type='quiz'):
                                if hasattr(content, 'quiz') and content.quiz:
                                    # Determine number of attempts
                                    if content.quiz.is_pre_check:
                                        # Only one attempt for surveys
                                        attempt_count = 1
                                    else:
                                        # 1-3 attempts for knowledge quizzes
                                        attempt_count = random.randint(1, min(3, content.quiz.attempts_allowed))
                                    
                                    for attempt_num in range(attempt_count):
                                        # Last attempt might be in progress
                                        if attempt_num == attempt_count - 1 and random.random() < 0.2:
                                            status = 'in_progress'
                                            score = None
                                        else:
                                            status = 'graded'
                                            # Score is higher for later attempts
                                            base_score = 60 + (attempt_num * 10)
                                            score = min(100, random.randint(base_score, base_score + 30))
                                        
                                        self.create_quiz_attempt(student, content.quiz, status, score)

        self.stdout.write(self.style.SUCCESS('Successfully seeded enhanced demo data'))