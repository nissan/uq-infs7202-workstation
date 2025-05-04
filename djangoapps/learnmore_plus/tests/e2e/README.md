# End-to-End Testing with Playwright

This directory contains end-to-end (E2E) tests for LearnMore Plus using Playwright, a browser automation library that allows you to automate UI interactions in Chrome, Firefox, and WebKit.

## Setup

### Install Node.js dependencies

```bash
# Install Node.js packages
npm init -y
npm install @playwright/test
```

### Install Playwright browsers

```bash
# Install all browsers (Chromium, Firefox, WebKit)
npx playwright install
```

## Running Tests

```bash
# Run all tests headlessly
npx playwright test

# Run tests in UI mode (with browser visible)
npx playwright test --ui

# Run specific test file
npx playwright test login.spec.js

# Run tests with specific browser
npx playwright test --project=chromium
```

## Test Structure

Tests are organized by feature area. Each test file should focus on a specific functionality:

- `auth.spec.js` - Tests for login, logout, registration
- `courses.spec.js` - Tests for course listing, details, enrollment
- `learning.spec.js` - Tests for accessing course content
- `admin.spec.js` - Tests for admin functionality

## Best Practices

1. Each test should be independent and should not depend on the state created by another test.
2. Use the Page Object Model pattern for cleaner, more maintainable tests.
3. Add clear test descriptions to make failures easier to understand.
4. Keep tests focused on user behavior rather than implementation details.
5. Include tests for error states, not just the happy path.