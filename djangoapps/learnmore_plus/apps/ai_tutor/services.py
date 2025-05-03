import os
import json
import logging
from typing import List, Dict, Any, Optional, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.embeddings import Embeddings

# Import the local Ollama chat model for development
from langchain_community.chat_models import ChatOllama

# For production, can use any of these depending on configuration
from langchain_openai import ChatOpenAI
# Updated imports to remove deprecation warnings
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

# For vector storage - updated import
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from apps.courses.models import Course, Module, Content
from .models import TutorSession, TutorMessage, TutorContextItem, ContentEmbedding

logger = logging.getLogger(__name__)
User = get_user_model()

class LLMFactory:
    """Factory for creating LLM instances based on configuration."""
    
    @staticmethod
    def get_chat_model(model_name: str = None) -> BaseChatModel:
        """Get a chat model based on configuration."""
        model_name = model_name or settings.DEFAULT_LLM_MODEL
        
        # Check for environment variables to determine which LLM provider to use
        if hasattr(settings, 'OLLAMA_BASE_URL') and settings.OLLAMA_BASE_URL:
            # Use Ollama for local development
            # Default to a good base model if not specified
            ollama_model = settings.OLLAMA_MODEL_NAME or "llama3"
            return ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=ollama_model,
                temperature=0.7,
            )
        elif hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            # Use OpenAI in production
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model_name=model_name or "gpt-3.5-turbo",
                temperature=0.7,
            )
        else:
            # Fallback to default model
            logger.warning("No LLM provider configured, using default Ollama")
            return ChatOllama(model="llama3", temperature=0.7)
    
    @staticmethod
    def get_embedding_model() -> Embeddings:
        """Get an embedding model based on configuration."""
        # Check for environment variables to determine which embedding provider to use
        if hasattr(settings, 'OLLAMA_BASE_URL') and settings.OLLAMA_BASE_URL:
            # First try to check if the model is available
            try:
                import requests
                response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_name = settings.OLLAMA_EMBEDDING_MODEL or "nomic-embed-text"
                    
                    # Check if the model is available, allowing for both exact match and with :latest tag
                    model_available = any(m.get("name") == model_name or 
                                          m.get("name") == f"{model_name}:latest" or
                                          m.get("name").startswith(f"{model_name}:") 
                                          for m in models)
                    
                    if not model_available:
                        logger.warning(
                            f"Embedding model '{model_name}' not found in Ollama. "
                            f"Please run: ollama pull {model_name}"
                        )
                        # If OpenAI is configured, fall back to that
                        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                            from langchain_openai import OpenAIEmbeddings
                            logger.info("Falling back to OpenAI embeddings")
                            return OpenAIEmbeddings(
                                api_key=settings.OPENAI_API_KEY,
                                model="text-embedding-3-small"
                            )
                        # Otherwise fall back to local HuggingFace embeddings
                        logger.info("Falling back to local HuggingFace embeddings")
                        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Error checking Ollama models: {str(e)}")
                
            # If we got here, try to use Ollama
            try:
                model_name = settings.OLLAMA_EMBEDDING_MODEL or "nomic-embed-text"
                
                # Find the actual model name with tag from available models
                found_model = None
                if 'models' in locals() and models:
                    for m in models:
                        if (m.get("name") == model_name or 
                            m.get("name") == f"{model_name}:latest" or 
                            m.get("name").startswith(f"{model_name}:")):
                            found_model = m.get("name")
                            break
                
                # If found, use the exact model name, otherwise fallback to the base name
                model_to_use = found_model if found_model else model_name
                
                logger.info(f"Using Ollama embedding model: {model_to_use}")
                return OllamaEmbeddings(
                    base_url=settings.OLLAMA_BASE_URL,
                    model=model_to_use
                )
            except Exception as e:
                logger.error(f"Error initializing Ollama embeddings: {str(e)}")
                # Fall back to alternatives
                
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            # Use OpenAI's embedding model
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                api_key=settings.OPENAI_API_KEY,
                model="text-embedding-3-small"
            )
        else:
            # Fallback to Hugging Face embeddings (local)
            logger.warning("No embedding provider configured, using local HuggingFace embeddings")
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

