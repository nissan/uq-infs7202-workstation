# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands

- Run server: `python manage.py runserver`
- Run tests: `pytest`
- Run single test: `pytest apps/path/to/test.py::TestClass::test_method`
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