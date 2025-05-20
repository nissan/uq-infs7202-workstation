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
def setup_course_with_normalized_quiz(setup_users):
    """Create a course with a module containing a quiz with normalized questions"""
    instructor = setup_users['instructor']
    
    # Create course and module
    course = Course.objects.create(
        title="Score Normalization Course",
        description="Course for testing score normalization",
        instructor=instructor,
        status='published'
    )
    
    module = Module.objects.create(
        course=course,
        title="Normalization Module",
        description="Module with normalized questions",
        order=1
    )
    
    # Create quiz
    quiz = Quiz.objects.create(
        module=module,
        title="Score Normalization Quiz",
        description="Testing score normalization features",
        instructions="Answer the questions",
        passing_score=70,
        is_published=True
    )
    
    # Create question with z-score normalization
    zscore_mcq = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text="Question with Z-Score normalization",
        order=1,
        points=10,
        allow_multiple=True,
        use_partial_credit=True,
        normalization_method='zscore',
        normalization_parameters={
            'mean': 5,
            'std_dev': 2
        }
    )
    
    # Create choices for z-score question
    Choice.objects.create(question=zscore_mcq, text="Choice 1", is_correct=True, points_value=2, order=0)
    Choice.objects.create(question=zscore_mcq, text="Choice 2", is_correct=True, points_value=3, order=1)
    Choice.objects.create(question=zscore_mcq, text="Choice 3", is_correct=True, points_value=4, order=2)
    Choice.objects.create(question=zscore_mcq, text="Choice 4", is_correct=False, points_value=-1, order=3)
    
    # Create question with min-max normalization
    minmax_mcq = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text="Question with Min-Max normalization",
        order=2,
        points=10,
        allow_multiple=True,
        use_partial_credit=True,
        normalization_method='minmax',
        normalization_parameters={
            'input_min': 0,
            'input_max': 9,
            'output_min': 1,
            'output_max': 10
        }
    )
    
    # Create choices for min-max question
    Choice.objects.create(question=minmax_mcq, text="Choice 1", is_correct=True, points_value=2, order=0)
    Choice.objects.create(question=minmax_mcq, text="Choice 2", is_correct=True, points_value=3, order=1)
    Choice.objects.create(question=minmax_mcq, text="Choice 3", is_correct=True, points_value=4, order=2)
    Choice.objects.create(question=minmax_mcq, text="Choice 4", is_correct=False, points_value=-1, order=3)
    
    # Create question with custom normalization
    custom_mcq = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text="Question with Custom normalization",
        order=3,
        points=10,
        allow_multiple=True,
        use_partial_credit=True,
        normalization_method='custom',
        normalization_parameters={
            'mapping': {
                '1': 3,
                '2': 4,
                '3': 5,
                '4': 6,
                '5': 7,
                '6': 8,
                '7': 9,
                '8': 9,
                '9': 10
            }
        }
    )
    
    # Create choices for custom question
    Choice.objects.create(question=custom_mcq, text="Choice 1", is_correct=True, points_value=2, order=0)
    Choice.objects.create(question=custom_mcq, text="Choice 2", is_correct=True, points_value=3, order=1)
    Choice.objects.create(question=custom_mcq, text="Choice 3", is_correct=True, points_value=4, order=2)
    Choice.objects.create(question=custom_mcq, text="Choice 4", is_correct=False, points_value=-1, order=3)
    
    # Enroll the student in the course
    course.enrollments.create(user=setup_users['student'], status='active')
    
    return {
        'course': course,
        'module': module,
        'quiz': quiz,
        'zscore_mcq': zscore_mcq,
        'minmax_mcq': minmax_mcq,
        'custom_mcq': custom_mcq
    }

@pytest.mark.django_db
def test_zscore_normalization(setup_users, setup_course_with_normalized_quiz):
    """Test Z-Score normalization directly on the model"""
    zscore_mcq = setup_course_with_normalized_quiz['zscore_mcq']
    
    # Get the choices
    choices = list(zscore_mcq.choices.all())
    
    # Test with different scores
    
    # Test 1: Score of 2
    is_correct, points, feedback = zscore_mcq.check_answer([choices[0].id])  # 2 points
    
    # Z-score: (2 - 5) / 2 = -1.5
    # Normalized: -1.5 * (10/4) + 5 = -1.5 * 2.5 + 5 = -3.75 + 5 = 1.25 ≈ 1
    assert points == 1
    
    # Test 2: Score of 5
    is_correct, points, feedback = zscore_mcq.check_answer([choices[0].id, choices[1].id])  # 2 + 3 = 5 points
    
    # Z-score: (5 - 5) / 2 = 0
    # Normalized: 0 * 2.5 + 5 = 5
    assert points == 5
    
    # Test 3: Score of 9
    is_correct, points, feedback = zscore_mcq.check_answer([choices[0].id, choices[1].id, choices[2].id])  # 2 + 3 + 4 = 9 points
    
    # Z-score: (9 - 5) / 2 = 2
    # Normalized: 2 * 2.5 + 5 = 5 + 5 = 10
    assert points == 10  # Capped at maximum points

