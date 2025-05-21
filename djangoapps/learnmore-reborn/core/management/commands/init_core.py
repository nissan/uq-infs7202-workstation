from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import ThemeSettings, AccessibilityElement
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize core app with default themes and accessibility elements'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.create_default_themes()
                self.create_accessibility_elements()
                self.stdout.write(self.style.SUCCESS('Successfully initialized core app'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing core app: {str(e)}'))
            logger.exception('Error in init_core command')

    def create_default_themes(self):
        # Check if default themes already exist
        if ThemeSettings.objects.exists():
            self.stdout.write(self.style.WARNING('Default themes already exist, skipping creation'))
            return

        self.stdout.write('Creating default themes...')
        
        # Create light theme (default)
        light_theme = ThemeSettings.objects.create(
            name='Light Theme',
            is_default=True,
            theme_mode='light',
            primary_color='#007bff',
            secondary_color='#6c757d',
            success_color='#28a745',
            danger_color='#dc3545',
            warning_color='#ffc107',
            info_color='#17a2b8',
            background_color='#ffffff',
            text_color='#212529',
            font_family="system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
            base_font_size='16px',
            heading_font_family="",
            border_radius='0.25rem',
            spacing_unit='1rem',
            container_max_width='1200px',
            enable_animations=True,
            reduce_motion=False,
            high_contrast_mode=False,
            font_scaling=1.0,
            increase_target_size=False,
            custom_css=''
        )
        self.stdout.write(self.style.SUCCESS(f'Created light theme: {light_theme.name}'))
        
        # Create dark theme
        dark_theme = ThemeSettings.objects.create(
            name='Dark Theme',
            is_default=False,
            theme_mode='dark',
            primary_color='#0d6efd',
            secondary_color='#6c757d',
            success_color='#198754',
            danger_color='#dc3545',
            warning_color='#ffc107',
            info_color='#0dcaf0',
            background_color='#121212',
            text_color='#e0e0e0',
            font_family="system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
            base_font_size='16px',
            heading_font_family="",
            border_radius='0.25rem',
            spacing_unit='1rem',
            container_max_width='1200px',
            enable_animations=True,
            reduce_motion=False,
            high_contrast_mode=False,
            font_scaling=1.0,
            increase_target_size=False,
            custom_css=''
        )
        self.stdout.write(self.style.SUCCESS(f'Created dark theme: {dark_theme.name}'))
        
        # Create high contrast theme
        hc_theme = ThemeSettings.objects.create(
            name='High Contrast',
            is_default=False,
            theme_mode='light',
            primary_color='#0000ff',
            secondary_color='#000000',
            success_color='#008000',
            danger_color='#ff0000',
            warning_color='#ff8000',
            info_color='#00b3ff',
            background_color='#ffffff',
            text_color='#000000',
            font_family="system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
            base_font_size='16px',
            heading_font_family="",
            border_radius='0.25rem',
            spacing_unit='1rem',
            container_max_width='1200px',
            enable_animations=False,
            reduce_motion=True,
            high_contrast_mode=True,
            font_scaling=1.1,
            increase_target_size=True,
            custom_css=''
        )
        self.stdout.write(self.style.SUCCESS(f'Created high contrast theme: {hc_theme.name}'))

    def create_accessibility_elements(self):
        # Check if accessibility elements already exist
        if AccessibilityElement.objects.exists():
            self.stdout.write(self.style.WARNING('Accessibility elements already exist, skipping creation'))
            return
            
        self.stdout.write('Creating accessibility elements...')
        
        # Create skip navigation targets
        elements = [
            {
                'name': 'Skip to Main Content',
                'element_type': 'skip_link',
                'element_id': 'main-content',
                'aria_label': 'Skip to main content',
                'is_skip_target': True,
                'priority': 1,
                'description': 'Allows keyboard users to skip navigation and go straight to main content'
            },
            {
                'name': 'Navigation Menu',
                'element_type': 'landmark',
                'element_id': 'main-nav',
                'aria_label': 'Main navigation',
                'is_skip_target': True,
                'priority': 2,
                'description': 'Main navigation menu landmark'
            },
            {
                'name': 'Search Form',
                'element_type': 'landmark',
                'element_id': 'search-form',
                'aria_label': 'Search',
                'is_skip_target': True,
                'priority': 3,
                'description': 'Site search form landmark'
            },
            {
                'name': 'Footer',
                'element_type': 'landmark',
                'element_id': 'footer',
                'aria_label': 'Footer',
                'is_skip_target': True,
                'priority': 4,
                'description': 'Page footer with site links and information'
            },
        ]
        
        for element_data in elements:
            element = AccessibilityElement.objects.create(**element_data)
            self.stdout.write(self.style.SUCCESS(f'Created accessibility element: {element.name}'))