class ContentIndexingService:
    """Service for indexing course content for retrieval augmented generation."""
    
    @classmethod
    def get_embedding_store_path(cls) -> str:
        """Get the path to the embeddings store."""
        base_dir = getattr(settings, 'VECTOR_DB_PATH', os.path.join(settings.BASE_DIR, 'vectorstore'))
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    
    @classmethod
    def get_vector_store(cls) -> Chroma:
        """Get or create a vector store for content embeddings."""
        embedding_function = LLMFactory.get_embedding_model()
        return Chroma(
            persist_directory=cls.get_embedding_store_path(),
            embedding_function=embedding_function,
            collection_name="course_content"
        )
    
    @classmethod
    def get_retriever(cls) -> VectorStoreRetriever:
        """Get a retriever for querying content."""
        vector_store = cls.get_vector_store()
        return vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Return top 5 results
        )
    
    @classmethod
    def index_content(cls, content_obj: Content) -> None:
        """Index a single content object for retrieval."""
        try:
            # Prepare metadata with additional error checking
            try:
                metadata = {
                    "content_id": content_obj.id,
                    "title": str(content_obj.title),
                    "content_type": str(content_obj.content_type),
                    "module_id": content_obj.module_id,
                }
                
                # Add additional metadata with error checking
                try:
                    metadata["module_title"] = str(content_obj.module.title)
                except Exception:
                    metadata["module_title"] = "Unknown Module"
                    
                try:
                    metadata["course_id"] = content_obj.module.course_id
                except Exception:
                    metadata["course_id"] = 0
                    
                try:
                    metadata["course_title"] = str(content_obj.module.course.title)
                except Exception:
                    metadata["course_title"] = "Unknown Course"
            except Exception as meta_error:
                # Fallback to minimal metadata if there's an error
                logger.error(f"Error creating metadata for content {content_obj.id}: {str(meta_error)}")
                metadata = {
                    "content_id": content_obj.id,
                    "title": "Unknown Content",
                    "content_type": "text",
                    "module_id": 0,
                    "module_title": "Unknown Module",
                    "course_id": 0,
                    "course_title": "Unknown Course",
                }
            
            # Clean up the content - remove HTML tags, etc.
            try:
                clean_text = cls._clean_content_text(content_obj.content)
            except Exception as text_error:
                logger.error(f"Error cleaning content text: {str(text_error)}")
                clean_text = "Content unavailable"
            
            # Create or update embedding in the database
            try:
                embedding_json = cls._generate_embedding_json(clean_text)
            except Exception as embed_error:
                logger.error(f"Error generating embedding JSON: {str(embed_error)}")
                # Create a fallback embedding of zeros
                mock_vector = [0.0] * 768  # Standard embedding size
                embedding_json = json.dumps(mock_vector)
            
            try:
                with transaction.atomic():
                    # Store in database for reference
                    ContentEmbedding.objects.update_or_create(
                        content=content_obj,
                        defaults={
                            'embedding_vector': embedding_json,
                            'chunk_text': clean_text[:1000] if len(clean_text) > 0 else "No content available"  # Store a preview
                        }
                    )
                    
                    # Store in vector database
                    try:
                        vector_store = cls.get_vector_store()
                        vector_store.add_texts(
                            texts=[clean_text],
                            metadatas=[metadata],
                            ids=[f"content_{content_obj.id}"]
                        )
                        # Removed vector_store.persist() call - Chroma 0.4.x+ automatically persists
                    except Exception as store_error:
                        logger.error(f"Error storing in vector database: {str(store_error)}")
                        # We've already saved to the database, so we'll consider this a partial success
            except Exception as db_error:
                logger.error(f"Error saving to database: {str(db_error)}")
                # This is a critical error, so we'll re-raise
                raise
                
            logger.info(f"Successfully indexed content: {content_obj.title} (ID: {content_obj.id})")
        except Exception as e:
            logger.error(f"Error indexing content {content_obj.id}: {str(e)}")
            # Convert error to string to remove any problematic objects
            error_str = str(e)
            if "_type" in error_str:
                logger.error("Detected _type error, likely from embeddings. Using fallback.")
                # We'll suppress this specific error
            else:
                # For other errors, we'll propagate them
                raise
    
    @classmethod
    def remove_content(cls, content_obj: Content) -> None:
        """Remove content from the vector database."""
        try:
            # Remove from vector database
            vector_store = cls.get_vector_store()
            vector_store.delete([f"content_{content_obj.id}"])
            # Removed vector_store.persist() call - Chroma 0.4.x+ automatically persists
            
            # Remove from database
            ContentEmbedding.objects.filter(content=content_obj).delete()
            
            logger.info(f"Successfully removed content from index: {content_obj.title} (ID: {content_obj.id})")
        except Exception as e:
            logger.error(f"Error removing content {content_obj.id} from index: {str(e)}")
    
    @classmethod
    def index_all_content(cls) -> None:
        """Index all content in the database."""
        count = 0
        for content in Content.objects.select_related('module__course').all():
            try:
                cls.index_content(content)
                count += 1
            except Exception as e:
                logger.error(f"Error indexing content {content.id}: {str(e)}")
        
        logger.info(f"Indexed {count} content items")
    
    @classmethod
    def search_content(cls, query: str, course_id: Optional[int] = None, 
                      module_id: Optional[int] = None, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant content based on a query.
        
        Args:
            query: The search query
            course_id: Optional course ID to filter results
            module_id: Optional module ID to filter results
            k: Number of results to return
            
        Returns:
            List of dictionaries containing content metadata and relevance score
        """
        try:
            retriever = cls.get_retriever()
            retriever.search_kwargs["k"] = k
            
            # Filter condition based on metadata
            filter_dict = {}
            if course_id:
                filter_dict["course_id"] = course_id
            if module_id:
                filter_dict["module_id"] = module_id
                
            if filter_dict:
                # If using Chroma, we need to convert to their filter format
                filter_condition = None
                for k, v in filter_dict.items():
                    if filter_condition is None:
                        filter_condition = {"$and": [{k: {"$eq": v}}]}
                    else:
                        filter_condition["$and"].append({k: {"$eq": v}})
                
                retriever.search_kwargs["filter"] = filter_condition
            
            # Perform the search
            docs = retriever.get_relevant_documents(query)
            
            # Format results
            results = []
            for doc in docs:
                results.append({
                    "content_id": doc.metadata.get("content_id"),
                    "title": doc.metadata.get("title", "Untitled"),
                    "content_type": doc.metadata.get("content_type"),
                    "module_id": doc.metadata.get("module_id"),
                    "module_title": doc.metadata.get("module_title", "Untitled"),
                    "course_id": doc.metadata.get("course_id"),
                    "course_title": doc.metadata.get("course_title", "Untitled"),
                    "text_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "relevance_score": getattr(doc, "score", 1.0),  # Some retrievers include a score
                })
            
            return results
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            return []
    
    @staticmethod
    def _clean_content_text(text: str) -> str:
        """Clean content text for embedding."""
        # Basic cleaning - in a real implementation, you might want
        # more sophisticated HTML/markdown parsing
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def _generate_embedding_json(text: str) -> str:
        """Generate embedding JSON for storage."""
        try:
            embedding_function = LLMFactory.get_embedding_model()
            embedding_vector = embedding_function.embed_query(text)
            
            # Handle different vector types with robust conversion
            try:
                # First, check if embedding_vector has _type attribute (LangChain object)
                if hasattr(embedding_vector, '_type'):
                    # Special handling for LangChain objects
                    if hasattr(embedding_vector, 'values') and callable(getattr(embedding_vector, 'values', None)):
                        embedding_vector = embedding_vector.values()
                    elif hasattr(embedding_vector, 'model_dump') and callable(getattr(embedding_vector, 'model_dump', None)):
                        # For Pydantic models 
                        embedding_data = embedding_vector.model_dump()
                        if isinstance(embedding_data, dict) and 'values' in embedding_data:
                            embedding_vector = embedding_data['values']
                        else:
                            embedding_vector = [0.0] * 768  # Fallback
                            logger.warning("Using fallback embedding: model_dump didn't contain values")
                    elif hasattr(embedding_vector, 'dict') and callable(getattr(embedding_vector, 'dict', None)):
                        # For older Pydantic models
                        embedding_data = embedding_vector.dict()
                        if isinstance(embedding_data, dict) and 'values' in embedding_data:
                            embedding_vector = embedding_data['values']
                        else:
                            embedding_vector = [0.0] * 768  # Fallback
                            logger.warning("Using fallback embedding: dict didn't contain values")
                    else:
                        # Generic fallback for complex objects
                        try:
                            # Try to convert directly to list
                            embedding_vector = list(embedding_vector)
                        except:
                            # Last resort fallback
                            logger.warning("Unable to extract vector data, using fallback zeros")
                            embedding_vector = [0.0] * 768  # Standard size
                
                # Check for numpy arrays (common in embeddings)
                if hasattr(embedding_vector, 'tolist') and callable(getattr(embedding_vector, 'tolist', None)):
                    embedding_vector = embedding_vector.tolist()
                
                # Handle if it's already a list 
                if not isinstance(embedding_vector, list):
                    # One more attempt to convert to list
                    try:
                        embedding_vector = list(embedding_vector)
                    except:
                        logger.warning("Failed to convert to list, using fallback")
                        embedding_vector = [0.0] * 768  # Fallback to standard size
                        
                # Final verification - ensure it's a basic list of numbers
                if not isinstance(embedding_vector, list) or len(embedding_vector) == 0:
                    logger.warning("Invalid vector format, using fallback")
                    embedding_vector = [0.0] * 768  # Fallback
                else:
                    # Check for non-serializable elements in the list
                    for i, val in enumerate(embedding_vector):
                        if not isinstance(val, (int, float)):
                            # Replace with 0.0 if not a number
                            embedding_vector[i] = 0.0
                            
            except Exception as e:
                logger.error(f"Error processing embedding vector: {str(e)}")
                embedding_vector = [0.0] * 768  # Fallback standard size
                
            # Ensure it's a basic Python type for JSON serialization
            return json.dumps(embedding_vector)
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            
            # Check if the error is related to missing Ollama models
            if "model \"nomic-embed-text\" not found" in str(e):
                logger.warning(
                    "The nomic-embed-text model is not available in Ollama. "
                    "Please run: ollama pull nomic-embed-text"
                )
                # Create a mock embedding vector (all zeros) as a fallback
                # This allows the system to continue without crashing
                mock_vector = [0.0] * 768  # Standard embedding size
                return json.dumps(mock_vector)
            
            return "[]"

class TutorService:
    """Service for AI tutor functionality."""
    
    SYSTEM_PROMPT = """
    You are an AI tutor for the LearnMore+ platform, designed to help students learn course material.
    
    Your responsibilities:
    1. Answer questions about course content
    2. Provide explanations in a clear, concise manner
    3. Use examples to illustrate concepts
    4. Help students understand difficult topics
    5. Relate content to real-world applications
    
    Guidelines:
    - Be supportive and encouraging
    - Avoid giving direct answers to quiz questions; instead guide students to the answer
    - Use the context provided about course content
    - Acknowledge when you don't know something
    - Keep responses focused on the student's needs
    
    Current course: {course_title}
    Current module: {module_title}
    Current content: {content_title}
    
    Available context from the course material:
    {context}
    """
    
    @classmethod
    def create_session(cls, user, course=None, module=None, content=None, title=None, session_type='general'):
        """Create a new tutor session."""
        session = TutorSession.objects.create(
            user=user,
            course=course,
            module=module,
            content=content,
            title=title or cls._generate_session_title(course, module, content),
            session_type=session_type,
            llm_model=settings.DEFAULT_LLM_MODEL if hasattr(settings, 'DEFAULT_LLM_MODEL') else 'default'
        )
        
        # Add initial context items if we have related content
        if content:
            cls.add_context_from_content(session, content)
        elif module:
            cls.add_context_from_module(session, module)
        elif course:
            cls.add_context_from_course(session, course)
        
        # Add system message to start the conversation
        cls.add_system_message(session)
        
        return session
    
    @classmethod
    def add_context_from_content(cls, session, content):
        """Add context from a content object."""
        TutorContextItem.objects.create(
            session=session,
            context_type='content',
            content_object_id=content.id,
            title=content.title,
            content=content.content,
            order=0
        )
    
    @classmethod
    def add_context_from_module(cls, session, module):
        """Add context from a module's contents."""
        # Get top content items from the module
        contents = module.contents.all().order_by('order')[:5]
        for i, content in enumerate(contents):
            TutorContextItem.objects.create(
                session=session,
                context_type='content',
                content_object_id=content.id,
                title=content.title,
                content=content.content,
                order=i
            )
    
    @classmethod
    def add_context_from_course(cls, session, course):
        """Add context about the course."""
        TutorContextItem.objects.create(
            session=session,
            context_type='course',
            content_object_id=course.id,
            title=f"About {course.title}",
            content=course.description,
            order=0
        )
        
        # Get module descriptions
        modules = course.modules.all().order_by('order')[:3]
        for i, module in enumerate(modules):
            TutorContextItem.objects.create(
                session=session,
                context_type='module',
                content_object_id=module.id,
                title=module.title,
                content=module.description,
                order=i+1
            )
    
    @classmethod
    def add_system_message(cls, session):
        """Add the initial system message to the session."""
        # Compile context from the session's context items
        context_items = session.get_context_items()
        context_text = "\n\n".join([f"--- {item.title} ---\n{item.content}" for item in context_items])
        
        # Get course/module/content titles if available
        course_title = session.course.title if session.course else "N/A"
        module_title = session.module.title if session.module else "N/A"
        content_title = session.content.title if session.content else "N/A"
        
        # Format the system message
        system_message = cls.SYSTEM_PROMPT.format(
            course_title=course_title,
            module_title=module_title,
            content_title=content_title,
            context=context_text
        )
        
        # Save as first message
        TutorMessage.objects.create(
            session=session,
            message_type='system',
            content=system_message
        )
        
        return system_message
    
    @classmethod
    def add_user_message(cls, session, message_text):
        """Add a user message to the session."""
        message = TutorMessage.objects.create(
            session=session,
            message_type='user',
            content=message_text
        )
        
        # Find relevant context based on the message
        relevant_context = cls._get_relevant_context(session, message_text)
        
        # Associate with the message
        if relevant_context:
            message.relevant_context_used.add(*relevant_context)
        
        return message
    
    @classmethod
    def generate_assistant_response(cls, session, message_text):
        """
        Generate an assistant response to a user message.
        
        Args:
            session: The TutorSession object
            message_text: The user's message text
            
        Returns:
            The assistant response message object
        """
        # Add the user message first
        user_message = cls.add_user_message(session, message_text)
        
        try:
            # Get message history
            messages = cls._prepare_chat_history(session)
            
            # Find relevant context
            relevant_context = cls._get_relevant_context(session, message_text)
            
            # Create LLM instance
            llm = LLMFactory.get_chat_model(session.llm_model)
            
            # Generate response
            response = llm.invoke(messages)
            response_text = response.content
            
            # Save the assistant message
            assistant_message = TutorMessage.objects.create(
                session=session,
                message_type='assistant',
                content=response_text,
                tokens_used=cls._estimate_tokens(response_text)  # Estimate tokens used
            )
            
            # Link relevant context
            if relevant_context:
                assistant_message.relevant_context_used.add(*relevant_context)
                
            # Update session
            session.updated_at = assistant_message.created_at
            session.save(update_fields=['updated_at'])
                
            return assistant_message
        except Exception as e:
            # Log the error
            logger.error(f"Error generating tutor response: {str(e)}")
            
            # Create error message
            error_response = TutorMessage.objects.create(
                session=session,
                message_type='assistant',
                content="I'm sorry, I encountered an error while trying to respond. Please try again or contact support if the issue persists."
            )
            
            return error_response
    
    @classmethod
    def _prepare_chat_history(cls, session):
        """Prepare the chat history for the LLM."""
        messages = []
        
        # Get all messages in order
        for msg in session.messages.all().order_by('created_at'):
            if msg.message_type == 'system':
                messages.append(SystemMessage(content=msg.content))
            elif msg.message_type == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.message_type == 'assistant':
                messages.append(AIMessage(content=msg.content))
        
        return messages
    
    @classmethod
    def _get_relevant_context(cls, session, query):
        """Get relevant context items for the query."""
        # First, check existing context items in the session
        existing_items = list(session.context_items.all())
        
        # If we have a course, use it to filter results
        course_id = session.course.id if session.course else None
        module_id = session.module.id if session.module else None
        
        # Search for relevant content
        results = ContentIndexingService.search_content(
            query=query,
            course_id=course_id,
            module_id=module_id,
            k=3  # Get top 3 results
        )
        
        # Create context items for new results
        new_items = []
        for i, result in enumerate(results):
            # Skip if already have this content as context
            if any(item.context_type == 'content' and 
                  item.content_object_id == result['content_id'] for item in existing_items):
                continue
                
            # Otherwise create a new context item
            try:
                content = Content.objects.get(id=result['content_id'])
                item = TutorContextItem.objects.create(
                    session=session,
                    context_type='content',
                    content_object_id=result['content_id'],
                    title=result['title'],
                    content=content.content,
                    relevance_score=result.get('relevance_score', 0.8),
                    order=len(existing_items) + i
                )
                new_items.append(item)
            except Content.DoesNotExist:
                continue
        
        # Return all context items to link to the message
        return existing_items + new_items
    
    @staticmethod
    def _generate_session_title(course, module, content):
        """Generate a title for the session based on context."""
        if content:
            return f"Session about {content.title}"
        elif module:
            return f"Session about {module.title}"
        elif course:
            return f"Session for {course.title}"
        else:
            return f"General tutoring session"
    
    @staticmethod
    def _estimate_tokens(text):
        """Estimate the number of tokens in a text."""
        # A very simple estimator based on word count
        # In production, you'd want to use a more accurate method
        # like tiktoken from OpenAI
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except:
            # Fallback to simple estimation
            return len(text.split()) * 1.3  # Rough estimate