@pytest.mark.django_db
def test_minmax_normalization(setup_users, setup_course_with_normalized_quiz):
    """Test Min-Max normalization directly on the model"""
    minmax_mcq = setup_course_with_normalized_quiz['minmax_mcq']
    
    # Get the choices
    choices = list(minmax_mcq.choices.all())
    
    # Test with different scores
    
    # Test 1: Score of 2
    is_correct, points, feedback = minmax_mcq.check_answer([choices[0].id])  # 2 points
    
    # Min-Max: 1 + (2 - 0) * (10 - 1) / (9 - 0) = 1 + 2 * 1 = 3
    assert points == 3
    
    # Test 2: Score of 5
    is_correct, points, feedback = minmax_mcq.check_answer([choices[0].id, choices[1].id])  # 2 + 3 = 5 points
    
    # Min-Max: 1 + (5 - 0) * (10 - 1) / (9 - 0) = 1 + 5 * 1 = 6
    assert points == 6
    
    # Test 3: Score of 9
    is_correct, points, feedback = minmax_mcq.check_answer([choices[0].id, choices[1].id, choices[2].id])  # 2 + 3 + 4 = 9 points
    
    # Min-Max: 1 + (9 - 0) * (10 - 1) / (9 - 0) = 1 + 9 * 1 = 10
    assert points == 10

@pytest.mark.django_db
def test_custom_normalization(setup_users, setup_course_with_normalized_quiz):
    """Test Custom normalization directly on the model"""
    custom_mcq = setup_course_with_normalized_quiz['custom_mcq']
    
    # Get the choices
    choices = list(custom_mcq.choices.all())
    
    # Test with different scores
    
    # Test 1: Score of 2
    is_correct, points, feedback = custom_mcq.check_answer([choices[0].id])  # 2 points
    
    # Custom: Mapping '2' -> 4
    assert points == 4
    
    # Test 2: Score of 5
    is_correct, points, feedback = custom_mcq.check_answer([choices[0].id, choices[1].id])  # 2 + 3 = 5 points
    
    # Custom: Mapping '5' -> 7
    assert points == 7
    
    # Test 3: Score of 9
    is_correct, points, feedback = custom_mcq.check_answer([choices[0].id, choices[1].id, choices[2].id])  # 2 + 3 + 4 = 9 points
    
    # Custom: Mapping '9' -> 10
    assert points == 10

@pytest.mark.django_db
def test_normalization_in_quiz_attempt(setup_users, setup_course_with_normalized_quiz, client):
    """Test normalization in a complete quiz attempt flow"""
    student = setup_users['student']
    quiz = setup_course_with_normalized_quiz['quiz']
    zscore_mcq = setup_course_with_normalized_quiz['zscore_mcq']
    minmax_mcq = setup_course_with_normalized_quiz['minmax_mcq']
    custom_mcq = setup_course_with_normalized_quiz['custom_mcq']
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Start a quiz attempt
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Answer all questions in one go
    
    # Answer Z-Score question (2 + 3 = 5 points -> normalized to 5 points)
    zscore_choices = list(zscore_mcq.choices.all())
    data = {
        'question_id': zscore_mcq.id,
        'choices[]': [zscore_choices[0].id, zscore_choices[1].id],
        'time_spent': 60
    }
    response = client.post(reverse('submit-answer', args=[attempt.id, zscore_mcq.id]), data)
    assert response.status_code == 302
    
    # Answer Min-Max question (2 + 3 = 5 points -> normalized to 6 points)
    minmax_choices = list(minmax_mcq.choices.all())
    data = {
        'question_id': minmax_mcq.id,
        'choices[]': [minmax_choices[0].id, minmax_choices[1].id],
        'time_spent': 60
    }
    response = client.post(reverse('submit-answer', args=[attempt.id, minmax_mcq.id]), data)
    assert response.status_code == 302
    
    # Answer Custom question (2 + 3 = 5 points -> normalized to 7 points)
    custom_choices = list(custom_mcq.choices.all())
    data = {
        'question_id': custom_mcq.id,
        'choices[]': [custom_choices[0].id, custom_choices[1].id],
        'time_spent': 60
    }
    response = client.post(reverse('submit-answer', args=[attempt.id, custom_mcq.id]), data)
    assert response.status_code == 302
    
    # Complete the quiz
    response = client.post(reverse('finish-quiz', args=[attempt.id]))
    assert response.status_code == 302
    
    # Verify the attempt score
    attempt.refresh_from_db()
    
    # Check individual question scores
    zscore_response = QuestionResponse.objects.get(attempt=attempt, question=zscore_mcq)
    assert zscore_response.points_earned == 5
    
    minmax_response = QuestionResponse.objects.get(attempt=attempt, question=minmax_mcq)
    assert minmax_response.points_earned == 6
    
    custom_response = QuestionResponse.objects.get(attempt=attempt, question=custom_mcq)
    assert custom_response.points_earned == 7
    
    # Verify total score: 5 + 6 + 7 = 18
    assert attempt.score == 18
    assert attempt.max_score == 30  # 3 questions * 10 points = 30
    assert attempt.is_passed  # 18/30 = 60%, passing score is 70%