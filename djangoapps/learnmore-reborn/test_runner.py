import logging
import os
import warnings
from django.test.runner import DiscoverRunner

class QuietTestRunner(DiscoverRunner):
    """
    A test runner that:
    1. Suppresses logging output below ERROR level during tests
    2. Uses test_settings.py for all tests
    3. Disables authentication for tests
    
    This is useful for eliminating warnings that are expected during tests,
    such as 400/401 responses from deliberately invalid API requests.
    """
    
    def __init__(self, *args, **kwargs):
        # Use test settings
        os.environ['DJANGO_SETTINGS_MODULE'] = 'learnmore.test_settings'
        
        # Import CSRF bypass module to monkey-patch Django
        import csrf_bypass
        
        # Run the parent constructor
        super().__init__(*args, **kwargs)
    
    def setup_test_environment(self, **kwargs):
        # Set up the test environment
        super().setup_test_environment(**kwargs)
        
        # Store the original logging level for django.request
        self._old_level = logging.getLogger('django.request').level
        
        # Set the logging level to ERROR to suppress WARNING messages
        logging.getLogger('django.request').setLevel(logging.ERROR)
        
        # Suppress warnings during tests
        warnings.simplefilter('ignore')
        
        # Explicitly patch settings for DRF tests
        from django.conf import settings
        settings.REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [],
            'DEFAULT_PERMISSION_CLASSES': [],
            'UNAUTHENTICATED_USER': None
        }
        
        # Patch views to be CSRF exempt
        settings.TEST_MODE = True
        import patch_views  # This will patch all views automatically
    
    def teardown_test_environment(self, **kwargs):
        # Restore the original logging level
        logging.getLogger('django.request').setLevel(self._old_level)
        
        # Restore warnings behavior
        warnings.resetwarnings()
        
        # Tear down the test environment
        super().teardown_test_environment(**kwargs)