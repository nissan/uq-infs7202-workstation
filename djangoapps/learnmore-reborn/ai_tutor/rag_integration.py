"""
RAG (Retrieval Augmented Generation) integration for the AI Tutor system.
This module provides functionality to ingest course content into a vector database
and retrieve relevant content to enhance AI tutor responses.
"""

import os
import json
from django.conf import settings
from .models import TutorKnowledgeBase, TutorSession, TutorMessage
from courses.models import Course, Module, Quiz, Question

try:
    from langchain.vectorstores import Chroma
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders import TextLoader
    from langchain.schema import Document
    import numpy as np
    LANGCHAIN_AVAILABLE = True
    
    # Create a mock embedding class for demo purposes when OpenAI keys aren't available
    class MockEmbeddings:
        """Mock embedding class that generates random embeddings for demonstration."""
        def __init__(self, embedding_dim=1536):
            self.embedding_dim = embedding_dim
        
        def embed_documents(self, texts):
            """Generate random embeddings for a list of texts."""
            return [self.embed_query(text) for text in texts]
        
        def embed_query(self, text):
            """Generate a random embedding for a single text."""
            # Use hash of text to get consistent embeddings for the same text
            np.random.seed(hash(text) % 2**32)
            embedding = np.random.uniform(-1, 1, self.embedding_dim)
            # Normalize the embedding to unit length
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()

except ImportError:
    LANGCHAIN_AVAILABLE = False

# Configuration
VECTOR_DB_DIR = os.path.join(settings.BASE_DIR, 'ai_tutor', 'vector_db')
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def get_embedding_model():
    """Get the embedding model based on configuration."""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain is required for RAG integration")
    
    # For demonstration purposes, use our mock embeddings
    # In production, you would use OpenAI or another embedding provider:
    # return OpenAIEmbeddings()
    return MockEmbeddings()

def get_vector_store():
    """Get or create the vector store for knowledge base documents."""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain is required for RAG integration")
    
    # Create directory if it doesn't exist
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    
    # Initialize the vector store with the embedding model
    embedding_model = get_embedding_model()
    return Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embedding_model)

def split_text(text, metadata=None):
    """Split text into chunks for embedding."""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain is required for RAG integration")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    
    if not metadata:
        metadata = {}
    
    # Split text into chunks
    chunks = text_splitter.split_text(text)
    
    # Create Document objects with metadata
    documents = [
        Document(page_content=chunk, metadata=metadata)
        for chunk in chunks
    ]
    
    return documents

def ingest_knowledge_base():
    """Ingest all knowledge base content into the vector store."""
    if not LANGCHAIN_AVAILABLE:
        return {"status": "error", "message": "LangChain is required for RAG integration"}
    
    vector_store = get_vector_store()
    
    # Get all knowledge base items
    knowledge_bases = TutorKnowledgeBase.objects.all()
    
    documents = []
    for kb in knowledge_bases:
        metadata = {
            "source": "knowledge_base",
            "id": kb.id,
            "title": kb.title,
            "course_id": kb.course_id,
            "module_id": kb.module_id
        }
        
        kb_documents = split_text(kb.content, metadata)
        documents.extend(kb_documents)
    
    # Add documents to vector store
    if documents:
        vector_store.add_documents(documents)
        return {"status": "success", "count": len(documents)}
    
    return {"status": "warning", "message": "No knowledge base content to ingest"}

def ingest_course_content(course_id=None):
    """Ingest course content into the vector store."""
    if not LANGCHAIN_AVAILABLE:
        return {"status": "error", "message": "LangChain is required for RAG integration"}
    
    vector_store = get_vector_store()
    
    # Get courses to ingest
    courses = Course.objects.all()
    if course_id:
        courses = courses.filter(id=course_id)
    
    document_count = 0
    
    # Process each course
    for course in courses:
        # Course description
        course_metadata = {
            "source": "course",
            "id": course.id,
            "title": course.title,
            "type": "description"
        }
        
        course_documents = split_text(course.description, course_metadata)
        vector_store.add_documents(course_documents)
        document_count += len(course_documents)
        
        # Process modules
        for module in course.modules.all():
            module_metadata = {
                "source": "module",
                "id": module.id,
                "title": module.title,
                "course_id": course.id,
                "course_title": course.title,
                "type": "content"
            }
            
            # Only process if module has content
            if module.content:
                module_documents = split_text(module.content, module_metadata)
                vector_store.add_documents(module_documents)
                document_count += len(module_documents)
            
            # Process quizzes
            for quiz in module.quizzes.all():
                quiz_metadata = {
                    "source": "quiz",
                    "id": quiz.id,
                    "title": quiz.title,
                    "module_id": module.id,
                    "module_title": module.title,
                    "course_id": course.id,
                    "course_title": course.title,
                    "type": "quiz"
                }
                
                # Combine quiz description and instructions
                quiz_content = f"Quiz: {quiz.title}\n\nDescription: {quiz.description}\n\nInstructions: {quiz.instructions}"
                quiz_documents = split_text(quiz_content, quiz_metadata)
                vector_store.add_documents(quiz_documents)
                document_count += len(quiz_documents)
    
    return {"status": "success", "count": document_count}

