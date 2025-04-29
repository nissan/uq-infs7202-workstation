from django.apps import AppConfig


class ThemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "theme"
    verbose_name = "Theme"

    def ready(self):
        try:
            import theme.signals  # noqa
        except ImportError:
            pass
