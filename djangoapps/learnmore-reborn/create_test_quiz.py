#!/usr/bin/env python
import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import (
    Course, Module, Quiz, Question, MultipleChoiceQuestion, 
    TrueFalseQuestion, Choice, Enrollment
)

User = get_user_model()

def create_test_quiz():
    """Create a test quiz with sample questions for demonstration."""
    print("Creating test quiz data...")
    
    # Check if we have at least one user
    if not User.objects.exists():
        print("Creating a test user...")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        user.is_staff = True
        if hasattr(user, 'profile'):
            user.profile.is_instructor = True
            user.profile.save()
        user.save()
    else:
        user = User.objects.first()
        
    # Get or create a course
    course, created = Course.objects.get_or_create(
        title='Python Programming Basics',
        defaults={
            'slug': 'python-programming-basics',
            'description': 'Learn the basics of Python programming language.',
            'instructor': user,
            'status': 'published',
            'enrollment_type': 'open',
            'course_type': 'self_paced'
        }
    )
    if created:
        print(f"Created course: {course.title}")
    else:
        print(f"Using existing course: {course.title}")
    
    # Get or create a module
    module, created = Module.objects.get_or_create(
        title='Introduction to Python',
        course=course,
        defaults={
            'description': 'Introduction to Python programming language fundamentals.',
            'order': 1,
            'content_type': 'mixed',
            'estimated_time_minutes': 60,
            'content': '# Introduction to Python\n\nPython is a versatile programming language used for web development, data analysis, AI, and more.'
        }
    )
    if created:
        print(f"Created module: {module.title}")
    else:
        print(f"Using existing module: {module.title}")
    
    # Auto-enroll the user in the course
    enrollment, created = Enrollment.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            'status': 'active'
        }
    )
    if created:
        print(f"Enrolled user in course: {course.title}")
    
    # Create a quiz
    quiz, created = Quiz.objects.get_or_create(
        title='Python Basics Quiz',
        module=module,
        defaults={
            'description': 'Test your knowledge of Python basics',
            'instructions': 'Answer the following questions to test your understanding of Python basics.',
            'time_limit_minutes': 10,
            'passing_score': 70,
            'randomize_questions': False,
            'allow_multiple_attempts': True,
            'max_attempts': 3,
            'is_published': True
        }
    )
    if created:
        print(f"Created quiz: {quiz.title}")
    else:
        print(f"Using existing quiz: {quiz.title}")
        # Clear existing questions if quiz already exists
        quiz.questions.all().delete()
        print("Cleared existing questions")
    
    # Create multiple choice questions
    mcq1 = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text='What is the output of `print(2 + 2)`?',
        order=1,
        points=1,
        explanation='The `+` operator adds two numbers together.',
        allow_multiple=False
    )
    print(f"Created multiple choice question: {mcq1.text}")
    
    # Create choices for the first question
    Choice.objects.create(question=mcq1, text='2', is_correct=False, order=1, feedback='Incorrect. The `+` operator adds the values.')
    Choice.objects.create(question=mcq1, text='4', is_correct=True, order=2, feedback='Correct! 2 + 2 = 4')
    Choice.objects.create(question=mcq1, text='22', is_correct=False, order=3, feedback='Incorrect. That would be string concatenation with "2" + "2".')
    Choice.objects.create(question=mcq1, text='Error', is_correct=False, order=4, feedback='Incorrect. This is a valid Python expression.')
    
    # Create another multiple choice question with multiple correct answers
    mcq2 = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text='Which of the following are valid Python data types? (Select all that apply)',
        order=2,
        points=2,
        explanation='Python has several built-in data types including numbers, strings, lists, tuples, and dictionaries.',
        allow_multiple=True
    )
    print(f"Created multiple choice question: {mcq2.text}")
    
    # Create choices for the second question
    Choice.objects.create(question=mcq2, text='int', is_correct=True, order=1, feedback='Correct! int is a built-in numeric type.')
    Choice.objects.create(question=mcq2, text='string', is_correct=True, order=2, feedback='Correct! string is a built-in type for text.')
    Choice.objects.create(question=mcq2, text='array', is_correct=False, order=3, feedback='Incorrect. Python has lists rather than arrays in its built-in types.')
    Choice.objects.create(question=mcq2, text='dictionary', is_correct=True, order=4, feedback='Correct! dictionary is a built-in mapping type.')
    
    # Create true/false questions
    tf1 = TrueFalseQuestion.objects.create(
        quiz=quiz,
        text='Python is a compiled language.',
        order=3,
        points=1,
        explanation='Python is an interpreted language, not a compiled language.',
        correct_answer=False
    )
    print(f"Created true/false question: {tf1.text}")
    
    tf2 = TrueFalseQuestion.objects.create(
        quiz=quiz,
        text='In Python, indentation is important for defining code blocks.',
        order=4,
        points=1,
        explanation='Python uses indentation to define code blocks, unlike many other languages that use braces {}.',
        correct_answer=True
    )
    print(f"Created true/false question: {tf2.text}")
    
    print("Test quiz creation complete!")
    print(f"Quiz ID: {quiz.id}")
    print(f"Username: {user.username}")
    print("Password: testpassword")
    print(f"Course: {course.title} (slug: {course.slug})")
    
if __name__ == '__main__':
    create_test_quiz()