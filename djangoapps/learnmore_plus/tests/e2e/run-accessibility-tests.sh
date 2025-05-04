#!/bin/bash

echo "Running Accessibility Tests..."

# Make sure the script is executable
chmod +x "$0"

# Set working directory to the script location
cd "$(dirname "$0")"

# Find all accessibility test files
ACCESSIBILITY_TESTS=$(find ./tests -name "*-accessibility.spec.js")

if [ -z "$ACCESSIBILITY_TESTS" ]; then
  echo "No accessibility tests found. Generate them first using:"
  echo "  node scripts/generate-accessibility-test.js <component-name>"
  exit 1
fi

# Run all accessibility tests
npx playwright test $ACCESSIBILITY_TESTS --project=chromium

echo "Accessibility tests completed."