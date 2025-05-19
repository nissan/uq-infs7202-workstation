# Test Tagging Approach

This document explains how we use test tags in our Playwright end-to-end tests to organize and prioritize test execution.

## Test Tag Categories

We use the following test tag categories:

### 1. `@critical`

Critical tests verify core functionality that must work for the application to be considered operational. These tests are run as part of CI/CD pipelines and before any deployment.

Examples of critical functionality:
- User authentication
- Course access and navigation
- Quiz functionality
- Content uploads
- Accessibility features

### 2. `@smoke` (For future implementation)

Smoke tests are a subset of critical tests that verify the application is up and running with basic functionality. These tests are quick to run and should be executed frequently.

### 3. `@regression` (For future implementation)

Regression tests are more comprehensive and validate that new changes don't break existing functionality. These tests are run less frequently, typically before major releases.

### 4. `@performance` (For future implementation)

Performance tests evaluate the application's speed, responsiveness, and stability under various conditions. These tests are typically run on a schedule or before major releases.

### 5. `@accessibility` (For future implementation)

Accessibility tests specifically check for compliance with accessibility standards (WCAG). These tests help ensure the application is usable by people with disabilities.

## How Tags Are Implemented

We implement test tags using Playwright's test filtering capabilities. All critical tests are marked with the `@critical` tag in the test description.

While our primary test runner script (`run-critical-tests.sh`) currently lists each test file explicitly for clarity and control, we've added the tagging capability to support future enhancements. The script includes a commented-out alternative that uses the `--grep` option for tag-based filtering:

```bash
# Alternative approach with tag filtering
npx playwright test --project=chromium --grep="@critical"
```

This dual approach gives us flexibility - we can run tests individually with precise control over execution order, or we can switch to tag-based filtering to automatically include all tests of a specific category.

## Test Organization

Instead of manually adding tags to each test file, we use a helper module (`critical-tests.js`) that automatically adds the `@critical` tag to all tests that import it:

```javascript
// critical-tests.js
const { test: baseTest } = require('@playwright/test');

exports.test = baseTest.extend({
  // Add any specific setup for critical tests here
})('Critical Tests @critical');

module.exports = {
  test: exports.test,
  expect: baseTest.expect,
};
```

This approach ensures consistent tagging without having to manually add tags to each test case.

## Running Tests by Tag

To run tests with specific tags:

```bash
# Run critical tests
./run-critical-tests.sh

# Run tests with specific tags (future implementation)
npx playwright test --grep="@smoke"
npx playwright test --grep="@regression"
npx playwright test --grep="@performance"
npx playwright test --grep="@accessibility"

# Run tests with multiple tags (future implementation)
npx playwright test --grep="@critical|@smoke"

# Run tests excluding specific tags (future implementation)
npx playwright test --grep-invert="@slow"
```

## Future Enhancements

In the future, we plan to:

1. Add more tag categories to better organize our tests
2. Create separate runner scripts for different test categories
3. Implement automated test scheduling based on tags
4. Add reporting that shows test coverage by tag category