#!/usr/bin/env python
import os
import django
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learnmore_plus.settings.dev")
django.setup()

def check_template_exists(template_name):
    """Check if a template exists and can be loaded"""
    try:
        template = get_template(template_name)
        return True, template.origin.name
    except TemplateDoesNotExist:
        return False, None

# Check the main template
main_template = "components/home.html"
exists, path = check_template_exists(main_template)
print(f"Template '{main_template}': {'Exists at ' + path if exists else 'DOES NOT EXIST'}")

# Check included templates
components_to_check = [
    "components/organisms/hero-section.html",
    "components/organisms/features-grid.html",
    "components/organisms/steps-section.html",
    "components/organisms/testimonials-section.html",
    "components/organisms/courses-grid.html",
    "components/organisms/cta-section.html",
    "components/molecules/feature-card.html",
    "components/molecules/step-card.html",
    "components/molecules/testimonial-card.html",
    "components/molecules/course-card.html",
    "components/atoms/button.html",
    "components/atoms/icon.html"
]

for template in components_to_check:
    exists, path = check_template_exists(template)
    print(f"Template '{template}': {'Exists at ' + path if exists else 'DOES NOT EXIST'}")