from django.test import TestCase, Client
from django.urls import reverse, URLPattern, URLResolver
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.template import TemplateSyntaxError
from django.urls.exceptions import NoReverseMatch
from django.conf import settings
import importlib
import inspect
import sys

User = get_user_model()


class CoreViewsTestCase(TestCase):
    """Test case for core views."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
    
    def test_home_page_loads(self):
        """Test the home page loads successfully."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'components/home.html')
    
    def test_about_page_loads(self):
        """Test the about page loads successfully."""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'components/about.html')
    
    def test_navigation_contains_correct_links(self):
        """Test the navigation contains the correct links."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('courses:course_catalog'))
        self.assertContains(response, reverse('core:about'))
        
        # Test nav when logged in
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Log Out')


class ComponentRenderingTestCase(TestCase):
    """Test case for component rendering."""
    
    def test_button_component_renders(self):
        """Test the button component renders correctly."""
        rendered = render_to_string(
            'components/atoms/button.html',
            {'text': 'Test Button', 'variant': 'primary'}
        )
        self.assertIn('Test Button', rendered)
        self.assertIn('bg-primary-600', rendered)
    
    def test_button_with_conditional_defaults(self):
        """Test the button component with conditional defaults."""
        # Test without variant (should use default)
        rendered = render_to_string(
            'components/atoms/button.html',
            {'text': 'Default Button'}
        )
        self.assertIn('Test Button', rendered)
        
        # Test with variant override
        rendered = render_to_string(
            'components/atoms/button.html',
            {'text': 'Success Button', 'variant': 'success'}
        )
        self.assertIn('Success Button', rendered)
        self.assertIn('bg-success', rendered)
        
        # Test with multiple additional parameters
        rendered = render_to_string(
            'components/atoms/button.html',
            {
                'text': 'Complex Button',
                'variant': 'danger',
                'size': 'lg',
                'classes': 'rounded-pill shadow-sm'
            }
        )
        self.assertIn('Complex Button', rendered)
        self.assertIn('bg-danger', rendered)
        self.assertIn('btn-lg', rendered)
        self.assertIn('rounded-pill shadow-sm', rendered)
    
    def test_heading_component_renders(self):
        """Test the heading component renders correctly."""
        rendered = render_to_string(
            'components/atoms/typography/heading.html',
            {'level': '1', 'text': 'Test Heading'}
        )
        self.assertIn('Test Heading', rendered)
        self.assertIn('<h1', rendered)
        
        # Test with custom classes
        rendered = render_to_string(
            'components/atoms/typography/heading.html',
            {'level': '2', 'text': 'Test Heading 2', 'classes': 'display-4 text-primary'}
        )
        self.assertIn('Test Heading 2', rendered)
        self.assertIn('<h2 class="display-4 text-primary"', rendered)
    
    def test_feature_card_component_renders(self):
        """Test the feature card component renders correctly."""
        rendered = render_to_string(
            'components/molecules/feature-card.html',
            {'title': 'Test Feature', 'description': 'Test Description', 'icon': 'test'}
        )
        self.assertIn('Test Feature', rendered)
        self.assertIn('Test Description', rendered)
        self.assertIn('data-lucide="test"', rendered)
    
    def test_button_link_component_renders(self):
        """Test the button-link component renders correctly."""
        rendered = render_to_string(
            'components/atoms/button-link.html',
            {'url': '/test-url/', 'text': 'Test Link', 'variant': 'info'}
        )
        self.assertIn('<a href="/test-url/"', rendered)
        self.assertIn('Test Link', rendered)
        self.assertIn('bg-info', rendered)
        
        # Test with custom target
        rendered = render_to_string(
            'components/atoms/button-link.html',
            {'url': 'https://example.com', 'text': 'External Link', 'target': '_blank'}
        )
        self.assertIn('target="_blank"', rendered)
        self.assertIn('External Link', rendered)
    
    def test_icon_component_renders(self):
        """Test that the icon component renders correctly."""
        rendered = render_to_string(
            'components/atoms/icon.html',
            {'name': 'star', 'size': 24}
        )
        self.assertIn('data-lucide="star"', rendered)
        self.assertIn('width="24"', rendered)
        self.assertIn('height="24"', rendered)
    
    def test_card_component_renders(self):
        """Test that the card component renders correctly."""
        rendered = render_to_string(
            'components/molecules/card.html',
            {
                'title': 'Card Title',
                'content': 'Card content goes here',
                'image_url': '/static/test-image.jpg',
                'footer': 'Card footer'
            }
        )
        self.assertIn('Card Title', rendered)
        self.assertIn('Card content goes here', rendered)
        self.assertIn('/static/test-image.jpg', rendered)
        self.assertIn('Card footer', rendered)
    
    def test_badge_component_renders(self):
        """Test that the badge component renders correctly."""
        rendered = render_to_string(
            'components/atoms/badge.html',
            {'text': 'New', 'variant': 'danger'}
        )
        self.assertIn('New', rendered)
        self.assertIn('bg-danger', rendered)
    
    def test_step_card_component_renders(self):
        """Test that the step card component renders correctly."""
        rendered = render_to_string(
            'components/molecules/step-card.html',
            {
                'step_number': 1,
                'title': 'First Step',
                'description': 'This is the first step of the process'
            }
        )
        self.assertIn('First Step', rendered)
        self.assertIn('This is the first step of the process', rendered)
        self.assertIn('1', rendered)
        
        # Test with another step number
        rendered = render_to_string(
            'components/molecules/step-card.html',
            {
                'step_number': 3, 
                'title': 'Third Step', 
                'description': 'Final step'
            }
        )
        self.assertIn('Third Step', rendered)
        self.assertIn('3', rendered)


class PageTemplateTestCase(TestCase):
    """Test case for checking if key page templates load without errors."""
    
    def test_home_page_template(self):
        """Test that the home page template renders correctly."""
        try:
            rendered = render_to_string('components/home.html', {'user': None})
            self.assertTrue(len(rendered) > 0, "Home page template rendered empty content")
        except Exception as e:
            self.fail(f"Error rendering home template: {str(e)}")
            
    def test_about_page_template(self):
        """Test that the about page template renders correctly."""
        try:
            rendered = render_to_string('components/about.html', {'user': None})
            self.assertTrue(len(rendered) > 0, "About page template rendered empty content")
        except Exception as e:
            self.fail(f"Error rendering about template: {str(e)}")
            
    def test_base_layout_template(self):
        """Test that the base layout template renders correctly."""
        try:
            # Render the base template with minimal content
            rendered = render_to_string('base.html', {
                'user': None,
                'block_title': 'Test Title',
                'block_content': '<p>Test content</p>',
            })
            self.assertTrue(len(rendered) > 0, "Base template rendered empty content")
        except Exception as e:
            self.fail(f"Error rendering base template: {str(e)}")
    
    def test_all_template_pages(self):
        """Test that all template pages render without errors."""
        import os
        from django.conf import settings
        
        template_pages = [
            'components/home.html', 
            'components/about.html',
            'components/templates/courses/catalog.html',
            'components/templates/courses/detail.html',
            'components/templates/dashboard/home.html',
        ]
        
        for template in template_pages:
            try:
                rendered = render_to_string(template, {'user': None})
                self.assertTrue(len(rendered) > 0, f"{template} rendered empty content")
            except Exception as e:
                self.fail(f"Error rendering {template}: {str(e)}")


class TemplateSyntaxErrorTests(TestCase):
    """Test for specific template syntax errors that have caused issues."""
    
    def test_nested_with_if_patterns(self):
        """Test that the nested 'with' and 'if' pattern doesn't cause errors."""
        components_with_pattern = [
            'components/atoms/button.html',
            'components/atoms/button-link.html',
            'components/molecules/step-card.html',
            'components/atoms/typography/heading.html',
            'components/molecules/feature-card.html',
            'components/atoms/card.html',  # Added this component since it had issues
            'components/organisms/steps-section.html',  # Added this component since it had issues
        ]
        
        # Test components that have the "with" conditionals pattern
        for component in components_with_pattern:
            try:
                rendered = render_to_string(component, {'user': None})
                self.assertTrue(len(rendered) > 0, f"{component} rendered empty content")
            except TemplateSyntaxError as e:
                self.fail(f"Template syntax error in {component}: {str(e)}")
            except Exception as e:
                self.fail(f"Other error in {component}: {str(e)}")
    
    def test_proper_endwith_tag_pairing(self):
        """Test that all components with {% with %} tags have proper {% endwith %} pairing."""
        # This test specifically checks for the issue that broke the landing page
        import os
        import re
        from django.conf import settings
        
        components_dir = os.path.join(settings.BASE_DIR, 'templates', 'components')
        
        def check_directory(directory):
            issues = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, settings.BASE_DIR)
                        
                        with open(file_path, 'r') as f:
                            content = f.read()
                            
                            # Pattern 1: Check if {% if not var %}{% with var="value" %}{% endif %} is followed by {% if not var %}{% endwith %}{% endif %}
                            if_with_pattern = r'{% if not (\w+) %}{% with \1="[^"]*" %}{% endif %}'
                            if_endwith_pattern = r'{% if not \1 %}{% endwith %}{% endif %}'
                            
                            with_tags = re.findall(r'{% with', content)
                            endwith_tags = re.findall(r'{% endwith', content)
                            
                            if len(with_tags) != len(endwith_tags):
                                issues.append(f"{relative_path}: Mismatched with and endwith tags ({len(with_tags)} vs {len(endwith_tags)})")
                                
                            # Specific pattern that caused issues - detect inline conditionals with with tags
                            inline_if_with = re.findall(r'{% if not \w+ %}{% with', content)
                            if inline_if_with:
                                # There should be a properly formatted version with newlines and indentation
                                proper_format = re.findall(r'{% if not \w+ %}\s+{% with', content)
                                if len(inline_if_with) != len(proper_format):
                                    issues.append(f"{relative_path}: Contains inline if-with pattern which may cause issues")
            
            return issues
        
        issues = check_directory(components_dir)
        self.assertEqual(len(issues), 0, f"Found template syntax issues: {', '.join(issues)}")
    
    def test_button_component_with_variants(self):
        """Test the button component with various variants to validate conditional pattern."""
        variants = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', None]
        
        for variant in variants:
            context = {'text': 'Test Button'}
            if variant:
                context['variant'] = variant
                
            try:
                rendered = render_to_string('components/atoms/button.html', context)
                self.assertTrue(len(rendered) > 0, "Button rendered empty content")
                if variant:
                    self.assertIn(f"bg-{variant}", rendered)
            except Exception as e:
                self.fail(f"Error rendering button with variant={variant}: {str(e)}")
    
    def test_card_component_with_variants(self):
        """Test the card component with various variants to validate conditional pattern."""
        variants = ['default', 'hover', 'border', None]
        
        for variant in variants:
            context = {'end': False}
            if variant:
                context['variant'] = variant
                
            try:
                # Test opening tag
                rendered1 = render_to_string('components/atoms/card.html', context)
                self.assertTrue(len(rendered1) > 0, "Card rendered empty content")
                
                # Test closing tag
                end_context = context.copy()
                end_context['end'] = True
                rendered2 = render_to_string('components/atoms/card.html', end_context)
                self.assertTrue(len(rendered2) > 0, "Card closing tag rendered empty content")
                
            except Exception as e:
                self.fail(f"Error rendering card with variant={variant}: {str(e)}")
    
    def test_nested_includes_with_parameters(self):
        """Test that complex nested includes with parameters work correctly."""
        try:
            # A component that includes other components with parameters
            rendered = render_to_string('components/organisms/sections/features-section.html', {
                'title': 'Features',
                'features': [
                    {'title': 'Feature 1', 'description': 'Description 1', 'icon': 'star'},
                    {'title': 'Feature 2', 'description': 'Description 2', 'icon': 'rocket'},
                ]
            })
            self.assertTrue(len(rendered) > 0, "Features section rendered empty content")
            self.assertIn('Feature 1', rendered)
            self.assertIn('Feature 2', rendered)
        except Exception as e:
            self.fail(f"Error rendering nested components: {str(e)}")
    
    def test_url_params_in_templates(self):
        """Test that URL parameters are correctly processed in templates."""
        try:
            # Test a component that includes URL parameters
            rendered = render_to_string('components/atoms/button-link.html', {
                'url': reverse('core:about'),
                'text': 'About Link'
            })
            self.assertTrue(len(rendered) > 0, "Button link rendered empty content")
            self.assertIn('href=', rendered)
            self.assertIn('About Link', rendered)
        except Exception as e:
            self.fail(f"Error rendering component with URL parameter: {str(e)}")
            
    def test_home_page_template_renders_without_errors(self):
        """Test that the home page template renders without errors."""
        try:
            rendered = render_to_string('components/home.html', {
                'user': None,
                # Include typical context variables that the home page would expect
                'image_path': '/static/images/course-placeholder.svg',
                'catalog_url': '/courses/catalog/',
                'register_url': '/accounts/register/',
            })
            self.assertTrue(len(rendered) > 0, "Home page rendered empty content")
        except Exception as e:
            self.fail(f"Error rendering home template: {str(e)}")


