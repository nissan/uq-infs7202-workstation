import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from ai_tutor.models import (
    TutorSession,
    TutorMessage,
    TutorKnowledgeBase,
    TutorFeedback
)
from courses.models import Course, Module
from unittest.mock import patch

User = get_user_model()

@pytest.mark.django_db
class TestTutorSessionAPI:
    """Test cases for the TutorSession API endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Return an API client for testing."""
        return APIClient()
    
    @pytest.fixture
    def authenticated_client(self):
        """Return an authenticated API client for testing."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        client = APIClient()
        client.force_authenticate(user=user)
        return client, user
    
    def test_list_sessions_unauthorized(self, api_client):
        """Test that unauthorized users cannot list sessions."""
        url = reverse('tutor-session-list')
        response = api_client.get(url)
        assert response.status_code == 401
    
    def test_list_sessions_authorized(self, authenticated_client):
        """Test that authorized users can list their sessions."""
        client, user = authenticated_client
        
        # Create sessions for the user
        course = Course.objects.create(title='Test Course')
        
        session1 = TutorSession.objects.create(
            user=user,
            title='Session 1',
            status='active',
            course=course
        )
        
        session2 = TutorSession.objects.create(
            user=user,
            title='Session 2',
            status='completed'
        )
        
        # Create a session for another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )
        
        other_session = TutorSession.objects.create(
            user=other_user,
            title='Other Session',
            status='active'
        )
        
        # Test listing sessions
        url = reverse('tutor-session-list')
        response = client.get(url)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Should only see own sessions
        assert len(data) == 2
        
        # Check that session data is correct
        session_titles = [s['title'] for s in data]
        assert 'Session 1' in session_titles
        assert 'Session 2' in session_titles
        assert 'Other Session' not in session_titles
    
    def test_create_session(self, authenticated_client):
        """Test creating a new session."""
        client, user = authenticated_client
        
        # Create a course
        course = Course.objects.create(title='Test Course')
        
        # Create session data
        session_data = {
            'title': 'New Session',
            'course': course.id
        }
        
        # Test creating session
        url = reverse('tutor-session-list')
        response = client.post(url, session_data, format='json')
        
        # Check response
        assert response.status_code == 201
        data = response.json()
        
        # Check that session was created correctly
        assert data['title'] == 'New Session'
        assert data['course'] == course.id
        assert data['user'] == user.id
        assert data['status'] == 'active'
        
        # Verify in database
        session = TutorSession.objects.get(id=data['id'])
        assert session.title == 'New Session'
        assert session.course == course
        assert session.user == user
    
    def test_retrieve_session(self, authenticated_client):
        """Test retrieving a session."""
        client, user = authenticated_client
        
        # Create a session
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Add some messages
        TutorMessage.objects.create(
            session=session,
            message_type='user',
            content='Hello'
        )
        
        TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='Hi there, how can I help you?'
        )
        
        # Test retrieving session
        url = reverse('tutor-session-detail', args=[session.id])
        response = client.get(url)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Check that session data is correct
        assert data['title'] == 'Test Session'
        assert data['status'] == 'active'
        assert len(data['messages']) == 2
        
        # Check that messages are included
        assert data['messages'][0]['message_type'] == 'user'
        assert data['messages'][0]['content'] == 'Hello'
        assert data['messages'][1]['message_type'] == 'tutor'
        assert data['messages'][1]['content'] == 'Hi there, how can I help you?'
    
    @patch('ai_tutor.api_views.tutor_langchain_service.get_tutor_response')
    def test_send_message(self, mock_get_response, authenticated_client):
        """Test sending a message to the tutor."""
        client, user = authenticated_client
        
        # Create a session
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Mock the LangChain response
        mock_get_response.return_value = {
            'content': 'This is a test response',
            'sources': ['knowledge_base:1'],
            'metadata': {'model': 'test-model'}
        }
        
        # Test sending message
        url = reverse('tutor-session-send-message', args=[session.id])
        message_data = {
            'session': session.id,
            'content': 'What is machine learning?'
        }
        
        response = client.post(url, message_data, format='json')
        
        # Check response
        assert response.status_code == 201
        data = response.json()
        
        # Check that both messages were created
        assert 'user_message' in data
        assert 'tutor_response' in data
        assert data['user_message']['content'] == 'What is machine learning?'
        assert data['tutor_response']['content'] == 'This is a test response'
        
        # Verify in database
        messages = TutorMessage.objects.filter(session=session)
        assert messages.count() == 2
        
        user_messages = messages.filter(message_type='user')
        assert user_messages.count() == 1
        assert user_messages.first().content == 'What is machine learning?'
        
        tutor_messages = messages.filter(message_type='tutor')
        assert tutor_messages.count() == 1
        assert tutor_messages.first().content == 'This is a test response'
        assert tutor_messages.first().metadata['sources'] == ['knowledge_base:1']
        assert tutor_messages.first().metadata['model'] == 'test-model'


@pytest.mark.django_db
class TestTutorMessageAPI:
    """Test cases for the TutorMessage API endpoints."""
    
    @pytest.fixture
    def authenticated_client(self):
        """Return an authenticated API client for testing."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        client = APIClient()
        client.force_authenticate(user=user)
        return client, user
    
    def test_list_messages(self, authenticated_client):
        """Test listing messages for a session."""
        client, user = authenticated_client
        
        # Create a session
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Add some messages
        TutorMessage.objects.create(
            session=session,
            message_type='user',
            content='Hello'
        )
        
        TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='Hi there, how can I help you?'
        )
        
        # Create another session with messages
        other_session = TutorSession.objects.create(
            user=user,
            title='Other Session',
            status='active'
        )
        
        TutorMessage.objects.create(
            session=other_session,
            message_type='user',
            content='Other message'
        )
        
        # Test listing all messages
        url = reverse('tutor-message-list')
        response = client.get(url)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Should see all messages for all sessions
        assert len(data) == 3
        
        # Test filtering by session
        url = f"{url}?session={session.id}"
        response = client.get(url)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Should only see messages for the specified session
        assert len(data) == 2
        message_contents = [m['content'] for m in data]
        assert 'Hello' in message_contents
        assert 'Hi there, how can I help you?' in message_contents
        assert 'Other message' not in message_contents


@pytest.mark.django_db
class TestTutorFeedbackAPI:
    """Test cases for the TutorFeedback API endpoints."""
    
    @pytest.fixture
    def authenticated_client(self):
        """Return an authenticated API client for testing."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        client = APIClient()
        client.force_authenticate(user=user)
        return client, user
    
    def test_create_feedback(self, authenticated_client):
        """Test creating feedback for a message."""
        client, user = authenticated_client
        
        # Create a session
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Add a tutor message
        message = TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='This is a test response'
        )
        
        # Test creating feedback
        url = reverse('tutor-feedback-list')
        feedback_data = {
            'session': session.id,
            'message': message.id,
            'rating': 5,
            'helpful': True,
            'comment': 'Very helpful response!'
        }
        
        response = client.post(url, feedback_data, format='json')
        
        # Check response
        assert response.status_code == 201
        data = response.json()
        
        # Check that feedback was created correctly
        assert data['session'] == session.id
        assert data['message'] == message.id
        assert data['rating'] == 5
        assert data['helpful'] is True
        assert data['comment'] == 'Very helpful response!'
        
        # Verify in database
        feedback = TutorFeedback.objects.get(id=data['id'])
        assert feedback.session == session
        assert feedback.message == message
        assert feedback.rating == 5
        assert feedback.helpful is True
        assert feedback.comment == 'Very helpful response!'