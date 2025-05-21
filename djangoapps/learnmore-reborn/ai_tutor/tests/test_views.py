import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from ai_tutor.models import (
    TutorSession,
    TutorMessage,
    TutorFeedback
)
from courses.models import Course, Module
from unittest.mock import patch

User = get_user_model()

@pytest.mark.django_db
class TestAITutorViews:
    """Test cases for the AI Tutor views."""
    
    @pytest.fixture
    def client(self):
        """Return a client for testing."""
        return Client()
    
    @pytest.fixture
    def authenticated_client(self):
        """Return an authenticated client for testing."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        client = Client()
        client.force_login(user)
        return client, user
    
    def test_dashboard_view_unauthenticated(self, client):
        """Test that unauthenticated users are redirected from the dashboard."""
        url = reverse('ai_tutor_dashboard')
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login
        assert 'login' in response.url
    
    def test_dashboard_view_authenticated(self, authenticated_client):
        """Test that authenticated users can access the dashboard."""
        client, user = authenticated_client
        
        # Create some sessions for the user
        session1 = TutorSession.objects.create(
            user=user,
            title='Session 1',
            status='active'
        )
        
        session2 = TutorSession.objects.create(
            user=user,
            title='Session 2',
            status='completed'
        )
        
        # Create some courses
        course1 = Course.objects.create(title='Course 1')
        course2 = Course.objects.create(title='Course 2')
        
        # Test dashboard view
        url = reverse('ai_tutor_dashboard')
        response = client.get(url)
        
        # Check response
        assert response.status_code == 200
        
        # Check context
        assert 'user_sessions' in response.context
        assert 'courses' in response.context
        
        # Check sessions
        sessions = list(response.context['user_sessions'])
        assert len(sessions) == 2
        assert session1 in sessions
        assert session2 in sessions
        
        # Check template
        assert 'ai_tutor/dashboard.html' in [t.name for t in response.templates]
    
    def test_create_session_view(self, authenticated_client):
        """Test creating a new session."""
        client, user = authenticated_client
        
        # Create a course
        course = Course.objects.create(title='Test Course')
        
        # Create a module
        module = Module.objects.create(
            title='Test Module',
            course=course,
            order=1
        )
        
        # Test creating a session
        url = reverse('create_tutor_session')
        session_data = {
            'title': 'New Session',
            'course': str(course.id),
            'module': str(module.id)
        }
        
        response = client.post(url, session_data)
        
        # Check redirect to session view
        assert response.status_code == 302
        assert 'ai_tutor_session' in response.url
        
        # Verify session was created
        session = TutorSession.objects.get(title='New Session')
        assert session.user == user
        assert session.course == course
        assert session.module == module
        assert session.status == 'active'
        
        # Verify welcome message was created
        welcome_message = TutorMessage.objects.filter(session=session, message_type='tutor').first()
        assert welcome_message is not None
        assert "Hello" in welcome_message.content
    
    def test_session_view(self, authenticated_client):
        """Test viewing a session."""
        client, user = authenticated_client
        
        # Create a session
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Add some messages
        user_message = TutorMessage.objects.create(
            session=session,
            message_type='user',
            content='Hello'
        )
        
        tutor_message = TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='Hi there, how can I help you?'
        )
        
        # Test session view
        url = reverse('ai_tutor_session', args=[session.id])
        response = client.get(url)
        
        # Check response
        assert response.status_code == 200
        
        # Check context
        assert 'session' in response.context
        assert 'messages' in response.context
        
        # Check session
        assert response.context['session'] == session
        
        # Check messages
        messages = list(response.context['messages'])
        assert len(messages) == 2
        assert user_message in messages
        assert tutor_message in messages
        
        # Check template
        assert 'ai_tutor/session.html' in [t.name for t in response.templates]
    
    def test_session_view_other_user(self, authenticated_client):
        """Test that users cannot view other users' sessions."""
        client, user = authenticated_client
        
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )
        
        # Create a session for the other user
        other_session = TutorSession.objects.create(
            user=other_user,
            title='Other Session',
            status='active'
        )
        
        # Test accessing other user's session
        url = reverse('ai_tutor_session', args=[other_session.id])
        response = client.get(url)
        
        # Should get 404
        assert response.status_code == 404
    
    @patch('ai_tutor.views.tutor_langchain_service.get_tutor_response')
    def test_send_message_view(self, mock_get_response, authenticated_client):
        """Test sending a message in a session."""
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
        
        # Test sending a message
        url = reverse('send_tutor_message', args=[session.id])
        message_data = {
            'message': 'What is machine learning?'
        }
        
        response = client.post(url, message_data)
        
        # Check response is JSON
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        # Parse JSON
        data = response.json()
        assert data['status'] == 'success'
        assert 'user_message' in data
        assert 'tutor_message' in data
        
        # Check message data
        assert data['user_message']['content'] == 'What is machine learning?'
        assert data['tutor_message']['content'] == 'This is a test response'
        
        # Verify messages were created in database
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
    
    def test_provide_feedback_view(self, authenticated_client):
        """Test providing feedback on a message."""
        client, user = authenticated_client
        
        # Create a session
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Add a message
        message = TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='This is a test response'
        )
        
        # Test providing feedback
        url = reverse('provide_tutor_feedback', args=[message.id])
        feedback_data = {
            'helpful': 'true',
            'rating': '5',
            'comment': 'Very helpful response!'
        }
        
        response = client.post(url, feedback_data)
        
        # Check response is JSON
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        # Parse JSON
        data = response.json()
        assert data['status'] == 'success'
        assert 'feedback_id' in data
        
        # Verify feedback was created
        feedback = TutorFeedback.objects.get(id=data['feedback_id'])
        assert feedback.session == session
        assert feedback.message == message
        assert feedback.user == user
        assert feedback.helpful is True
        assert feedback.rating == 5
        assert feedback.comment == 'Very helpful response!'
    
    def test_end_session_view(self, authenticated_client):
        """Test ending a session."""
        client, user = authenticated_client
        
        # Create a session
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Test ending the session
        url = reverse('end_tutor_session', args=[session.id])
        response = client.post(url)
        
        # Check redirect to dashboard
        assert response.status_code == 302
        assert reverse('ai_tutor_dashboard') in response.url
        
        # Verify session was completed
        session.refresh_from_db()
        assert session.status == 'completed'
        
        # Verify closing message was created
        system_message = TutorMessage.objects.filter(
            session=session,
            message_type='system'
        ).first()
        
        assert system_message is not None
        assert "completed" in system_message.content.lower()