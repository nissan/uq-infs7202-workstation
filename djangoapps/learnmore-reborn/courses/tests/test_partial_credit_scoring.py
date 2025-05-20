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

from courses.models import (
    Course, Module, Quiz, MultipleChoiceQuestion, Choice,
    QuizAttempt, QuestionResponse
)

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
    
    student = User.objects.create_user(
        username='student',
        email='student@example.com',
        password='testpass123'
    )
    
    return {
        'instructor': instructor,
        'student': student
    }

@pytest.fixture
def setup_course_with_partial_credit_quiz(setup_users):
    """Create a course with a module containing a quiz with partial credit questions"""
    instructor = setup_users['instructor']
    
    # Create course and module
    course = Course.objects.create(
        title="Partial Credit Course",
        description="Course for testing partial credit scoring",
        instructor=instructor,
        status='published'
    )
    
    module = Module.objects.create(
        course=course,
        title="Scoring Module",
        description="Module with partial credit questions",
        order=1
    )
    
    # Create quiz
    quiz = Quiz.objects.create(
        module=module,
        title="Partial Credit Quiz",
        description="Testing advanced scoring features",
        instructions="Select the best answers",
        passing_score=70,
        is_published=True
    )
    
    # Create a standard multiple choice question
    standard_mcq = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text="Which of the following are programming languages?",
        order=1,
        points=10,
        allow_multiple=True,
        use_partial_credit=False
    )
    
    # Create choices for standard question
    Choice.objects.create(question=standard_mcq, text="Python", is_correct=True, order=0)
    Choice.objects.create(question=standard_mcq, text="Java", is_correct=True, order=1)
    Choice.objects.create(question=standard_mcq, text="HTML", is_correct=False, order=2)
    Choice.objects.create(question=standard_mcq, text="CSS", is_correct=False, order=3)
    
    # Create a partial credit multiple choice question
    partial_mcq = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text="Rate your familiarity with the following technologies:",
        order=2,
        points=10,
        allow_multiple=True,
        use_partial_credit=True,
        minimum_score=0
    )
    
    # Create choices with point values for partial credit question
    Choice.objects.create(
        question=partial_mcq, 
        text="Expert in Python", 
        is_correct=True, 
        points_value=5, 
        order=0
    )
    Choice.objects.create(
        question=partial_mcq, 
        text="Familiar with Java", 
        is_correct=True, 
        points_value=3, 
        order=1
    )
    Choice.objects.create(
        question=partial_mcq, 
        text="No experience with Ruby", 
        is_correct=False, 
        points_value=-2, 
        order=2
    )
    Choice.objects.create(
        question=partial_mcq, 
        text="I don't use any of these", 
        is_correct=False, 
        is_neutral=True, 
        points_value=0, 
        order=3
    )
    
    # Create another partial credit question with minimum score
    minimum_mcq = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text="Select the best frameworks for web development:",
        order=3,
        points=10,
        allow_multiple=True,
        use_partial_credit=True,
        minimum_score=2  # At least 2 points even with negative selections
    )
    
    # Create choices with point values including negative
    Choice.objects.create(
        question=minimum_mcq, 
        text="Django", 
        is_correct=True, 
        points_value=4, 
        order=0
    )
    Choice.objects.create(
        question=minimum_mcq, 
        text="React", 
        is_correct=True, 
        points_value=4, 
        order=1
    )
    Choice.objects.create(
        question=minimum_mcq, 
        text="Flask", 
        is_correct=True, 
        points_value=3, 
        order=2
    )
    Choice.objects.create(
        question=minimum_mcq, 
        text="Notepad", 
        is_correct=False, 
        points_value=-5, 
        order=3
    )
    
    # Enroll the student in the course
    course.enrollments.create(user=setup_users['student'], status='active')
    
    return {
        'course': course,
        'module': module,
        'quiz': quiz,
        'standard_mcq': standard_mcq,
        'partial_mcq': partial_mcq,
        'minimum_mcq': minimum_mcq
    }

