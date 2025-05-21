#!/usr/bin/env python
"""
Script to ingest course content into the RAG (Retrieval Augmented Generation) system.
This script extracts content from courses, modules, and creates knowledge base entries
to be used by the AI tutor for more contextual responses.

Usage:
    python manage.py shell < ingest_rag_content.py
"""

import os
import django
import json
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

from ai_tutor.models import TutorKnowledgeBase
from courses.models import Course, Module, Quiz
from ai_tutor.rag_integration import (
    create_knowledge_base_from_content,
    ingest_course_content,
    ingest_knowledge_base
)

def ingest_all_rag_content():
    """Ingest all content into the RAG system."""
    print("Starting RAG content ingestion process...")
    
    # Step 1: Create knowledge base entries from existing content
    print("\n1. Creating knowledge base entries from course content...")
    result = create_knowledge_base_from_content()
    print(f"Created {result['created']} new and updated {result['updated']} existing knowledge base entries.")
    
    # Step 2: Ingest all knowledge base entries
    print("\n2. Ingesting knowledge base content into vector store...")
    try:
        kb_result = ingest_knowledge_base()
        if kb_result.get("status") == "success":
            print(f"Successfully ingested {kb_result.get('count', 0)} knowledge base chunks.")
        else:
            print(f"Warning: {kb_result.get('message', 'Unknown issue with knowledge base ingestion.')}")
    except ImportError:
        print("Warning: LangChain is required for RAG integration.")
        print("Install it with: pip install langchain>=0.1.0 langchain-openai>=0.0.2 langchain-community>=0.0.10 chromadb>=0.4.0")
    
    # Step 3: Ingest course content directly
    print("\n3. Ingesting course content directly into vector store...")
    try:
        course_result = ingest_course_content()
        if course_result.get("status") == "success":
            print(f"Successfully ingested {course_result.get('count', 0)} course content chunks.")
        else:
            print(f"Warning: {course_result.get('message', 'Unknown issue with course content ingestion.')}")
    except ImportError:
        print("Warning: LangChain is required for RAG integration.")
    
    # Step 4: Verify the knowledge base entries
    kb_entries = TutorKnowledgeBase.objects.all()
    print(f"\n4. Verification: Created {kb_entries.count()} knowledge base entries in total.")
    
    # Display summary of knowledge base coverage
    courses_with_kb = set(kb.course_id for kb in kb_entries if kb.course_id)
    modules_with_kb = set(kb.module_id for kb in kb_entries if kb.module_id)
    
    print(f"Knowledge base covers {len(courses_with_kb)} courses and {len(modules_with_kb)} modules.")
    
    # List courses without knowledge base entries
    all_courses = set(Course.objects.values_list('id', flat=True))
    courses_without_kb = all_courses - courses_with_kb
    if courses_without_kb:
        print(f"Warning: {len(courses_without_kb)} courses have no knowledge base entries.")
    
    print("\nRAG content ingestion complete!")

if __name__ == "__main__":
    ingest_all_rag_content()