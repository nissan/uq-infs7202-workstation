#!/bin/bash

# Setup script for Phase 5 branch
# This script creates a new branch for Phase 5 based on the latest code from Phase 4

# Exit on error
set -e

# Define branches
CURRENT_BRANCH="phase-4-learning-interface"
NEW_BRANCH="phase-5-quiz-system"

# Check if we're on the correct branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "$CURRENT_BRANCH" ]; then
    echo "Currently on branch $BRANCH, not $CURRENT_BRANCH"
    echo "Please checkout the $CURRENT_BRANCH branch first"
    exit 1
fi

# Make sure we have the latest changes
echo "Pulling latest changes from $CURRENT_BRANCH..."
git pull origin $CURRENT_BRANCH

# Create and switch to the new branch
echo "Creating and switching to new branch $NEW_BRANCH..."
git checkout -b $NEW_BRANCH

# Initial commit for new phase
echo "Creating initial commit for Phase 5..."
git add PHASE_5_CHECKLIST.md docs/PHASE_4_SUMMARY.md
git commit -m "Setup Phase 5: Quiz System - Basics

- Add Phase 5 checklist
- Add Phase 4 summary document
- Start basic quiz system implementation"

echo ""
echo "Phase 5 branch setup complete!"
echo "You are now on branch: $NEW_BRANCH"
echo ""
echo "Next steps:"
echo "1. Start implementing the quiz models in courses/models.py"
echo "2. Run 'python manage.py makemigrations courses' to create migrations"
echo "3. Update the admin.py file to register the new models"
echo "4. Work through the PHASE_5_CHECKLIST.md items"
echo ""
echo "Remember to commit your changes regularly!"