#!/bin/bash

# This script runs the test suite for the LearnMore Plus project

echo "Running LearnMore Plus Test Suite"
echo "--------------------------------"

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Parse arguments
APP="$1"
TEST="$2"

if [ -z "$APP" ] && [ -z "$TEST" ]; then
    # Run all tests with pytest if available
    echo "Running all tests..."
    if command -v pytest &> /dev/null; then
        pytest
    else
        echo "pytest not found, using Django's test runner..."
        python manage.py test
    fi
elif [ -z "$TEST" ]; then
    # Run tests for a specific app
    echo "Running tests for $APP app..."
    if command -v pytest &> /dev/null; then
        pytest apps/$APP
    else
        python manage.py test apps.$APP
    fi
else
    # Run a specific test
    echo "Running $TEST in $APP app..."
    if command -v pytest &> /dev/null; then
        pytest apps/$APP/tests.py::$TEST
    else
        python manage.py test apps.$APP.tests.$TEST
    fi
fi

# Always run template syntax error tests specifically
echo -e "\nChecking for template syntax errors..."
if command -v pytest &> /dev/null; then
    pytest apps/core/tests.py::TemplateSyntaxErrorTests
else
    python manage.py test apps.core.tests.TemplateSyntaxErrorTests
fi

# Check the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "--------------------------------"
    echo "✅ All tests passed!"
else
    echo "--------------------------------"
    echo "❌ Some tests failed. Please check the output above for details."
    exit $EXIT_CODE
fi