"""
Script to create test data for courses and enrollments
Run with: python create_test_data.py
"""
import os
import django
import random
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Course, Module, Enrollment
from django.utils import timezone

User = get_user_model()

def create_test_data():
    # Create users if they don't exist
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        print(f"Created admin user: {admin_user.username}")
    else:
        admin_user = User.objects.get(username='admin')
        print(f"Using existing admin user: {admin_user.username}")
    
    # Create test users
    test_users = []
    for i in range(1, 6):
        username = f'user{i}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'user{i}@example.com',
                password='userpassword'
            )
            test_users.append(user)
            print(f"Created test user: {user.username}")
        else:
            user = User.objects.get(username=username)
            test_users.append(user)
            print(f"Using existing test user: {user.username}")
    
    # Create test instructors
    test_instructors = []
    for i in range(1, 4):
        username = f'instructor{i}'
        if not User.objects.filter(username=username).exists():
            instructor = User.objects.create_user(
                username=username,
                email=f'instructor{i}@example.com',
                password='instructorpassword'
            )
            test_instructors.append(instructor)
            print(f"Created test instructor: {instructor.username}")
        else:
            instructor = User.objects.get(username=username)
            test_instructors.append(instructor)
            print(f"Using existing test instructor: {instructor.username}")
    
    # Sample course data
    course_data = [
        {
            'title': 'Introduction to Python Programming',
            'description': 'Learn the basics of Python programming language. This course covers variables, data types, control flow, functions, and more.',
            'status': 'published',
            'enrollment_type': 'open',
            'max_students': 50,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=90),
        },
        {
            'title': 'Web Development with Django',
            'description': 'Master web development using Django framework. Build robust and scalable web applications with Python and Django.',
            'status': 'published',
            'enrollment_type': 'open',
            'max_students': 30,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=120),
        },
        {
            'title': 'Data Science Fundamentals',
            'description': 'Explore the world of data science using Python libraries like NumPy, Pandas, and Matplotlib. Learn data manipulation, visualization, and basic machine learning concepts.',
            'status': 'published',
            'enrollment_type': 'restricted',
            'max_students': 25,
            'start_date': timezone.now() + timedelta(days=30),
            'end_date': timezone.now() + timedelta(days=150),
        },
        {
            'title': 'Advanced JavaScript',
            'description': 'Take your JavaScript skills to the next level with advanced concepts like closures, prototypes, async/await, and modern ES6+ features.',
            'status': 'published',
            'enrollment_type': 'open',
            'max_students': 0,  # Unlimited
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=60),
        },
        {
            'title': 'DevOps for Beginners',
            'description': 'Learn the principles and practices of DevOps. Explore tools like Docker, Kubernetes, Jenkins, and more.',
            'status': 'draft',
            'enrollment_type': 'open',
            'max_students': 40,
            'start_date': timezone.now() + timedelta(days=45),
            'end_date': timezone.now() + timedelta(days=135),
        }
    ]
    
    # Create courses
    courses = []
    for data in course_data:
        # Randomly select an instructor
        instructor = random.choice(test_instructors)
        
        # Check if course already exists
        if not Course.objects.filter(title=data['title']).exists():
            course = Course.objects.create(
                title=data['title'],
                description=data['description'],
                status=data['status'],
                enrollment_type=data['enrollment_type'],
                max_students=data['max_students'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                instructor=instructor
            )
            courses.append(course)
            print(f"Created course: {course.title}")
        else:
            course = Course.objects.get(title=data['title'])
            courses.append(course)
            print(f"Using existing course: {course.title}")
    
    # Create modules for each course
    for course in courses:
        # Skip if course already has modules
        if Module.objects.filter(course=course).exists():
            print(f"Course '{course.title}' already has modules. Skipping module creation.")
            continue
        
        # Create 3-5 modules per course
        num_modules = random.randint(3, 5)
        for i in range(1, num_modules + 1):
            module = Module.objects.create(
                course=course,
                title=f"Module {i}: {course.title} - Part {i}",
                description=f"This is module {i} of {course.title}. It covers essential topics related to this part of the course.",
                order=i
            )
            print(f"Created module: {module.title} for course: {course.title}")
    
    # Create enrollments
    published_courses = Course.objects.filter(status='published')
    for user in test_users:
        # Enroll user in 1-3 random courses
        num_enrollments = random.randint(1, min(3, len(published_courses)))
        courses_to_enroll = random.sample(list(published_courses), num_enrollments)
        
        for course in courses_to_enroll:
            # Skip if user is already enrolled
            if Enrollment.objects.filter(user=user, course=course).exists():
                print(f"User '{user.username}' is already enrolled in '{course.title}'. Skipping enrollment.")
                continue
            
            enrollment = Enrollment.objects.create(
                user=user,
                course=course,
                status='active',
                progress=random.randint(0, 100)
            )
            print(f"Enrolled user: {user.username} in course: {course.title}")
    
    print("\nTest data creation complete!")

if __name__ == '__main__':
    create_test_data()