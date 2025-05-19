#!/bin/bash

# This script runs the critical tests that verify core functionality
# All tests are implemented as Playwright tests in their respective files

echo "Running Critical Tests..."

# Make the script is executable
chmod +x "$0"

# Set working directory to the script location
cd "$(dirname "$0")"

# Create results directory
mkdir -p test-results/critical

# Run critical tests one by one
echo "1. Testing Tailwind CSS implementation..."
npx playwright test tailwind-visual-regression.spec.js --project=chromium

echo "2. Testing course access..."
npx playwright test basic-course-verification.spec.js --project=chromium

echo "3. Testing quiz access..."
npx playwright test basic-quiz-verification.spec.js --project=chromium

echo "4. Testing quiz functionality..."
npx playwright test quiz-feature-verification.spec.js --project=chromium

echo "5. Testing quiz taking workflow..."
npx playwright test quiz-taking-test.spec.js --project=chromium

echo "6. Testing complete quiz workflow..."
npx playwright test complete-quiz-workflow.spec.js --project=chromium

echo "7. Testing instructor quiz management..."
npx playwright test instructor-quiz-management.spec.js --project=chromium

echo "8. Testing timed quiz features..."
npx playwright test timed-quiz-features.spec.js --project=chromium

echo "9. Testing QR code routes..."
# Only run the test for the QR code statistics API fix we made
PLAYWRIGHT_TEST_MATCH="statistics" npx playwright test qr-codes.spec.js --project=chromium

echo "10. Testing AI Tutor functionality..."
npx playwright test ai-tutor-functionality.spec.js --project=chromium

echo "11. Testing Assignment Management..."
npx playwright test assignment-management.spec.js --project=chromium

echo "12. Testing Accessibility Features..."
npx playwright test accessibility-tests.spec.js --project=chromium

echo "13. Testing File Upload Functionality..."
npx playwright test file-upload-tests.spec.js --project=chromium

echo "14. Testing Social Authentication..."
npx playwright test social-auth-tests.spec.js --project=chromium

echo "15. Testing Prerequisite Quiz Enforcement..."
npx playwright test prerequisite-quiz-enforcement.spec.js --project=chromium

echo "16. Testing AI Tutor Context Levels..."
npx playwright test ai-tutor-context-levels.spec.js --project=chromium

echo "17. Testing QR Code Scanning..."
npx playwright test qr-code-scanning.spec.js --project=chromium

# Alternative approach: Run all critical tests with tag filtering
# echo "Running all critical tests..."
# npx playwright test --project=chromium --grep="@critical"

# Generate HTML report
npx playwright show-report

echo "Tests completed. Check results above and view the HTML report for details."
echo "To view the report, run: npx playwright show-report"