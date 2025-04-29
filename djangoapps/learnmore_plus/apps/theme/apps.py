from django.apps import AppConfig


class ThemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.theme"
    verbose_name = "Theme"

    def ready(self):
        try:
            import apps.theme.signals  # noqa
        except ImportError:
            pass