@pytest.mark.django_db
def test_standard_multiple_choice_scoring(setup_users, setup_course_with_partial_credit_quiz, client):
    """Test standard multiple choice scoring (all or nothing)"""
    student = setup_users['student']
    quiz = setup_course_with_partial_credit_quiz['quiz']
    standard_mcq = setup_course_with_partial_credit_quiz['standard_mcq']
    
    # Get the choices
    choices = list(standard_mcq.choices.all())
    correct_choices = [c.id for c in choices if c.is_correct]
    incorrect_choices = [c.id for c in choices if not c.is_correct]
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Start a quiz attempt
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Test 1: All correct choices selected - should get full points
    data = {
        'question_id': standard_mcq.id,
        'choices[]': correct_choices,
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, standard_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify correct scoring
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=standard_mcq
    )
    assert question_response.is_correct
    assert question_response.points_earned == standard_mcq.points
    
    # Reset for next test
    question_response.delete()
    
    # Test 2: Missing one correct choice - should get zero points
    data = {
        'question_id': standard_mcq.id,
        'choices[]': [correct_choices[0]],  # Only one of the correct choices
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, standard_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify scoring
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=standard_mcq
    )
    assert not question_response.is_correct
    assert question_response.points_earned == 0
    
    # Reset for next test
    question_response.delete()
    
    # Test 3: One correct and one incorrect choice - should get zero points
    data = {
        'question_id': standard_mcq.id,
        'choices[]': [correct_choices[0], incorrect_choices[0]],
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, standard_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify scoring
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=standard_mcq
    )
    assert not question_response.is_correct
    assert question_response.points_earned == 0

@pytest.mark.django_db
def test_partial_credit_scoring(setup_users, setup_course_with_partial_credit_quiz, client):
    """Test partial credit scoring for multiple choice questions"""
    student = setup_users['student']
    quiz = setup_course_with_partial_credit_quiz['quiz']
    partial_mcq = setup_course_with_partial_credit_quiz['partial_mcq']
    
    # Get the choices
    choices = list(partial_mcq.choices.all())
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Start a quiz attempt
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Test 1: Selecting choices with positive points (5 + 3 = 8 points)
    data = {
        'question_id': partial_mcq.id,
        'choices[]': [choices[0].id, choices[1].id],  # 5 points + 3 points
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, partial_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify partial credit scoring
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=partial_mcq
    )
    assert question_response.points_earned == 8
    
    # Reset for next test
    question_response.delete()
    
    # Test 2: Selecting a mix of positive and negative (5 + 3 - 2 = 6 points)
    data = {
        'question_id': partial_mcq.id,
        'choices[]': [choices[0].id, choices[1].id, choices[2].id],  # 5 points + 3 points - 2 points
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, partial_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify partial credit scoring
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=partial_mcq
    )
    assert question_response.points_earned == 6
    
    # Reset for next test
    question_response.delete()
    
    # Test 3: Selecting neutral choice should not affect score (5 points + 0 points = 5 points)
    data = {
        'question_id': partial_mcq.id,
        'choices[]': [choices[0].id, choices[3].id],  # 5 points + 0 points (neutral)
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, partial_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify partial credit scoring
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=partial_mcq
    )
    assert question_response.points_earned == 5
    
    # Reset for next test
    question_response.delete()
    
    # Test 4: Only negative points should give 0 (minimum score is 0 for this question)
    data = {
        'question_id': partial_mcq.id,
        'choices[]': [choices[2].id],  # -2 points
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, partial_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify minimum score is enforced
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=partial_mcq
    )
    assert question_response.points_earned == 0  # Min score is 0

