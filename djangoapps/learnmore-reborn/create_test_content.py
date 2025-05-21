"""
Script to create test content for the LearnMore platform.
Creates courses, modules, quizzes, and enrolls test users.

Usage:
    python manage.py shell < create_test_content.py
"""

from django.contrib.auth.models import User
from users.models import UserProfile
from courses.models import Course, Module, Quiz, Question, MultipleChoiceQuestion, TrueFalseQuestion, Enrollment
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
professor = User.objects.get(username='professor')
teacher = User.objects.get(username='teacher')
student1 = User.objects.get(username='student1')
student2 = User.objects.get(username='student2')
student3 = User.objects.get(username='student3')

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
                "quizzes": [
                    {
                        "title": "Python Syntax Quiz",
                        "description": "Test your knowledge of Python syntax.",
                        "time_limit_minutes": 15,
                        "questions": [
                            {
                                "type": "multiple_choice",
                                "text": "Which of the following is a valid Python variable name?",
                                "choices": [
                                    {"text": "1variable", "is_correct": False},
                                    {"text": "_variable", "is_correct": True},
                                    {"text": "variable-1", "is_correct": False},
                                    {"text": "variable@1", "is_correct": False}
                                ]
                            },
                            {
                                "type": "true_false",
                                "text": "Python is a strongly typed language.",
                                "is_correct": False
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Functions and Modules",
                "description": "Learn how to create and use functions and modules in Python."
            }
        ]
    },
    {
        "title": "Data Science with Python",
        "description": "Explore data science concepts and techniques using Python libraries like NumPy, Pandas, and Matplotlib.",
        "instructor": teacher,
        "modules": [
            {
                "title": "Introduction to NumPy",
                "description": "Learn the basics of NumPy for numerical computing."
            },
            {
                "title": "Data Analysis with Pandas",
                "description": "Explore data manipulation and analysis with Pandas."
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
                "description": "Introduction to HTML markup and document structure."
            },
            {
                "title": "CSS Styling",
                "description": "Learn to style web pages using CSS."
            },
            {
                "title": "JavaScript Fundamentals",
                "description": "Introduction to JavaScript programming for the web."
            }
        ]
    },
    {
        "title": "Machine Learning Essentials",
        "description": "An introduction to machine learning concepts, algorithms, and applications.",
        "instructor": teacher,
        "modules": [
            {
                "title": "Supervised Learning",
                "description": "Learn about classification and regression techniques."
            },
            {
                "title": "Unsupervised Learning",
                "description": "Explore clustering and dimensionality reduction."
            }
        ]
    }
]

created_courses = 0
created_modules = 0
created_quizzes = 0
created_questions = 0
created_enrollments = 0

with transaction.atomic():
    for course_data in COURSES:
        # Create course
        course = Course.objects.create(
            title=course_data["title"],
            description=course_data["description"],
            instructor=course_data["instructor"],
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() + timedelta(days=60),
            enrollment_type="open",
            course_type="standard",
            analytics_enabled=True
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
                        passing_score=70
                    )
                    created_quizzes += 1
                    
                    # Create questions
                    for question_data in quiz_data.get("questions", []):
                        if question_data["type"] == "multiple_choice":
                            question = MultipleChoiceQuestion.objects.create(
                                quiz=quiz,
                                text=question_data["text"],
                                points=10
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
                                is_correct=question_data["is_correct"]
                            )
                            
                        created_questions += 1
            
            # Add a generic quiz if none specified
            else:
                quiz = Quiz.objects.create(
                    module=module,
                    title=f"{module_data['title']} Quiz",
                    description=f"Test your knowledge of {module_data['title']}",
                    time_limit_minutes=20,
                    passing_score=70
                )
                created_quizzes += 1
                
                # Create some generic questions
                for i in range(3):
                    if i % 2 == 0:
                        question = MultipleChoiceQuestion.objects.create(
                            quiz=quiz,
                            text=f"Sample multiple choice question {i+1} for {module_data['title']}?",
                            points=10
                        )
                        
                        # Create choices
                        question.choices.create(text="Option A", is_correct=True, order=1)
                        question.choices.create(text="Option B", is_correct=False, order=2)
                        question.choices.create(text="Option C", is_correct=False, order=3)
                        question.choices.create(text="Option D", is_correct=False, order=4)
                    else:
                        question = TrueFalseQuestion.objects.create(
                            quiz=quiz,
                            text=f"Sample true/false question {i+1} for {module_data['title']}.",
                            points=5,
                            is_correct=random.choice([True, False])
                        )
                        
                    created_questions += 1
        
        # Enroll students in courses
        for student in [student1, student2, student3]:
            Enrollment.objects.create(
                user=student,
                course=course,
                status="active",
                enrollment_date=timezone.now() - timedelta(days=random.randint(1, 20))
            )
            created_enrollments += 1

print(f"Created {created_courses} courses, {created_modules} modules, {created_quizzes} quizzes, and {created_questions} questions.")
print(f"Created {created_enrollments} student enrollments.")
print("Test content has been successfully created.")