def retrieve_relevant_content(query, session_id=None, k=3):
    """Retrieve relevant content from the vector store based on the query."""
    if not LANGCHAIN_AVAILABLE:
        return {"status": "error", "message": "LangChain is required for RAG integration"}
    
    vector_store = get_vector_store()
    
    # Prepare filters based on session context
    filter_metadata = {}
    if session_id:
        session = TutorSession.objects.filter(id=session_id).first()
        if session:
            if session.course_id:
                filter_metadata["course_id"] = session.course_id
            if session.module_id:
                filter_metadata["module_id"] = session.module_id
    
    # Retrieve relevant documents
    documents = vector_store.similarity_search(query, k=k, filter=filter_metadata if filter_metadata else None)
    
    results = []
    for doc in documents:
        # Extract the content and metadata
        results.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    
    return results

def enhance_tutor_response(user_message, session_id=None):
    """Enhance tutor response by retrieving relevant content from the vector store."""
    if not LANGCHAIN_AVAILABLE:
        return {"content": "I'm sorry, but the RAG system is not available right now. I'll do my best to help with what I know.", "sources": []}
    
    # Retrieve relevant content for the user's query
    relevant_docs = retrieve_relevant_content(user_message, session_id)
    
    # Format the sources for citation
    sources = []
    context = ""
    
    for doc in relevant_docs:
        # Format the context from the retrieved documents
        content = doc["content"]
        metadata = doc["metadata"]
        
        source_type = metadata.get("source", "unknown")
        if source_type == "course":
            source_title = f"Course: {metadata.get('title', 'Unknown Course')}"
        elif source_type == "module":
            source_title = f"Module: {metadata.get('title', 'Unknown Module')} (from {metadata.get('course_title', 'Unknown Course')})"
        elif source_type == "quiz":
            source_title = f"Quiz: {metadata.get('title', 'Unknown Quiz')} (from {metadata.get('module_title', 'Unknown Module')})"
        elif source_type == "knowledge_base":
            source_title = f"Knowledge Base: {metadata.get('title', 'Unknown Source')}"
        else:
            source_title = "Unknown Source"
        
        # Add to the context
        context += f"\n### {source_title} ###\n{content}\n\n"
        
        # Add to sources for citation
        sources.append({
            "title": source_title,
            "source_type": source_type,
            "id": metadata.get("id")
        })
    
    # Here we would pass the enriched context to the LLM for a response
    # For now, we'll just return the context and sources
    return {
        "context": context,
        "sources": sources
    }

def create_knowledge_base_from_content():
    """Create knowledge base entries from existing course content."""
    created_count = 0
    updated_count = 0
    
    # Process courses
    for course in Course.objects.all():
        # Create or update a knowledge base entry for the course overview
        kb, created = TutorKnowledgeBase.objects.update_or_create(
            title=f"Course Overview: {course.title}",
            course=course,
            module=None,
            defaults={
                "content": f"# {course.title}\n\n{course.description}"
            }
        )
        
        if created:
            created_count += 1
        else:
            updated_count += 1
        
        # Process modules
        for module in course.modules.all():
            if module.content:
                # Create or update a knowledge base entry for the module
                kb, created = TutorKnowledgeBase.objects.update_or_create(
                    title=f"Module: {module.title}",
                    course=course,
                    module=module,
                    defaults={
                        "content": module.content
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
    
    return {
        "status": "success",
        "created": created_count,
        "updated": updated_count
    }