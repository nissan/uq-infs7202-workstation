# Atomic Design Component System

LearnMore Plus uses an atomic design methodology for its UI components. This document explains the component structure and usage guidelines.

## Overview

Atomic design is a methodology composed of five distinct stages working together to create interface design systems in a more deliberate and hierarchical manner:

1. **Atoms**: Basic building blocks of matter (buttons, inputs, labels, etc.)
2. **Molecules**: Groups of atoms bonded together (search forms, navigation menu items, etc.)
3. **Organisms**: Groups of molecules joined together (headers, feature sections, etc.)
4. **Templates**: Page-level objects that place components into a layout
5. **Pages**: Specific instances of templates with real content

## Directory Structure

Our components are organized according to the atomic design hierarchy:

```
templates/
├── components/
│   ├── atoms/
│   │   ├── buttons/
│   │   ├── forms/
│   │   ├── icons/
│   │   ├── typography/
│   │   └── ui/
│   ├── molecules/
│   │   ├── cards/
│   │   ├── forms/
│   │   └── navigation/
│   ├── organisms/
│   │   ├── forms/
│   │   ├── headers/
│   │   ├── footers/
│   │   └── sections/
│   └── templates/
│       ├── home.html
│       ├── about.html
│       └── courses/
├── base.html
```

## Component Usage

### Basic Principles

1. All components should accept common parameters (classes, id, attributes, etc.)
2. Components should have sensible defaults that can be overridden
3. Components should be self-contained and reusable
4. Documentation for each component should be provided in comments

### Using Components

To use a component in a template:

```django
{% include "components/atoms/buttons/button.html" with text="Click Me" variant="primary" %}
```

### Parameters and Defaults

Most components support these common parameters:

- `variant`: Visual style variant (primary, secondary, success, danger, etc.)
- `size`: Component size (sm, md, lg)
- `classes`: Additional CSS classes to add
- `attributes`: Additional HTML attributes

### Template Patterns

Components use two patterns for handling default values:

#### Recommended Pattern (Using the Default Filter)

The preferred and most robust way to handle defaults is using Django's `default` filter:

```django
{% with variant=variant|default:"primary" %}

<!-- Component markup using the variant variable -->
<button class="btn btn-{{ variant }}">{{ text }}</button>

{% endwith %}
```

This pattern is simpler, cleaner, and less prone to syntax errors.

#### Alternative Pattern (Using Conditional With Tags)

If you need to conditionally set defaults, use this pattern with proper spacing and indentation:

```django
{% if not variant %}
    {% with variant="primary" %}
{% endif %}

<!-- Component markup using the variant variable -->
<button class="btn btn-{{ variant }}">{{ text }}</button>

{% if not variant %}
    {% endwith %}
{% endif %}
```

**Important:** This pattern requires careful attention to indentation and spacing to prevent template syntax errors. See `docs/template-patterns.md` for more details on proper implementation.

## Component Reference

### Atoms

#### Buttons

**Button** (`components/atoms/buttons/button.html`)
- Parameters:
  - `text`: Button text
  - `variant`: Button style (primary, secondary, success, danger, warning, info)
  - `size`: Button size (sm, md, lg)
  - `type`: Button type (button, submit, reset)
  - `disabled`: Boolean to disable the button
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/atoms/buttons/button.html" with text="Save" variant="success" %}
```

**Button Link** (`components/atoms/buttons/button-link.html`)
- Parameters:
  - `url`: Link URL
  - `text`: Button text
  - `variant`: Button style
  - `target`: Link target (_blank, _self, etc.)
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/atoms/buttons/button-link.html" with url="/courses/" text="Browse Courses" variant="primary" %}
```

#### Typography

**Heading** (`components/atoms/typography/heading.html`)
- Parameters:
  - `level`: Heading level (1-6)
  - `text`: Heading text
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/atoms/typography/heading.html" with level=1 text="Page Title" %}
```

**Paragraph** (`components/atoms/typography/paragraph.html`)
- Parameters:
  - `text`: Paragraph text
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/atoms/typography/paragraph.html" with text="Lorem ipsum dolor sit amet..." %}
```

