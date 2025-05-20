try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    import unittest
    
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import json
import time

from courses.models import (
    Course, Module, Quiz, EssayQuestion, QuizAttempt, QuestionResponse,
    QuestionAnalytics, QuizAnalytics
)
from progress.models import Progress, ModuleProgress

User = get_user_model()

# Skip module if pytest isn't available
if not PYTEST_AVAILABLE:
    raise unittest.SkipTest("Pytest not available")

@pytest.fixture
def setup_users():
    """Create test users"""
    instructor = User.objects.create_user(
        username='instructor',
        email='instructor@example.com',
        password='testpass123'
    )
    instructor.profile.is_instructor = True
    instructor.profile.save()
    
    students = []
    for i in range(3):
        student = User.objects.create_user(
            username=f'student{i+1}',
            email=f'student{i+1}@example.com',
            password='testpass123'
        )
        students.append(student)
    
    return {
        'instructor': instructor,
        'students': students
    }

@pytest.fixture
def setup_course_with_essay_quiz(setup_users):
    """Create a course with a module containing an essay question quiz"""
    instructor = setup_users['instructor']
    
    # Create course and module
    course = Course.objects.create(
        title="Essay Testing Course",
        description="Course for testing essay question functionality",
        instructor=instructor,
        status='published'
    )
    
    module = Module.objects.create(
        course=course,
        title="Essay Module",
        description="Module with essay questions",
        order=1
    )
    
    # Create quiz with essay questions
    quiz = Quiz.objects.create(
        module=module,
        title="Essay Integration Quiz",
        description="Testing essay question integration",
        instructions="Answer all questions thoughtfully",
        passing_score=70,
        is_published=True,
        randomize_questions=False
    )
    
    # Create multiple essay questions
    essay_questions = []
    for i in range(3):
        question = EssayQuestion.objects.create(
            quiz=quiz,
            text=f"Essay Question {i+1}: {['Explain the software testing process.', 'Discuss the benefits of code reviews.', 'Describe continuous integration practices.'][i]}",
            order=i+1,
            points=10,
            min_word_count=50,
            max_word_count=500,
            rubric=f"Detailed rubric for question {i+1}",
            example_answer=f"Example answer for question {i+1}..."
        )
        essay_questions.append(question)
    
    # Enroll the students in the course
    for student in setup_users['students']:
        course.enrollments.create(user=student, status='active')
    
    return {
        'course': course,
        'module': module,
        'quiz': quiz,
        'essay_questions': essay_questions
    }

@pytest.mark.integration
@pytest.mark.django_db
def test_complete_essay_quiz_workflow(setup_users, setup_course_with_essay_quiz, client):
    """
    Test the entire workflow from student taking an essay quiz to instructor
    grading responses and checking progress tracking.
    """
    student = setup_users['students'][0]
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_questions = setup_course_with_essay_quiz['essay_questions']
    
    # 1. Student logs in and starts quiz
    client.login(username=student.username, password='testpass123')
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # 2. Student answers each essay question
    for i, question in enumerate(essay_questions):
        essay_text = f"This is my answer to question {i+1} about {question.text.split(':')[1][:20]}... " * 20
        
        data = {
            'question_id': question.id,
            'essay_text': essay_text,
            'time_spent': 180 + (i * 60)  # 3, 4, 5 minutes per question
        }
        
        response = client.post(reverse('submit-response', args=[attempt.id]), data)
        assert response.status_code == 302
    
    # 3. Student completes the quiz
    response = client.post(reverse('complete-quiz', args=[attempt.id]))
    assert response.status_code == 302
    
    # 4. Instructor logs in to grade essays
    client.logout()
    client.login(username=instructor.username, password='testpass123')
    
    # 5. Check pending grading
    response = client.get(reverse('pending-essay-grading', args=[quiz.id]))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "3 responses pending grading" in content
    
    # 6. Get all responses to grade
    responses = QuestionResponse.objects.filter(
        attempt=attempt,
        question__question_type='essay',
        graded_at__isnull=True
    ).order_by('question__order')
    
    # 7. Instructor grades each essay
    for i, response_obj in enumerate(responses):
        # Vary the grades to test scoring
        points = [7, 8, 9][i]  # 7, 8, 9 points for the three questions
        
        grading_data = {
            'points': points,
            'feedback': f'Good essay on {response_obj.question.text.split(":")[1][:20]}, but could use more detail.'
        }
        
        response = client.post(reverse('grade-essay-response', args=[response_obj.id]), grading_data)
        assert response.status_code == 302
    
    # 8. Verify all responses are graded
    responses = QuestionResponse.objects.filter(attempt=attempt)
    for response_obj in responses:
        assert response_obj.graded_at is not None
        assert response_obj.points_earned > 0
        assert response_obj.instructor_comment is not None
    
    # 9. Check the attempt score
    attempt.refresh_from_db()
    assert attempt.score == 24  # 7 + 8 + 9 = 24
    assert attempt.max_score == 30  # 3 questions * 10 points = 30
    assert attempt.is_passed  # 24/30 = 80%, passing score is 70%
    
    # 10. Check progress tracking integration
    module_progress = ModuleProgress.objects.get(
        progress__user=student,
        module=setup_course_with_essay_quiz['module']
    )
    assert module_progress.status == 'completed'

