#!/bin/bash

# run_tests.sh - A script to run different types of tests for the LearnMore app

# Set variables
PYTHON="python3"
MANAGE_PY="manage.py"
VERBOSITY=1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to display help
show_help() {
    echo "Usage: $0 [options] [test_path]"
    echo
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -v, --verbose   Increase verbosity"
    echo "  -a, --all       Run all tests"
    echo "  -t, --templates Run only template tests"
    echo "  -i, --api       Run only API tests"
    echo "  -n, --integration Run only integration tests"
    echo
    echo "Examples:"
    echo "  $0 -a            # Run all tests"
    echo "  $0 -t            # Run only template tests"
    echo "  $0 courses       # Run all tests in the courses app"
    echo "  $0 courses.tests.test_templates  # Run specific test module"
    exit 0
}

# Process options
TEST_PATH=""
RUN_TEMPLATE_TESTS=0
RUN_API_TESTS=0
RUN_INTEGRATION_TESTS=0
RUN_ALL_TESTS=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -v|--verbose)
            VERBOSITY=2
            shift
            ;;
        -a|--all)
            RUN_ALL_TESTS=1
            shift
            ;;
        -t|--templates)
            RUN_TEMPLATE_TESTS=1
            shift
            ;;
        -i|--api)
            RUN_API_TESTS=1
            shift
            ;;
        -n|--integration)
            RUN_INTEGRATION_TESTS=1
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# If no specific test type is selected, run all tests
if [[ $RUN_TEMPLATE_TESTS -eq 0 && $RUN_API_TESTS -eq 0 && $RUN_INTEGRATION_TESTS -eq 0 && $RUN_ALL_TESTS -eq 0 ]]; then
    if [[ -z "$TEST_PATH" ]]; then
        # No path specified, default to all tests
        RUN_ALL_TESTS=1
    else
        # Path specified, run tests at that path
        echo "Running tests at path: $TEST_PATH"
        $PYTHON $MANAGE_PY test $TEST_PATH --verbosity=$VERBOSITY
        exit $?
    fi
fi

# Run the selected tests
if [[ $RUN_ALL_TESTS -eq 1 ]]; then
    echo "Running all tests..."
    $PYTHON $MANAGE_PY test --verbosity=$VERBOSITY
    exit $?
fi

# Build the test path pattern
TEST_PATTERN=""
if [[ $RUN_TEMPLATE_TESTS -eq 1 ]]; then
    TEST_PATTERN="courses.tests.test_templates"
fi

if [[ $RUN_API_TESTS -eq 1 ]]; then
    if [[ ! -z "$TEST_PATTERN" ]]; then
        TEST_PATTERN="$TEST_PATTERN courses.tests.test_api_views"
    else
        TEST_PATTERN="courses.tests.test_api_views"
    fi
fi

if [[ $RUN_INTEGRATION_TESTS -eq 1 ]]; then
    if [[ ! -z "$TEST_PATTERN" ]]; then
        TEST_PATTERN="$TEST_PATTERN courses.tests.test_template_api_integration"
    else
        TEST_PATTERN="courses.tests.test_template_api_integration"
    fi
fi

echo "Running tests: $TEST_PATTERN"
$PYTHON $MANAGE_PY test $TEST_PATTERN --verbosity=$VERBOSITY
exit $?