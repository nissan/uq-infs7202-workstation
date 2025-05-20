from django.apps import AppConfig


class AiTutorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_tutor'
    verbose_name = 'AI Tutor'
    
    def ready(self):
        """
        Perform initialization tasks when the app is ready.
        This could include setting up LangChain components, initializing vector stores,
        or other necessary configurations.
        """
        # Import is here to avoid circular imports
        from . import langchain_utils
        
        # For now, just log that we're initializing
        # In the future, this would initialize the vector store and LangChain components
        try:
            # This is a placeholder and won't actually do anything yet
            # When fully implemented, this would initialize the vector store
            langchain_utils.initialize_vector_store()
        except Exception as e:
            # Just log the error but don't crash the app initialization
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error initializing AI Tutor components: {str(e)}")
