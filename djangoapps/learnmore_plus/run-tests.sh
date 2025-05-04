#!/bin/bash

# Run tests with coverage and generate report
echo "Running tests with coverage..."
python -m pytest --cov=apps --cov-config=.coveragerc --cov-report=term-missing

# Run only component tests
run_component_tests() {
    echo "Running component tests only..."
    python -m pytest tests/test_components.py -v
}

# Run only view tests
run_view_tests() {
    echo "Running view tests only..."
    python -m pytest apps/core/tests.py -v
}

# Run only integration tests
run_integration_tests() {
    echo "Running integration tests only..."
    python -m pytest tests/test_integration.py -v
}

# Run only URL tests
run_url_tests() {
    echo "Running URL tests only..."
    python -m pytest tests/test_urls.py -v
}

# Handle command line arguments
if [ "$1" == "components" ]; then
    run_component_tests
elif [ "$1" == "views" ]; then
    run_view_tests
elif [ "$1" == "integration" ]; then
    run_integration_tests
elif [ "$1" == "urls" ]; then
    run_url_tests
fi