**Badge** (`components/atoms/typography/badge.html`)
- Parameters:
  - `text`: Badge text
  - `variant`: Badge style
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/atoms/typography/badge.html" with text="New" variant="danger" %}
```

### Molecules

#### Cards

**Card** (`components/molecules/cards/card.html`)
- Parameters:
  - `title`: Card title
  - `content`: Card body content
  - `footer`: Card footer content
  - `image_url`: URL for card image
  - `image_alt`: Alt text for image
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/molecules/cards/card.html" with title="Card Title" content="Card content goes here" image_url="/static/images/example.jpg" %}
```

**Feature Card** (`components/molecules/cards/feature-card.html`)
- Parameters:
  - `title`: Feature title
  - `description`: Feature description
  - `icon`: Icon name
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/molecules/cards/feature-card.html" with title="Easy to Use" description="Our platform is designed for simplicity" icon="users" %}
```

**Step Card** (`components/molecules/cards/step-card.html`)
- Parameters:
  - `step_number`: Step number
  - `title`: Step title
  - `description`: Step description
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/molecules/cards/step-card.html" with step_number=1 title="Create an Account" description="Sign up to get started" %}
```

### Organisms

#### Sections

**Features Section** (`components/organisms/sections/features-section.html`)
- Parameters:
  - `title`: Section title
  - `features`: List of feature objects (title, description, icon)
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/organisms/sections/features-section.html" with title="Key Features" features=features_list %}
```

**Hero Section** (`components/organisms/sections/hero-section.html`)
- Parameters:
  - `title`: Hero title
  - `subtitle`: Hero subtitle
  - `cta_text`: Call-to-action button text
  - `cta_url`: Call-to-action URL
  - `image_url`: Background image URL
  - `classes`: Additional CSS classes

Example:
```django
{% include "components/organisms/sections/hero-section.html" with title="Learn Anywhere, Anytime" subtitle="Flexible learning for everyone" cta_text="Get Started" cta_url="/register/" %}
```

## Best Practices

1. **Consistency**: Use the existing components rather than creating new ones for similar functionality
2. **Testing**: Ensure components render correctly with different parameter combinations
3. **Documentation**: Keep component documentation up to date
4. **Accessibility**: Ensure components follow accessibility best practices
5. **Responsiveness**: Design components to work well on all screen sizes

## Adding New Components

When adding a new component:

1. Determine the appropriate level (atom, molecule, organism, template)
2. Create the component file in the appropriate directory
3. Add documentation comments at the top of the file
4. Include parameter handling with sensible defaults
5. Add tests for the component in `apps/core/tests.py`

## Testing Components

We have a comprehensive test suite for our components. To run component tests:

```bash
# Run all UI component tests
pytest apps/core/tests.py::ComponentRenderingTestCase

# Run specific component test
pytest apps/core/tests.py::ComponentRenderingTestCase::test_button_component_renders

# Run template syntax error tests
pytest apps/core/tests.py::TemplateSyntaxErrorTests
```

### Testing for Template Syntax Issues

We've improved our testing to catch template syntax issues before they cause production errors:

1. **Automated Tests**: `TemplateSyntaxErrorTests` specifically checks for proper template tag nesting and usage.

2. **Standalone Script**: `check_templates.py` can scan all templates for common issues:
   ```bash
   python check_templates.py
   ```

3. **Test Runner Script**: The `run_tests.sh` script includes targeted tests for template syntax:
   ```bash
   ./run_tests.sh core TemplateSyntaxErrorTests
   ```

4. **Test Pattern**: Our tests verify that component templates follow the recommended patterns for default values and proper tag nesting.

For more details on template syntax testing and best practices, see `docs/template-patterns.md` and `docs/template-fixes-summary.md`.