@pytest.mark.integration
@pytest.mark.django_db
def test_essay_analytics_integration(setup_users, setup_course_with_essay_quiz, client):
    """
    Test the integration of essay questions with the analytics system, including 
    calculation of metrics across multiple students and attempts.
    """
    students = setup_users['students']
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_questions = setup_course_with_essay_quiz['essay_questions']
    
    api_client = APIClient()
    
    # Have each student take the quiz and submit different quality responses
    for student_idx, student in enumerate(students):
        # Student logs in
        client.login(username=student.username, password='testpass123')
        
        # Start quiz
        response = client.post(reverse('start-quiz', args=[quiz.id]))
        assert response.status_code == 302
        
        # Get the attempt
        attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
        
        # Answer each essay question
        for question_idx, question in enumerate(essay_questions):
            # Make different quality answers based on student index
            quality = ["poor", "average", "excellent"][student_idx]
            essay_text = f"This is a {quality} quality answer to the question about {question.text.split(':')[1][:20]}... " * 20
            
            data = {
                'question_id': question.id,
                'essay_text': essay_text,
                'time_spent': 180 + (question_idx * 60)  # 3, 4, 5 minutes
            }
            
            response = client.post(reverse('submit-response', args=[attempt.id]), data)
            assert response.status_code == 302
        
        # Complete the quiz
        response = client.post(reverse('complete-quiz', args=[attempt.id]))
        assert response.status_code == 302
        
        client.logout()
    
    # Instructor logs in to grade essays
    client.login(username=instructor.username, password='testpass123')
    api_client.force_authenticate(user=instructor)
    
    # Get all ungraded responses
    responses = QuestionResponse.objects.filter(
        question__quiz=quiz,
        question__question_type='essay',
        graded_at__isnull=True
    ).order_by('attempt__user', 'question__order')
    
    # Grade each essay with different scores based on student and question
    for response_obj in responses:
        student_idx = students.index(response_obj.attempt.user)
        question_idx = essay_questions.index(response_obj.question.essayquestion)
        
        # Score matrix: students get different scores based on their index
        score_matrix = [
            [5, 4, 3],  # Student 1 scores
            [7, 6, 8],  # Student 2 scores
            [9, 10, 9]  # Student 3 scores
        ]
        
        points = score_matrix[student_idx][question_idx]
        
        grading_data = {
            'points': points,
            'feedback': f'This response received {points} out of 10 points.'
        }
        
        # Use API for grading
        response = api_client.post(f'/api/courses/responses/{response_obj.id}/grade/', grading_data)
        assert response.status_code == status.HTTP_200_OK
    
    # Recalculate analytics
    response = api_client.post(f'/api/courses/quizzes/{quiz.id}/recalculate_analytics/')
    assert response.status_code == status.HTTP_200_OK
    
    # Check quiz analytics
    response = api_client.get(f'/api/courses/quizzes/{quiz.id}/analytics/')
    assert response.status_code == status.HTTP_200_OK
    quiz_analytics = response.json()
    
    # Verify quiz metrics
    assert quiz_analytics['total_attempts'] == 3
    assert quiz_analytics['completed_attempts'] == 3
    assert quiz_analytics['passing_attempts'] == 2  # Students 2 and 3 passed, Student 1 failed
    
    # The average score should be (12 + 21 + 28) / 3 = 20.33 out of 30, or ~67.8%
    assert 67.0 <= float(quiz_analytics['avg_score']) <= 68.0
    
    # Check individual question analytics
    for question in essay_questions:
        response = api_client.get(f'/api/courses/questions/{question.id}/analytics/')
        assert response.status_code == status.HTTP_200_OK
        question_analytics = response.json()
        
        # Each question has 3 attempts (one from each student)
        assert question_analytics['total_attempts'] == 3
        
        # Calculate expected correct attempts based on scoring
        question_idx = essay_questions.index(question)
        scores = [
            [5, 4, 3],  # Student 1 scores
            [7, 6, 8],  # Student 2 scores
            [9, 10, 9]  # Student 3 scores
        ]
        
        correct_attempts = sum(1 for i in range(3) if scores[i][question_idx] >= 7)
        assert question_analytics['correct_attempts'] == correct_attempts