class AllPagesTestCase(TestCase):
    """Test case for checking that all pages load without errors."""
    
    def setUp(self):
        """Set up test dependencies."""
        from django.contrib.auth.models import Group
        
        # Create required groups if they don't exist
        groups = ['Student', 'Instructor', 'Course Coordinator']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
            
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )
        
    def get_all_urls(self):
        """Get all URLs from the urlpatterns."""
        def get_urls(patterns, namespace=None):
            all_urls = []
            for pattern in patterns:
                if isinstance(pattern, URLResolver):
                    new_namespace = pattern.namespace
                    if namespace and new_namespace:
                        new_namespace = f"{namespace}:{new_namespace}"
                    all_urls.extend(get_urls(pattern.url_patterns, new_namespace))
                elif isinstance(pattern, URLPattern):
                    if hasattr(pattern, 'name') and pattern.name:
                        url_name = pattern.name
                        if namespace:
                            url_name = f"{namespace}:{url_name}"
                        all_urls.append(url_name)
            return all_urls
    
        from learnmore_plus.urls import urlpatterns
        return get_urls(urlpatterns)
    
    def test_basic_unauthenticated_pages(self):
        """Test all basic pages that don't require authentication."""
        # These are some standard pages we know should be accessible without auth
        basic_pages = [
            'home',
            'core:about',
            'courses:course_catalog',
            'login',
            'register',
        ]
        
        for page in basic_pages:
            try:
                response = self.client.get(reverse(page))
                self.assertIn(response.status_code, [200, 302], 
                             f"Page {page} returned status {response.status_code}")
            except NoReverseMatch:
                self.fail(f"Could not reverse URL for {page}")
            except Exception as e:
                self.fail(f"Error loading page {page}: {str(e)}")
    
    def test_authenticated_pages(self):
        """Test pages that require authentication."""
        # Login first
        self.client.login(username='testuser', password='testpassword123')
        
        authenticated_pages = [
            'courses:student_dashboard',
            'ai_tutor:session_list',
            'logout',
        ]
        
        for page in authenticated_pages:
            try:
                response = self.client.get(reverse(page))
                self.assertIn(response.status_code, [200, 302], 
                             f"Page {page} returned status {response.status_code}")
            except NoReverseMatch:
                self.fail(f"Could not reverse URL for {page}")
            except Exception as e:
                self.fail(f"Error loading page {page}: {str(e)}")
    
    def test_admin_pages(self):
        """Test pages that require admin access."""
        # Login as admin
        self.client.login(username='adminuser', password='adminpassword123')
        
        admin_pages = [
            'courses:admin_dashboard',
            'dashboard:home',
        ]
        
        for page in admin_pages:
            try:
                response = self.client.get(reverse(page))
                self.assertIn(response.status_code, [200, 302], 
                             f"Page {page} returned status {response.status_code}")
            except NoReverseMatch:
                self.fail(f"Could not reverse URL for {page}")
            except Exception as e:
                self.fail(f"Error loading page {page}: {str(e)}")
                
    def test_key_pages_load(self):
        """Test that key pages load successfully."""
        # Login as admin
        self.client.login(username='adminuser', password='adminpassword123')
        
        # Test home page
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200, "Home page failed to load")
        
        # Test about page
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200, "About page failed to load")
        
        # Test course catalog
        response = self.client.get(reverse('courses:course_catalog'))
        self.assertEqual(response.status_code, 200, "Course catalog failed to load")