# Demo User Test Scripts

This directory contains Playwright test scripts that automate the simulation of user journeys for our demo users. These tests help ensure that demo scenarios continue to work correctly after code changes.

## Demo Users Included

The test suite includes automated journeys for all key user roles:

1. **Student Demo** (`student-demo.spec.js`)
   - Uses the demo account: `john.doe` / `john.doe123`
   - Tests course browsing, enrollment, content viewing, quiz taking, and AI tutor usage

2. **Instructor Demo** (`instructor-demo.spec.js`)
   - Uses the demo account: `dr.smith` / `dr.smith123`
   - Tests course management, content creation, student progress tracking, and analytics

3. **Course Coordinator Demo** (`coordinator-demo.spec.js`)
   - Uses the demo account: `coordinator` / `coordinator123` (or `coord123`)
   - Tests course coordination, instructor assignment, enrollment management, and analytics

4. **Administrator Demo** (`admin-demo.spec.js`)
   - Uses the demo account: `admin` / `admin123`
   - Tests system-wide administration features, user management, activity logs, and analytics

## Running the Demo Tests

### Running All Demo Tests

```bash
# Run all demo tests
npm test
```

### Running Tests for a Specific User Role

```bash
# Run just the student demo tests
npx playwright test student-demo.spec.js

# Run just the instructor demo tests
npx playwright test instructor-demo.spec.js

# Run just the coordinator demo tests
npx playwright test coordinator-demo.spec.js

# Run just the admin demo tests
npx playwright test admin-demo.spec.js
```

### Running Tests in UI Mode

```bash
# For more visibility into the testing process, use UI mode
npx playwright test student-demo.spec.js --ui
```

## Demo Test Design Principles

1. **Realistic User Journeys**: Tests simulate actual user behavior, not just isolated function testing
2. **Graceful Fallbacks**: Tests accommodate variations in data or UI state
3. **Non-destructive Testing**: Tests avoid creating/deleting data where possible
4. **Complete Coverage**: All key features for each user role are covered

## Maintaining Demo Tests

When you make changes to the application that affect user workflows, you should update these tests to match. In particular, pay attention to:

1. **Selector Changes**: If you rename CSS classes or restructure HTML, update the selectors
2. **Flow Changes**: If you change the user journey (add steps, change workflow), update the tests
3. **New Features**: Add tests for new features that should be part of demo scenarios

## Test Structure

Each demo test file follows the same structure:

1. **Login Setup**: Logs in as the appropriate demo user
2. **Core Functionality Tests**: Individual tests for each key aspect of the user's role
3. **AI Tutor Test**: A test of the AI tutor functionality for this user type

## Visual and UI Tests

In addition to functional tests, we've implemented specialized tests for visual styling and UI framework verification:

1. **Visual Verification Tests** (`visual-verification.spec.js`)
   - Tests dark mode transitions
   - Verifies styling consistency across pages
   - Checks responsive layouts on different device sizes
   - Validates modal functionality and styling

2. **QR Code UI Tests** (`qr-codes.spec.js`)
   - Tests QR code modal display and interactions
   - Verifies proper theme handling for QR code components
   - Tests download functionality and printable QR sheets

3. **Tailwind Visual Regression Tests** (`tailwind-visual-regression.spec.js`)
   - Advanced testing of Tailwind CSS implementation
   - Verifies color schemes in light and dark modes
   - Confirms absence of Bootstrap classes
   - Tests responsive behavior at all Tailwind breakpoints
   - Validates proper usage of Tailwind utilities across components

## Auto-generated Reports

After running tests, detailed reports are available in the `playwright-report` directory. Open `playwright-report/index.html` in a browser to view details of test runs, including screenshots of failures.

---

To update these tests or fix failing tests, run them with the `--update-snapshots` flag or in UI mode to debug visually.