@pytest.mark.integration
@pytest.mark.django_db
def test_essay_question_with_progress_tracking(setup_users, setup_course_with_essay_quiz, client):
    """
    Test the integration of essay questions with the progress tracking system.
    """
    student = setup_users['students'][0]
    instructor = setup_users['instructor']
    course = setup_course_with_essay_quiz['course']
    module = setup_course_with_essay_quiz['module']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_questions = setup_course_with_essay_quiz['essay_questions']
    
    # 1. Student logs in and starts quiz
    client.login(username=student.username, password='testpass123')
    
    # Check initial progress (should be empty)
    progress, created = Progress.objects.get_or_create(user=student, course=course)
    module_progress, created = ModuleProgress.objects.get_or_create(progress=progress, module=module)
    assert module_progress.status != 'completed'
    
    # 2. Start and take the quiz
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302
    
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Answer all questions
    for question in essay_questions:
        data = {
            'question_id': question.id,
            'essay_text': f"This is my answer to {question.text}. " * 20,
            'time_spent': 240  # 4 minutes
        }
        
        response = client.post(reverse('submit-response', args=[attempt.id]), data)
        assert response.status_code == 302
    
    # Complete the quiz
    response = client.post(reverse('complete-quiz', args=[attempt.id]))
    assert response.status_code == 302
    
    # Progress should not be updated yet since essays need grading
    module_progress.refresh_from_db()
    assert module_progress.status != 'completed'
    
    # 3. Instructor logs in to grade
    client.logout()
    client.login(username=instructor.username, password='testpass123')
    
    # Grade all responses with passing scores
    responses = QuestionResponse.objects.filter(
        attempt=attempt,
        graded_at__isnull=True
    )
    
    for response_obj in responses:
        grading_data = {
            'points': 8,  # 8/10 points is a passing grade
            'feedback': 'Good essay response.'
        }
        
        response = client.post(reverse('grade-essay-response', args=[response_obj.id]), grading_data)
        assert response.status_code == 302
    
    # 4. Verify the attempt is now passed
    attempt.refresh_from_db()
    assert attempt.is_passed
    
    # 5. Check that module progress is updated
    module_progress.refresh_from_db()
    assert module_progress.status == 'completed'
    assert module_progress.completed_at is not None
    
    # 6. Check course progress percentage
    progress.refresh_from_db()
    # With one module completed out of one total, progress should be 100%
    assert progress.calculate_percentage() == 100

@pytest.mark.integration
@pytest.mark.django_db
def test_essay_question_with_timed_quiz(setup_users, setup_course_with_essay_quiz, client):
    """
    Test essay questions within a timed quiz context.
    """
    student = setup_users['students'][0]
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_questions = setup_course_with_essay_quiz['essay_questions']
    
    # Set a time limit on the quiz
    quiz.time_limit_minutes = 10
    quiz.save()
    
    # 1. Student logs in and starts quiz
    client.login(username=student.username, password='testpass123')
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Answer only 2 out of 3 questions (simulating time running out)
    for i, question in enumerate(essay_questions[:2]):
        data = {
            'question_id': question.id,
            'essay_text': f"This is my answer to question {i+1}. " * 20,
            'time_spent': 240  # 4 minutes each
        }
        
        response = client.post(reverse('submit-response', args=[attempt.id]), data)
        assert response.status_code == 302
    
    # Simulate timeout
    attempt.status = 'timed_out'
    attempt.completed_at = timezone.now()
    attempt.save()
    
    # 2. Instructor logs in to grade
    client.logout()
    client.login(username=instructor.username, password='testpass123')
    
    # Grade the submitted responses
    responses = QuestionResponse.objects.filter(
        attempt=attempt,
        graded_at__isnull=True
    )
    
    # Verify only 2 responses to grade
    assert responses.count() == 2
    
    for response_obj in responses:
        grading_data = {
            'points': 8,
            'feedback': 'Good essay response, despite time constraints.'
        }
        
        response = client.post(reverse('grade-essay-response', args=[response_obj.id]), grading_data)
        assert response.status_code == 302
    
    # 3. Check the attempt score
    attempt.refresh_from_db()
    # 16 points earned out of 30 possible = 53.3% (below 70% passing threshold)
    assert attempt.score == 16
    assert attempt.max_score == 30
    assert not attempt.is_passed