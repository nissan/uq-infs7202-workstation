#!/bin/bash
# Run specific tests for the progress app

# Activate virtual environment
source venv/bin/activate

# Make sure we're in the project directory
cd "$(dirname "$0")"

# Run the tests for progress app
echo "Running tests for progress app..."
python manage.py test progress.tests.test_model_base

# Return the exit code
exit $?