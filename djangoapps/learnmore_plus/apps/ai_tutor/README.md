# AI Tutor for LearnMore Plus

The AI Tutor app provides intelligent tutoring capabilities to the LearnMore Plus platform, allowing students to get personalized help with course content using large language models (LLMs).

## Features

- Chat-based interface for asking questions about course content
- Context-aware responses using Retrieval Augmented Generation (RAG)
- Support for multiple LLM providers (local Ollama for development, cloud providers for production)
- Persistent chat sessions organized by course, module, or specific content
- Automatic content indexing for vector search
- Session management and history

## Setup

1. Add the 'apps.ai_tutor' app to INSTALLED_APPS in settings.py
2. Configure the LLM settings in settings.py:
   ```python
   # AI Tutor settings
   DEFAULT_LLM_MODEL = os.getenv('DEFAULT_LLM_MODEL', 'llama3')
   OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
   OLLAMA_MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME', 'llama3')
   OLLAMA_EMBEDDING_MODEL = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
   OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
   VECTOR_DB_PATH = os.path.join(BASE_DIR, 'vectorstore')
   ```
3. Run migrations: `python manage.py migrate`
4. Include the AI tutor URLs in your main URL configuration
5. Index existing course content: `python manage.py index_course_content`

## Local Development with Ollama

For local development, you can use Ollama to run LLMs locally:

1. Install Ollama: https://ollama.ai/
2. Run a compatible model: `ollama run llama3` or `ollama run nomic-embed-text`
3. Ensure the OLLAMA_BASE_URL points to your Ollama server (default: http://localhost:11434)

## Production Configuration

For production deployment, configure the appropriate environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key for using OpenAI models
- `DEFAULT_LLM_MODEL`: The default model to use (e.g., 'gpt-3.5-turbo')

## Key Components

- **LLMFactory**: Abstracts LLM provider selection based on configuration
- **ContentIndexingService**: Handles vector embeddings and retrieval for content
- **TutorService**: Core service for generating responses with context
- **TutorSession**: Model for persisting chat sessions
- **TutorContextItem**: Model for storing context items for RAG
- **TutorMessage**: Model for storing conversation messages

## Integration Points

The AI Tutor is integrated into the platform at these key points:

1. Course Detail Page: "Get AI Tutor Help" button
2. Course Learning Page: AI Tutor sidebar
3. Main Navigation: AI Tutor link for authenticated users
4. Session/Chat interface: accessible from the AI Tutor section

## Dependencies

- langchain: Framework for LLM applications
- langchain-core: Core components for langchain
- langchain-openai: OpenAI integration for langchain
- langchain-community: Community models integration for langchain
- tiktoken: OpenAI's tokenizer
- chromadb: Vector database for embeddings
- sentence-transformers: Embedding models

## Best Practices

- Use the content indexing command after adding or updating course content
- Keep context items focused and relevant
- Provide clear session titles for better organization
- Monitor token usage to manage costs (when using paid providers)