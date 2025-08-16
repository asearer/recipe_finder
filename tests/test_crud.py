import pytest
from sqlalchemy.orm import Session
from backend import crud, models
from backend.schemas import UserCreate


class TestUserCRUD:
    """Test cases for user CRUD operations."""
    
    def test_get_user_by_username_exists(self, db_session: Session):
        """Test getting a user that exists."""
        # Create a user first
        user = models.User(username="testuser", hashed_password="hashedpass123")
        db_session.add(user)
        db_session.commit()
        
        # Get the user
        found_user = crud.get_user_by_username(db_session, "testuser")
        
        assert found_user is not None
        assert found_user.username == "testuser"
        assert found_user.hashed_password == "hashedpass123"
    
    def test_get_user_by_username_not_exists(self, db_session: Session):
        """Test getting a user that doesn't exist."""
        found_user = crud.get_user_by_username(db_session, "nonexistentuser")
        
        assert found_user is None
    
    def test_get_user_by_username_case_sensitive(self, db_session: Session):
        """Test that username lookup is case sensitive."""
        user = models.User(username="TestUser", hashed_password="hashedpass123")
        db_session.add(user)
        db_session.commit()
        
        # Try to get with different case
        found_user = crud.get_user_by_username(db_session, "testuser")
        
        assert found_user is None
    
    def test_create_user(self, db_session: Session):
        """Test creating a new user."""
        username = "newuser"
        hashed_password = "hashedpass123"
        
        user = crud.create_user(db_session, username, hashed_password)
        
        assert user.id is not None
        assert user.username == username
        assert user.hashed_password == hashed_password
        
        # Verify user was saved to database
        db_session.refresh(user)
        assert user.id is not None
    
    def test_create_user_duplicate_username(self, db_session: Session):
        """Test creating a user with duplicate username."""
        username = "duplicateuser"
        hashed_password1 = "hashedpass123"
        hashed_password2 = "hashedpass456"
        
        # Create first user
        user1 = crud.create_user(db_session, username, hashed_password1)
        assert user1.username == username
        
        # Try to create second user with same username
        with pytest.raises(Exception):  # Should raise integrity error
            crud.create_user(db_session, username, hashed_password2)


class TestIngredientCRUD:
    """Test cases for ingredient CRUD operations."""
    
    def test_create_or_get_ingredient_new(self, db_session: Session):
        """Test creating a new ingredient."""
        ingredient_name = "newingredient"
        
        ingredient = crud.create_or_get_ingredient(db_session, ingredient_name)
        
        assert ingredient.id is not None
        assert ingredient.name == ingredient_name.lower()
        assert ingredient.name == "newingredient"
    
    def test_create_or_get_ingredient_existing(self, db_session: Session):
        """Test getting an existing ingredient."""
        ingredient_name = "existingingredient"
        
        # Create ingredient first
        ingredient1 = crud.create_or_get_ingredient(db_session, ingredient_name)
        first_id = ingredient1.id
        
        # Get the same ingredient again
        ingredient2 = crud.create_or_get_ingredient(db_session, ingredient_name)
        
        assert ingredient2.id == first_id
        assert ingredient2.name == ingredient_name.lower()
    
    def test_create_or_get_ingredient_whitespace_trimming(self, db_session: Session):
        """Test that ingredient names are trimmed of whitespace."""
        ingredient_name = "  ingredient with spaces  "
        
        ingredient = crud.create_or_get_ingredient(db_session, ingredient_name)
        
        assert ingredient.name == "ingredient with spaces"
    
    def test_create_or_get_ingredient_case_insensitive(self, db_session: Session):
        """Test that ingredient names are stored in lowercase."""
        ingredient_name = "INGREDIENT"
        
        ingredient = crud.create_or_get_ingredient(db_session, ingredient_name)
        
        assert ingredient.name == "ingredient"
    
    def test_create_or_get_ingredient_empty_string(self, db_session: Session):
        """Test handling of empty ingredient name."""
        ingredient_name = ""
        
        ingredient = crud.create_or_get_ingredient(db_session, ingredient_name)
        
        assert ingredient.name == ""
    
    def test_create_or_get_ingredient_special_characters(self, db_session: Session):
        """Test ingredient names with special characters."""
        ingredient_name = "ingredient-123_456"
        
        ingredient = crud.create_or_get_ingredient(db_session, ingredient_name)
        
        assert ingredient.name == "ingredient-123_456"


