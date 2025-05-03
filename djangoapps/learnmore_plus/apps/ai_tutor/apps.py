from django.apps import AppConfig


class AiTutorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_tutor'
    label = 'ai_tutor'  # Set the app label explicitly
    verbose_name = 'AI Tutor'
    
    def ready(self):
        import apps.ai_tutor.signals  # noqa