@pytest.mark.django_db
def test_minimum_score_enforcement(setup_users, setup_course_with_partial_credit_quiz, client):
    """Test that minimum score is enforced for partial credit questions"""
    student = setup_users['student']
    quiz = setup_course_with_partial_credit_quiz['quiz']
    minimum_mcq = setup_course_with_partial_credit_quiz['minimum_mcq']
    
    # Get the choices
    choices = list(minimum_mcq.choices.all())
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Start a quiz attempt
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Test 1: Selecting only negative points (-5) should result in minimum score (2)
    data = {
        'question_id': minimum_mcq.id,
        'choices[]': [choices[3].id],  # -5 points (Notepad)
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, minimum_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify minimum score is enforced
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=minimum_mcq
    )
    assert question_response.points_earned == 2  # Min score is 2
    
    # Reset for next test
    question_response.delete()
    
    # Test 2: Mixed positive and negative but still below minimum (4 - 5 = -1, should be 2)
    data = {
        'question_id': minimum_mcq.id,
        'choices[]': [choices[0].id, choices[3].id],  # 4 points (Django) - 5 points (Notepad)
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, minimum_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify minimum score is enforced
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=minimum_mcq
    )
    assert question_response.points_earned == 2  # Min score is 2
    
    # Reset for next test
    question_response.delete()
    
    # Test 3: Above minimum but below maximum (4 + 3 = 7)
    data = {
        'question_id': minimum_mcq.id,
        'choices[]': [choices[0].id, choices[2].id],  # 4 points (Django) + 3 points (Flask)
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, minimum_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify score calculation
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=minimum_mcq
    )
    assert question_response.points_earned == 7
    
    # Reset for next test
    question_response.delete()
    
    # Test 4: Above maximum (4 + 4 + 3 = 11, should be capped at 10)
    data = {
        'question_id': minimum_mcq.id,
        'choices[]': [choices[0].id, choices[1].id, choices[2].id],  # 4 + 4 + 3 = 11 points
        'time_spent': 60
    }
    
    response = client.post(reverse('submit-answer', args=[attempt.id, minimum_mcq.id]), data)
    assert response.status_code == 302
    
    # Verify maximum points capping
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=minimum_mcq
    )
    assert question_response.points_earned == 10  # Max is 10 (question.points)

@pytest.mark.django_db
def test_partial_credit_integration(setup_users, setup_course_with_partial_credit_quiz, client):
    """Test integration of partial credit questions in a complete quiz attempt"""
    student = setup_users['student']
    quiz = setup_course_with_partial_credit_quiz['quiz']
    standard_mcq = setup_course_with_partial_credit_quiz['standard_mcq']
    partial_mcq = setup_course_with_partial_credit_quiz['partial_mcq']
    minimum_mcq = setup_course_with_partial_credit_quiz['minimum_mcq']
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Start a quiz attempt
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Answer all questions in one go
    
    # Answer standard MCQ correctly (10 points)
    std_choices = list(standard_mcq.choices.all())
    std_correct_choices = [c.id for c in std_choices if c.is_correct]
    
    data = {
        'question_id': standard_mcq.id,
        'choices[]': std_correct_choices,
        'time_spent': 60
    }
    response = client.post(reverse('submit-answer', args=[attempt.id, standard_mcq.id]), data)
    assert response.status_code == 302
    
    # Answer partial credit MCQ (8 points: 5 + 3)
    partial_choices = list(partial_mcq.choices.all())
    data = {
        'question_id': partial_mcq.id,
        'choices[]': [partial_choices[0].id, partial_choices[1].id],
        'time_spent': 60
    }
    response = client.post(reverse('submit-answer', args=[attempt.id, partial_mcq.id]), data)
    assert response.status_code == 302
    
    # Answer minimum score MCQ (7 points: 4 + 3)
    min_choices = list(minimum_mcq.choices.all())
    data = {
        'question_id': minimum_mcq.id,
        'choices[]': [min_choices[0].id, min_choices[2].id],
        'time_spent': 60
    }
    response = client.post(reverse('submit-answer', args=[attempt.id, minimum_mcq.id]), data)
    assert response.status_code == 302
    
    # Complete the quiz
    response = client.post(reverse('finish-quiz', args=[attempt.id]))
    assert response.status_code == 302
    
    # Verify the attempt score
    attempt.refresh_from_db()
    assert attempt.score == 25  # 10 + 8 + 7 = 25
    assert attempt.max_score == 30  # 3 questions * 10 points = 30
    assert attempt.is_passed  # 25/30 = 83.3%, passing score is 70%