class TestRecipeCRUD:
    """Test cases for recipe CRUD operations."""
    
    def test_create_recipe_basic(self, db_session: Session):
        """Test creating a basic recipe."""
        title = "Test Recipe"
        description = "A test recipe"
        image_url = "https://example.com/image.jpg"
        ingredient_names = ["tomato", "cheese"]
        owner_id = None
        
        recipe = crud.create_recipe(db_session, title, description, image_url, ingredient_names, owner_id)
        
        assert recipe.id is not None
        assert recipe.title == title
        assert recipe.description == description
        assert recipe.image_url == image_url
        assert recipe.owner_id == owner_id
        assert len(recipe.ingredients) == 2
        
        # Check ingredients were created
        ingredient_names_lower = [name.lower() for name in ingredient_names]
        for ingredient in recipe.ingredients:
            assert ingredient.name in ingredient_names_lower
    
    def test_create_recipe_with_owner(self, db_session: Session):
        """Test creating a recipe with an owner."""
        # Create user first
        user = models.User(username="testuser", hashed_password="hashedpass123")
        db_session.add(user)
        db_session.commit()
        
        title = "Owned Recipe"
        description = "A recipe with an owner"
        image_url = None
        ingredient_names = ["flour", "water"]
        owner_id = user.id
        
        recipe = crud.create_recipe(db_session, title, description, image_url, ingredient_names, owner_id)
        
        assert recipe.owner_id == user.id
        assert recipe.owner == user
    
    def test_create_recipe_no_ingredients(self, db_session: Session):
        """Test creating a recipe with no ingredients."""
        title = "Recipe No Ingredients"
        description = None
        image_url = None
        ingredient_names = []
        owner_id = None
        
        recipe = crud.create_recipe(db_session, title, description, image_url, ingredient_names, owner_id)
        
        assert recipe.ingredients == []
    
    def test_create_recipe_duplicate_ingredients(self, db_session: Session):
        """Test creating a recipe with duplicate ingredient names."""
        title = "Recipe Duplicate Ingredients"
        description = None
        image_url = None
        ingredient_names = ["tomato", "tomato", "cheese"]
        owner_id = None
        
        recipe = crud.create_recipe(db_session, title, description, image_url, ingredient_names, owner_id)
        
        # Should create unique ingredients
        unique_ingredient_names = set(name.lower() for name in ingredient_names)
        assert len(recipe.ingredients) == len(unique_ingredient_names)
    
    def test_get_recipe_exists(self, db_session: Session):
        """Test getting a recipe that exists."""
        # Create a recipe first
        recipe = models.Recipe(title="Test Recipe")
        db_session.add(recipe)
        db_session.commit()
        
        found_recipe = crud.get_recipe(db_session, recipe.id)
        
        assert found_recipe is not None
        assert found_recipe.id == recipe.id
        assert found_recipe.title == "Test Recipe"
    
    def test_get_recipe_not_exists(self, db_session: Session):
        """Test getting a recipe that doesn't exist."""
        found_recipe = crud.get_recipe(db_session, 99999)
        
        assert found_recipe is None
    
    def test_list_recipes_empty(self, db_session: Session):
        """Test listing recipes when database is empty."""
        recipes = crud.list_recipes(db_session)
        
        assert recipes == []
    
    def test_list_recipes_with_data(self, db_session: Session):
        """Test listing recipes with data."""
        # Create multiple recipes
        recipe1 = models.Recipe(title="Recipe 1")
        recipe2 = models.Recipe(title="Recipe 2")
        recipe3 = models.Recipe(title="Recipe 3")
        db_session.add_all([recipe1, recipe2, recipe3])
        db_session.commit()
        
        recipes = crud.list_recipes(db_session)
        
        assert len(recipes) == 3
        recipe_titles = [r.title for r in recipes]
        assert "Recipe 1" in recipe_titles
        assert "Recipe 2" in recipe_titles
        assert "Recipe 3" in recipe_titles
    
    def test_list_recipes_with_skip(self, db_session: Session):
        """Test listing recipes with skip parameter."""
        # Create multiple recipes
        recipe1 = models.Recipe(title="Recipe 1")
        recipe2 = models.Recipe(title="Recipe 2")
        recipe3 = models.Recipe(title="Recipe 3")
        db_session.add_all([recipe1, recipe2, recipe3])
        db_session.commit()
        
        recipes = crud.list_recipes(db_session, skip=1)
        
        assert len(recipes) == 2
        assert recipes[0].title == "Recipe 2"
        assert recipes[1].title == "Recipe 3"
    
    def test_list_recipes_with_limit(self, db_session: Session):
        """Test listing recipes with limit parameter."""
        # Create multiple recipes
        recipe1 = models.Recipe(title="Recipe 1")
        recipe2 = models.Recipe(title="Recipe 2")
        recipe3 = models.Recipe(title="Recipe 3")
        db_session.add_all([recipe1, recipe2, recipe3])
        db_session.commit()
        
        recipes = crud.list_recipes(db_session, limit=2)
        
        assert len(recipes) == 2
        assert recipes[0].title == "Recipe 1"
        assert recipes[1].title == "Recipe 2"
    
    def test_list_recipes_with_skip_and_limit(self, db_session: Session):
        """Test listing recipes with both skip and limit parameters."""
        # Create multiple recipes
        recipe1 = models.Recipe(title="Recipe 1")
        recipe2 = models.Recipe(title="Recipe 2")
        recipe3 = models.Recipe(title="Recipe 3")
        recipe4 = models.Recipe(title="Recipe 4")
        db_session.add_all([recipe1, recipe2, recipe3, recipe4])
        db_session.commit()
        
        recipes = crud.list_recipes(db_session, skip=1, limit=2)
        
        assert len(recipes) == 2
        assert recipes[0].title == "Recipe 2"
        assert recipes[1].title == "Recipe 3"


