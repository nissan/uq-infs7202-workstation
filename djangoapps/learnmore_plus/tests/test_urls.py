from django.test import TestCase
from django.urls import reverse, resolve
from apps.core.views import home, about


class URLTestCase(TestCase):
    """Test case for URL configuration."""
    
    def test_home_url_resolves(self):
        """Test the home URL resolves to the correct view."""
        url = reverse('home')
        self.assertEqual(url, '/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, home)
    
    def test_about_url_resolves(self):
        """Test the about URL resolves to the correct view."""
        url = reverse('core:about')
        self.assertEqual(url, '/about/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, about)
    
    def test_all_template_urls_are_accessible(self):
        """Test all URLs used in templates are accessible."""
        # Define URLs that should exist in the system
        urls_to_check = [
            'home',
            'core:about',
            'courses:course_catalog',
            'courses:admin_dashboard',
            'courses:instructor_dashboard',
            'courses:coordinator_dashboard',
            'courses:student_dashboard',
            'login',
            'register',
            'logout',
            'ai_tutor:session_list',
        ]
        
        # Verify all URLs resolve without errors
        for url_name in urls_to_check:
            try:
                url = reverse(url_name)
                self.assertTrue(url.startswith('/'))
            except Exception as e:
                self.fail(f"URL {url_name} could not be resolved: {e}")
    
    def test_footer_urls(self):
        """Test footer URLs."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check for footer sections
        self.assertContains(response, 'Platform')
        self.assertContains(response, 'Resources')
        self.assertContains(response, 'Company')
        
        # Check copyright
        self.assertContains(response, '2025 LearnMore Plus')


class AtomicDesignURLTestCase(TestCase):
    """Test case for atomic design templates."""
    
    def test_home_uses_atomic_template(self):
        """Test the home page uses the atomic design template."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'components/home.html')