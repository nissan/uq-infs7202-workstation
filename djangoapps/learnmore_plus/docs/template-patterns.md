# Django Template Patterns

This document explains the proper patterns to use in Django templates for our component system.

## Component Structure

We have transitioned from a full Atomic Design pattern (atoms, molecules, organisms) to a simplified, flattened component structure:

```
templates/
└── components/
    ├── elements/     # Basic UI elements like buttons, icons, typography
    └── sections/     # Larger components like headers, footers, hero sections
```

This flattened structure helps avoid deeply nested includes that were causing template rendering issues.

## Template Tag Implementation

We now use Django template tags to implement reusable components. These tags are defined in `apps/core/templatetags/component_tags.py`:

```python
@register.inclusion_tag('components/elements/button.html')
def button(text, url="#", variant="primary", size="md", classes=""):
    return {
        'text': text,
        'url': url,
        'variant': variant,
        'size': size,
        'classes': classes
    }
```

To use these components in templates:

```django
{% load component_tags %}

{% button text="Click Me" url="core:home" variant="primary" %}
```

## URL Handling in Components

For components that need to handle URLs (like buttons or links), we've implemented a flexible system that supports:

1. Named Django URL patterns (e.g., `core:home`)
2. Absolute URLs (e.g., `https://example.com`)
3. Anchor links (e.g., `#section1`)

The implementation in button.html:

```django
<a href="{% if url %}{% if url|slice:':5' == 'http:' or url|slice:':6' == 'https:' %}{{ url }}{% elif url|slice:':1' == '#' %}{{ url }}{% else %}{% url url %}{% endif %}{% else %}#{% endif %}" 
   class="btn btn-{{ variant }} btn-{{ size }} {{ classes }}">
   {{ text }}
</a>
```

## Conditional Defaults with `with` Tags

A common pattern in our components is setting default values for parameters that might not be provided. For example, a button component might have a default variant of "primary" if no variant is specified.

### ✅ CORRECT Pattern (Safe)

The proper way to implement conditional defaults is to use properly nested tags with appropriate whitespace and indentation:

```django
{% if not variant %}
    {% with variant="primary" %}
{% endif %}

<!-- Component HTML here -->

{% if not variant %}
    {% endwith %}
{% endif %}
```

### ❌ INCORRECT Pattern (Will Cause Errors)

DO NOT use the inline pattern without proper spacing and indentation:

```django
{% if not variant %}{% with variant="primary" %}{% endif %}

<!-- Component HTML here -->

{% if not variant %}{% endwith %}{% endif %}
```

The incorrect pattern can cause Django template syntax errors because the template parser gets confused about the proper nesting of tags. The specific error is usually:

```
TemplateSyntaxError: Invalid block tag on line X: 'endif', expected 'endwith'
```

## Multiple Conditional Defaults

When setting multiple default values, maintain proper spacing between each conditional block:

```django
{% if not variant %}
    {% with variant="primary" %}
{% endif %}

{% if not size %}
    {% with size="md" %}
{% endif %}

<!-- Component HTML here -->

{% if not size %}
    {% endwith %}
{% endif %}

{% if not variant %}
    {% endwith %}
{% endif %}
```

## Template Tag Pairing

Always ensure that template tags are properly paired:

- Every `{% if %}` must have a matching `{% endif %}`
- Every `{% with %}` must have a matching `{% endwith %}`
- Every `{% block %}` must have a matching `{% endblock %}`
- Every `{% for %}` must have a matching `{% endfor %}`

## Testing for Template Syntax Issues

We have automated tests in `apps/core/tests.py` that specifically check for these issues. You can run them with:

```bash
./run_tests.sh core TemplateSyntaxErrorTests
```

Or to run a specific test:

```bash
./run_tests.sh core TemplateSyntaxErrorTests.test_proper_endwith_tag_pairing
```

## Playwright Testing for Templates

We've implemented Playwright end-to-end testing to catch template rendering issues. These tests validate that our pages render correctly in real browsers:

```bash
# Run Playwright tests from the tests/e2e directory
cd tests/e2e
npx playwright test
```

See `docs/playwright-testing.md` for more information on our E2E testing approach.

## Why This Matters

Improper template tag nesting can cause the entire page to fail to render, even if the issue is in a small component. This is because Django's template parser evaluates all tags during the rendering process, and incorrect nesting breaks the parser's ability to process the template.

Always be careful with template tag nesting, especially when combining conditional logic with variable assignments using `{% with %}` tags.