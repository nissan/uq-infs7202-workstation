# Playwright E2E Testing

This document outlines the implementation of end-to-end (E2E) testing for the LearnMore Plus platform using Playwright.

## Overview

We've implemented Playwright for automated browser testing to ensure the application functions correctly from a user's perspective. These tests simulate real user interactions with the application, covering critical user journeys and ensuring features work as expected across different browsers.

## Test Structure

Our Playwright tests follow the Page Object Model (POM) pattern for better organization and maintenance:

```
tests/e2e/
├── playwright.config.js             # Playwright configuration
├── package.json                     # Node dependencies
├── page-objects/                    # Page objects for different sections
│   ├── LoginPage.js                 # Login page interactions
│   ├── CourseCatalogPage.js         # Course catalog page interactions
│   ├── CourseDetailPage.js          # Course detail page interactions
│   ├── DashboardPage.js             # Dashboard page interactions
│   ├── AiTutorPage.js               # AI Tutor page interactions
│   └── NavigationComponent.js       # Common navigation elements
└── tests/                           # Test specifications
    ├── auth.spec.js                 # Authentication tests
    ├── course-catalog.spec.js       # Course catalog tests
    ├── course-detail.spec.js        # Course detail tests
    ├── admin-demo.spec.js           # Admin user journey tests
    ├── coordinator-demo.spec.js     # Coordinator user journey tests
    ├── instructor-demo.spec.js      # Instructor user journey tests
    └── student-demo.spec.js         # Student user journey tests
```

## Setup and Configuration

### Installation

```bash
# Navigate to the e2e test directory
cd tests/e2e

# Install dependencies
npm install

# Install Playwright browsers
npx playwright install
```

### Configuration

Our Playwright configuration (`playwright.config.js`) includes:

```javascript
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:8000',
    actionTimeout: 0,
    trace: 'on-first-retry',
    video: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
    {
      name: 'firefox',
      use: { browserName: 'firefox' },
    },
    {
      name: 'webkit',
      use: { browserName: 'webkit' },
    },
  ],
  webServer: {
    command: 'cd ../.. && python manage.py runserver',
    port: 8000,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

This configuration:
- Sets appropriate timeouts for tests and expectations
- Enables parallel test execution when possible
- Configures retry logic for CI environments
- Captures videos, screenshots, and traces for debugging failed tests
- Sets up testing across Chromium, Firefox, and WebKit browsers
- Automatically starts the Django development server for testing

## Page Object Model Implementation

We follow the Page Object Model pattern to make our tests more maintainable:

### Example: LoginPage.js

```javascript
// LoginPage.js
class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('#id_username');
    this.passwordInput = page.locator('#id_password');
    this.loginButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message');
  }

  async goto() {
    await this.page.goto('/accounts/login/');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async getErrorMessage() {
    return this.errorMessage.innerText();
  }
}

module.exports = { LoginPage };
```

### Example: CourseDetailPage.js

```javascript
// CourseDetailPage.js
class CourseDetailPage {
  constructor(page) {
    this.page = page;
    this.courseTitle = page.locator('h1.course-title');
    this.enrollButton = page.locator('button.enroll-button');
    this.modulesList = page.locator('.modules-list');
    this.aiTutorButton = page.locator('.ai-tutor-button');
  }

  async goto(courseId) {
    await this.page.goto(`/courses/${courseId}/`);
  }

  async enrollInCourse() {
    await this.enrollButton.click();
  }

  async openAiTutor() {
    await this.aiTutorButton.click();
  }
}

module.exports = { CourseDetailPage };
```

## Test Examples

### Authentication Test

```javascript
// auth.spec.js
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/LoginPage');

test.describe('Authentication', () => {
  test('should allow a user to log in with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Check if redirected to dashboard after login
    await expect(page).toHaveURL(/.*dashboard.*/);
  });

  test('should show error with invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('invalid-user', 'wrong-password');
    
    // Check if error message is displayed
    const errorText = await loginPage.getErrorMessage();
    expect(errorText).toContain('Please enter a correct username and password');
  });
});
```

### User Journey Test: Student Demo

```javascript
// student-demo.spec.js
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/LoginPage');
const { CourseCatalogPage } = require('../page-objects/CourseCatalogPage');
const { CourseDetailPage } = require('../page-objects/CourseDetailPage');
const { AiTutorPage } = require('../page-objects/AiTutorPage');

