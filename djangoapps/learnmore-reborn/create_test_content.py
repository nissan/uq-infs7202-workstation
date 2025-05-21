"""
Script to create test content for the LearnMore platform.
Creates courses, modules, quizzes, and enrolls test users.

Usage:
    python manage.py shell < create_test_content.py
"""

from django.contrib.auth.models import User
from users.models import UserProfile
from courses.models import Course, Module, Quiz, Question, MultipleChoiceQuestion, TrueFalseQuestion, EssayQuestion, Enrollment
from django.db import transaction
from django.utils import timezone
import os
import django
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

# Get test users
admin_user = User.objects.get(username='admin')
professor = User.objects.get(username='instructor1')
teacher = User.objects.get(username='instructor2')
student1 = User.objects.get(username='student1')
student2 = User.objects.get(username='student2')

# Sample quiz templates for reuse
QUIZ_TEMPLATES = {
    'multiple_choice': {
        'title': 'Multiple Choice Assessment',
        'description': 'Test your knowledge with multiple choice questions.',
        'time_limit_minutes': 20,
        'questions': [
            {
                'type': 'multiple_choice',
                'text': 'What is the correct answer to this question?',
                'choices': [
                    {'text': 'Option A (Correct)', 'is_correct': True},
                    {'text': 'Option B', 'is_correct': False},
                    {'text': 'Option C', 'is_correct': False},
                    {'text': 'Option D', 'is_correct': False}
                ]
            },
            {
                'type': 'multiple_choice',
                'text': 'Select all that apply:',
                'choices': [
                    {'text': 'First correct option', 'is_correct': True},
                    {'text': 'Second correct option', 'is_correct': True},
                    {'text': 'Incorrect option', 'is_correct': False},
                    {'text': 'Another incorrect option', 'is_correct': False}
                ]
            }
        ]
    },
    'true_false': {
        'title': 'True/False Assessment',
        'description': 'Test your understanding with true/false questions.',
        'time_limit_minutes': 15,
        'questions': [
            {
                'type': 'true_false',
                'text': 'This statement is true.',
                'correct_answer': True
            },
            {
                'type': 'true_false',
                'text': 'This statement is false.',
                'correct_answer': False
            }
        ]
    },
    'essay': {
        'title': 'Essay Assessment',
        'description': 'Demonstrate your understanding through written responses.',
        'time_limit_minutes': 45,
        'questions': [
            {
                'type': 'essay',
                'text': 'Explain the key concepts covered in this module.',
                'min_word_count': 200,
                'max_word_count': 1000,
                'rubric': 'Evaluation will be based on:\n1. Understanding of concepts (40%)\n2. Clarity of explanation (30%)\n3. Use of examples (20%)\n4. Writing quality (10%)'
            }
        ]
    }
}

# Sample course data
COURSES = [
    {
        "title": "Introduction to Python Programming",
        "description": "Learn the fundamentals of Python programming language, including variables, data types, control flow, functions, and more.",
        "instructor": professor,
        "modules": [
            {
                "title": "Python Basics",
                "description": "Introduction to Python syntax and basic concepts.",
                "quizzes": [QUIZ_TEMPLATES['multiple_choice']]
            },
            {
                "title": "Functions and Modules",
                "description": "Learn how to create and use functions and modules in Python.",
                "quizzes": [QUIZ_TEMPLATES['true_false']]
            },
            {
                "title": "Object-Oriented Programming",
                "description": "Understanding classes, objects, and inheritance in Python.",
                "quizzes": [QUIZ_TEMPLATES['essay']]
            },
            {
                "title": "File Handling",
                "description": "Working with files and data persistence in Python.",
                "quizzes": [QUIZ_TEMPLATES['multiple_choice']]
            },
            {
                "title": "Error Handling",
                "description": "Managing exceptions and errors in Python programs.",
                "quizzes": [QUIZ_TEMPLATES['true_false']]
            },
            {
                "title": "Advanced Python Concepts",
                "description": "Exploring advanced Python features and best practices.",
                "quizzes": [QUIZ_TEMPLATES['essay']]
            }
        ]
    },
    {
        "title": "Data Science with Python",
        "description": "Explore data science concepts and techniques using Python libraries.",
        "instructor": teacher,
        "modules": [
            {
                "title": "Introduction to NumPy",
                "description": "Learn the basics of NumPy for numerical computing.",
                "quizzes": [QUIZ_TEMPLATES['multiple_choice']]
            },
            {
                "title": "Data Analysis with Pandas",
                "description": "Explore data manipulation and analysis with Pandas.",
                "quizzes": [QUIZ_TEMPLATES['true_false']]
            },
            {
                "title": "Data Visualization",
                "description": "Creating effective visualizations with Matplotlib and Seaborn.",
                "quizzes": [QUIZ_TEMPLATES['essay']]
            },
            {
                "title": "Statistical Analysis",
                "description": "Applying statistical methods to data analysis.",
                "quizzes": [QUIZ_TEMPLATES['multiple_choice']]
            },
            {
                "title": "Machine Learning Basics",
                "description": "Introduction to machine learning concepts and algorithms.",
                "quizzes": [QUIZ_TEMPLATES['true_false']]
            },
            {
                "title": "Data Science Project",
                "description": "Complete a comprehensive data science project.",
                "quizzes": [QUIZ_TEMPLATES['essay']]
            }
        ]
    },
    {
        "title": "Web Development Fundamentals",
        "description": "Learn the fundamentals of web development, including HTML, CSS, and JavaScript.",
        "instructor": professor,
        "modules": [
            {
                "title": "HTML Basics",
                "description": "Introduction to HTML markup and document structure.",
                "quizzes": [QUIZ_TEMPLATES['multiple_choice']]
            },
            {
                "title": "CSS Styling",
                "description": "Learn to style web pages using CSS.",
                "quizzes": [QUIZ_TEMPLATES['true_false']]
            },
            {
                "title": "JavaScript Fundamentals",
                "description": "Introduction to JavaScript programming for the web.",
                "quizzes": [QUIZ_TEMPLATES['essay']]
            },
            {
                "title": "Responsive Design",
                "description": "Creating websites that work on all devices.",
                "quizzes": [QUIZ_TEMPLATES['multiple_choice']]
            },
            {
                "title": "Web Accessibility",
                "description": "Making websites accessible to all users.",
                "quizzes": [QUIZ_TEMPLATES['true_false']]
            },
            {
                "title": "Web Development Project",
                "description": "Build a complete website from scratch.",
                "quizzes": [QUIZ_TEMPLATES['essay']]
            }
        ]
    }
]

