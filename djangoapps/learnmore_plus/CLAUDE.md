# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands

- Run server: `python manage.py runserver`
- Run tests: `pytest`
- Run single test: `pytest apps/path/to/test.py::TestClass::test_method`
- Run component tests: `./run-tests.sh components`
- Run view tests: `./run-tests.sh views`
- Run integration tests: `./run-tests.sh integration`
- Run URL tests: `./run-tests.sh urls`
- Run all tests with coverage: `./run-tests.sh`
- Lint code: `flake8`
- Format code: `black .`
- Sort imports: `isort .`
- Check test coverage: `coverage run -m pytest && coverage report`
- Test API endpoints: `./test_endpoints.sh`

## Code Style Guidelines

- Format with Black (line length 88)
- Sort imports with isort
- Follow Django naming conventions (snake_case for functions/variables, PascalCase for classes)
- Models: define `class Meta` with ordering and permissions
- Views: use class-based views when appropriate
- Error handling: use Django's built-in form validation; handle exceptions properly
- Type hints are encouraged but not enforced (legacy code may lack typing)
- Maintain Django's app-based structure
- URL naming: use consistent URL naming patterns
- Templates should extend base templates and use Django template language features

## Testing Guidelines

- Write tests for all new functionality
- Follow Django's testing best practices
- Categorize tests into:
  - **Unit tests**: Test individual components in isolation
  - **Integration tests**: Test interactions between components
  - **URL tests**: Verify URL patterns and reverse lookups
  - **Component tests**: Test atomic design components
- Use pytest fixtures from `conftest.py` when possible
- Aim for at least 80% test coverage for new code
- Run tests before committing changes
- Include both positive and negative test cases