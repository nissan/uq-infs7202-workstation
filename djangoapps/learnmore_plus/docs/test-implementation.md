# Test Implementation Documentation

This document outlines the test implementation for the LearnMore Plus platform, focusing on the comprehensive testing strategy for key features including the atomic design components, AI tutor, and QR code functionality.

## Testing Overview

Our testing strategy follows these principles:

1. **Comprehensive Coverage**: Tests for all key features and components
2. **Isolation**: Testing components in isolation to identify issues
3. **Integration**: Testing components working together
4. **Regression Prevention**: Tests to prevent regressions when making changes
5. **Specific Solutions**: Tests that focus on previously identified issues

## Test Suite Structure

The test suite is organized by Django app, with each app having its own `tests.py` file or test directory:

```
apps/
├── core/
│   └── tests.py           # Tests for core functionality and UI components
├── ai_tutor/
│   └── tests.py           # Tests for AI tutor functionality
├── qr_codes/
│   └── tests.py           # Tests for QR code functionality
└── ...
```

## Core Features Testing

### Atomic Design Components

The `apps/core/tests.py` file contains comprehensive tests for our atomic design components:

1. **ComponentRenderingTestCase**: Tests that individual components render correctly
   - Tests for atoms like buttons, typography elements, and icons
   - Tests for molecules like cards and navigation elements
   - Tests for organisms like headers and section layouts
   - Tests with various parameter combinations to ensure flexibility

2. **TemplateSyntaxErrorTests**: Specific tests for template syntax patterns that have caused issues
   - Tests for conditional defaults using the {% if not var %}{% with var="default" %}{% endif %} pattern
   - Tests for nested includes with parameters
   - Tests for URL parameters in templates

3. **PageTemplateTestCase**: Tests that complete page templates render without errors
   - Tests for core templates like home and about pages
   - Tests for template inheritance and blocks
   - Tests for context variable handling

### AI Tutor Testing

The `apps/ai_tutor/tests.py` file contains tests for the AI tutor functionality:

1. **AiTutorModelTests**: Tests for AI tutor models
   - Tests for TutorSession model
   - Tests for TutorMessage model
   - Tests for TutorContextItem model
   - Tests for ContentEmbedding model

2. **TutorServiceTests**: Tests for AI tutor services
   - Tests for the TutorService which handles tutor session management
   - Tests for generating assistant responses with mocked LLMs
   - Tests for context management and message creation

3. **LLMFactoryTests**: Tests for LLM integration
   - Tests for getting chat models from different providers
   - Tests for properly configuring LLM instances

4. **ContentIndexingServiceTests**: Tests for the content indexing functionality
   - Tests for vector store creation
   - Tests for embedding generation
   - Tests for content indexing and retrieval

5. **AiTutorViewTests**: Tests for AI tutor views
   - Tests for session listing and creation
   - Tests for chat view functionality
   - Tests for message handling

6. **APIEndpointTests**: Tests for AI tutor API endpoints
   - Tests for session API endpoints
   - Tests for chat message API endpoints

### QR Code Testing

The `apps/qr_codes/tests.py` file contains tests for QR code functionality:

1. **QRCodeModelTests**: Tests for QR code models
   - Tests for QRCode model
   - Tests for QRCodeScan model
   - Tests for QR code image generation

2. **QRCodeServiceTests**: Tests for QR code services
   - Tests for creating QR codes
   - Tests for recording scans
   - Tests for retrieving QR codes
   - Tests for calculating scan statistics

3. **QRCodeViewTests**: Tests for QR code views
   - Tests for scan redirects
   - Tests for QR code detail views
   - Tests for statistics views
   - Tests for printing QR code sheets

4. **QRCodeTemplateTagTests**: Tests for QR code template tags
   - Tests for getting QR codes in templates
   - Tests for getting QR code URLs

## Test Configuration

We use pytest for running tests with custom configuration in `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = learnmore_plus.settings.dev
python_files = test_*.py tests.py
testpaths = apps
addopts = --reuse-db --no-migrations
markers =
    unit: mark a test as a unit test
    integration: mark a test as an integration test
    functional: mark a test as a functional test
    ui: mark a test as UI component test
    slow: mark a test as slow (e.g., heavy database operations)
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

## Mocking External Services

Several tests use Python's `unittest.mock` to mock external services:

1. **LLM Services**: Mocked in AI tutor tests to avoid actual API calls
   - Chat models mocked to return predefined responses
   - Embedding models mocked to return predetermined vectors

2. **PDF Generation**: Mocked in QR code tests to avoid actual PDF generation
   - Weasyprint HTML mocked to return a simple binary response

## Test Data

Test data is created in each test class's `setUp` method:

1. **Test Users**: Various user types are created with different permissions
2. **Test Courses**: Sample courses, modules, and content for testing functionality
3. **Test Sessions**: AI tutor sessions for testing session management
4. **Test QR Codes**: QR codes for testing code generation and scanning

## Running Tests

Tests can be run using the following commands:

```bash
# Run all tests
pytest

# Run tests for a specific app
pytest apps/core/
pytest apps/ai_tutor/
pytest apps/qr_codes/

# Run tests with a specific marker
pytest -m unit
pytest -m integration
pytest -m ui

# Run tests with coverage
coverage run -m pytest
coverage report
```

## Continuous Integration Considerations

While not currently implemented, these tests are designed to be run in CI environments with the following considerations:

1. **Database Setup**: Tests use Django's test database
2. **External Services**: All external services are mocked
3. **Static Files**: Tests don't rely on collectstatic being run
4. **Test Isolation**: Tests are isolated and don't affect each other

## Future Test Improvements

Areas for future test improvement include:

1. **UI Testing**: Adding Selenium tests for end-to-end UI testing
2. **Performance Testing**: Adding performance tests for critical paths
3. **Security Testing**: Adding tests for security features
4. **Load Testing**: Testing the system under load to identify bottlenecks

## Summary

Our comprehensive test suite ensures that key features of the LearnMore Plus platform function correctly and remain stable as the codebase evolves. The tests focus on the atomic design components, AI tutor functionality, and QR code system, providing confidence that the platform meets its requirements and remains robust through future changes.