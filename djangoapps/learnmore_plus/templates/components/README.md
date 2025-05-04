# Atomic Design Component System

This directory contains the atomic design component system for LearnMore Plus.

## Component Structure

The components are organized according to atomic design principles:

- **Atoms**: Smallest building blocks (buttons, icons, typography elements)
- **Molecules**: Groups of atoms that function together (cards, form fields)
- **Organisms**: Groups of molecules that form a distinct section (headers, footers, hero sections)
- **Templates**: Page templates that use components to define the layout
- **Pages**: Specific instances of templates with real content

## Usage Guidelines

### Default Values

Components should use the default filter to handle optional parameters:

```django
{% with variant=variant|default:"primary" %}
<!-- Component markup -->
{% endwith %}
```

### Component Organization

1. All components should be well-documented with clear parameters
2. Use proper indentation for readability
3. Group related components together
4. Add comments to explain complex logic

### Includes

When including components, use the full path to avoid ambiguity:

```django
{% include "components/atoms/button.html" with text="Click me" %}
```

## Known Issues and Workarounds

There was an issue with raw template code being displayed on pages. This was fixed by:

1. Resolving URL conflicts in the project's URL configuration
2. Simplifying the atomic home template to use fewer nested components
3. Adding a debug route at `/debug/` to test component rendering

For components that cause rendering issues, consider these approaches:

1. Write the HTML directly instead of using complex component includes
2. Use simpler templates with fewer nested components
3. Ensure all template tags are properly closed and formatted

## Feature Flag

The atomic design system can be enabled with `?atomic=true` in the URL.

Example: `http://localhost:8000/?atomic=true`