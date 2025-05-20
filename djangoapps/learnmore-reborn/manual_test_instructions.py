#!/usr/bin/env python
import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from courses.models import (
    Course, Quiz, QuizAttempt
)

User = get_user_model()

def get_test_instructions():
    """Generate manual testing instructions for the quiz system."""
    
    # Find a test user and quiz
    user = User.objects.first()
    if not user:
        print("No users found in the database.")
        return
    
    quiz = Quiz.objects.filter(is_published=True).first()
    if not quiz:
        print("No published quizzes found in the database.")
        return
    
    # Get course and module info
    course = quiz.module.course
    module = quiz.module
    
    # Get attempt info if available
    attempt = QuizAttempt.objects.filter(quiz=quiz, user=user).first()
    
    # Base URL
    base_url = "http://127.0.0.1:8000"
    
    print("\n=== MANUAL TESTING INSTRUCTIONS FOR QUIZ SYSTEM ===\n")
    print(f"Server is running at: {base_url}")
    print(f"Login credentials: {user.username} / testpassword\n")
    
    print("1. COURSE AND MODULE ACCESS")
    print(f"   - Course Detail: {base_url}/courses/course/{course.slug}/")
    print(f"   - Module Detail: {base_url}/courses/module/{module.id}/")
    
    print("\n2. QUIZ SYSTEM TESTING")
    print(f"   - Quiz List: {base_url}/courses/quizzes/")
    print(f"   - Quiz Detail: {base_url}/courses/quiz/{quiz.id}/")
    
    print("\n3. QUIZ ATTEMPT WORKFLOW")
    print(f"   - Start Quiz: Click 'Start Quiz' button on the quiz detail page")
    if attempt:
        if attempt.status == 'in_progress':
            print(f"   - Continue Attempt: {base_url}/courses/quiz-attempt/{attempt.id}/")
        else:
            print(f"   - View Results: {base_url}/courses/quiz-attempt/{attempt.id}/result/")
            print(f"   - View Attempt History: {base_url}/courses/quiz/{quiz.id}/attempts/")
    
    print("\n4. MANUAL TESTING STEPS")
    print("   a. Navigate to the Quiz List page and verify filtering works")
    print("   b. Go to a Quiz Detail page and view quiz information")
    print("   c. Start a new quiz attempt and answer questions")
    print("   d. Test question navigation and ensure responses are saved")
    print("   e. Finish the quiz to see results")
    print("   f. Check attempt history to see all attempts")
    print("   g. Verify quiz results show correct/incorrect answers properly")
    
    print("\n=== END OF INSTRUCTIONS ===\n")

if __name__ == '__main__':
    get_test_instructions()