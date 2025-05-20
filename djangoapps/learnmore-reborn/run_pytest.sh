#!/bin/bash

# run_pytest.sh - A script to run pytest tests for the LearnMore app

# Set variables
VERBOSITY="-v"
TEST_PATH=""
MARKERS=""
COVERAGE=""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install pytest if not already installed
if ! python -c "import pytest" &> /dev/null; then
    echo "Installing pytest and required packages..."
    pip install pytest pytest-django pytest-cov pytest-mock
fi

# Function to display help
show_help() {
    echo "Usage: $0 [options] [test_path]"
    echo
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -v, --verbose     Increase verbosity"
    echo "  -q, --quiet       Decrease verbosity"
    echo "  -f, --failfast    Stop on first failure"
    echo "  -c, --coverage    Run with coverage report"
    echo "  -m <marker>       Run tests with specific marker"
    echo "                    Available markers: api, template, integration, unit, slow"
    echo
    echo "Examples:"
    echo "  $0 -m template               # Run all template tests"
    echo "  $0 courses/tests/test_pytest.py  # Run specific test file"
    echo "  $0 -c                        # Run with coverage report"
    echo "  $0 -m \"api or template\"      # Run API or template tests"
    exit 0
}

# Process command line arguments
while (( "$#" )); do
  case "$1" in
    -h|--help)
      show_help
      ;;
    -v|--verbose)
      VERBOSITY="-vv"
      shift
      ;;
    -q|--quiet)
      VERBOSITY=""
      shift
      ;;
    -f|--failfast)
      FAILFAST="--exitfirst"
      shift
      ;;
    -c|--coverage)
      COVERAGE="--cov=courses --cov-report=term-missing"
      shift
      ;;
    -m)
      MARKERS="-m \"$2\""
      shift 2
      ;;
    *)
      TEST_PATH="$1"
      shift
      ;;
  esac
done

# Run tests using pytest
echo "Running tests with pytest..."
eval "python -m pytest $VERBOSITY $FAILFAST $MARKERS $COVERAGE $TEST_PATH"