try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    import unittest
    
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
import json
import time
import tempfile
import os
from django.utils import timezone

from courses.models import (
    Course, Module, Quiz, EssayQuestion, QuizAttempt, QuestionResponse
)
from progress.models import Progress

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
    
    # Create another instructor for permission testing
    other_instructor = User.objects.create_user(
        username='other_instructor',
        email='other_instructor@example.com',
        password='testpass123'
    )
    other_instructor.profile.is_instructor = True
    other_instructor.profile.save()
    
    return {
        'instructor': instructor,
        'student': student,
        'other_instructor': other_instructor
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
def test_essay_response_below_min_word_count(setup_users, setup_course_with_essay_quiz, client):
    """Test that an essay response below the minimum word count is rejected"""
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
    
    # Prepare essay response data with insufficient word count (less than 50 words)
    essay_text = "This is a test essay response that is too short."
    data = {
        'question_id': essay_question.id,
        'essay_text': essay_text,
        'time_spent': 60  # 1 minute
    }
    
    # Submit the essay response
    response = client.post(reverse('submit-response', args=[attempt.id]), data)
    assert response.status_code == 302  # Redirect to next question or quiz
    
    # Verify the response was saved but marked with error
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=essay_question
    )
    assert question_response is not None
    assert question_response.response_data['essay_text'] == essay_text
    assert question_response.is_correct is False
    assert "too short" in question_response.feedback

@pytest.mark.django_db
def test_essay_response_above_max_word_count(setup_users, setup_course_with_essay_quiz, client):
    """Test that an essay response above the maximum word count is rejected"""
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
    
    # Prepare essay response data with excessive word count (more than 500 words)
    # 60 words repeated 10 times = 600 words
    essay_text = "This is a test essay response that exceeds the maximum word count. It contains many words that are unnecessary and redundant. The purpose is to test the validation of the maximum word count restriction. We need to make sure that the system properly identifies responses that are too verbose and provides appropriate feedback to guide the student in editing their response to meet the requirements. " * 10
    
    data = {
        'question_id': essay_question.id,
        'essay_text': essay_text,
        'time_spent': 300  # 5 minutes
    }
    
    # Submit the essay response
    response = client.post(reverse('submit-response', args=[attempt.id]), data)
    assert response.status_code == 302  # Redirect to next question or quiz
    
    # Verify the response was saved but marked with error
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=essay_question
    )
    assert question_response is not None
    assert question_response.is_correct is False
    assert "exceeds maximum word count" in question_response.feedback

@pytest.mark.django_db
def test_essay_without_word_count_restrictions(setup_users, setup_course_with_essay_quiz, client):
    """Test an essay question without word count restrictions"""
    # Modify the essay question to remove word count restrictions
    essay_question = setup_course_with_essay_quiz['essay_question']
    essay_question.min_word_count = 0
    essay_question.max_word_count = 0
    essay_question.save()
    
    student = setup_users['student']
    quiz = setup_course_with_essay_quiz['quiz']
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Start a quiz attempt
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302  # Redirect to quiz assessment
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Submit a very short essay
    essay_text = "Very short response."
    data = {
        'question_id': essay_question.id,
        'essay_text': essay_text,
        'time_spent': 30  # 30 seconds
    }
    
    # Submit the essay response
    response = client.post(reverse('submit-response', args=[attempt.id]), data)
    assert response.status_code == 302  # Redirect to next question or quiz
    
    # Verify the response was saved without word count error
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=essay_question
    )
    assert question_response is not None
    assert question_response.response_data['essay_text'] == essay_text
    assert question_response.is_correct is False  # Still pending grading
    assert "word count" not in question_response.feedback
    assert "submitted successfully" in question_response.feedback

@pytest.mark.django_db
def test_empty_essay_response(setup_users, setup_course_with_essay_quiz, client):
    """Test that an empty essay response is rejected"""
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
    
    # Submit an empty essay
    data = {
        'question_id': essay_question.id,
        'essay_text': '',
        'time_spent': 10  # 10 seconds
    }
    
    # Submit the essay response
    response = client.post(reverse('submit-response', args=[attempt.id]), data)
    assert response.status_code == 302  # Redirect to next question or quiz
    
    # Verify the response was saved with empty error
    question_response = QuestionResponse.objects.get(
        attempt=attempt,
        question=essay_question
    )
    assert question_response is not None
    assert question_response.response_data['essay_text'] == ''
    assert question_response.is_correct is False
    assert "No response provided" in question_response.feedback

