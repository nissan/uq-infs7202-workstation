"""
LangChain service implementation for the AI Tutor system.
This file contains the core LangChain integration for working with LLMs and vector stores.
"""

import os
from typing import List, Dict, Any, Optional
import logging
from django.conf import settings
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.docstore.document import Document
from langchain_core.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from .models import TutorSession, TutorMessage, TutorKnowledgeBase, TutorConfiguration

logger = logging.getLogger(__name__)

# Default paths for vector store
VECTOR_STORE_PATH = os.path.join(settings.BASE_DIR, 'ai_tutor', 'vector_store')
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """You are an AI tutor for {course_title}. Your goal is to help the student understand concepts, 
answer their questions, and guide their learning. Use the provided context to give accurate, helpful responses. 
If you don't know something, admit it rather than making up information. Aim to be educational rather than just providing answers."""

class TutorLangChainService:
    """Service for handling LangChain integration with the AI Tutor system."""
    
    def __init__(self, use_openai_api_key=None):
        """Initialize the LangChain service with optional API key override."""
        self.api_key = use_openai_api_key or os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment. (Please set it in your .env file.)")
        elif not self.api_key.startswith("sk-"):
            logger.error("OPENAI_API_KEY (or override) does not appear valid (expected to start with 'sk-').")
            raise ValueError("Invalid OPENAI_API_KEY (or override).")
        self.embeddings = None
        self.llm = None
        self.vector_store = None
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize LangChain components (embeddings, LLM, and vector store)."""
        try:
            if not self.api_key:
                logger.warning("No OpenAI API key found. Using placeholder responses.")
                return
            
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.api_key
            )
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                openai_api_key=self.api_key,
                temperature=0.7,
                model_name="gpt-3.5-turbo",
                verbose=True,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            )
            
            # Initialize vector store if it exists
            if os.path.exists(VECTOR_STORE_PATH) and os.listdir(VECTOR_STORE_PATH):
                self.vector_store = Chroma(
                    persist_directory=VECTOR_STORE_PATH,
                    embedding_function=self.embeddings
                )
                logger.info(f"Loaded existing vector store from {VECTOR_STORE_PATH}")
            else:
                logger.info("No existing vector store found. It will be created when documents are added.")
        
        except Exception as e:
            logger.error(f"Error initializing LangChain components: {str(e)}")
    
    def create_vector_store(self, documents: List[Document]):
        """Create a new vector store from documents."""
        try:
            if not self.embeddings:
                logger.warning("Embeddings not initialized. Cannot create vector store.")
                return False
            
            # Create vector store
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=VECTOR_STORE_PATH
            )
            
            # Persist the vector store
            self.vector_store.persist()
            logger.info(f"Created and persisted vector store at {VECTOR_STORE_PATH}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            return False
    
    def update_vector_store(self, documents: List[Document]):
        """Add documents to an existing vector store or create a new one."""
        try:
            if not self.embeddings:
                logger.warning("Embeddings not initialized. Cannot update vector store.")
                return False
            
            if not self.vector_store:
                return self.create_vector_store(documents)
            
            # Add documents to existing store
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error updating vector store: {str(e)}")
            return False
    
    def get_session_context(self, session: TutorSession) -> Dict[str, Any]:
        """Get context information for a tutor session."""
        context = {
            "session_id": session.id,
            "user_id": session.user.id,
            "username": session.user.username,
            "course_title": session.course.title if session.course else "General Topics",
            "module_title": session.module.title if session.module else None,
            "quiz_title": session.quiz.title if session.quiz else None,
        }
        return context
    
    def get_conversation_history(self, session: TutorSession, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get the conversation history for a tutor session."""
        messages = TutorMessage.objects.filter(session=session).order_by('created_at')
        
        # Convert to format expected by LangChain (system messages are excluded)
        history = []
        for msg in messages:
            if msg.message_type == 'user':
                history.append({"role": "human", "content": msg.content})
            elif msg.message_type == 'tutor':
                history.append({"role": "ai", "content": msg.content})
        
        # Return the last N messages
        return history[-max_messages:] if max_messages > 0 else history
    
    def get_retrieval_chain(self, session: TutorSession):
        """Create a conversational retrieval chain for the tutor session."""
        if not self.llm or not self.vector_store:
            logger.warning("LLM or vector store not initialized. Cannot create retrieval chain.")
            return None
        
        try:
            # Get context for the session
            context = self.get_session_context(session)
            
            # Create memory with existing conversation history
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Get system prompt template
            config = TutorConfiguration.objects.filter(is_active=True).first()
            system_prompt = config.system_prompt if config else DEFAULT_SYSTEM_PROMPT
            
            # Format the system prompt with context
            formatted_system_prompt = system_prompt.format(**context)
            
            # Create QA chain
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
                memory=memory,
                verbose=True,
                return_source_documents=True,
                condense_question_prompt=PromptTemplate.from_template(
                    "Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.\n\n"
                    "Chat History:\n{chat_history}\n"
                    "Follow Up Input: {question}\n"
                    "Standalone question:"
                ),
                combine_docs_chain_kwargs={
                    "prompt": PromptTemplate.from_template(
                        f"{formatted_system_prompt}\n\n"
                        "Context information is below.\n"
                        "---------------------\n"
                        "{context}\n"
                        "---------------------\n"
                        "Given the context information and not prior knowledge, "
                        "answer the question: {question}"
                    )
                }
            )
            
            return qa_chain
            
        except Exception as e:
            logger.error(f"Error creating retrieval chain: {str(e)}")
            return None
    
    def get_tutor_response(self, session: TutorSession, message_content: str) -> Dict[str, Any]:
        """Generate a response from the AI tutor using LangChain."""
        if not self.api_key:
            # Return placeholder response if no API key
            return {
                "content": f"I understand you're asking about '{message_content}'. "
                          f"This is a placeholder response because the LLM service is not configured.",
                "sources": [],
                "metadata": {"placeholder": True}
            }
        
        try:
            # Get retrieval chain
            chain = self.get_retrieval_chain(session)
            
            if not chain:
                return {
                    "content": "I'm sorry, but I'm having trouble accessing my knowledge. Please try again later.",
                    "sources": [],
                    "metadata": {"error": "retrieval_chain_unavailable"}
                }
            
            # Load conversation history into memory
            history = self.get_conversation_history(session)
            for i in range(0, len(history), 2):
                if i + 1 < len(history):
                    chain.memory.chat_memory.add_user_message(history[i]["content"])
                    chain.memory.chat_memory.add_ai_message(history[i+1]["content"])
            
            # Generate response
            response = chain({"question": message_content})
            
            # Extract sources if available
            sources = []
            if "source_documents" in response:
                for doc in response["source_documents"]:
                    if hasattr(doc, "metadata") and "source" in doc.metadata:
                        sources.append(doc.metadata["source"])
            
            return {
                "content": response["answer"],
                "sources": sources,
                "metadata": {"model": "gpt-3.5-turbo", "temperature": 0.7}
            }
            
        except Exception as e:
            logger.error(f"Error generating tutor response: {str(e)}")
            return {
                "content": "I apologize, but I encountered an error processing your question. Please try again.",
                "sources": [],
                "metadata": {"error": str(e)}
            }
    
    def process_knowledge_base(self, force_recreate: bool = False):
        """Process all knowledge base entries and add them to the vector store."""
        try:
            # Check if we should recreate the vector store
            if force_recreate and os.path.exists(VECTOR_STORE_PATH):
                import shutil
                shutil.rmtree(VECTOR_STORE_PATH)
                os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
                self.vector_store = None
                logger.info("Existing vector store deleted for recreation")
            
            # Get all knowledge base entries
            entries = TutorKnowledgeBase.objects.all()
            logger.info(f"Processing {entries.count()} knowledge base entries")
            
            if entries.count() == 0:
                logger.warning("No knowledge base entries found to process")
                return False
            
            # Create text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            # Process entries into documents
            documents = []
            for entry in entries:
                # Create metadata
                metadata = {
                    "id": entry.id,
                    "title": entry.title,
                    "source": f"knowledge_base:{entry.id}",
                    "course_id": entry.course.id if entry.course else None,
                    "module_id": entry.module.id if entry.module else None,
                }
                
                # Split content into chunks
                entry_documents = text_splitter.create_documents(
                    texts=[entry.content],
                    metadatas=[metadata]
                )
                
                documents.extend(entry_documents)
            
            logger.info(f"Created {len(documents)} document chunks from knowledge base entries")
            
            # Update or create vector store
            if self.vector_store:
                success = self.update_vector_store(documents)
            else:
                success = self.create_vector_store(documents)
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing knowledge base: {str(e)}")
            return False


# Singleton instance for global use
tutor_langchain_service = TutorLangChainService()