class TestRecipeSearch:
    """Test cases for recipe search functionality."""
    
    def test_search_recipes_by_ingredients_empty_query(self, db_session: Session):
        """Test search with empty ingredient list."""
        recipes = crud.search_recipes_by_ingredients(db_session, [])
        
        assert recipes == []
    
    def test_search_recipes_by_ingredients_no_matches(self, db_session: Session):
        """Test search with no matching recipes."""
        # Create a recipe with different ingredients
        recipe = crud.create_recipe(
            db_session, "Pizza", "A pizza", None, ["dough", "cheese"], None
        )
        
        # Search for different ingredients
        recipes = crud.search_recipes_by_ingredients(db_session, ["tomato", "basil"])
        
        assert recipes == []
    
    def test_search_recipes_by_ingredients_single_match(self, db_session: Session):
        """Test search with single ingredient match."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Pizza", "A pizza", None, ["tomato", "cheese", "dough"], None
        )
        
        # Search for one ingredient
        recipes = crud.search_recipes_by_ingredients(db_session, ["tomato"])
        
        assert len(recipes) == 1
        assert recipes[0].title == "Pizza"
    
    def test_search_recipes_by_ingredients_multiple_matches(self, db_session: Session):
        """Test search with multiple ingredient matches."""
        # Create recipes
        recipe1 = crud.create_recipe(
            db_session, "Pizza", "A pizza", None, ["tomato", "cheese", "dough"], None
        )
        recipe2 = crud.create_recipe(
            db_session, "Pasta", "A pasta", None, ["tomato", "basil"], None
        )
        recipe3 = crud.create_recipe(
            db_session, "Salad", "A salad", None, ["lettuce", "cucumber"], None
        )
        
        # Search for tomato (should find pizza and pasta)
        recipes = crud.search_recipes_by_ingredients(db_session, ["tomato"])
        
        assert len(recipes) == 2
        recipe_titles = [r.title for r in recipes]
        assert "Pizza" in recipe_titles
        assert "Pasta" in recipe_titles
        assert "Salad" not in recipe_titles
    
    def test_search_recipes_by_ingredients_all_ingredients(self, db_session: Session):
        """Test search requiring all specified ingredients."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Pizza", "A pizza", None, ["tomato", "cheese", "dough"], None
        )
        
        # Search for all ingredients (should find the recipe)
        recipes = crud.search_recipes_by_ingredients(db_session, ["tomato", "cheese"])
        
        assert len(recipes) == 1
        assert recipes[0].title == "Pizza"
    
    def test_search_recipes_by_ingredients_case_insensitive(self, db_session: Session):
        """Test that ingredient search is case insensitive."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Pizza", "A pizza", None, ["Tomato", "Cheese"], None
        )
        
        # Search with lowercase
        recipes = crud.search_recipes_by_ingredients(db_session, ["tomato"])
        
        assert len(recipes) == 1
        assert recipes[0].title == "Pizza"
    
    def test_search_recipes_by_ingredients_whitespace_handling(self, db_session: Session):
        """Test that ingredient search handles whitespace correctly."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Pizza", "A pizza", None, ["tomato", "cheese"], None
        )
        
        # Search with whitespace
        recipes = crud.search_recipes_by_ingredients(db_session, ["  tomato  ", " cheese "])
        
        assert len(recipes) == 1
        assert recipes[0].title == "Pizza"


