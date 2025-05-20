import pytest
from django.test import TestCase
from django.utils.text import slugify
from apps.courses.models import Category


@pytest.mark.django_db
class TestCategoryModel:
    """
    Tests for the Category model CRUD operations.
    """
    
    def test_create_category(self):
        """Test creating a new category."""
        name = "Test Category"
        description = "Test category description"
        
        category = Category.objects.create(
            name=name, 
            slug=slugify(name),
            description=description
        )
        
        assert category.id is not None
        assert category.name == name
        assert category.slug == slugify(name)
        assert category.description == description
        assert category.created_at is not None
        assert category.updated_at is not None
    
    def test_read_category(self):
        """Test retrieving a category."""
        name = "Test Read Category"
        slug = slugify(name)
        description = "Category for testing reading"
        
        # Create the category first
        original = Category.objects.create(
            name=name, 
            slug=slug,
            description=description
        )
        
        # Retrieve the category by ID
        retrieved_by_id = Category.objects.get(id=original.id)
        assert retrieved_by_id.name == name
        assert retrieved_by_id.slug == slug
        
        # Retrieve the category by slug
        retrieved_by_slug = Category.objects.get(slug=slug)
        assert retrieved_by_slug.id == original.id
        assert retrieved_by_slug.name == name
    
    def test_update_category(self):
        """Test updating a category."""
        # Create a category
        name = "Original Category"
        category = Category.objects.create(
            name=name,
            slug=slugify(name),
            description="Original description"
        )
        
        # Update the category
        new_name = "Updated Category"
        new_description = "Updated description"
        
        # Store original timestamps to check that updated_at changes
        original_created_at = category.created_at
        original_updated_at = category.updated_at
        
        # Modify and save
        category.name = new_name
        category.slug = slugify(new_name)
        category.description = new_description
        category.save()
        
        # Refresh from database
        category.refresh_from_db()
        
        # Assertions
        assert category.name == new_name
        assert category.slug == slugify(new_name)
        assert category.description == new_description
        assert category.created_at == original_created_at  # Should not change
        assert category.updated_at > original_updated_at  # Should be updated
    
    def test_delete_category(self):
        """Test deleting a category."""
        # Create a category
        name = "Category to Delete"
        category = Category.objects.create(
            name=name,
            slug=slugify(name),
            description="This category will be deleted"
        )
        
        # Verify created
        category_id = category.id
        assert Category.objects.filter(id=category_id).exists()
        
        # Delete the category
        category.delete()
        
        # Verify deleted
        assert not Category.objects.filter(id=category_id).exists()
    
    def test_str_representation(self):
        """Test the string representation of a category."""
        name = "Test Category"
        category = Category.objects.create(
            name=name,
            slug=slugify(name),
            description="Description"
        )
        
        assert str(category) == name