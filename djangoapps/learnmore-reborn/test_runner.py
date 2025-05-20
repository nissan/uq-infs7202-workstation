import logging
from django.test.runner import DiscoverRunner

class QuietTestRunner(DiscoverRunner):
    """
    A test runner that suppresses logging output below ERROR level during tests.
    
    This is useful for eliminating warnings that are expected during tests,
    such as 400/401 responses from deliberately invalid API requests.
    """
    
    def setup_test_environment(self, **kwargs):
        # Set up the test environment
        super().setup_test_environment(**kwargs)
        
        # Store the original logging level for django.request
        self._old_level = logging.getLogger('django.request').level
        
        # Set the logging level to ERROR to suppress WARNING messages
        logging.getLogger('django.request').setLevel(logging.ERROR)
    
    def teardown_test_environment(self, **kwargs):
        # Restore the original logging level
        logging.getLogger('django.request').setLevel(self._old_level)
        
        # Tear down the test environment
        super().teardown_test_environment(**kwargs)