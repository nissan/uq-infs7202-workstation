# Model Testing Guide - CRUD Operations

This guide explains how to write comprehensive CRUD (Create, Read, Update, Delete) tests for models in the LearnMore Plus system.

## Table of Contents
- [Overview](#overview)
- [Test Structure](#test-structure)
- [Testing Each CRUD Operation](#testing-each-crud-operation)
- [Fixtures](#fixtures)
- [Common Patterns](#common-patterns)
- [Running the Tests](#running-the-tests)
- [Troubleshooting](#troubleshooting)

## Overview

Testing database models is critical to ensure that our application correctly handles data. CRUD tests verify that our models can:
- Create new records in the database
- Read existing records
- Update records with new information
- Delete records when they're no longer needed

Each model in our system should have comprehensive CRUD tests.

## Test Structure

We use pytest for testing, with tests organized by model. The directory structure is:

```
apps/
  app_name/
    tests/
      __init__.py
      test_model_name.py  # One file per model
      test_models.py      # Optional aggregator file
```

Each test file follows this structure:

```python
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.app_name.models import ModelName, RelatedModel

User = get_user_model()

@pytest.mark.django_db
class TestModelNameModel:
    """
    Tests for the ModelName model CRUD operations.
    """
    
    @pytest.fixture
    def setup_data(self):
        """Set up test data and dependencies."""
        # Create related objects needed for testing
        # Return data needed for tests
    
    def test_create_model(self, setup_data):
        """Test creating a new model instance."""
        # ...
    
    def test_read_model(self, setup_data):
        """Test retrieving model instance(s)."""
        # ...
    
    def test_update_model(self, setup_data):
        """Test updating a model instance."""
        # ...
    
    def test_delete_model(self, setup_data):
        """Test deleting a model instance."""
        # ...
    
    # Additional tests for model-specific functionality
```

## Testing Each CRUD Operation

### Create

Test that a model instance can be created with all required fields and that optional fields work as expected.

```python
def test_create_model(self, setup_data):
    """Test creating a new model instance."""
    # Create the instance
    instance = ModelName.objects.create(
        field1="value1",
        field2="value2",
        # ...
    )
    
    # Assertions
    assert instance.id is not None
    assert instance.field1 == "value1"
    assert instance.field2 == "value2"
    assert instance.created_at is not None  # If your model has this field
    assert instance.updated_at is not None  # If your model has this field
```

### Read

Test that a model instance can be retrieved in different ways.

```python
def test_read_model(self, setup_data):
    """Test retrieving a model instance."""
    # Create instance first
    original = ModelName.objects.create(
        field1="value1",
        field2="value2",
        # ...
    )
    
    # Retrieve by ID
    retrieved_by_id = ModelName.objects.get(id=original.id)
    assert retrieved_by_id.field1 == "value1"
    
    # Retrieve by field
    retrieved_by_field = ModelName.objects.get(field1="value1")
    assert retrieved_by_field.id == original.id
    
    # Test filtering
    filtered_instances = ModelName.objects.filter(field2="value2")
    assert original in filtered_instances
```

### Update

Test that a model instance can be updated.

```python
def test_update_model(self, setup_data):
    """Test updating a model instance."""
    # Create instance first
    instance = ModelName.objects.create(
        field1="original value",
        field2="original value",
        # ...
    )
    
    # Store original timestamps
    original_created_at = instance.created_at
    original_updated_at = instance.updated_at
    
    # Update fields
    instance.field1 = "updated value"
    instance.field2 = "updated value"
    instance.save()
    
    # Refresh from database
    instance.refresh_from_db()
    
    # Assertions
    assert instance.field1 == "updated value"
    assert instance.field2 == "updated value"
    assert instance.created_at == original_created_at  # Should not change
    assert instance.updated_at > original_updated_at  # Should be updated
```

### Delete

Test that a model instance can be deleted.

```python
def test_delete_model(self, setup_data):
    """Test deleting a model instance."""
    # Create instance first
    instance = ModelName.objects.create(
        field1="value1",
        field2="value2",
        # ...
    )
    
    # Verify created
    instance_id = instance.id
    assert ModelName.objects.filter(id=instance_id).exists()
    
    # Delete the instance
    instance.delete()
    
    # Verify deleted
    assert not ModelName.objects.filter(id=instance_id).exists()
```

## Fixtures

Fixtures are a key part of pytest. They allow you to set up data for your tests and are defined using the `@pytest.fixture` decorator.

### Local Fixtures

Fixtures specific to a test class should be defined within the class:

```python
@pytest.fixture
def setup_data(self):
    """Set up test data."""
    # Create data
    return data
```

### Global Fixtures

For shared data (like users, categories), define fixtures in `conftest.py`:

```python
# In conftest.py
@pytest.fixture
def admin_user():
    """Create and return an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword123'
    )
```

## Common Patterns

### Testing Model Properties

```python
def test_property_method(self, setup_data):
    """Test model property methods."""
    instance = ModelName.objects.create(...)
    assert instance.calculated_property == expected_value
```

### Testing Unique Constraints

```python
def test_unique_constraint(self, setup_data):
    """Test unique constraint."""
    ModelName.objects.create(unique_field="unique_value")
    
    # This should raise an exception
    with pytest.raises(Exception) as excinfo:
        ModelName.objects.create(unique_field="unique_value")
```

### Testing Model Relationships

```python
def test_relationships(self, setup_data):
    """Test model relationships."""
    parent = ParentModel.objects.create(...)
    child = ChildModel.objects.create(parent=parent)
    
    assert child.parent == parent
    assert child in parent.children.all()
```

### Testing String Representation

```python
def test_str_representation(self, setup_data):
    """Test string representation."""
    instance = ModelName.objects.create(name="Test Name")
    assert str(instance) == "Test Name"
```

## Running the Tests

To run model tests:

```bash
# Run all tests for an app
pytest apps/app_name/tests/

# Run tests for a specific model
pytest apps/app_name/tests/test_model_name.py

# Run a specific test
pytest apps/app_name/tests/test_model_name.py::TestModelNameModel::test_create_model

# Run with verbose output
pytest apps/app_name/tests/ -v
```

## Troubleshooting

### Common Issues

1. **Missing Migrations**: Ensure all model changes have corresponding migrations.
2. **Fixture Issues**: Make sure fixtures create all required related objects.
3. **Transaction Issues**: Use `@pytest.mark.django_db` to enable transaction support.
4. **Model Field Changes**: Update tests when model fields change.

### Test Isolation

Each test should be isolated and not depend on the state from previous tests:

- Use fixtures to set up test data
- Clean up after tests if they modify shared resources
- Avoid global state changes

### Database Resets

Pytest-django automatically resets the database between tests. If you need to force a database reset:

```bash
pytest --reuse-db=False
```

## Best Practices

1. **Test Coverage**: Aim for 100% model field coverage in CRUD tests.
2. **Assertions**: Use specific assertions that clearly identify what's being tested.
3. **Test Edge Cases**: Include tests for model constraints, edge cases, and error conditions.
4. **Maintain Tests**: Update tests when model definitions change.
5. **Keep Tests Fast**: Minimize database operations in fixtures.