test.describe('Student Journey', () => {
  test('complete student journey from login to course completion', async ({ page }) => {
    // Login as student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Browse course catalog
    const catalogPage = new CourseCatalogPage(page);
    await catalogPage.goto();
    await catalogPage.filterByCategory('Programming');
    
    // Select and view a course
    await catalogPage.openCourse('Introduction to Python');
    
    // Enroll in the course
    const detailPage = new CourseDetailPage(page);
    await detailPage.enrollInCourse();
    
    // Access course content
    await page.click('text=Start Learning');
    
    // Use AI Tutor
    await detailPage.openAiTutor();
    const tutorPage = new AiTutorPage(page);
    await tutorPage.askQuestion('What is a variable in Python?');
    
    // Verify tutor response
    const response = await tutorPage.getLastResponse();
    expect(response).toContain('variable');
    
    // Complete a quiz
    await page.goto('/courses/my-courses/');
    await page.click('text=Introduction to Python');
    await page.click('text=Module 1: Getting Started');
    await page.click('text=Take Quiz');
    
    // Submit quiz answers
    await page.fill('.quiz-answer:first-child', 'Python is a programming language');
    await page.click('button[type="submit"]');
    
    // Verify completion
    expect(await page.isVisible('text=Quiz Completed')).toBeTruthy();
  });
});
```

## Role-Based User Journey Tests

We've implemented comprehensive role-based user journey tests to validate the experience for different user types:

1. **Student Journey Tests** (`student-demo.spec.js`)
   - Course browsing and enrollment
   - Content access and navigation
   - Quiz taking and progress tracking
   - AI Tutor interaction
   - QR code scanning

2. **Instructor Journey Tests** (`instructor-demo.spec.js`)
   - Course creation and editing
   - Module and content management
   - Quiz creation and analysis
   - Student progress monitoring
   - QR code generation

3. **Coordinator Journey Tests** (`coordinator-demo.spec.js`)
   - Course assignment management
   - Instructor allocation
   - Enrollment management
   - Course analytics review

4. **Admin Journey Tests** (`admin-demo.spec.js`)
   - User management
   - System configuration
   - Activity monitoring
   - System health checks

## Running Tests

```bash
# Run all tests
npx playwright test

# Run a specific test file
npx playwright test auth.spec.js

# Run tests against a specific browser
npx playwright test --project=chromium

# Run in debug mode with UI
npx playwright test --debug

# Generate and open report
npx playwright test --reporter=html && npx playwright show-report
```

## CI/CD Integration

These tests are designed to run in CI/CD pipelines. Add this configuration to your CI workflow:

```yaml
name: E2E Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 16
      - name: Install dependencies
        run: npm ci
        working-directory: ./tests/e2e
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
        working-directory: ./tests/e2e
      - name: Run Playwright tests
        run: npx playwright test
        working-directory: ./tests/e2e
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: tests/e2e/playwright-report/
          retention-days: 30
```

## Best Practices

1. **Use Page Objects** to organize test code and improve maintainability
2. **Test critical user journeys** rather than every possible interaction
3. **Make tests independent** so they can run in any order
4. **Use explicit waits** rather than arbitrary timeouts
5. **Take screenshots on failure** to help diagnose issues
6. **Use meaningful test descriptions** that clearly communicate what is being tested
7. **Run tests across multiple browsers** to catch browser-specific issues
8. **Minimize test flakiness** by handling asynchronous operations properly
9. **Store test credentials securely** using environment variables

## Future Improvements

1. **Visual regression testing** to catch unexpected UI changes
2. **Network request mocking** for testing edge cases
3. **Performance measurement** to track page load and interaction times
4. **Accessibility testing** integration using Playwright's accessibility features
5. **Device emulation** to test responsive design across different screen sizes
6. **Parallel test execution** for faster test runs in production
7. **Extended test coverage** for additional user journeys and edge cases