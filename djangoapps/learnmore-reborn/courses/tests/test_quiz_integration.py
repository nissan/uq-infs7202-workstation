# Using try/except to handle pytest import for different environments
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    # If pytest isn't available, set a flag to skip tests during Django test runs
    HAS_PYTEST = False
    # Create mock decorators that do nothing
    class mock_pytest:
        @staticmethod
        def mark(*args, **kwargs):
            class Mark:
                def __call__(self, func):
                    return func
            return Mark()
        @staticmethod
        def fixture(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
    # Assign the mock to pytest if it's not available
    pytest = mock_pytest()

from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import (
    Course, Module, Quiz, MultipleChoiceQuestion, TrueFalseQuestion,
    Choice, QuizAttempt, QuestionResponse, Enrollment
)

User = get_user_model()

@pytest.fixture
def create_quiz_data():
    # Create a test user
    user = User.objects.create_user(
        username='quiztestuser',
        email='quiztest@example.com',
        password='testpassword'
    )
    
    # Create user profile if needed
    if hasattr(User, 'profile'):
        from users.models import UserProfile
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=user,
                is_instructor=True  # Give instructor permissions
            )
    
    # Create a course
    course = Course.objects.create(
        title='Test Course',
        slug='test-course',
        description='Course for quiz testing',
        instructor=user,
        status='published',
        enrollment_type='open'
    )
    
    # Create a module
    module = Module.objects.create(
        title='Test Module',
        course=course,
        description='Module for quiz testing',
        order=1
    )
    
    # Create a quiz
    quiz = Quiz.objects.create(
        title='Test Quiz',
        module=module,
        description='A test quiz for integration testing',
        instructions='Answer all questions',
        time_limit_minutes=10,
        passing_score=70,
        is_published=True,
        allow_multiple_attempts=True
    )
    
    # Create a multiple choice question
    mcq = MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        text='What is 2+2?',
        order=1,
        points=1,
        allow_multiple=False
    )
    
    # Create choices
    Choice.objects.create(question=mcq, text='3', is_correct=False, order=1)
    Choice.objects.create(question=mcq, text='4', is_correct=True, order=2)
    Choice.objects.create(question=mcq, text='5', is_correct=False, order=3)
    
    # Create a true/false question
    tf_question = TrueFalseQuestion.objects.create(
        quiz=quiz,
        text='The sky is blue.',
        order=2,
        points=1,
        correct_answer=True
    )
    
    # Enroll the user in the course
    enrollment = Enrollment.objects.create(
        user=user,
        course=course,
        status='active'
    )
    
    return {
        'user': user,
        'course': course,
        'module': module,
        'quiz': quiz,
        'mcq': mcq,
        'tf_question': tf_question
    }

