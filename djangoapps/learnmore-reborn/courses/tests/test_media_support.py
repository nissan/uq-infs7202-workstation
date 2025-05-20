import os
import tempfile
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    import unittest
    
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.conf import settings

from courses.models import (
    Course, Module, Quiz, Question, Choice, MultipleChoiceQuestion, QuizAttempt
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
def temp_media_root():
    """Create a temporary media root for test file uploads"""
    temp_dir = tempfile.mkdtemp()
    
    # Override media root for this test
    with override_settings(MEDIA_ROOT=temp_dir):
        yield temp_dir
        
    # Cleanup after test
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

@pytest.fixture
def image_file():
    """Create a simple test image file"""
    file_content = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00'
        b'\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c'
        b'\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00'
        b'IEND\xaeB`\x82'
    )
    return SimpleUploadedFile('test.png', file_content, content_type='image/png')

@pytest.mark.django_db
def test_question_with_image(setup_users, temp_media_root, image_file):
    """Test creating and displaying a question with an image"""
    instructor = setup_users['instructor']
    
    # Create course and module
    course = Course.objects.create(
        title="Media Test Course",
        description="Testing media functionality",
        instructor=instructor,
        status='published'
    )
    
    module = Module.objects.create(
        course=course,
        title="Media Test Module",
        description="Test module description",
        order=1
    )
    
    # Create quiz
    quiz = Quiz.objects.create(
        module=module,
        title="Media Quiz",
        description="Testing media support",
        instructions="Answer questions with media",
        passing_score=70,
        is_published=True
    )
    
    # Create a question with an image
    question = Question.objects.create(
        quiz=quiz,
        text="What does this image show?",
        question_type='multiple_choice',
        order=1,
        points=5,
        image=image_file,
        image_alt_text="Test image alt text",
        media_caption="This is a test image caption"
    )
    
    # Create multiple choice details
    mc_question = MultipleChoiceQuestion.objects.create(
        question_ptr=question
    )
    
    # Create choices
    choice1 = Choice.objects.create(
        question=mc_question,
        text="First choice",
        is_correct=True,
        order=1
    )
    
    choice2 = Choice.objects.create(
        question=mc_question,
        text="Second choice",
        is_correct=False,
        order=2,
        image=image_file,
        image_alt_text="Choice image alt text"
    )
    
    # Verify the question and choice images are saved
    question.refresh_from_db()
    choice2.refresh_from_db()
    
    assert question.image.name is not None
    assert "test.png" in question.image.name
    assert question.image_alt_text == "Test image alt text"
    assert question.media_caption == "This is a test image caption"
    
    assert choice2.image.name is not None
    assert "test.png" in choice2.image.name
    assert choice2.image_alt_text == "Choice image alt text"
    
    # Create a student quiz attempt
    student = setup_users['student']
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=student,
        started_at='2023-01-01T10:00:00Z'
    )
    
    return {
        'quiz': quiz,
        'question': question,
        'mc_question': mc_question,
        'choice1': choice1,
        'choice2': choice2,
        'attempt': attempt,
        'student': student
    }

@pytest.mark.django_db
@pytest.mark.template
def test_quiz_assessment_displays_media(test_question_with_image, client):
    """Test that the quiz assessment page displays question and choice media"""
    data = test_question_with_image
    student = data['student']
    quiz = data['quiz']
    attempt = data['attempt']
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Get the quiz assessment page
    response = client.get(reverse('quiz-assessment', args=[attempt.id]))
    assert response.status_code == 200
    
    # Check if the page contains the image URLs and media elements
    content = response.content.decode('utf-8')
    
    # Question image should be displayed
    assert 'question-media' in content
    assert data['question'].image.url in content
    assert data['question'].image_alt_text in content
    assert data['question'].media_caption in content
    
    # Choice image should be displayed
    assert 'choice-media' in content
    assert data['choice2'].image.url in content
    assert data['choice2'].image_alt_text in content
    
    # Lightbox functionality should be included
    assert 'lightbox' in content
    assert 'media-enlargeable' in content

@pytest.mark.django_db
@pytest.mark.template
def test_quiz_results_displays_media(test_question_with_image, client):
    """Test that the quiz results page displays question and choice media"""
    data = test_question_with_image
    student = data['student']
    quiz = data['quiz']
    attempt = data['attempt']
    
    # Create a completed response 
    from courses.models import QuestionResponse
    response_obj = QuestionResponse.objects.create(
        attempt=attempt,
        question=data['question'],
        response_data={'selected_choice': data['choice1'].id},
        is_correct=True,
        points_earned=5
    )
    
    # Mark attempt as completed
    attempt.status = 'completed'
    attempt.completed_at = '2023-01-01T11:00:00Z'
    attempt.score = 5
    attempt.max_score = 5
    attempt.is_passed = True
    attempt.save()
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Get the quiz results page
    response = client.get(reverse('quiz-results', args=[attempt.id]))
    assert response.status_code == 200
    
    # Check if the page contains the image URLs and media elements
    content = response.content.decode('utf-8')
    
    # Question image should be displayed
    assert 'question-media' in content
    assert data['question'].image.url in content
    assert data['question'].image_alt_text in content
    assert data['question'].media_caption in content
    
    # Choice image should be displayed
    assert 'choice-media' in content
    assert data['choice2'].image.url in content
    
    # Lightbox functionality should be included
    assert 'lightbox' in content
    assert 'media-enlargeable' in content

@pytest.mark.django_db
def test_external_media_url(setup_users, client):
    """Test creating and displaying a question with an external media URL"""
    instructor = setup_users['instructor']
    student = setup_users['student']
    
    # Create course and module
    course = Course.objects.create(
        title="External Media Test Course",
        description="Testing external media functionality",
        instructor=instructor,
        status='published'
    )
    
    module = Module.objects.create(
        course=course,
        title="External Media Test Module",
        description="Test module description",
        order=1
    )
    
    # Create quiz
    quiz = Quiz.objects.create(
        module=module,
        title="External Media Quiz",
        description="Testing external media support",
        instructions="Answer questions with external media",
        passing_score=70,
        is_published=True
    )
    
    # Create a question with an external media URL
    question = Question.objects.create(
        quiz=quiz,
        text="What does this external media show?",
        question_type='multiple_choice',
        order=1,
        points=5,
        external_media_url="https://example.com/test-image.jpg",
        media_caption="This is an external media test"
    )
    
    # Create multiple choice details
    mc_question = MultipleChoiceQuestion.objects.create(
        question_ptr=question
    )
    
    # Create choices
    Choice.objects.create(
        question=mc_question,
        text="First choice",
        is_correct=True,
        order=1
    )
    
    Choice.objects.create(
        question=mc_question,
        text="Second choice",
        is_correct=False,
        order=2
    )
    
    # Create a student quiz attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=student,
        started_at='2023-01-01T10:00:00Z'
    )
    
    # Login as student
    client.login(username='student', password='testpass123')
    
    # Get the quiz assessment page
    response = client.get(reverse('quiz-assessment', args=[attempt.id]))
    assert response.status_code == 200
    
    # Check if the page contains the external media URL
    content = response.content.decode('utf-8')
    assert 'question-media' in content
    assert question.external_media_url in content
    assert question.media_caption in content
    
    # Test with YouTube video URL
    question.external_media_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    question.save()
    
    # Get the quiz assessment page again
    response = client.get(reverse('quiz-assessment', args=[attempt.id]))
    assert response.status_code == 200
    
    # Check if the page contains the YouTube embed
    content = response.content.decode('utf-8')
    assert 'youtube.com' in content
    assert 'iframe' in content