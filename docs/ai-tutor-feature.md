# AI Tutor Feature Documentation

## Overview

The AI Tutor is an intelligent learning assistant that provides personalized support to students within the LearnMore+ platform. It uses large language models (LLMs) and Retrieval Augmented Generation (RAG) to offer context-aware assistance based on course content.

## Key Features

1. **Intelligent Tutoring**
   - Context-aware responses based on course content
   - Support for various question types and learning styles
   - Explanation of complex concepts with examples
   - Ability to refer to specific course materials

2. **Flexible Backend Support**
   - Local LLM support via Ollama for development
   - Cloud provider support (OpenAI, Anthropic, Google) for production
   - Configurable model selection based on needs
   - Fallback options for reliability

3. **Session Management**
   - Persistent chat sessions organized by course, module, or content
   - Session history tracking and context retention
   - Custom session creation for different learning focuses
   - Session management interface for users

4. **Content Awareness**
   - Automatic indexing of course content via vector embeddings
   - Retrieval of relevant content when answering questions
   - Connection between course materials and AI responses
   - Custom context items for specialized knowledge

5. **User Interface**
   - Three-panel layout with navigation, chat, and reference sections
   - Mobile-responsive design that adapts to different devices
   - Real-time message updates and typing indicators
   - Suggested topics and learning paths

## Technical Architecture

The AI Tutor is built with a modular architecture that separates concerns:

### Models

1. **TutorSession**
   - Manages session metadata and relationships
   - Links to courses, modules, or content items
   - Tracks session status and user associations
   - Supports different session types (course, module, content, general)

2. **TutorMessage**
   - Stores conversation history
   - Supports different message types (user, assistant, system)
   - Tracks metadata like timestamps and token usage
   - Associates messages with relevant context items

3. **TutorContextItem**
   - Stores context snippets for RAG
   - Links to various content objects
   - Manages context ordering and relevance scoring
   - Provides reference material for the tutor

4. **ContentEmbedding**
   - Stores vector embeddings of course content
   - Enables semantic search capabilities
   - Links embeddings to source content
   - Provides data for retrieval-augmented generation

### Services

1. **LLMFactory**
   - Abstracts LLM provider selection
   - Configures appropriate model parameters
   - Supports multiple model providers
   - Handles fallback options

2. **ContentIndexingService**
   - Manages vector embeddings for course content
   - Provides search functionality across content
   - Handles content updates and re-indexing
   - Manages the Chroma vector database
   - Uses newer langchain-chroma integrations

3. **TutorService**
   - Core service for generating AI responses
   - Manages conversation flow and context
   - Handles message creation and retrieval
   - Integrates retrieval results with LLM generation

### User Interface

The AI Tutor interface is designed for an optimal learning experience:

1. **Left Panel (Navigation)**
   - Course structure navigation
   - Topic selection and search
   - Progress indicators
   - Suggested topics

2. **Center Panel (Chat)**
   - Message history display
   - Input area for questions
   - Real-time response updates
   - Support for rich content in messages

3. **Right Panel (Reference)**
   - Context display from course materials
   - Key concept explanations
   - Formula references
   - Session management options

## Integration Points

The AI Tutor integrates with the LearnMore+ platform at several key points:

1. **Course Pages**
   - Link from course detail pages to course-specific tutor
   - Integration in module and content pages
   - Contextual help buttons in learning materials

2. **User Navigation**
   - Main navigation link for authenticated users
   - Session management via dashboard
   - Recent conversations in user profile

3. **Learning Experience**
   - Embedded tutor panel in learning interface
   - Contextual help for current module/content
   - Progress tracking integration

## Configuration

The AI Tutor can be configured through the following settings:

```python
# AI Tutor settings in settings.py
DEFAULT_LLM_MODEL = os.getenv('DEFAULT_LLM_MODEL', 'llama3')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME', 'llama3')
OLLAMA_EMBEDDING_MODEL = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')  # Required for content indexing
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'vectorstore')
```

#### Required Packages

```bash
# Core LangChain and provider-specific packages
pip install langchain-core langchain-community
pip install langchain-openai  # For OpenAI integration
pip install langchain-ollama  # For Ollama integration
pip install langchain-huggingface  # For HuggingFace embeddings
pip install langchain-chroma  # For vector storage
```

## Demo Setup

The AI Tutor comes with a demo data seeding command to help you explore its capabilities:

```bash
python manage.py seed_ai_tutor_demo
```

This command:
- Creates sample tutor sessions for demo users
- Seeds realistic conversations based on session types
- Indexes course content for retrieval
- Sets up the necessary database records for testing

## Usage Examples

### Course-Level Tutoring

Ideal for broad questions about a course:

- "What are the main topics covered in this course?"
- "How are the modules connected to each other?"
- "What's the best way to approach studying this material?"
- "What are the prerequisites I should understand first?"

### Module-Level Tutoring

Focused on specific modules within a course:

- "Can you explain the key concepts in this module?"
- "How does this module relate to what we learned before?"
- "What are the most important takeaways from this section?"
- "I'm struggling with concept X in this module, can you help?"

### Content-Level Tutoring

Highly specific to individual content items:

- "What does this diagram represent?"
- "Can you explain this code example in more detail?"
- "I don't understand the formula presented here."
- "How would I apply this concept in a real-world scenario?"

### General Tutoring

For broader learning questions:

- "What are effective study techniques for technical subjects?"
- "How can I improve my problem-solving skills?"
- "Can you recommend resources for learning more about topic X?"
- "How should I prepare for assessments effectively?"

## Future Enhancements

Planned improvements for the AI Tutor include:

1. **Enhanced RAG Techniques**
   - Fine-tuning for educational content
   - Multi-vector retrieval strategies
   - Hybrid search methods for improved context

2. **Learning Analytics**
   - Question pattern analysis
   - Difficulty detection
   - Learning gap identification
   - Instructor dashboards for tutoring insights

3. **Interactive Learning Elements**
   - Tutor-generated practice questions
   - Step-by-step problem solving
   - Visual concept mapping
   - Learning path recommendations

4. **Advanced Personalization**
   - Learning style adaptation
   - Progress-based assistance
   - Personalized example generation
   - Spaced repetition integration