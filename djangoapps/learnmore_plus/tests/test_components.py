from django.test import TestCase
from django.template.loader import render_to_string
from bs4 import BeautifulSoup


class AtomComponentsTestCase(TestCase):
    """Test cases for atomic components."""
    
    def test_button_variants(self):
        """Test the button component renders all variants correctly."""
        variants = ['primary', 'secondary', 'outline', 'ghost']
        
        for variant in variants:
            rendered = render_to_string(
                'components/atoms/button.html',
                {'text': f'Test {variant.capitalize()} Button', 'variant': variant}
            )
            soup = BeautifulSoup(rendered, 'html.parser')
            button = soup.find('a')
            
            self.assertIn(f'Test {variant.capitalize()} Button', button.text)
            
            # Check variant-specific classes
            if variant == 'primary':
                self.assertIn('bg-primary-600', button['class'])
            elif variant == 'secondary':
                self.assertIn('bg-gray-100', button['class'])
            elif variant == 'outline':
                self.assertIn('border', button['class'])
            elif variant == 'ghost':
                self.assertIn('hover:bg-gray-50', button['class'])
    
    def test_button_sizes(self):
        """Test the button component renders all sizes correctly."""
        sizes = ['sm', 'md', 'lg']
        
        for size in sizes:
            rendered = render_to_string(
                'components/atoms/button.html',
                {'text': 'Button', 'size': size}
            )
            soup = BeautifulSoup(rendered, 'html.parser')
            button = soup.find('a')
            
            if size == 'sm':
                self.assertIn('h-8', button['class'])
            elif size == 'md':
                self.assertIn('h-10', button['class'])
            elif size == 'lg':
                self.assertIn('h-12', button['class'])
    
    def test_badge_component(self):
        """Test the badge component."""
        variants = ['primary', 'secondary', 'outline', 'success', 'warning', 'danger']
        
        for variant in variants:
            rendered = render_to_string(
                'components/atoms/badge.html',
                {'text': f'Test Badge', 'variant': variant}
            )
            soup = BeautifulSoup(rendered, 'html.parser')
            badge = soup.find('span')
            
            self.assertIn('Test Badge', badge.text)
            
            # Check variant-specific classes
            if variant == 'primary':
                self.assertIn('bg-primary-600', badge['class'])
            elif variant == 'success':
                self.assertIn('bg-green-', badge['class'])
            elif variant == 'warning':
                self.assertIn('bg-yellow-', badge['class'])
            elif variant == 'danger':
                self.assertIn('bg-red-', badge['class'])
    
    def test_typography_components(self):
        """Test typography components."""
        # Test heading
        for level in range(1, 7):
            rendered = render_to_string(
                'components/atoms/typography/heading.html',
                {'level': str(level), 'text': f'Heading {level}'}
            )
            soup = BeautifulSoup(rendered, 'html.parser')
            heading = soup.find(f'h{level}')
            
            self.assertIsNotNone(heading)
            self.assertIn(f'Heading {level}', heading.text)
        
        # Test paragraph
        sizes = ['sm', 'md', 'lg', 'xl']
        for size in sizes:
            rendered = render_to_string(
                'components/atoms/typography/paragraph.html',
                {'text': 'Test paragraph', 'size': size}
            )
            soup = BeautifulSoup(rendered, 'html.parser')
            paragraph = soup.find('p')
            
            self.assertIsNotNone(paragraph)
            self.assertIn('Test paragraph', paragraph.text)
            
            if size == 'sm':
                self.assertIn('text-sm', paragraph['class'])
            elif size == 'lg':
                self.assertIn('text-lg', paragraph['class'])
            elif size == 'xl':
                self.assertIn('text-xl', paragraph['class'])


class MoleculeComponentsTestCase(TestCase):
    """Test cases for molecular components."""
    
    def test_feature_card_component(self):
        """Test the feature card component."""
        rendered = render_to_string(
            'components/molecules/feature-card.html',
            {
                'title': 'Feature Title',
                'description': 'Feature Description',
                'icon': 'star'
            }
        )
        soup = BeautifulSoup(rendered, 'html.parser')
        
        # Check title and description
        self.assertIn('Feature Title', soup.text)
        self.assertIn('Feature Description', soup.text)
        
        # Check icon
        icon = soup.find('i', attrs={'data-lucide': 'star'})
        self.assertIsNotNone(icon)
    
    def test_testimonial_card_component(self):
        """Test the testimonial card component."""
        rendered = render_to_string(
            'components/molecules/testimonial-card.html',
            {
                'quote': 'This is a testimonial',
                'name': 'John Doe',
                'role': 'Customer',
                'initials': 'JD'
            }
        )
        soup = BeautifulSoup(rendered, 'html.parser')
        
        # Check quote, name, and role
        self.assertIn('This is a testimonial', soup.text)
        self.assertIn('John Doe', soup.text)
        self.assertIn('Customer', soup.text)
        
        # Check avatar with initials
        avatar = soup.find(text='JD')
        self.assertIsNotNone(avatar)
    
    def test_step_card_component(self):
        """Test the step card component."""
        rendered = render_to_string(
            'components/molecules/step-card.html',
            {
                'number': '1',
                'title': 'Step Title',
                'description': 'Step Description',
                'has_connector': True
            }
        )
        soup = BeautifulSoup(rendered, 'html.parser')
        
        # Check number, title, and description
        self.assertIn('1', soup.text)
        self.assertIn('Step Title', soup.text)
        self.assertIn('Step Description', soup.text)
        
        # Check connector
        connector = soup.find('div', class_='step-connector')
        self.assertIsNotNone(connector)


class OrganismComponentsTestCase(TestCase):
    """Test cases for organism components."""
    
    def test_section_heading_component(self):
        """Test the section heading component."""
        rendered = render_to_string(
            'components/molecules/section-heading.html',
            {
                'title': 'Section Title',
                'subtitle': 'Section Subtitle'
            }
        )
        soup = BeautifulSoup(rendered, 'html.parser')
        
        # Check title and subtitle
        self.assertIn('Section Title', soup.text)
        self.assertIn('Section Subtitle', soup.text)
        
        # Check heading style elements
        heading = soup.find('h2')
        self.assertIsNotNone(heading)
        
        # Check decorative underline
        span = heading.find('span')
        self.assertIsNotNone(span)
    
    def test_hero_section_component(self):
        """Test the hero section component."""
        rendered = render_to_string(
            'components/organisms/hero-section.html',
            {
                'title': 'Hero Title',
                'subtitle': 'Hero Subtitle',
                'image_url': '/test.jpg',
                'primary_button_text': 'Primary Button',
                'primary_button_url': '#primary',
                'secondary_button_text': 'Secondary Button',
                'secondary_button_url': '#secondary'
            }
        )
        soup = BeautifulSoup(rendered, 'html.parser')
        
        # Check title and subtitle
        self.assertIn('Hero Title', soup.text)
        self.assertIn('Hero Subtitle', soup.text)
        
        # Check buttons
        self.assertIn('Primary Button', soup.text)
        self.assertIn('Secondary Button', soup.text)
        
        # Check image
        img = soup.find('img')
        self.assertIsNotNone(img)
        self.assertEqual(img['src'], '/test.jpg')