class TestRecipeUpdate:
    """Test cases for recipe update functionality."""
    
    def test_update_recipe_title(self, db_session: Session):
        """Test updating recipe title."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Old Title", "Old description", None, ["ingredient1"], None
        )
        
        # Update title
        updated_recipe = crud.update_recipe(
            db_session, recipe, "New Title", None, None, None
        )
        
        assert updated_recipe.title == "New Title"
        assert updated_recipe.description == "Old description"  # Unchanged
    
    def test_update_recipe_description(self, db_session: Session):
        """Test updating recipe description."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Title", "Old description", None, ["ingredient1"], None
        )
        
        # Update description
        updated_recipe = crud.update_recipe(
            db_session, recipe, None, "New description", None, None
        )
        
        assert updated_recipe.description == "New description"
        assert updated_recipe.title == "Title"  # Unchanged
    
    def test_update_recipe_image_url(self, db_session: Session):
        """Test updating recipe image URL."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Title", "Description", "old_url.jpg", ["ingredient1"], None
        )
        
        # Update image URL
        updated_recipe = crud.update_recipe(
            db_session, recipe, None, None, "new_url.jpg", None
        )
        
        assert updated_recipe.image_url == "new_url.jpg"
        assert updated_recipe.title == "Title"  # Unchanged
    
    def test_update_recipe_ingredients(self, db_session: Session):
        """Test updating recipe ingredients."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Title", "Description", None, ["old_ingredient"], None
        )
        
        # Update ingredients
        new_ingredients = ["new_ingredient1", "new_ingredient2"]
        updated_recipe = crud.update_recipe(
            db_session, recipe, None, None, None, new_ingredients
        )
        
        assert len(updated_recipe.ingredients) == 2
        ingredient_names = [ing.name for ing in updated_recipe.ingredients]
        assert "new_ingredient1" in ingredient_names
        assert "new_ingredient2" in ingredient_names
        assert "old_ingredient" not in ingredient_names
    
    def test_update_recipe_multiple_fields(self, db_session: Session):
        """Test updating multiple recipe fields at once."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Old Title", "Old description", "old_url.jpg", ["old_ingredient"], None
        )
        
        # Update multiple fields
        updated_recipe = crud.update_recipe(
            db_session, recipe, "New Title", "New description", "new_url.jpg", ["new_ingredient"]
        )
        
        assert updated_recipe.title == "New Title"
        assert updated_recipe.description == "New description"
        assert updated_recipe.image_url == "new_url.jpg"
        assert len(updated_recipe.ingredients) == 1
        assert updated_recipe.ingredients[0].name == "new_ingredient"
    
    def test_update_recipe_no_changes(self, db_session: Session):
        """Test updating recipe with no changes."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Title", "Description", "url.jpg", ["ingredient"], None
        )
        
        # Update with None values (no changes)
        updated_recipe = crud.update_recipe(
            db_session, recipe, None, None, None, None
        )
        
        assert updated_recipe.title == "Title"
        assert updated_recipe.description == "Description"
        assert updated_recipe.image_url == "url.jpg"
        assert len(updated_recipe.ingredients) == 1


class TestRecipeDelete:
    """Test cases for recipe deletion."""
    
    def test_delete_recipe(self, db_session: Session):
        """Test deleting a recipe."""
        # Create a recipe
        recipe = crud.create_recipe(
            db_session, "Title", "Description", None, ["ingredient"], None
        )
        recipe_id = recipe.id
        
        # Delete the recipe
        crud.delete_recipe(db_session, recipe)
        
        # Verify it's gone
        found_recipe = crud.get_recipe(db_session, recipe_id)
        assert found_recipe is None
    
    def test_delete_recipe_with_ingredients(self, db_session: Session):
        """Test deleting a recipe with ingredients."""
        # Create a recipe with ingredients
        recipe = crud.create_recipe(
            db_session, "Title", "Description", None, ["ingredient1", "ingredient2"], None
        )
        
        # Delete the recipe
        crud.delete_recipe(db_session, recipe)
        
        # Recipe should be gone
        found_recipe = crud.get_recipe(db_session, recipe.id)
        assert found_recipe is None
        
        # Ingredients should still exist (they're not deleted)
        ingredients = db_session.query(models.Ingredient).all()
        assert len(ingredients) == 2
