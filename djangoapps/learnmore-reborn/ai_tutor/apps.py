from django.apps import AppConfig


class AiTutorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_tutor'
    verbose_name = 'AI Tutor'
    
    def ready(self):
        """
        Perform initialization tasks when the app is ready.
        This includes setting up LangChain components and initializing vector stores.
        """
        # Don't run initialization during migrations
        import sys
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return
            
        # Import is here to avoid circular imports
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Initialize LangChain service
            from .langchain_service import tutor_langchain_service
            
            # Log service initialization
            if tutor_langchain_service.api_key:
                logger.info("LangChain service initialized successfully")
            else:
                logger.warning(
                    "LangChain service initialized without API key. "
                    "AI Tutor will use placeholder responses. "
                    "Set OPENAI_API_KEY environment variable to enable actual LLM responses."
                )
                
            # Check vector store status
            if tutor_langchain_service.vector_store:
                logger.info("Vector store loaded successfully")
            else:
                logger.info(
                    "No vector store found. Use the initialize_vector_store or "
                    "populate_knowledge_base management command to create one."
                )
                
        except Exception as e:
            # Just log the error but don't crash the app initialization
            logger.error(f"Error initializing AI Tutor components: {str(e)}")
