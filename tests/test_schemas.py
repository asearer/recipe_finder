import pytest
from pydantic import ValidationError
from backend.schemas import (
    UserCreate, Token, IngredientBase, IngredientCreate, 
    Ingredient, RecipeBase, RecipeCreate, Recipe
)


class TestUserCreateSchema:
    """Test cases for UserCreate schema."""
    
    def test_valid_user_create(self):
        """Test creating a valid user."""
        user_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        user = UserCreate(**user_data)
        
        assert user.username == "testuser"
        assert user.password == "testpass123"
    
    def test_user_create_missing_username(self):
        """Test that username is required."""
        with pytest.raises(ValidationError):
            UserCreate(password="testpass123")
    
    def test_user_create_missing_password(self):
        """Test that password is required."""
        with pytest.raises(ValidationError):
            UserCreate(username="testuser")
    
    def test_user_create_empty_username(self):
        """Test that username cannot be empty."""
        with pytest.raises(ValidationError):
            UserCreate(username="", password="testpass123")
    
    def test_user_create_empty_password(self):
        """Test that password cannot be empty."""
        with pytest.raises(ValidationError):
            UserCreate(username="testuser", password="")


class TestTokenSchema:
    """Test cases for Token schema."""
    
    def test_valid_token(self):
        """Test creating a valid token."""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        token = Token(**token_data)
        
        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.token_type == "bearer"
    
    def test_token_default_type(self):
        """Test that token_type defaults to 'bearer'."""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        token = Token(**token_data)
        
        assert token.token_type == "bearer"
    
    def test_token_missing_access_token(self):
        """Test that access_token is required."""
        with pytest.raises(ValidationError):
            Token(token_type="bearer")


class TestIngredientBaseSchema:
    """Test cases for IngredientBase schema."""
    
    def test_valid_ingredient_base(self):
        """Test creating a valid ingredient base."""
        ingredient_data = {"name": "tomato"}
        ingredient = IngredientBase(**ingredient_data)
        
        assert ingredient.name == "tomato"
    
    def test_ingredient_base_missing_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            IngredientBase()
    
    def test_ingredient_base_empty_name(self):
        """Test that name cannot be empty."""
        with pytest.raises(ValidationError):
            IngredientBase(name="")


class TestIngredientCreateSchema:
    """Test cases for IngredientCreate schema."""
    
    def test_valid_ingredient_create(self):
        """Test creating a valid ingredient create."""
        ingredient_data = {"name": "tomato"}
        ingredient = IngredientCreate(**ingredient_data)
        
        assert ingredient.name == "tomato"
    
    def test_ingredient_create_inherits_from_base(self):
        """Test that IngredientCreate inherits from IngredientBase."""
        ingredient_data = {"name": "tomato"}
        ingredient = IngredientCreate(**ingredient_data)
        
        assert isinstance(ingredient, IngredientBase)
        assert ingredient.name == "tomato"


class TestIngredientSchema:
    """Test cases for Ingredient schema."""
    
    def test_valid_ingredient(self):
        """Test creating a valid ingredient."""
        ingredient_data = {
            "id": 1,
            "name": "tomato"
        }
        ingredient = Ingredient(**ingredient_data)
        
        assert ingredient.id == 1
        assert ingredient.name == "tomato"
    
    def test_ingredient_missing_id(self):
        """Test that id is required."""
        with pytest.raises(ValidationError):
            Ingredient(name="tomato")
    
    def test_ingredient_missing_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            Ingredient(id=1)


