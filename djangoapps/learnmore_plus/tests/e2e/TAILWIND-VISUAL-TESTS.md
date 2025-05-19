# Tailwind CSS Visual Regression Tests

This document provides guidance on running and interpreting the Tailwind CSS visual regression tests implemented in the LearnMore Plus platform.

## Overview

The `tailwind-visual-regression.spec.js` file contains specialized tests designed to verify that the application correctly implements Tailwind CSS and maintains visual consistency across themes and viewport sizes. These tests specifically focus on:

1. **UI Framework Verification**: Ensuring the application uses Tailwind CSS classes rather than Bootstrap
2. **Color Scheme Consistency**: Verifying proper light/dark mode implementation
3. **Responsive Layout**: Testing at each Tailwind breakpoint
4. **Component Styling**: Checking components like modals for proper Tailwind implementation

## Running the Tests

### Run All Tailwind Visual Tests

```bash
npx playwright test tailwind-visual-regression.spec.js
```

### Run with Visual UI for Debugging

```bash
npx playwright test tailwind-visual-regression.spec.js --ui
```

### Run a Single Test

```bash
npx playwright test tailwind-visual-regression.spec.js:42  # Line number of test
```

### Run and Update Screenshots

```bash
npx playwright test tailwind-visual-regression.spec.js --update-snapshots
```

## Understanding Test Output

The tests generate screenshots to provide visual evidence of proper styling:

- `light-mode-home.png` & `dark-mode-home.png`: Home page in both themes
- `qr-modal-light.png` & `qr-modal-dark.png`: QR code modal in both themes
- `home-sm.png`, `home-md.png`, etc.: Home page at different Tailwind breakpoints
- `catalog-sm.png`, `catalog-md.png`, etc.: Catalog page at different Tailwind breakpoints

## What These Tests Verify

### 1. Theme Color Verification

The test `should maintain consistent styling in light and dark mode` verifies:

- Background colors change appropriately between modes
- Text colors change appropriately for readability
- Border colors adjust to match the theme
- Component colors (buttons, cards, etc.) maintain proper contrast

### 2. Tailwind Class Usage

The test `should use Tailwind CSS for component styling (not Bootstrap)` checks:

- Presence of Tailwind utility classes (`flex-`, `grid-`, `p-`, etc.)
- Absence of Bootstrap classes (`.container-fluid`, `.row`, `.col`, etc.)
- Counts of Tailwind vs. Bootstrap classes across key pages

### 3. QR Code Modal Styling

The test `should verify QR code modal styling with Tailwind` ensures:

- Modal uses Tailwind's positioning classes (fixed, flex, etc.)
- Dark mode variants are applied correctly (`dark:bg-`, `dark:text-`, etc.)
- Modal styling changes appropriately when theme changes
- Modal uses modern Tailwind layout methods (Flex or Grid)

### 4. Responsive Layout Tests

The test `should verify responsive layout with Tailwind breakpoints` checks:

- Content adjusts at each Tailwind breakpoint (xs, sm, md, lg, xl, 2xl)
- Mobile navigation appears/disappears at the correct breakpoints
- Grid layouts adjust appropriately for screen size
- Content remains visually balanced across viewport sizes

## Maintaining These Tests

When making visual changes to the application, update these tests as follows:

1. **CSS Framework Changes**: If changing class names or styling conventions, update the selectors in the tests
2. **Breakpoint Changes**: If modifying the responsive breakpoints, update the viewport dimensions in the tests
3. **Color Scheme Changes**: If changing the color palette, update the color expectations in the tests
4. **Component Changes**: If modifying component structure, update the component selectors

## Common Issues and Solutions

### Known Issues

1. **QR Code Modal Test**: Currently skipped because it depends on courses being available in the test environment. In a production environment, this test would verify modal styling with proper test data.

2. **Route Updates**: The QR code routes are accessed via `/qr/` (not `/qr-codes/`). This has been updated in the tests.

3. **Annotation Conflict**: There was an issue with the QR code statistics page where `scan_count` annotation conflicted with a model field. This was fixed by renaming the annotation to `total_scans`.

### Screenshots Don't Match Expected

If the application styling has intentionally changed:

```bash
npx playwright test tailwind-visual-regression.spec.js --update-snapshots
```

### Test Fails in CI but Passes Locally

This is usually due to rendering differences. Try:

1. Adding tolerance to color comparisons
2. Using more specific element targeting
3. Implementing more robust style checking (e.g., checking CSS variables rather than computed colors)

### Missing Elements in Tests

If selectors can't find elements, check:

1. Class name changes in the application
2. HTML structure changes
3. Conditional rendering that might hide elements

## Interpreting Test Failures

| Failure Type | Likely Cause | Solution |
|--------------|--------------|----------|
| Color mismatch | Theme implementation issue | Check dark mode variants and CSS variables |
| Missing Tailwind classes | Regression to Bootstrap or inline styles | Ensure components use Tailwind utilities |
| Responsive layout failures | Breakpoint implementation issue | Check media query implementation and Tailwind config |
| Modal styling mismatch | Framework conflict or override | Verify no Bootstrap modal classes are being used |

By maintaining these visual regression tests, we ensure the application consistently uses Tailwind CSS and maintains proper theming support across all components and viewports.