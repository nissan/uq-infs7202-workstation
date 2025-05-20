#!/bin/bash

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Running model tests for all apps..."

# Run tests for specific model test files
python manage.py test courses.tests.test_models progress.tests.test_models users.tests.test_models

# Output test coverage (if coverage is installed)
if command -v coverage &> /dev/null; then
    echo "Running tests with coverage..."
    coverage run --source='.' manage.py test courses.tests.test_models progress.tests.test_models users.tests.test_models
    coverage report
else
    echo "Coverage not installed. Install with: pip install coverage"
fi

echo "Model tests completed."