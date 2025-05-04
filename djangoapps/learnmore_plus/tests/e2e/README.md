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

### Specialized Test Scripts

We provide several specialized test scripts for different test types:

```bash
# Run demo scenario tests (covers all README demo scenarios)
./run-demo-tests.sh

# Run accessibility tests
./run-accessibility-tests.sh

# Run performance tests
./run-performance-tests.sh

# Run visual verification tests with screenshots
node scripts/run-visual-tests.js
```

## Test Structure

Tests are organized by feature area and type. Each test file focuses on a specific functionality:

### Functional Tests
- `auth.spec.js` - Tests for login, logout, registration
- `courses.spec.js` - Tests for course listing, details, enrollment
- `navigation.spec.js` - Tests for site navigation

### User Role Tests
- `student-demo.spec.js` - Simulates student user journeys
- `instructor-demo.spec.js` - Simulates instructor user journeys
- `coordinator-demo.spec.js` - Simulates coordinator user journeys
- `admin-demo.spec.js` - Simulates admin user journeys

### Feature Tests
- `qr-codes.spec.js` - Tests QR code functionality
- `demo-scenarios.spec.js` - Tests for specific demo scenarios from README

### Visual Tests
- `visual-verification.spec.js` - Tests for visual consistency and dark mode

### Non-Functional Tests
- `*-accessibility.spec.js` - Tests for accessibility compliance
- `*-performance.spec.js` - Tests for performance benchmarks

## Test Generation

We provide scripts to generate test stubs for new features:

```bash
# Generate a basic test for a new page
node scripts/generate-test.js page-name

# Generate an accessibility test
node scripts/generate-accessibility-test.js component-name

# Generate a performance test
node scripts/generate-performance-test.js page-name
```

## Page Object Model

We use the Page Object Model (POM) pattern to make tests more maintainable:

```javascript
// Example of a page object
class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('input[name="username"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.loginButton = page.locator('button[type="submit"]');
  }

  async goto() {
    await this.page.goto('/login/');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}
```

Page objects are located in the `page-objects` directory.

## Test Documentation

For more detailed information about our test approach:

- `TEST-COVERAGE.md` - Detailed mapping of tests to demo scenarios
- `README-demo-tests.md` - Information about demo user tests

## Best Practices

1. Each test should be independent and not depend on state created by another test.
2. Use page objects for cleaner, more maintainable tests.
3. Add clear test descriptions to make failures easier to understand.
4. Keep tests focused on user behavior rather than implementation details.
5. Include tests for error states, not just the happy path.
6. Test with different browsers and viewport sizes.
7. Include visual verification and accessibility testing.
8. Write performance tests for critical pages and interactions.