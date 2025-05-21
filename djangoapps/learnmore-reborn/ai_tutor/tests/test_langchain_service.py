import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from ai_tutor.models import (
    TutorSession,
    TutorMessage,
    TutorKnowledgeBase,
    TutorFeedback,
    TutorConfiguration
)
from ai_tutor.langchain_service import TutorLangChainService
from courses.models import Course, Module
from langchain_community.docstore.document import Document

User = get_user_model()

@pytest.mark.django_db
class TestLangChainService:
    """Test cases for the LangChain service integration."""
    
    def test_initialization_without_api_key(self):
        """Test that the service initializes properly without an API key."""
        # Test with no API key
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            service = TutorLangChainService()
            assert service.api_key == ''
            assert service.embeddings is None
            assert service.llm is None
            assert service.vector_store is None
    
    def test_initialization_with_api_key(self):
        """Test that the service initializes properly with an API key."""
        # Test with mock API key
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            # Mock the OpenAI embeddings and LLM
            with patch('ai_tutor.langchain_service.OpenAIEmbeddings') as mock_embeddings, \
                 patch('ai_tutor.langchain_service.ChatOpenAI') as mock_llm, \
                 patch('ai_tutor.langchain_service.Chroma') as mock_chroma, \
                 patch('ai_tutor.langchain_service.os.path.exists', return_value=False):
                
                service = TutorLangChainService()
                
                # Assert embeddings and LLM were initialized
                assert service.api_key == 'test_key'
                assert mock_embeddings.called
                assert mock_llm.called
                assert not mock_chroma.called  # Chroma shouldn't be called if no vector store exists
    
    def test_get_session_context(self):
        """Test that the session context is properly extracted."""
        # Create test user and session
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        course = Course.objects.create(
            title='Test Course',
            description='Course for testing'
        )
        
        module = Module.objects.create(
            title='Test Module',
            course=course,
            order=1
        )
        
        session = TutorSession.objects.create(
            user=user,
            course=course,
            module=module,
            title='Test Session',
            status='active'
        )
        
        # Create LangChain service
        service = TutorLangChainService()
        
        # Get session context
        context = service.get_session_context(session)
        
        # Assert context contains the correct information
        assert context['session_id'] == session.id
        assert context['user_id'] == user.id
        assert context['username'] == user.username
        assert context['course_title'] == course.title
        assert context['module_title'] == module.title
        assert context['quiz_title'] is None
    
    def test_get_conversation_history(self):
        """Test that the conversation history is properly extracted."""
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
        
        # Create messages
        user_message1 = TutorMessage.objects.create(
            session=session,
            message_type='user',
            content='Hello'
        )
        
        tutor_message1 = TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='Hi there, how can I help you?'
        )
        
        system_message = TutorMessage.objects.create(
            session=session,
            message_type='system',
            content='System message that should be ignored'
        )
        
        user_message2 = TutorMessage.objects.create(
            session=session,
            message_type='user',
            content='What is a neural network?'
        )
        
        tutor_message2 = TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content='Neural networks are computational models...'
        )
        
        # Create LangChain service
        service = TutorLangChainService()
        
        # Get conversation history
        history = service.get_conversation_history(session)
        
        # Assert history contains the correct messages in correct order (system messages excluded)
        assert len(history) == 4
        assert history[0]['role'] == 'human'
        assert history[0]['content'] == user_message1.content
        assert history[1]['role'] == 'ai'
        assert history[1]['content'] == tutor_message1.content
        assert history[2]['role'] == 'human'
        assert history[2]['content'] == user_message2.content
        assert history[3]['role'] == 'ai'
        assert history[3]['content'] == tutor_message2.content
        
        # Test with max_messages limit
        limited_history = service.get_conversation_history(session, max_messages=2)
        assert len(limited_history) == 2
        assert limited_history[0]['role'] == 'human'
        assert limited_history[0]['content'] == user_message2.content
        assert limited_history[1]['role'] == 'ai'
        assert limited_history[1]['content'] == tutor_message2.content
    
    def test_get_tutor_response_without_api_key(self):
        """Test that placeholder responses are returned when no API key is available."""
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
        
        # Create LangChain service with no API key
        service = TutorLangChainService()
        service.api_key = ''
        
        # Get tutor response
        response = service.get_tutor_response(session, "What is a neural network?")
        
        # Assert response contains placeholder text
        assert "placeholder response" in response['content'].lower()
        assert response['sources'] == []
        assert response['metadata']['placeholder'] is True
    
    @patch('ai_tutor.langchain_service.ConversationalRetrievalChain.from_llm')
    def test_get_retrieval_chain(self, mock_chain_from_llm):
        """Test that the retrieval chain is properly created."""
        # Create a mock chain
        mock_chain = MagicMock()
        mock_chain_from_llm.return_value = mock_chain
        
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
        
        # Create a tutor configuration
        config = TutorConfiguration.objects.create(
            name='Test Config',
            system_prompt='You are a helpful AI tutor for {course_title}.'
        )
        
        # Create LangChain service with mocked components
        service = TutorLangChainService()
        service.llm = MagicMock()
        service.vector_store = MagicMock()
        service.vector_store.as_retriever.return_value = "mock_retriever"
        
        # Get retrieval chain
        chain = service.get_retrieval_chain(session)
        
        # Assert chain was created and configured
        assert chain == mock_chain
        assert mock_chain_from_llm.called
        
        # Extract args from the call
        call_args = mock_chain_from_llm.call_args[1]
        assert call_args['llm'] == service.llm
        assert call_args['retriever'] == "mock_retriever"
        assert 'memory' in call_args
        assert call_args['verbose'] is True
        assert call_args['return_source_documents'] is True
        
        # Test without LLM or vector store
        service.llm = None
        service.vector_store = None
        chain = service.get_retrieval_chain(session)
        
        # Assert chain is None when components are missing
        assert chain is None
    
    def test_process_knowledge_base(self):
        """Test processing knowledge base entries."""
        # Create mock knowledge base entries
        course = Course.objects.create(
            title='Test Course',
            description='Course for testing'
        )
        
        TutorKnowledgeBase.objects.create(
            title='Test Knowledge 1',
            content='This is test content 1',
            course=course
        )
        
        TutorKnowledgeBase.objects.create(
            title='Test Knowledge 2',
            content='This is test content 2',
            course=course
        )
        
        # Create LangChain service with mocked components
        with patch('ai_tutor.langchain_service.RecursiveCharacterTextSplitter') as mock_splitter, \
             patch.object(TutorLangChainService, 'create_vector_store') as mock_create, \
             patch.object(TutorLangChainService, 'update_vector_store') as mock_update:
            
            # Mock the text splitter to return documents
            mock_splitter_instance = MagicMock()
            mock_splitter.return_value = mock_splitter_instance
            
            # Mock document creation
            mock_splitter_instance.create_documents.return_value = [Document(page_content="test", metadata={})]
            
            # Mock vector store operations
            mock_create.return_value = True
            mock_update.return_value = True
            
            # Create service
            service = TutorLangChainService()
            
            # Test creating a new vector store
            service.vector_store = None
            result = service.process_knowledge_base()
            
            # Assert vector store was created
            assert result is True
            assert mock_create.called
            assert not mock_update.called
            
            # Test updating an existing vector store
            mock_create.reset_mock()
            mock_update.reset_mock()
            
            service.vector_store = MagicMock()
            result = service.process_knowledge_base()
            
            # Assert vector store was updated
            assert result is True
            assert mock_update.called
            assert not mock_create.called