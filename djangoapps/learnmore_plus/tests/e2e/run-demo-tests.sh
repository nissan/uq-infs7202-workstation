#!/bin/bash

echo "Running Demo Scenario Tests..."

# Make sure the script is executable
chmod +x "$0"

# Set working directory to the script location
cd "$(dirname "$0")"

# Run only demo scenario tests
npx playwright test demo-scenarios.spec.js student-demo.spec.js instructor-demo.spec.js admin-demo.spec.js coordinator-demo.spec.js qr-codes.spec.js visual-verification.spec.js tailwind-visual-regression.spec.js --project=chromium

echo "Tests completed."