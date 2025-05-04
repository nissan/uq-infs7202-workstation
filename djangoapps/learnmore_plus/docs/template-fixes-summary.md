# Template Syntax Fixes Summary

## Issue Identified

We identified a template syntax issue where Django's template parser was encountering errors with a specific pattern in our atomic design components. The error message was:

```
TemplateSyntaxError: Invalid block tag on line X: 'endif', expected 'endwith'
```

This was happening because of improperly nested template tags in several components.

## Problematic Pattern

The problematic pattern was:

```django
{% if not var %}{% with var="value" %}{% endif %}
...
{% if not var %}{% endwith %}{% endif %}
```

In this pattern, the `{% with %}` and `{% endwith %}` tags weren't properly paired within the `{% if %}` blocks, causing Django's template parser to get confused about what tag should come next.

## Fixed Pattern

We updated all templates to use the proper pattern with clear indentation and spacing:

```django
{% if not var %}
    {% with var="value" %}
{% endif %}
...
{% if not var %}
    {% endwith %}
{% endif %}
```

## Templates Fixed

We fixed the following templates:

1. `/templates/components/atoms/typography/heading.html`
2. `/templates/components/atoms/typography/paragraph.html`
3. `/templates/components/atoms/typography/badge.html`
4. `/templates/components/atoms/typography/link.html`
5. `/templates/components/atoms/badge.html`
6. `/templates/components/atoms/button.html`
7. `/templates/components/organisms/testimonials-section.html`
8. `/templates/components/organisms/courses-grid.html`
9. `/templates/components/organisms/features-grid.html`
10. `/templates/components/organisms/sections/cta-section.html`

## Created Test Tools

We created/enhanced the following tools to detect and prevent these issues in the future:

1. Added a comprehensive test in `apps/core/tests.py` under the `TemplateSyntaxErrorTests` class, specifically the `test_proper_endwith_tag_pairing` method.
2. Created a standalone Python script `check_templates.py` that can be run independently to check for template syntax issues without needing to start the Django app.
3. Enhanced the `run_tests.sh` script to include specific tests for template syntax.
4. Created documentation in `docs/template-patterns.md` explaining the proper pattern to use for conditional defaults in templates.

## Lessons Learned

1. Django template tags must be properly nested and paired.
2. When using `{% with %}` tags inside `{% if %}` blocks, ensure the `{% endwith %}` tag is also inside the same `{% if %}` block.
3. Proper indentation and spacing makes template syntax easier to understand and less error-prone.
4. Automated tests are essential for catching template syntax issues before they make it to production.

## Preventing Future Issues

To prevent similar issues in the future:

1. Follow the patterns documented in `docs/template-patterns.md`
2. Run the template syntax tests before deploying changes
3. Use the `check_templates.py` script as part of your pre-commit checks
4. Maintain proper indentation and spacing in all templates

With these fixes and guidelines, the template syntax issues should be resolved, and the site's landing page should now render correctly.