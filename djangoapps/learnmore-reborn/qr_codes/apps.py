from django.apps import AppConfig


class QrCodesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qr_codes'
    verbose_name = 'QR Codes'
    
    def ready(self):
        """Initialize app when Django starts."""
        # Import signals to register them
        import qr_codes.signals