# Only run these tests when pytest is available
if HAS_PYTEST:
    @pytest.mark.django_db
    @pytest.mark.integration
    def test_quiz_list_view(client, create_quiz_data):
        """Test the quiz list view shows the quiz."""
        data = create_quiz_data
        client.login(username='quiztestuser', password='testpassword')
        
        # Set session variables to mimic Django's login
        session = client.session
        session['_auth_user_id'] = str(data['user'].pk)
        session.save()
        
        response = client.get(reverse('quiz-list'))
        assert response.status_code == 200
        assert data['quiz'].title in str(response.content)

    @pytest.mark.django_db
    @pytest.mark.integration
    def test_quiz_detail_view(client, create_quiz_data):
        """Test the quiz detail view shows quiz information."""
        data = create_quiz_data
        client.login(username='quiztestuser', password='testpassword')
        
        # Set session variables to mimic Django's login
        session = client.session
        session['_auth_user_id'] = str(data['user'].pk)
        session.save()
        
        response = client.get(reverse('quiz-detail', args=[data['quiz'].id]))
        assert response.status_code == 200
        assert data['quiz'].title in str(response.content)
        assert data['quiz'].description in str(response.content)
        assert str(data['quiz'].passing_score) in str(response.content)

    @pytest.mark.django_db
    @pytest.mark.integration
    def test_start_quiz(client, create_quiz_data):
        """Test starting a quiz creates an attempt."""
        data = create_quiz_data
        client.login(username='quiztestuser', password='testpassword')
        
        # Set session variables to mimic Django's login
        session = client.session
        session['_auth_user_id'] = str(data['user'].pk)
        session.save()
        
        # Start the quiz
        response = client.post(reverse('start-quiz', args=[data['quiz'].id]))
        assert response.status_code == 302  # Should redirect
        
        # Check if an attempt was created
        attempt = QuizAttempt.objects.filter(
            quiz=data['quiz'],
            user=data['user'],
            status='in_progress'
        ).first()
        
        assert attempt is not None
        assert attempt.attempt_number == 1

    @pytest.mark.django_db
    @pytest.mark.integration
    def test_submit_answer_and_finish_quiz(client, create_quiz_data):
        """Test submitting answers and finishing a quiz."""
        data = create_quiz_data
        client.login(username='quiztestuser', password='testpassword')
        
        # Set session variables to mimic Django's login
        session = client.session
        session['_auth_user_id'] = str(data['user'].pk)
        session.save()
        
        # Start the quiz
        client.post(reverse('start-quiz', args=[data['quiz'].id]))
        
        # Get the attempt
        attempt = QuizAttempt.objects.filter(
            quiz=data['quiz'],
            user=data['user'],
            status='in_progress'
        ).first()
        
        # Get choices
        correct_choice = Choice.objects.filter(
            question=data['mcq'],
            is_correct=True
        ).first()
        
        # Submit answer to multiple choice question
        response = client.post(
            reverse('submit-answer', args=[attempt.id, data['mcq'].id]),
            {'choice': correct_choice.id, 'time_spent': 30}
        )
        assert response.status_code == 302  # Should redirect
        
        # Submit answer to true/false question
        response = client.post(
            reverse('submit-answer', args=[attempt.id, data['tf_question'].id]),
            {'answer': 'true', 'time_spent': 20}
        )
        assert response.status_code == 302  # Should redirect
        
        # Finish the quiz
        response = client.post(reverse('finish-quiz', args=[attempt.id]))
        assert response.status_code == 302  # Should redirect to results
        
        # Check if the attempt was completed
        attempt.refresh_from_db()
        assert attempt.status == 'completed'
        assert attempt.is_passed == True  # Should pass with all correct answers
        assert attempt.score == 2  # 1 point per question, 2 questions

    @pytest.mark.django_db
    @pytest.mark.integration
    def test_quiz_result_view(client, create_quiz_data):
        """Test viewing quiz results."""
        data = create_quiz_data
        client.login(username='quiztestuser', password='testpassword')
        
        # Set session variables to mimic Django's login
        session = client.session
        session['_auth_user_id'] = str(data['user'].pk)
        session.save()
        
        # Start the quiz
        client.post(reverse('start-quiz', args=[data['quiz'].id]))
        
        # Get the attempt
        attempt = QuizAttempt.objects.filter(
            quiz=data['quiz'],
            user=data['user'],
            status='in_progress'
        ).first()
        
        # Get choices
        correct_choice = Choice.objects.filter(
            question=data['mcq'],
            is_correct=True
        ).first()
        
        # Submit answers
        client.post(
            reverse('submit-answer', args=[attempt.id, data['mcq'].id]),
            {'choice': correct_choice.id, 'time_spent': 30}
        )
        client.post(
            reverse('submit-answer', args=[attempt.id, data['tf_question'].id]),
            {'answer': 'true', 'time_spent': 20}
        )
        
        # Finish the quiz
        client.post(reverse('finish-quiz', args=[attempt.id]))
        
        # View results
        response = client.get(reverse('quiz-result', args=[attempt.id]))
        assert response.status_code == 200
        assert 'Passed!' in str(response.content)
        assert '2 / 2' in str(response.content)  # Score / Total
        assert '100' in str(response.content)  # 100% score