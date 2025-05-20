import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from ai_tutor.models import (
    TutorSession,
    TutorMessage,
    TutorKnowledgeBase,
    TutorFeedback,
    TutorConfiguration
)
from courses.models import Course, Module

User = get_user_model()

@pytest.mark.django_db
class TestTutorModels:
    """Test cases for the AI Tutor models."""
    
    def test_tutor_session_creation(self, client):
        """Test that a TutorSession can be created correctly."""
        # Create test user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test course and module
        course = Course.objects.create(
            title='Test Course',
            description='Course for testing'
        )
        
        module = Module.objects.create(
            title='Test Module',
            course=course,
            order=1
        )
        
        # Create a tutor session
        session = TutorSession.objects.create(
            user=user,
            course=course,
            module=module,
            title='Test Session',
            status='active'
        )
        
        # Assert that the session was created with the correct attributes
        assert session.user == user
        assert session.course == course
        assert session.module == module
        assert session.title == 'Test Session'
        assert session.status == 'active'
        assert session.created_at is not None
        assert session.updated_at is not None
        assert str(session) == f"{user.username} - Test Session"
    
    def test_tutor_message_creation(self, client):
        """Test that a TutorMessage can be created correctly."""
        # Create test user and session
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Create user message
        user_message = TutorMessage.objects.create(
            session=session,
            message_type='user',
            content='This is a test message'
        )
        
        # Create tutor response
        tutor_message = TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='This is a response to your test message'
        )
        
        # Assert messages were created correctly
        assert user_message.session == session
        assert user_message.message_type == 'user'
        assert user_message.content == 'This is a test message'
        assert user_message.created_at is not None
        
        assert tutor_message.session == session
        assert tutor_message.message_type == 'tutor'
        assert tutor_message.content == 'This is a response to your test message'
        assert tutor_message.created_at is not None
        
        # Check string representation
        assert 'user message in' in str(user_message)
        assert 'tutor message in' in str(tutor_message)
    
    def test_tutor_knowledge_base_creation(self, client):
        """Test that a TutorKnowledgeBase can be created correctly."""
        # Create test course
        course = Course.objects.create(
            title='Test Course',
            description='Course for testing'
        )
        
        # Create knowledge base entry
        knowledge = TutorKnowledgeBase.objects.create(
            title='Test Knowledge',
            content='This is test knowledge content',
            course=course
        )
        
        # Assert knowledge was created correctly
        assert knowledge.title == 'Test Knowledge'
        assert knowledge.content == 'This is test knowledge content'
        assert knowledge.course == course
        assert knowledge.created_at is not None
        assert knowledge.updated_at is not None
        assert str(knowledge) == 'Test Knowledge'
    
    def test_tutor_feedback_creation(self, client):
        """Test that a TutorFeedback can be created correctly."""
        # Create test user and session
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        session = TutorSession.objects.create(
            user=user,
            title='Test Session',
            status='active'
        )
        
        # Create message
        message = TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='This is a test message'
        )
        
        # Create feedback
        feedback = TutorFeedback.objects.create(
            session=session,
            user=user,
            message=message,
            rating=4,
            helpful=True,
            comment='This was very helpful!'
        )
        
        # Assert feedback was created correctly
        assert feedback.session == session
        assert feedback.user == user
        assert feedback.message == message
        assert feedback.rating == 4
        assert feedback.helpful is True
        assert feedback.comment == 'This was very helpful!'
        assert feedback.created_at is not None
        assert f"Feedback on {session} by {user.username}" in str(feedback)
    
    def test_tutor_configuration_creation(self, client):
        """Test that a TutorConfiguration can be created correctly."""
        # Create configuration
        config = TutorConfiguration.objects.create(
            name='Test Configuration',
            model_provider='openai',
            model_name='gpt-3.5-turbo',
            temperature=0.7,
            max_tokens=1000,
            system_prompt='You are a helpful AI tutor.'
        )
        
        # Assert configuration was created correctly
        assert config.name == 'Test Configuration'
        assert config.model_provider == 'openai'
        assert config.model_name == 'gpt-3.5-turbo'
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.system_prompt == 'You are a helpful AI tutor.'
        assert config.is_active is True
        assert config.created_at is not None
        assert config.updated_at is not None
        assert str(config) == 'Test Configuration'