@pytest.mark.django_db
def test_essay_attachment_support(setup_users, setup_course_with_essay_quiz, client):
    """Test that file attachments can be uploaded with essay responses"""
    # Modify the essay question to allow attachments
    essay_question = setup_course_with_essay_quiz['essay_question']
    essay_question.allow_attachments = True
    essay_question.save()
    
    student = setup_users['student']
    quiz = setup_course_with_essay_quiz['quiz']
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Start a quiz attempt
    response = client.post(reverse('start-quiz', args=[quiz.id]))
    assert response.status_code == 302  # Redirect to quiz assessment
    
    # Get the attempt
    attempt = QuizAttempt.objects.get(user=student, quiz=quiz)
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b'This is a test attachment file for the essay question.')
        temp_file_path = temp_file.name
    
    try:
        # Prepare the attachment
        with open(temp_file_path, 'rb') as file:
            file_content = file.read()
        
        # Create a SimpleUploadedFile
        test_file = SimpleUploadedFile(
            name='test_attachment.txt',
            content=file_content,
            content_type='text/plain'
        )
        
        # Prepare essay response data with attachment
        essay_text = "This is a test essay response. " * 10  # More than 50 words
        data = {
            'question_id': essay_question.id,
            'essay_text': essay_text,
            'attachment': test_file,
            'time_spent': 300  # 5 minutes
        }
        
        # Submit the essay response with attachment
        response = client.post(
            reverse('submit-response-with-attachment', args=[attempt.id]), 
            data,
            format='multipart'
        )
        assert response.status_code == 302  # Redirect to next question or quiz
        
        # Verify the response and attachment were saved
        question_response = QuestionResponse.objects.get(
            attempt=attempt,
            question=essay_question
        )
        assert question_response is not None
        assert question_response.response_data['essay_text'] == essay_text
        assert 'attachments' in question_response.response_data
        assert len(question_response.response_data['attachments']) == 1
        assert question_response.response_data['attachments'][0]['filename'] == 'test_attachment.txt'
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@pytest.mark.api
@pytest.mark.django_db
def test_essay_grading_permissions(setup_users, setup_course_with_essay_quiz):
    """Test that only the course instructor can grade essay responses"""
    student = setup_users['student']
    instructor = setup_users['instructor']
    other_instructor = setup_users['other_instructor']
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
    
    essay_text = "This is a test essay response for testing grading permissions. " * 10
    question_response = QuestionResponse.objects.create(
        attempt=attempt,
        question=essay_question,
        response_data={'essay_text': essay_text},
        is_correct=False,
        points_earned=0
    )
    
    # Create API client and try to grade with other instructor
    client = APIClient()
    client.force_authenticate(user=other_instructor)
    
    grading_data = {
        'points': 7,
        'feedback': 'This is feedback from another instructor.'
    }
    
    # Other instructor should not be able to grade
    response = client.post(f'/api/courses/responses/{question_response.id}/grade/', grading_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Now authenticate as course instructor
    client.force_authenticate(user=instructor)
    
    # Course instructor should be able to grade
    response = client.post(f'/api/courses/responses/{question_response.id}/grade/', grading_data)
    assert response.status_code == status.HTTP_200_OK
    
    # Refresh the question response from the database
    question_response.refresh_from_db()
    
    # Verify the response was graded
    assert question_response.graded_at is not None
    assert question_response.points_earned == 7
    assert question_response.instructor_comment == 'This is feedback from another instructor.'
    assert question_response.graded_by == instructor

@pytest.mark.api
@pytest.mark.django_db
def test_essay_grading_validation(setup_users, setup_course_with_essay_quiz):
    """Test validation of essay grading data"""
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
    
    essay_text = "This is a test essay response for testing grading validation. " * 10
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
    
    # Test with invalid points (negative)
    invalid_points_data = {
        'points': -3,
        'feedback': 'Test feedback.'
    }
    
    response = client.post(f'/api/courses/responses/{question_response.id}/grade/', invalid_points_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test with invalid points (above max)
    too_high_points_data = {
        'points': 15,  # Essay question is worth 10 points
        'feedback': 'Test feedback.'
    }
    
    response = client.post(f'/api/courses/responses/{question_response.id}/grade/', too_high_points_data)
    assert response.status_code == status.HTTP_200_OK  # Should accept but cap at max
    
    # Refresh the question response from the database
    question_response.refresh_from_db()
    
    # Verify points were capped at the maximum
    assert question_response.points_earned == 10  # Should be capped at 10 points

@pytest.mark.api
@pytest.mark.django_db
def test_essay_grading_effect_on_scores(setup_users, setup_course_with_essay_quiz):
    """Test that grading an essay correctly updates attempt scores"""
    student = setup_users['student']
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Create a quiz attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=student,
        status='completed',
        score=0,
        max_score=10
    )
    
    # Create an essay response
    essay_text = "This is a test essay response for checking score updates. " * 10
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
    
    # Grade the essay
    grading_data = {
        'points': 8,
        'feedback': 'Good essay with thoughtful analysis.'
    }
    
    response = client.post(f'/api/courses/responses/{question_response.id}/grade/', grading_data)
    assert response.status_code == status.HTTP_200_OK
    
    # Refresh the attempt from the database
    attempt.refresh_from_db()
    
    # Verify the attempt score was updated
    assert attempt.score == 8
    assert attempt.max_score == 10
    assert attempt.is_passed == True  # 8/10 = 80%, passing score is 70%

@pytest.mark.api
@pytest.mark.django_db
def test_essay_bulk_grading(setup_users, setup_course_with_essay_quiz):
    """Test the ability to grade multiple essay responses efficiently"""
    student = setup_users['student']
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Create multiple quiz attempts and responses
    responses = []
    for i in range(5):
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=student,
            status='completed',
            score=0,
            max_score=10,
            attempt_number=i+1
        )
        
        essay_text = f"Essay response #{i+1} about software testing. " * 10
        question_response = QuestionResponse.objects.create(
            attempt=attempt,
            question=essay_question,
            response_data={'essay_text': essay_text},
            is_correct=False,
            points_earned=0
        )
        responses.append(question_response)
    
    # Create API client and authenticate as instructor
    client = APIClient()
    client.force_authenticate(user=instructor)
    
    # Check the pending essays endpoint
    response = client.get(f'/api/courses/essay-questions/pending_grading/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # There should be 5 pending responses
    assert len(data) == 5
    
    # Grade each response
    for i, question_response in enumerate(responses):
        points = i + 5  # 5, 6, 7, 8, 9 points
        grading_data = {
            'points': points,
            'feedback': f'Feedback for essay {i+1}'
        }
        
        response = client.post(f'/api/courses/responses/{question_response.id}/grade/', grading_data)
        assert response.status_code == status.HTTP_200_OK
    
    # Check the pending essays endpoint again
    response = client.get(f'/api/courses/essay-questions/pending_grading/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # There should be 0 pending responses
    assert len(data) == 0

@pytest.mark.django_db
def test_essay_instructor_annotation(setup_users, setup_course_with_essay_quiz):
    """Test that instructors can annotate essay responses"""
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
    
    essay_text = "This is a test essay response for testing annotations. " * 10
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
    
    # Add an annotation
    annotation_data = {
        'response_id': question_response.id,
        'annotation': 'This paragraph could be improved with more concrete examples.'
    }
    
    response = client.post('/api/courses/quiz-attempts/annotate_response/', annotation_data)
    assert response.status_code == status.HTTP_200_OK
    
    # Verify the annotation was saved
    question_response.refresh_from_db()
    assert question_response.instructor_annotation == annotation_data['annotation']
    assert question_response.annotation_added_at is not None
    assert question_response.annotated_by == instructor

@pytest.mark.api
@pytest.mark.django_db
def test_essay_question_creation_api(setup_users, setup_course_with_essay_quiz):
    """Test creating essay questions through the API"""
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    
    # Create API client and authenticate as instructor
    client = APIClient()
    client.force_authenticate(user=instructor)
    
    # Create a new essay question
    new_question_data = {
        'quiz': quiz.id,
        'text': 'Describe the differences between unit testing, integration testing, and end-to-end testing.',
        'question_type': 'essay',
        'order': 2,
        'points': 15,
        'min_word_count': 200,
        'max_word_count': 1000,
        'rubric': '1-5 points: Basic understanding\n6-10 points: Good understanding\n11-15 points: Excellent understanding',
        'example_answer': 'Unit testing focuses on testing individual components in isolation...',
        'allow_attachments': True
    }
    
    response = client.post(f'/api/courses/quizzes/{quiz.id}/questions/essay/', new_question_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify the question was created with all fields
    data = response.json()
    
    # Fetch the created question from the database
    essay_question = EssayQuestion.objects.get(id=data['id'])
    
    assert essay_question.text == new_question_data['text']
    assert essay_question.min_word_count == new_question_data['min_word_count']
    assert essay_question.max_word_count == new_question_data['max_word_count']
    assert essay_question.rubric == new_question_data['rubric']
    assert essay_question.example_answer == new_question_data['example_answer']
    assert essay_question.allow_attachments == new_question_data['allow_attachments']
    assert essay_question.points == new_question_data['points']

@pytest.mark.django_db
def test_concurrent_essay_grading(setup_users, setup_course_with_essay_quiz):
    """Test that multiple instructors cannot grade the same essay simultaneously"""
    student = setup_users['student']
    instructor = setup_users['instructor']
    other_instructor = setup_users['other_instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Make the other instructor a co-instructor for the course
    course = setup_course_with_essay_quiz['course']
    course.instructor = other_instructor
    course.save()
    
    # Create a quiz attempt and response
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=student,
        status='completed',
        score=0,
        max_score=10
    )
    
    essay_text = "This is a test essay response for testing concurrent grading. " * 10
    question_response = QuestionResponse.objects.create(
        attempt=attempt,
        question=essay_question,
        response_data={'essay_text': essay_text},
        is_correct=False,
        points_earned=0
    )
    
    # Create API clients for both instructors
    client1 = APIClient()
    client1.force_authenticate(user=instructor)
    
    client2 = APIClient()
    client2.force_authenticate(user=other_instructor)
    
    # First instructor grades the essay
    grading_data1 = {
        'points': 7,
        'feedback': 'Feedback from instructor 1'
    }
    
    response1 = client1.post(f'/api/courses/responses/{question_response.id}/grade/', grading_data1)
    assert response1.status_code == status.HTTP_200_OK
    
    # Second instructor tries to grade the same essay
    grading_data2 = {
        'points': 9,
        'feedback': 'Feedback from instructor 2'
    }
    
    response2 = client2.post(f'/api/courses/responses/{question_response.id}/grade/', grading_data2)
    # This should fail or return an error since the essay is already graded
    assert response2.status_code != status.HTTP_200_OK
    
    # Verify the first instructor's grade was kept
    question_response.refresh_from_db()
    assert question_response.points_earned == 7
    assert question_response.instructor_comment == 'Feedback from instructor 1'
    assert question_response.graded_by == instructor

@pytest.mark.django_db
def test_essay_question_with_media(setup_users, setup_course_with_essay_quiz, client):
    """Test essay questions with images and external media"""
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    
    # Login as instructor
    client.login(username='instructor', password='testpass123')
    
    # Create an essay question with image and external media
    essay_question_data = {
        'quiz': quiz.id,
        'text': 'Analyze the diagram below and explain its implications.',
        'question_type': 'essay',
        'order': 2,
        'points': 20,
        'min_word_count': 100,
        'max_word_count': 800,
        'external_media_url': 'https://example.com/sample-diagram.png',
        'media_caption': 'System Architecture Diagram',
        'rubric': 'Detailed rubric for grading the architecture analysis'
    }
    
    response = client.post(reverse('add-essay-question', args=[quiz.id]), essay_question_data)
    assert response.status_code == 302  # Redirect after creation
    
    # Verify the question was created with media settings
    new_question = EssayQuestion.objects.get(text=essay_question_data['text'])
    assert new_question.external_media_url == essay_question_data['external_media_url']
    assert new_question.media_caption == essay_question_data['media_caption']

@pytest.mark.api
@pytest.mark.django_db
def test_essay_analytics(setup_users, setup_course_with_essay_quiz):
    """Test analytics for essay questions"""
    student = setup_users['student']
    instructor = setup_users['instructor']
    quiz = setup_course_with_essay_quiz['quiz']
    essay_question = setup_course_with_essay_quiz['essay_question']
    
    # Create multiple attempts and responses with different scores
    scores = [3, 5, 8, 10, 7]
    for i, score in enumerate(scores):
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=student,
            status='completed',
            score=score,
            max_score=10,
            attempt_number=i+1
        )
        
        essay_text = f"Essay response #{i+1} about software testing. " * 10
        response = QuestionResponse.objects.create(
            attempt=attempt,
            question=essay_question,
            response_data={'essay_text': essay_text},
            is_correct=score > 5,  # Set correct based on passing threshold
            points_earned=score,
            graded_at=timezone.now(),
            graded_by=instructor,
            instructor_comment=f"Feedback for essay {i+1}"
        )
        
        # Add some variation in time spent
        response.time_spent_seconds = (i+1) * 120  # 2, 4, 6, 8, 10 minutes
        response.save()
    
    # Create API client and authenticate as instructor
    client = APIClient()
    client.force_authenticate(user=instructor)
    
    # Calculate analytics
    response = client.post(f'/api/courses/quizzes/{quiz.id}/recalculate_analytics/')
    assert response.status_code == status.HTTP_200_OK
    
    # Get question analytics
    response = client.get(f'/api/courses/questions/{essay_question.id}/analytics/')
    assert response.status_code == status.HTTP_200_OK
    
    # Verify the analytics data
    data = response.json()
    assert data['total_attempts'] == 5
    assert data['correct_attempts'] == 3  # Scores 8, 10, 7 are above 5
    assert data['avg_time_seconds'] == 720  # Average of 2, 4, 6, 8, 10 minutes in seconds
    assert data['difficulty_index'] == 0.6  # 3/5 correct

@pytest.mark.django_db
def test_multiple_essay_questions_in_quiz(setup_users, setup_course_with_essay_quiz):
    """Test a quiz with multiple essay questions"""
    instructor = setup_users['instructor']
    student = setup_users['student']
    quiz = setup_course_with_essay_quiz['quiz']
    
    # Add a second essay question
    second_essay = EssayQuestion.objects.create(
        quiz=quiz,
        text="Compare and contrast different software development methodologies.",
        order=2,
        points=15,
        min_word_count=100,
        max_word_count=800,
        rubric="Detailed rubric for grading methodology comparison",
        example_answer="When comparing Agile, Waterfall, and DevOps..."
    )
    
    # Create API client and authenticate as student
    client = APIClient()
    client.force_authenticate(user=student)
    
    # Start a quiz attempt
    response = client.post(f'/api/courses/quizzes/{quiz.id}/start_attempt/')
    assert response.status_code == status.HTTP_201_CREATED
    
    # Get the attempt
    data = response.json()
    attempt_id = data['id']
    
    # Get the questions for this quiz
    response = client.get(f'/api/courses/quizzes/{quiz.id}/')
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data['questions']) == 2
    
    # Submit answers to both questions
    essay1_text = "This is a response to the first essay question about testing. " * 10
    response1_data = {
        'question': setup_course_with_essay_quiz['essay_question'].id,
        'response_data': {'essay_text': essay1_text},
        'time_spent_seconds': 300
    }
    
    response = client.post(f'/api/courses/quiz-attempts/{attempt_id}/submit_response/', response1_data)
    assert response.status_code == status.HTTP_200_OK
    
    essay2_text = "This is a response to the second essay question about methodologies. " * 15
    response2_data = {
        'question': second_essay.id,
        'response_data': {'essay_text': essay2_text},
        'time_spent_seconds': 450
    }
    
    response = client.post(f'/api/courses/quiz-attempts/{attempt_id}/submit_response/', response2_data)
    assert response.status_code == status.HTTP_200_OK
    
    # Complete the attempt
    response = client.post(f'/api/courses/quiz-attempts/{attempt_id}/complete/')
    assert response.status_code == status.HTTP_200_OK
    
    # Authenticate as instructor to grade
    client.force_authenticate(user=instructor)
    
    # Get pending essays to grade
    response = client.get('/api/courses/essay-questions/pending_grading/')
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 2  # Both essays should be pending grading
    
    # Grade both essays
    for response_item in data:
        grading_data = {
            'points': 10,
            'feedback': f'Good response to question {response_item["question_text"][:20]}...'
        }
        
        response = client.post(f'/api/courses/responses/{response_item["id"]}/grade/', grading_data)
        assert response.status_code == status.HTTP_200_OK
    
    # Check the attempt score after grading
    response = client.get(f'/api/courses/quiz-attempts/{attempt_id}/')
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    # Total score should be 20 (10 for each essay)
    # Max score should be 25 (10 for first essay + 15 for second essay)
    assert data['score'] == 20
    assert data['max_score'] == 25
    assert data['score_percentage'] == 80.0  # 20/25 = 80%
    assert data['is_passed'] == True  # 80% > 70% passing score