import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json

from courses.models import (
    Course, Module, Quiz, EssayQuestion, QuizAttempt, QuestionResponse
)
from progress.models import Progress

User = get_user_model()

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
def setup_course_with_essay_quiz(setup_users):
    """Create a course with a module containing an essay question quiz"""
    instructor = setup_users['instructor']
    
    # Create course and module
    course = Course.objects.create(
        title="Test Course",
        description="Test Description",
        instructor=instructor,
        status='published'
    )
    
    module = Module.objects.create(
        course=course,
        title="Test Module",
        description="Test module description",
        order=1
    )
    
    # Create quiz with essay question
    quiz = Quiz.objects.create(
        module=module,
        title="Essay Quiz",
        description="Test your writing skills",
        instructions="Answer the essay question thoughtfully",
        passing_score=70,
        is_published=True
    )
    
    # Create essay question
    essay_question = EssayQuestion.objects.create(
        quiz=quiz,
        text="Explain the importance of testing in software development.",
        order=1,
        points=10,
        min_word_count=50,
        max_word_count=500,
        rubric="1-3 points: Basic understanding\n4-7 points: Good understanding\n8-10 points: Excellent understanding",
        example_answer="Testing is crucial in software development for several reasons..."
    )
    
    return {
        'course': course,
        'module': module,
        'quiz': quiz,
        'essay_question': essay_question
    }

@pytest.mark.django_db
def test_essay_question_model(setup_course_with_essay_quiz):
    """Test that the EssayQuestion model is correctly set up"""
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    assert essay_question.question_type == 'essay'
    assert essay_question.min_word_count == 50
    assert essay_question.max_word_count == 500
    assert "Basic understanding" in essay_question.rubric
    assert essay_question.points == 10
    assert essay_question.allow_attachments is False

@pytest.mark.django_db
def test_essay_response_submission(setup_users, setup_course_with_essay_quiz, client):
    """Test that a student can submit an essay response"""
    student = setup_users['student']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Start a quiz attempt
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302  # Redirect to quiz assessment
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Prepare essay response data
    essay_text = "This is a test essay response that explains the importance of testing. " * 10
    data = {
        'question_id': essay_question.id,
        'essay_text': essay_text,
        'time_spent': 300  # 5 minutes
    }
    
    # Submit the essay response
    response = client.post(reverse('submit-response', args=[attempt.id]), data)
    assert response.status_code == 302  # Redirect to next question or quiz
    
    # Verify the response was saved
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=essay_question
    )
    assert question_response is not None
    assert question_response.response_data['essay_text'] == essay_text
    assert question_response.is_correct is False  # Essay questions are not auto-graded
    assert question_response.graded_at is None  # Should not be graded yet

@pytest.mark.django_db
def test_essay_grading_by_instructor(setup_users, setup_course_with_essay_quiz, client):
    """Test that an instructor can grade an essay response"""
    student = setup_users['student']
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Create a quiz attempt and response
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=student,
        status='completed',
        score=0,
        max_score=10
    )
    
    essay_text = "This is a test essay response that explains the importance of testing. " * 10
    question_response = QuestionResponse.objects.create(
        attempt=attempt,
        question=essay_question,
        response_data={'essay_text': essay_text},
        is_correct=False,
        points_earned=0
    )
    
    # Login as instructor
    client.login(username='instructor', password='testpass123')
    
    # Grade the essay
    grading_data = {
        'points': 8,
        'feedback': 'Good explanation of testing importance but could use more specific examples.'
    }
    
    response = client.post(reverse('grade-essay-response', args=[question_response.id]), grading_data)
    assert response.status_code == 302  # Should redirect to the next pending essay
    
    # Refresh the question response from the database
    question_response.refresh_from_db()
    
    # Verify the response was graded
    assert question_response.graded_at is not None
    assert question_response.points_earned == 8
    assert question_response.instructor_comment == grading_data['feedback']
    assert question_response.graded_by == instructor

@pytest.mark.django_db
def test_essay_pending_grading_list(setup_users, setup_course_with_essay_quiz, client):
    """Test that instructors can see a list of essays pending grading"""
    student = setup_users['student']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Create multiple quiz attempts and responses
    for i in range(3):
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=student,
            status='completed',
            score=0,
            max_score=10,
            attempt_number=i+1
        )
        
        essay_text = f"Essay response #{i+1} about software testing. " * 10
        QuestionResponse.objects.create(
            attempt=attempt,
            question=essay_question,
            response_data={'essay_text': essay_text},
            is_correct=False,
            points_earned=0
        )
    
    # Login as instructor
    client.login(username='instructor', password='testpass123')
    
    # Check the pending essays endpoint
    response = client.get(reverse('pending-essay-grading', args=[quiz.id]))
    assert response.status_code == 200
    
    # There should be 3 pending responses
    content = response.content.decode('utf-8')
    assert "3 responses pending grading" in content

@pytest.mark.api
@pytest.mark.django_db
def test_essay_question_api(setup_users, setup_course_with_essay_quiz):
    """Test the essay question API endpoints"""
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Create API client and authenticate
    client = APIClient()
    client.force_authenticate(user=instructor)
    
    # Test retrieving essay questions
    response = client.get(f'/api/courses/quizzes/{quiz.id}/questions/')
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 1
    assert data[0]['question_type'] == 'essay'
    assert data[0]['text'] == essay_question.text
    
    # Test creating a new essay question
    new_question_data = {
        'text': 'What are the benefits of test-driven development?',
        'question_type': 'essay',
        'points': 15,
        'order': 2,
        'min_word_count': 100,
        'max_word_count': 800,
        'rubric': 'Detailed rubric for grading TDD essay',
        'example_answer': 'TDD provides several benefits including...'
    }
    
    response = client.post(f'/api/courses/quizzes/{quiz.id}/questions/essay/', new_question_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify the new question was created
    assert EssayQuestion.objects.count() == 2
    new_question = EssayQuestion.objects.get(text=new_question_data['text'])
    assert new_question.min_word_count == 100
    assert new_question.points == 15

@pytest.mark.api
@pytest.mark.django_db
def test_essay_grading_api(setup_users, setup_course_with_essay_quiz):
    """Test the essay grading API endpoints"""
    student = setup_users['student']
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Create a quiz attempt and response
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=student,
        status='completed',
        score=0,
        max_score=10
    )
    
    essay_text = "This is a test essay response for API grading. " * 10
    question_response = QuestionResponse.objects.create(
        attempt=attempt,
        question=essay_question,
        response_data={'essay_text': essay_text},
        is_correct=False,
        points_earned=0
    )
    
    # Create API client and authenticate as instructor
    client = APIClient()
    client.force_authenticate(user=instructor)
    
    # Test grading the essay through API
    grading_data = {
        'points': 9,
        'feedback': 'Excellent analysis with good examples.'
    }
    
    response = client.post(f'/api/courses/responses/{question_response.id}/grade/', grading_data)
    assert response.status_code == status.HTTP_200_OK
    
    # Refresh the question response from the database
    question_response.refresh_from_db()
    
    # Verify the response was graded
    assert question_response.graded_at is not None
    assert question_response.points_earned == 9
    assert question_response.instructor_comment == grading_data['feedback']
    
    # Test that the attempt score was updated
    attempt.refresh_from_db()
    assert attempt.score == 9