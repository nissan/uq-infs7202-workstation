#!/bin/bash

echo "Running Performance Tests..."

# Make sure the script is executable
chmod +x "$0"

# Set working directory to the script location
cd "$(dirname "$0")"

# Find all performance test files
PERFORMANCE_TESTS=$(find ./tests -name "*-performance.spec.js")

if [ -z "$PERFORMANCE_TESTS" ]; then
  echo "No performance tests found. Generate them first using:"
  echo "  node scripts/generate-performance-test.js <page-name>"
  exit 1
fi

# Run all performance tests
npx playwright test $PERFORMANCE_TESTS --project=chromium

echo "Performance tests completed."