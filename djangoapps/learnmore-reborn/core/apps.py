from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Features'
    
    def ready(self):
        """Initialize signals and other configurations when the app is ready."""
        # Import signals to register them
        import core.signals
