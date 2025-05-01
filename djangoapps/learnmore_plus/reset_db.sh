#!/bin/bash

# Print a header
echo "=== Resetting LearnMore+ Database ==="
echo

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the reset commands
echo "Flushing database..."
python manage.py flush --no-input

echo "Generating test data..."
python manage.py generate_test_data

echo "Creating test users..."
python manage.py create_test_users

echo
echo "=== Database Reset Complete ==="
echo
echo "Test Users:"
echo "- Admin: admin/admin123"
echo "- Student: john/john123"
echo "- Instructor: drsmith/drsmith123" 