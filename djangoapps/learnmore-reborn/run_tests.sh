#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Default settings
VERBOSITY=1
PARALLEL=4
TEST_PATH=""
FAILFAST=""

# Process command line arguments
while (( "$#" )); do
  case "$1" in
    -v|--verbose)
      VERBOSITY=2
      shift
      ;;
    -q|--quiet)
      VERBOSITY=0
      shift
      ;;
    -f|--failfast)
      FAILFAST="--failfast"
      shift
      ;;
    --no-parallel)
      PARALLEL=1
      shift
      ;;
    --templates)
      TEST_PATH="courses.tests.test_templates"
      shift
      ;;
    --api)
      TEST_PATH="courses.tests.test_api_views"
      shift
      ;;
    --integration)
      TEST_PATH="courses.tests.test_template_api_integration"
      shift
      ;;
    --help)
      echo "Usage: $0 [options] [test_path]"
      echo ""
      echo "Options:"
      echo "  -v, --verbose       Increase verbosity"
      echo "  -q, --quiet         Decrease verbosity"
      echo "  -f, --failfast      Stop on first failure"
      echo "  --no-parallel       Run tests sequentially"
      echo "  --templates         Run template tests"
      echo "  --api               Run API tests"
      echo "  --integration       Run integration tests"
      echo "  --help              Show this help message"
      echo ""
      echo "Example:"
      echo "  $0 --templates      Run template tests"
      echo "  $0 courses          Run tests in the courses app"
      exit 0
      ;;
    *)
      TEST_PATH="$1"
      shift
      ;;
  esac
done

# Run tests using Django's test runner
echo "Running tests with Django's test runner..."
echo "Settings module: learnmore.test_settings"
DJANGO_SETTINGS_MODULE=learnmore.test_settings python manage.py test $TEST_PATH --verbosity=$VERBOSITY --parallel=$PARALLEL $FAILFAST