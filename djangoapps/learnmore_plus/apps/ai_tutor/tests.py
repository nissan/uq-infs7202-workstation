from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from unittest.mock import patch, MagicMock
import json

from apps.courses.models import Course, Module, Content
from .models import TutorSession, TutorMessage, TutorContextItem, ContentEmbedding
from .services import TutorService, ContentIndexingService, LLMFactory
from .views import chat_view, send_message, create_session, session_list

User = get_user_model()

class AiTutorModelTests(TestCase):
    """Test cases for AI Tutor models."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Create a module
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Module Description',
            order=1
        )
        
        # Create content
        self.content = Content.objects.create(
            module=self.module,
            title='Test Content',
            content='This is test content for testing the AI Tutor functionality.',
            content_type='text',
            order=1
        )
        
        # Create a tutor session
        self.session = TutorSession.objects.create(
            user=self.user,
            course=self.course,
            module=self.module,
            content=self.content,
            session_type='content',
            title='Test Session'
        )
        
        # Create context item
        self.context_item = TutorContextItem.objects.create(
            session=self.session,
            context_type='content',
            content_object_id=self.content.id,
            title='Test Context',
            content='Test context content',
            order=0
        )
        
        # Create messages
        self.system_message = TutorMessage.objects.create(
            session=self.session,
            message_type='system',
            content='Test system message'
        )
        
        self.user_message = TutorMessage.objects.create(
            session=self.session,
            message_type='user',
            content='What is this course about?'
        )
        
        self.assistant_message = TutorMessage.objects.create(
            session=self.session,
            message_type='assistant',
            content='This course is about testing AI tutoring functionality.'
        )
    
    def test_session_str_method(self):
        """Test the string representation of a TutorSession."""
        self.assertEqual(str(self.session), 'Test Session')
    
    def test_session_without_title(self):
        """Test the string representation of a TutorSession without a title."""
        session = TutorSession.objects.create(
            user=self.user,
            course=self.course,
            session_type='course'
        )
        self.assertEqual(str(session), f"Session for {self.course.title}")

    def test_context_item_str_method(self):
        """Test the string representation of a TutorContextItem."""
        self.assertEqual(str(self.context_item), 'Test Context')
    
    def test_message_str_method(self):
        """Test the string representation of a TutorMessage."""
        self.assertEqual(
            str(self.user_message), 
            f"{self.user_message.message_type} message in {self.session}"
        )
    
    def test_get_context_items(self):
        """Test getting context items for a session."""
        items = self.session.get_context_items()
        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first(), self.context_item)


class TutorServiceTests(TestCase):
    """Test cases for TutorService."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Create a module
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Module Description',
            order=1
        )
        
        # Create content
        self.content = Content.objects.create(
            module=self.module,
            title='Test Content',
            content='This is test content for testing the AI Tutor functionality.',
            content_type='text',
            order=1
        )
    
    @patch('apps.ai_tutor.services.LLMFactory.get_chat_model')
    def test_create_session(self, mock_get_chat_model):
        """Test creating a new tutor session."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Mock assistant response"
        mock_llm.invoke.return_value = mock_response
        mock_get_chat_model.return_value = mock_llm
        
        # Create a session
        session = TutorService.create_session(
            user=self.user,
            course=self.course,
            module=self.module,
            content=self.content,
            title='Test Session',
            session_type='content'
        )
        
        # Check the session was created
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.course, self.course)
        self.assertEqual(session.module, self.module)
        self.assertEqual(session.content, self.content)
        self.assertEqual(session.title, 'Test Session')
        self.assertEqual(session.session_type, 'content')
        
        # Check that context items were created
        self.assertTrue(session.context_items.exists())
        
        # Check that a system message was created
        self.assertTrue(session.messages.filter(message_type='system').exists())
    
    @patch('apps.ai_tutor.services.LLMFactory.get_chat_model')
    def test_generate_assistant_response(self, mock_get_chat_model):
        """Test generating an assistant response."""
        # Create a session
        session = TutorSession.objects.create(
            user=self.user,
            course=self.course,
            session_type='course'
        )
        
        # Create a system message
        TutorMessage.objects.create(
            session=session,
            message_type='system',
            content='Test system message'
        )
        
        # Mock the LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test assistant response"
        mock_llm.invoke.return_value = mock_response
        mock_get_chat_model.return_value = mock_llm
        
        # Generate a response
        message = TutorService.generate_assistant_response(session, "Test user message")
        
        # Check the response
        self.assertEqual(message.message_type, 'assistant')
        self.assertEqual(message.content, 'Test assistant response')
        
        # Check that user message was created
        self.assertTrue(session.messages.filter(message_type='user', content="Test user message").exists())


class AiTutorViewTests(TestCase):
    """Test cases for AI Tutor views."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a client and log in
        self.client = Client()
        self.client.login(username='testuser', password='password123')
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Create a module
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Module Description',
            order=1
        )
        
        # Create content
        self.content = Content.objects.create(
            module=self.module,
            title='Test Content',
            content='This is test content for testing the AI Tutor functionality.',
            content_type='text',
            order=1
        )
        
        # Create a tutor session
        self.session = TutorSession.objects.create(
            user=self.user,
            course=self.course,
            module=self.module,
            content=self.content,
            session_type='content',
            title='Test Session'
        )
        
        # Create messages
        self.system_message = TutorMessage.objects.create(
            session=self.session,
            message_type='system',
            content='Test system message'
        )
        
        self.user_message = TutorMessage.objects.create(
            session=self.session,
            message_type='user',
            content='What is this course about?'
        )
        
        self.assistant_message = TutorMessage.objects.create(
            session=self.session,
            message_type='assistant',
            content='This course is about testing AI tutoring functionality.'
        )
        
        # Set up request factory
        self.factory = RequestFactory()
    
    def test_session_list_view(self):
        """Test the session list view."""
        response = self.client.get(reverse('ai_tutor:session_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ai_tutor/session_list.html')
        self.assertContains(response, 'Test Session')
    
    def test_chat_view(self):
        """Test the chat view."""
        response = self.client.get(reverse('ai_tutor:chat', args=[self.session.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ai_tutor/chat.html')
        self.assertContains(response, 'What is this course about?')
        self.assertContains(response, 'This course is about testing AI tutoring functionality.')
    
    @patch('apps.ai_tutor.services.LLMFactory.get_chat_model')
    def test_send_message(self, mock_get_chat_model):
        """Test sending a message."""
        # Mock the LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test assistant response"
        mock_llm.invoke.return_value = mock_response
        mock_get_chat_model.return_value = mock_llm
        
        response = self.client.post(
            reverse('ai_tutor:send_message', args=[self.session.id]),
            {'message': 'Test user message'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['user_message']['content'], 'Test user message')
        self.assertEqual(data['assistant_message']['content'], 'Test assistant response')
    
    def test_course_tutor_view(self):
        """Test the course tutor view."""
        response = self.client.get(reverse('ai_tutor:course_tutor', args=[self.course.slug]))
        
        # Should redirect to the chat view
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('ai_tutor:chat', args=[1])))


class LLMFactoryTests(TestCase):
    """Test cases for LLMFactory."""
    
    @patch('apps.ai_tutor.services.ChatOllama')
    def test_get_chat_model_ollama(self, mock_chat_ollama):
        """Test getting a chat model from Ollama."""
        # Set up mock settings
        with self.settings(OLLAMA_BASE_URL='http://localhost:11434', OLLAMA_MODEL_NAME='llama3'):
            LLMFactory.get_chat_model()
            mock_chat_ollama.assert_called_once_with(
                base_url='http://localhost:11434',
                model='llama3',
                temperature=0.7
            )
    
    @patch('apps.ai_tutor.services.ChatOpenAI')
    def test_get_chat_model_openai(self, mock_chat_openai):
        """Test getting a chat model from OpenAI."""
        # Set up mock settings
        with self.settings(OPENAI_API_KEY='test-key', OLLAMA_BASE_URL=None):
            LLMFactory.get_chat_model()
            mock_chat_openai.assert_called_once()


class ContentIndexingServiceTests(TestCase):
    """Test cases for ContentIndexingService."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Create a module
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Module Description',
            order=1
        )
        
        # Create content
        self.content = Content.objects.create(
            module=self.module,
            title='Test Content',
            content='This is test content for testing the AI Tutor functionality.',
            content_type='text',
            order=1
        )
    
    @patch('apps.ai_tutor.services.LLMFactory.get_embedding_model')
    @patch('apps.ai_tutor.services.Chroma')
    def test_get_vector_store(self, mock_chroma, mock_get_embedding_model):
        """Test getting a vector store."""
        mock_embedding_function = MagicMock()
        mock_get_embedding_model.return_value = mock_embedding_function
        
        ContentIndexingService.get_vector_store()
        
        mock_chroma.assert_called_once()
        mock_get_embedding_model.assert_called_once()
    
    @patch('apps.ai_tutor.services.LLMFactory.get_embedding_model')
    @patch('apps.ai_tutor.services.Chroma')
    def test_index_content(self, mock_chroma, mock_get_embedding_model):
        """Test indexing content."""
        # Mock embedding model
        mock_embedding_function = MagicMock()
        mock_get_embedding_model.return_value = mock_embedding_function
        
        # Mock vector store
        mock_vector_store = MagicMock()
        mock_chroma.return_value = mock_vector_store
        
        # Mock JSON operations
        with patch('json.dumps') as mock_dumps:
            mock_dumps.return_value = '[]'
            
            # Index the content
            ContentIndexingService.index_content(self.content)
            
            # Check that the embedding was stored
            self.assertTrue(ContentEmbedding.objects.filter(content=self.content).exists())
            
            # Check vector store was called
            mock_vector_store.add_texts.assert_called_once()


class APIEndpointTests(TestCase):
    """Test cases for API endpoints."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a client and log in
        self.client = Client()
        self.client.login(username='testuser', password='password123')
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Create a tutor session
        self.session = TutorSession.objects.create(
            user=self.user,
            course=self.course,
            session_type='course',
            title='Test Session'
        )
        
        # Create messages
        self.user_message = TutorMessage.objects.create(
            session=self.session,
            message_type='user',
            content='Test user message'
        )
        
        self.assistant_message = TutorMessage.objects.create(
            session=self.session,
            message_type='assistant',
            content='Test assistant response'
        )
    
    def test_api_sessions_get(self):
        """Test the sessions API GET endpoint."""
        response = self.client.get(reverse('ai_tutor:api_sessions'))
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        self.assertTrue('sessions' in data)
        self.assertEqual(len(data['sessions']), 1)
        self.assertEqual(data['sessions'][0]['title'], 'Test Session')
    
    @patch('apps.ai_tutor.services.TutorService.create_session')
    def test_api_sessions_post(self, mock_create_session):
        """Test the sessions API POST endpoint."""
        # Mock the create_session method
        mock_session = MagicMock()
        mock_session.id = 99
        mock_session.title = 'New Test Session'
        mock_create_session.return_value = mock_session
        
        response = self.client.post(
            reverse('ai_tutor:api_sessions'),
            json.dumps({
                'course_id': self.course.id,
                'title': 'New Test Session',
                'session_type': 'course'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        self.assertEqual(data['title'], 'New Test Session')
        mock_create_session.assert_called_once()
    
    def test_api_chat_get(self):
        """Test the chat API GET endpoint."""
        response = self.client.get(reverse('ai_tutor:api_chat', args=[self.session.id]))
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        self.assertTrue('messages' in data)
        self.assertEqual(len(data['messages']), 2)
        self.assertEqual(data['messages'][0]['content'], 'Test user message')
        self.assertEqual(data['messages'][1]['content'], 'Test assistant response')
    
    @patch('apps.ai_tutor.services.TutorService.generate_assistant_response')
    def test_api_chat_post(self, mock_generate_response):
        """Test the chat API POST endpoint."""
        # Mock the generate_assistant_response method
        mock_message = MagicMock()
        mock_message.id = 99
        mock_message.content = 'New test response'
        mock_message.created_at = '2023-01-01T00:00:00Z'
        mock_generate_response.return_value = mock_message
        
        response = self.client.post(
            reverse('ai_tutor:api_chat', args=[self.session.id]),
            json.dumps({
                'message': 'New test message'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        self.assertEqual(data['content'], 'New test response')
        mock_generate_response.assert_called_once()