class TestRecipeBaseSchema:
    """Test cases for RecipeBase schema."""
    
    def test_valid_recipe_base(self):
        """Test creating a valid recipe base."""
        recipe_data = {
            "title": "Pizza",
            "description": "A delicious pizza",
            "image_url": "https://example.com/pizza.jpg"
        }
        recipe = RecipeBase(**recipe_data)
        
        assert recipe.title == "Pizza"
        assert recipe.description == "A delicious pizza"
        assert recipe.image_url == "https://example.com/pizza.jpg"
    
    def test_recipe_base_minimal(self):
        """Test creating a recipe with only required fields."""
        recipe_data = {"title": "Pizza"}
        recipe = RecipeBase(**recipe_data)
        
        assert recipe.title == "Pizza"
        assert recipe.description is None
        assert recipe.image_url is None
    
    def test_recipe_base_missing_title(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            RecipeBase(description="A delicious pizza")
    
    def test_recipe_base_empty_title(self):
        """Test that title cannot be empty."""
        with pytest.raises(ValidationError):
            RecipeBase(title="")
    
    def test_recipe_base_none_description(self):
        """Test that description can be None."""
        recipe_data = {
            "title": "Pizza",
            "description": None
        }
        recipe = RecipeBase(**recipe_data)
        
        assert recipe.description is None
    
    def test_recipe_base_none_image_url(self):
        """Test that image_url can be None."""
        recipe_data = {
            "title": "Pizza",
            "image_url": None
        }
        recipe = RecipeBase(**recipe_data)
        
        assert recipe.image_url is None


class TestRecipeCreateSchema:
    """Test cases for RecipeCreate schema."""
    
    def test_valid_recipe_create(self):
        """Test creating a valid recipe create."""
        recipe_data = {
            "title": "Pizza",
            "description": "A delicious pizza",
            "image_url": "https://example.com/pizza.jpg",
            "ingredients": ["tomato", "cheese", "dough"]
        }
        recipe = RecipeCreate(**recipe_data)
        
        assert recipe.title == "Pizza"
        assert recipe.description == "A delicious pizza"
        assert recipe.image_url == "https://example.com/pizza.jpg"
        assert recipe.ingredients == ["tomato", "cheese", "dough"]
    
    def test_recipe_create_empty_ingredients(self):
        """Test creating a recipe with empty ingredients list."""
        recipe_data = {
            "title": "Pizza",
            "ingredients": []
        }
        recipe = RecipeCreate(**recipe_data)
        
        assert recipe.ingredients == []
    
    def test_recipe_create_no_ingredients(self):
        """Test creating a recipe without ingredients."""
        recipe_data = {"title": "Pizza"}
        recipe = RecipeCreate(**recipe_data)
        
        assert recipe.ingredients == []
    
    def test_recipe_create_inherits_from_base(self):
        """Test that RecipeCreate inherits from RecipeBase."""
        recipe_data = {"title": "Pizza"}
        recipe = RecipeCreate(**recipe_data)
        
        assert isinstance(recipe, RecipeBase)
        assert recipe.title == "Pizza"


class TestRecipeSchema:
    """Test cases for Recipe schema."""
    
    def test_valid_recipe(self):
        """Test creating a valid recipe."""
        recipe_data = {
            "id": 1,
            "title": "Pizza",
            "description": "A delicious pizza",
            "image_url": "https://example.com/pizza.jpg",
            "ingredients": [
                {"id": 1, "name": "tomato"},
                {"id": 2, "name": "cheese"}
            ],
            "owner_id": 1
        }
        recipe = Recipe(**recipe_data)
        
        assert recipe.id == 1
        assert recipe.title == "Pizza"
        assert recipe.description == "A delicious pizza"
        assert recipe.image_url == "https://example.com/pizza.jpg"
        assert len(recipe.ingredients) == 2
        assert recipe.owner_id == 1
    
    def test_recipe_minimal(self):
        """Test creating a recipe with minimal fields."""
        recipe_data = {
            "id": 1,
            "title": "Pizza",
            "ingredients": []
        }
        recipe = Recipe(**recipe_data)
        
        assert recipe.id == 1
        assert recipe.title == "Pizza"
        assert recipe.description is None
        assert recipe.image_url is None
        assert recipe.ingredients == []
        assert recipe.owner_id is None
    
    def test_recipe_missing_id(self):
        """Test that id is required."""
        with pytest.raises(ValidationError):
            Recipe(title="Pizza", ingredients=[])
    
    def test_recipe_missing_title(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            Recipe(id=1, ingredients=[])
    
    def test_recipe_missing_ingredients(self):
        """Test that ingredients is required."""
        with pytest.raises(ValidationError):
            Recipe(id=1, title="Pizza")
    
    def test_recipe_none_owner_id(self):
        """Test that owner_id can be None."""
        recipe_data = {
            "id": 1,
            "title": "Pizza",
            "ingredients": [],
            "owner_id": None
        }
        recipe = Recipe(**recipe_data)
        
        assert recipe.owner_id is None
