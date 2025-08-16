import pytest
from sqlalchemy.orm import Session
from backend.models import User, Recipe, Ingredient


class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, db_session: Session):
        """Test creating a user."""
        user = User(username="testuser", hashed_password="hashedpass123")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.hashed_password == "hashedpass123"
    
    def test_user_unique_username(self, db_session: Session):
        """Test that usernames must be unique."""
        user1 = User(username="testuser", hashed_password="hashedpass123")
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(username="testuser", hashed_password="hashedpass456")
        db_session.add(user2)
        
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            db_session.commit()
    
    def test_user_username_not_null(self, db_session: Session):
        """Test that username cannot be null."""
        user = User(hashed_password="hashedpass123")
        db_session.add(user)
        
        with pytest.raises(Exception):
            db_session.commit()


class TestRecipeModel:
    """Test cases for Recipe model."""
    
    def test_create_recipe(self, db_session: Session):
        """Test creating a recipe."""
        user = User(username="testuser", hashed_password="hashedpass123")
        db_session.add(user)
        db_session.commit()
        
        recipe = Recipe(
            title="Test Recipe",
            description="A test recipe",
            image_url="https://example.com/image.jpg",
            owner_id=user.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        assert recipe.id is not None
        assert recipe.title == "Test Recipe"
        assert recipe.description == "A test recipe"
        assert recipe.image_url == "https://example.com/image.jpg"
        assert recipe.owner_id == user.id
        assert recipe.owner == user
    
    def test_recipe_title_not_null(self, db_session: Session):
        """Test that recipe title cannot be null."""
        recipe = Recipe(description="A test recipe")
        db_session.add(recipe)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_recipe_owner_relationship(self, db_session: Session):
        """Test recipe owner relationship."""
        user = User(username="testuser", hashed_password="hashedpass123")
        db_session.add(user)
        db_session.commit()
        
        recipe = Recipe(title="Test Recipe", owner_id=user.id)
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        assert recipe.owner == user
        assert user in db_session.query(User).all()
    
    def test_recipe_ingredients_relationship(self, db_session: Session):
        """Test recipe ingredients relationship."""
        recipe = Recipe(title="Test Recipe")
        db_session.add(recipe)
        
        ingredient1 = Ingredient(name="tomato")
        ingredient2 = Ingredient(name="cheese")
        db_session.add_all([ingredient1, ingredient2])
        db_session.commit()
        
        recipe.ingredients.append(ingredient1)
        recipe.ingredients.append(ingredient2)
        db_session.commit()
        db_session.refresh(recipe)
        
        assert len(recipe.ingredients) == 2
        assert ingredient1 in recipe.ingredients
        assert ingredient2 in recipe.ingredients


class TestIngredientModel:
    """Test cases for Ingredient model."""
    
    def test_create_ingredient(self, db_session: Session):
        """Test creating an ingredient."""
        ingredient = Ingredient(name="tomato")
        db_session.add(ingredient)
        db_session.commit()
        db_session.refresh(ingredient)
        
        assert ingredient.id is not None
        assert ingredient.name == "tomato"
    
    def test_ingredient_name_not_null(self, db_session: Session):
        """Test that ingredient name cannot be null."""
        ingredient = Ingredient()
        db_session.add(ingredient)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_ingredient_unique_name(self, db_session: Session):
        """Test that ingredient names must be unique."""
        ingredient1 = Ingredient(name="tomato")
        db_session.add(ingredient1)
        db_session.commit()
        
        ingredient2 = Ingredient(name="tomato")
        db_session.add(ingredient2)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_ingredient_recipes_relationship(self, db_session: Session):
        """Test ingredient recipes relationship."""
        ingredient = Ingredient(name="tomato")
        db_session.add(ingredient)
        
        recipe1 = Recipe(title="Recipe 1")
        recipe2 = Recipe(title="Recipe 2")
        db_session.add_all([recipe1, recipe2])
        db_session.commit()
        
        ingredient.recipes.append(recipe1)
        ingredient.recipes.append(recipe2)
        db_session.commit()
        db_session.refresh(ingredient)
        
        assert len(ingredient.recipes) == 2
        assert recipe1 in ingredient.recipes
        assert recipe2 in ingredient.recipes


class TestManyToManyRelationship:
    """Test cases for many-to-many relationships."""
    
    def test_recipe_ingredient_many_to_many(self, db_session: Session):
        """Test many-to-many relationship between recipes and ingredients."""
        recipe = Recipe(title="Pizza")
        db_session.add(recipe)
        
        tomato = Ingredient(name="tomato")
        cheese = Ingredient(name="cheese")
        dough = Ingredient(name="dough")
        db_session.add_all([tomato, cheese, dough])
        db_session.commit()
        
        recipe.ingredients.extend([tomato, cheese, dough])
        db_session.commit()
        db_session.refresh(recipe)
        
        assert len(recipe.ingredients) == 3
        assert tomato in recipe.ingredients
        assert cheese in recipe.ingredients
        assert dough in recipe.ingredients
        
        # Test reverse relationship
        assert recipe in tomato.recipes
        assert recipe in cheese.recipes
        assert recipe in dough.recipes
    
    def test_remove_ingredient_from_recipe(self, db_session: Session):
        """Test removing an ingredient from a recipe."""
        recipe = Recipe(title="Pizza")
        db_session.add(recipe)
        
        tomato = Ingredient(name="tomato")
        cheese = Ingredient(name="cheese")
        db_session.add_all([tomato, cheese])
        db_session.commit()
        
        recipe.ingredients.extend([tomato, cheese])
        db_session.commit()
        
        assert len(recipe.ingredients) == 2
        
        # Remove tomato
        recipe.ingredients.remove(tomato)
        db_session.commit()
        db_session.refresh(recipe)
        
        assert len(recipe.ingredients) == 1
        assert cheese in recipe.ingredients
        assert tomato not in recipe.ingredients