# Generate additional courses
ADDITIONAL_COURSES = [
    {
        "title": f"Advanced Topic {i}",
        "description": f"Comprehensive course on advanced topic {i} with detailed modules and assessments.",
        "instructor": random.choice([professor, teacher]),
        "modules": [
            {
                "title": f"Module {j} - {random.choice(['Introduction', 'Advanced Concepts', 'Practical Applications', 'Case Studies', 'Project Work'])}",
                "description": f"Detailed exploration of module {j} concepts and applications.",
                "quizzes": [random.choice(list(QUIZ_TEMPLATES.values()))]
            } for j in range(1, 7)  # 6 modules per course
        ]
    } for i in range(1, 18)  # 17 additional courses
]

COURSES.extend(ADDITIONAL_COURSES)

# Create test content
with transaction.atomic():
    created_courses = 0
    created_modules = 0
    created_quizzes = 0
    created_questions = 0
    created_enrollments = 0
    
    for course_data in COURSES:
        # Create course
        course = Course.objects.create(
            title=course_data["title"],
            description=course_data["description"],
            instructor=course_data["instructor"],
            status="published"
        )
        created_courses += 1
        
        # Create modules
        for i, module_data in enumerate(course_data["modules"]):
            module = Module.objects.create(
                course=course,
                title=module_data["title"],
                description=module_data["description"],
                order=i + 1
            )
            created_modules += 1
            
            # Create quizzes if specified
            if "quizzes" in module_data:
                for quiz_data in module_data["quizzes"]:
                    quiz = Quiz.objects.create(
                        module=module,
                        title=quiz_data["title"],
                        description=quiz_data["description"],
                        time_limit_minutes=quiz_data.get("time_limit_minutes", 30),
                        passing_score=70,
                        is_published=True
                    )
                    created_quizzes += 1
                    
                    # Create questions
                    for question_data in quiz_data.get("questions", []):
                        if question_data["type"] == "multiple_choice":
                            question = MultipleChoiceQuestion.objects.create(
                                quiz=quiz,
                                text=question_data["text"],
                                points=10,
                                allow_multiple=any(choice["is_correct"] for choice in question_data["choices"])
                            )
                            
                            # Create choices
                            for i, choice_data in enumerate(question_data["choices"]):
                                question.choices.create(
                                    text=choice_data["text"],
                                    is_correct=choice_data["is_correct"],
                                    order=i + 1
                                )
                                
                        elif question_data["type"] == "true_false":
                            question = TrueFalseQuestion.objects.create(
                                quiz=quiz,
                                text=question_data["text"],
                                points=5,
                                correct_answer=question_data["correct_answer"]
                            )
                            
                        elif question_data["type"] == "essay":
                            question = EssayQuestion.objects.create(
                                quiz=quiz,
                                text=question_data["text"],
                                points=20,
                                min_word_count=question_data.get("min_word_count", 200),
                                max_word_count=question_data.get("max_word_count", 1000),
                                rubric=question_data.get("rubric", "")
                            )
                            
                        created_questions += 1
        
        # Enroll students in courses
        for student in [student1, student2]:
            Enrollment.objects.create(
                user=student,
                course=course,
                status="active"
            )
            created_enrollments += 1

print(f"Created {created_courses} courses, {created_modules} modules, {created_quizzes} quizzes, and {created_questions} questions.")
print(f"Created {created_enrollments} student enrollments.")
print("Test content has been successfully created.")