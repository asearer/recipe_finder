import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.schemas import UserCreate, RecipeCreate


class TestAuthenticationEndpoints:
    """Test cases for authentication endpoints."""
    
    def test_signup_success(self, client: TestClient, db_session: Session):
        """Test successful user signup."""
        user_data = {
            "username": "newuser",
            "password": "newpass123"
        }
        
        response = client.post("/signup", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_signup_duplicate_username(self, client: TestClient, db_session: Session):
        """Test signup with duplicate username."""
        user_data = {
            "username": "duplicateuser",
            "password": "pass123"
        }
        
        # First signup should succeed
        response1 = client.post("/signup", json=user_data)
        assert response1.status_code == 200
        
        # Second signup with same username should fail
        response2 = client.post("/signup", json=user_data)
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Username already taken"
    
    def test_signup_missing_username(self, client: TestClient):
        """Test signup with missing username."""
        user_data = {"password": "pass123"}
        
        response = client.post("/signup", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_signup_missing_password(self, client: TestClient):
        """Test signup with missing password."""
        user_data = {"username": "testuser"}
        
        response = client.post("/signup", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, client: TestClient, db_session: Session):
        """Test successful user login."""
        # First create a user
        user_data = {
            "username": "loginuser",
            "password": "loginpass123"
        }
        client.post("/signup", json=user_data)
        
        # Then try to login
        response = client.post("/login", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_username(self, client: TestClient, db_session: Session):
        """Test login with invalid username."""
        user_data = {
            "username": "nonexistentuser",
            "password": "pass123"
        }
        
        response = client.post("/login", json=user_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_login_invalid_password(self, client: TestClient, db_session: Session):
        """Test login with invalid password."""
        # First create a user
        user_data = {
            "username": "loginuser2",
            "password": "correctpass123"
        }
        client.post("/signup", json=user_data)
        
        # Then try to login with wrong password
        wrong_password_data = {
            "username": "loginuser2",
            "password": "wrongpass123"
        }
        
        response = client.post("/login", json=wrong_password_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"


class TestRecipeEndpoints:
    """Test cases for recipe endpoints."""
    
    def test_create_recipe_authenticated(self, client: TestClient, test_user_token: str):
        """Test creating a recipe with authentication."""
        recipe_data = {
            "title": "Authenticated Recipe",
            "description": "A recipe created by authenticated user",
            "image_url": "https://example.com/image.jpg",
            "ingredients": ["tomato", "cheese", "bread"]
        }
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.post("/recipes", json=recipe_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == recipe_data["title"]
        assert data["description"] == recipe_data["description"]
        assert data["image_url"] == recipe_data["image_url"]
        assert len(data["ingredients"]) == 3
        assert data["owner_id"] is not None
    
    def test_create_recipe_unauthenticated(self, client: TestClient):
        """Test creating a recipe without authentication."""
        recipe_data = {
            "title": "Unauthenticated Recipe",
            "description": "A recipe created without authentication",
            "ingredients": ["tomato", "cheese"]
        }
        
        response = client.post("/recipes", json=recipe_data)
        
        assert response.status_code == 200  # Should still work, just no owner
        data = response.json()
        assert data["title"] == recipe_data["title"]
        assert data["owner_id"] is None
    
    def test_create_recipe_missing_title(self, client: TestClient):
        """Test creating a recipe with missing title."""
        recipe_data = {
            "description": "A recipe without title",
            "ingredients": ["tomato"]
        }
        
        response = client.post("/recipes", json=recipe_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_recipe_empty_ingredients(self, client: TestClient):
        """Test creating a recipe with empty ingredients."""
        recipe_data = {
            "title": "Recipe No Ingredients",
            "ingredients": []
        }
        
        response = client.post("/recipes", json=recipe_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ingredients"] == []
    
    def test_list_recipes_empty(self, client: TestClient):
        """Test listing recipes when none exist."""
        response = client.get("/recipes")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_list_recipes_with_data(self, client: TestClient, db_session: Session):
        """Test listing recipes with data."""
        # Create some recipes first
        recipe_data1 = {"title": "Recipe 1", "ingredients": ["ingredient1"]}
        recipe_data2 = {"title": "Recipe 2", "ingredients": ["ingredient2"]}
        
        client.post("/recipes", json=recipe_data1)
        client.post("/recipes", json=recipe_data2)
        
        response = client.get("/recipes")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        recipe_titles = [r["title"] for r in data]
        assert "Recipe 1" in recipe_titles
        assert "Recipe 2" in recipe_titles
    
    def test_list_recipes_with_pagination(self, client: TestClient, db_session: Session):
        """Test listing recipes with pagination."""
        # Create multiple recipes
        for i in range(5):
            recipe_data = {"title": f"Recipe {i+1}", "ingredients": [f"ingredient{i+1}"]}
            client.post("/recipes", json=recipe_data)
        
        # Test with skip and limit
        response = client.get("/recipes?skip=1&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Recipe 2"
        assert data[1]["title"] == "Recipe 3"
    
    def test_get_recipe_exists(self, client: TestClient, db_session: Session):
        """Test getting a recipe that exists."""
        # Create a recipe first
        recipe_data = {"title": "Test Recipe", "ingredients": ["test_ingredient"]}
        create_response = client.post("/recipes", json=recipe_data)
        recipe_id = create_response.json()["id"]
        
        # Get the recipe
        response = client.get(f"/recipes/{recipe_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recipe_id
        assert data["title"] == "Test Recipe"
    
    def test_get_recipe_not_exists(self, client: TestClient):
        """Test getting a recipe that doesn't exist."""
        response = client.get("/recipes/99999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Not found"
    
    def test_update_recipe_owner(self, client: TestClient, test_user_token: str, test_recipe):
        """Test updating a recipe by its owner."""
        recipe_data = {
            "title": "Updated Recipe Title",
            "description": "Updated description",
            "ingredients": ["new_ingredient1", "new_ingredient2"]
        }
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.put(f"/recipes/{test_recipe.id}", json=recipe_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == recipe_data["title"]
        assert data["description"] == recipe_data["description"]
        assert len(data["ingredients"]) == 2
    
    def test_update_recipe_not_owner(self, client: TestClient, test_recipe):
        """Test updating a recipe by someone who is not the owner."""
        # Create another user and get their token
        other_user_data = {"username": "otheruser", "password": "otherpass123"}
        client.post("/signup", json=other_user_data)
        
        login_response = client.post("/login", json=other_user_data)
        other_user_token = login_response.json()["access_token"]
        
        recipe_data = {
            "title": "Unauthorized Update",
            "ingredients": ["unauthorized_ingredient"]
        }
        
        headers = {"Authorization": f"Bearer {other_user_token}"}
        response = client.put(f"/recipes/{test_recipe.id}", json=recipe_data, headers=headers)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not allowed"
    
    def test_update_recipe_unauthenticated(self, client: TestClient, test_recipe):
        """Test updating a recipe without authentication."""
        recipe_data = {
            "title": "Unauthenticated Update",
            "ingredients": ["unauthorized_ingredient"]
        }
        
        response = client.put(f"/recipes/{test_recipe.id}", json=recipe_data)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not allowed"
    
    def test_update_recipe_not_exists(self, client: TestClient, test_user_token: str):
        """Test updating a recipe that doesn't exist."""
        recipe_data = {
            "title": "Updated Title",
            "ingredients": ["ingredient"]
        }
        
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.put("/recipes/99999", json=recipe_data, headers=headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Not found"
    
    def test_delete_recipe_owner(self, client: TestClient, test_user_token: str, test_recipe):
        """Test deleting a recipe by its owner."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.delete(f"/recipes/{test_recipe.id}", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["ok"] is True
        
        # Verify recipe is deleted
        get_response = client.get(f"/recipes/{test_recipe.id}")
        assert get_response.status_code == 404
    
    def test_delete_recipe_not_owner(self, client: TestClient, test_recipe):
        """Test deleting a recipe by someone who is not the owner."""
        # Create another user and get their token
        other_user_data = {"username": "otheruser2", "password": "otherpass123"}
        client.post("/signup", json=other_user_data)
        
        login_response = client.post("/login", json=other_user_data)
        other_user_token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {other_user_token}"}
        response = client.delete(f"/recipes/{test_recipe.id}", headers=headers)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not allowed"
    
    def test_delete_recipe_unauthenticated(self, client: TestClient, test_recipe):
        """Test deleting a recipe without authentication."""
        response = client.delete(f"/recipes/{test_recipe.id}")
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not allowed"
    
    def test_delete_recipe_not_exists(self, client: TestClient, test_user_token: str):
        """Test deleting a recipe that doesn't exist."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = client.delete("/recipes/99999", headers=headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Not found"


class TestSearchEndpoints:
    """Test cases for search endpoints."""
    
    def test_search_empty_query(self, client: TestClient):
        """Test search with empty query."""
        response = client.get("/search")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_search_single_ingredient(self, client: TestClient, db_session: Session):
        """Test search with single ingredient."""
        # Create a recipe with tomato
        recipe_data = {"title": "Tomato Recipe", "ingredients": ["tomato", "cheese"]}
        client.post("/recipes", json=recipe_data)
        
        response = client.get("/search?q=tomato")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Tomato Recipe"
    
    def test_search_multiple_ingredients(self, client: TestClient, db_session: Session):
        """Test search with multiple ingredients."""
        # Create recipes
        recipe1_data = {"title": "Pizza", "ingredients": ["tomato", "cheese", "dough"]}
        recipe2_data = {"title": "Pasta", "ingredients": ["tomato", "basil"]}
        recipe3_data = {"title": "Salad", "ingredients": ["lettuce", "cucumber"]}
        
        client.post("/recipes", json=recipe1_data)
        client.post("/recipes", json=recipe2_data)
        client.post("/recipes", json=recipe3_data)
        
        # Search for tomato (should find pizza and pasta)
        response = client.get("/search?q=tomato")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        recipe_titles = [r["title"] for r in data]
        assert "Pizza" in recipe_titles
        assert "Pasta" in recipe_titles
    
    def test_search_comma_separated_ingredients(self, client: TestClient, db_session: Session):
        """Test search with comma-separated ingredients."""
        # Create a recipe
        recipe_data = {"title": "Pizza", "ingredients": ["tomato", "cheese", "dough"]}
        client.post("/recipes", json=recipe_data)
        
        # Search with comma-separated ingredients
        response = client.get("/search?q=tomato,cheese")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Pizza"
    
    def test_search_no_matches(self, client: TestClient, db_session: Session):
        """Test search with no matching recipes."""
        # Create a recipe
        recipe_data = {"title": "Pizza", "ingredients": ["dough", "cheese"]}
        client.post("/recipes", json=recipe_data)
        
        # Search for different ingredients
        response = client.get("/search?q=tomato,basil")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_search_case_insensitive(self, client: TestClient, db_session: Session):
        """Test that search is case insensitive."""
        # Create a recipe
        recipe_data = {"title": "Pizza", "ingredients": ["Tomato", "Cheese"]}
        client.post("/recipes", json=recipe_data)
        
        # Search with lowercase
        response = client.get("/search?q=tomato")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Pizza"
    
    def test_search_whitespace_handling(self, client: TestClient, db_session: Session):
        """Test that search handles whitespace correctly."""
        # Create a recipe
        recipe_data = {"title": "Pizza", "ingredients": ["tomato", "cheese"]}
        client.post("/recipes", json=recipe_data)
        
        # Search with whitespace
        response = client.get("/search?q=  tomato  , cheese ")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Pizza"


class TestAuthenticationMiddleware:
    """Test cases for authentication middleware."""
    
    def test_get_current_user_valid_token(self, client: TestClient, test_user_token: str):
        """Test getting current user with valid token."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Use a recipe endpoint that requires authentication
        response = client.get("/recipes", headers=headers)
        
        assert response.status_code == 200
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = client.get("/recipes", headers=headers)
        
        assert response.status_code == 200  # Should still work, just no user
    
    def test_get_current_user_malformed_header(self, client: TestClient):
        """Test getting current user with malformed authorization header."""
        headers = {"Authorization": "InvalidScheme token_here"}
        
        response = client.get("/recipes", headers=headers)
        
        assert response.status_code == 200  # Should still work, just no user
    
    def test_get_current_user_no_header(self, client: TestClient):
        """Test getting current user with no authorization header."""
        response = client.get("/recipes")
        
        assert response.status_code == 200  # Should still work, just no user
    
    def test_get_current_user_empty_token(self, client: TestClient):
        """Test getting current user with empty token."""
        headers = {"Authorization": "Bearer "}
        
        response = client.get("/recipes", headers=headers)
        
        assert response.status_code == 200  # Should still work, just no user


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_not_found(self, client: TestClient):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
    
    def test_422_validation_error(self, client: TestClient):
        """Test 422 error for validation failures."""
        # Try to create user with invalid data
        user_data = {"username": "", "password": ""}
        
        response = client.post("/signup", json=user_data)
        
        assert response.status_code == 422
    
    def test_400_bad_request(self, client: TestClient, db_session: Session):
        """Test 400 error for bad requests."""
        # Try to signup with duplicate username
        user_data = {"username": "duplicateuser", "password": "pass123"}
        
        # First signup
        client.post("/signup", json=user_data)
        
        # Second signup with same username
        response = client.post("/signup", json=user_data)
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already taken"
    
    def test_401_unauthorized(self, client: TestClient, db_session: Session):
        """Test 401 error for unauthorized access."""
        # Try to login with invalid credentials
        user_data = {"username": "nonexistent", "password": "wrongpass"}
        
        response = client.post("/login", json=user_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    
    def test_403_forbidden(self, client: TestClient, test_recipe):
        """Test 403 error for forbidden access."""
        # Create another user
        other_user_data = {"username": "otheruser3", "password": "otherpass123"}
        client.post("/signup", json=other_user_data)
        
        # Try to update recipe owned by different user
        recipe_data = {"title": "Unauthorized", "ingredients": ["ingredient"]}
        
        response = client.put(f"/recipes/{test_recipe.id}", json=recipe_data)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not allowed"
