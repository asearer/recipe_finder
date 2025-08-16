import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestCompleteUserWorkflow:
    """Test complete user workflow from signup to recipe management."""
    
    def test_complete_user_workflow(self, client: TestClient, db_session: Session):
        """Test complete user workflow: signup -> login -> create recipe -> update -> delete."""
        # 1. User signup
        user_data = {
            "username": "workflowuser",
            "password": "workflowpass123"
        }
        
        signup_response = client.post("/signup", json=user_data)
        assert signup_response.status_code == 200
        signup_data = signup_response.json()
        assert "access_token" in signup_data
        
        # 2. User login
        login_response = client.post("/login", json=user_data)
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        
        # 3. Create recipe with authentication
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        recipe_data = {
            "title": "Workflow Recipe",
            "description": "A recipe created during workflow test",
            "ingredients": ["tomato", "cheese", "bread"]
        }
        
        create_response = client.post("/recipes", json=recipe_data, headers=headers)
        assert create_response.status_code == 200
        created_recipe = create_response.json()
        assert created_recipe["title"] == recipe_data["title"]
        assert created_recipe["owner_id"] is not None
        
        # 4. Update the recipe
        update_data = {
            "title": "Updated Workflow Recipe",
            "description": "Updated description",
            "ingredients": ["tomato", "cheese", "bread", "basil"]
        }
        
        update_response = client.put(
            f"/recipes/{created_recipe['id']}", 
            json=update_data, 
            headers=headers
        )
        assert update_response.status_code == 200
        updated_recipe = update_response.json()
        assert updated_recipe["title"] == update_data["title"]
        assert updated_recipe["description"] == update_data["description"]
        assert len(updated_recipe["ingredients"]) == 4
        
        # 5. Delete the recipe
        delete_response = client.delete(
            f"/recipes/{created_recipe['id']}", 
            headers=headers
        )
        assert delete_response.status_code == 200
        
        # 6. Verify recipe is deleted
        get_response = client.get(f"/recipes/{created_recipe['id']}")
        assert get_response.status_code == 404


class TestRecipeSearchWorkflow:
    """Test complete recipe search workflow."""
    
    def test_recipe_search_workflow(self, client: TestClient, db_session: Session):
        """Test complete recipe search workflow: create recipes -> search -> verify results."""
        # 1. Create multiple recipes with different ingredients
        recipes_data = [
            {
                "title": "Margherita Pizza",
                "description": "Classic Italian pizza",
                "ingredients": ["tomato", "mozzarella", "basil", "dough"]
            },
            {
                "title": "Caprese Salad",
                "description": "Fresh Italian salad",
                "ingredients": ["tomato", "mozzarella", "basil", "olive oil"]
            },
            {
                "title": "Pasta Carbonara",
                "description": "Creamy pasta dish",
                "ingredients": ["pasta", "eggs", "pecorino", "guanciale"]
            },
            {
                "title": "Greek Salad",
                "description": "Mediterranean salad",
                "ingredients": ["cucumber", "tomato", "olives", "feta"]
            }
        ]
        
        created_recipes = []
        for recipe_data in recipes_data:
            response = client.post("/recipes", json=recipe_data)
            assert response.status_code == 200
            created_recipes.append(response.json())
        
        # 2. Test search for tomato-based recipes
        search_response = client.get("/search?q=tomato")
        assert search_response.status_code == 200
        tomato_recipes = search_response.json()
        assert len(tomato_recipes) == 3  # Margherita, Caprese, Greek
        
        tomato_recipe_titles = [r["title"] for r in tomato_recipes]
        assert "Margherita Pizza" in tomato_recipe_titles
        assert "Caprese Salad" in tomato_recipe_titles
        assert "Greek Salad" in tomato_recipe_titles
        assert "Pasta Carbonara" not in tomato_recipe_titles
        
        # 3. Test search for multiple ingredients
        search_response = client.get("/search?q=tomato,basil")
        assert search_response.status_code == 200
        tomato_basil_recipes = search_response.json()
        assert len(tomato_basil_recipes) == 2  # Margherita, Caprese
        
        # 4. Test search for no matches
        search_response = client.get("/search?q=chicken,beef")
        assert search_response.status_code == 200
        no_match_recipes = search_response.json()
        assert no_match_recipes == []
        
        # 5. Test search with empty query
        search_response = client.get("/search")
        assert search_response.status_code == 200
        empty_search_recipes = search_response.json()
        assert empty_search_recipes == []


class TestMultiUserRecipeManagement:
    """Test recipe management with multiple users."""
    
    def test_multi_user_recipe_management(self, client: TestClient, db_session: Session):
        """Test recipe management with multiple users and ownership."""
        # 1. Create two users
        user1_data = {"username": "user1", "password": "pass123"}
        user2_data = {"username": "user2", "password": "pass456"}
        
        user1_signup = client.post("/signup", json=user1_data)
        user2_signup = client.post("/signup", json=user2_data)
        
        assert user1_signup.status_code == 200
        assert user2_signup.status_code == 200
        
        # 2. Login both users
        user1_login = client.post("/login", json=user1_data)
        user2_login = client.post("/login", json=user2_data)
        
        user1_token = user1_login.json()["access_token"]
        user2_token = user2_login.json()["access_token"]
        
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # 3. User1 creates a recipe
        recipe1_data = {
            "title": "User1's Recipe",
            "description": "A recipe owned by user1",
            "ingredients": ["ingredient1", "ingredient2"]
        }
        
        recipe1_response = client.post("/recipes", json=recipe1_data, headers=user1_headers)
        assert recipe1_response.status_code == 200
        recipe1 = recipe1_response.json()
        assert recipe1["owner_id"] is not None
        
        # 4. User2 creates a recipe
        recipe2_data = {
            "title": "User2's Recipe",
            "description": "A recipe owned by user2",
            "ingredients": ["ingredient3", "ingredient4"]
        }
        
        recipe2_response = client.post("/recipes", json=recipe2_data, headers=user2_headers)
        assert recipe2_response.status_code == 200
        recipe2 = recipe2_response.json()
        assert recipe2["owner_id"] is not None
        
        # 5. User1 tries to update User2's recipe (should fail)
        update_data = {"title": "Unauthorized Update", "ingredients": ["new_ingredient"]}
        update_response = client.put(
            f"/recipes/{recipe2['id']}", 
            json=update_data, 
            headers=user1_headers
        )
        assert update_response.status_code == 403
        
        # 6. User2 tries to update User1's recipe (should fail)
        update_response = client.put(
            f"/recipes/{recipe1['id']}", 
            json=update_data, 
            headers=user2_headers
        )
        assert update_response.status_code == 403
        
        # 7. User1 updates their own recipe (should succeed)
        update_data = {"title": "Updated User1 Recipe", "ingredients": ["new_ingredient1"]}
        update_response = client.put(
            f"/recipes/{recipe1['id']}", 
            json=update_data, 
            headers=user1_headers
        )
        assert update_response.status_code == 200
        updated_recipe = update_response.json()
        assert updated_recipe["title"] == "Updated User1 Recipe"
        
        # 8. User2 deletes their own recipe (should succeed)
        delete_response = client.delete(f"/recipes/{recipe2['id']}", headers=user2_headers)
        assert delete_response.status_code == 200
        
        # 9. Verify User2's recipe is deleted
        get_response = client.get(f"/recipes/{recipe2['id']}")
        assert get_response.status_code == 404
        
        # 10. Verify User1's recipe still exists
        get_response = client.get(f"/recipes/{recipe1['id']}")
        assert get_response.status_code == 200


class TestDataPersistence:
    """Test data persistence across requests."""
    
    def test_data_persistence(self, client: TestClient, db_session: Session):
        """Test that data persists across different requests."""
        # 1. Create a user
        user_data = {"username": "persistuser", "password": "persistpass123"}
        signup_response = client.post("/signup", json=user_data)
        assert signup_response.status_code == 200
        
        # 2. Create a recipe
        recipe_data = {"title": "Persistent Recipe", "ingredients": ["persistent_ingredient"]}
        create_response = client.post("/recipes", json=recipe_data)
        assert create_response.status_code == 200
        created_recipe = create_response.json()
        
        # 3. Verify recipe exists in list
        list_response = client.get("/recipes")
        assert list_response.status_code == 200
        recipes_list = list_response.json()
        assert len(recipes_list) == 1
        assert recipes_list[0]["title"] == "Persistent Recipe"
        
        # 4. Get specific recipe
        get_response = client.get(f"/recipes/{created_recipe['id']}")
        assert get_response.status_code == 200
        retrieved_recipe = get_response.json()
        assert retrieved_recipe["title"] == "Persistent Recipe"
        assert retrieved_recipe["id"] == created_recipe["id"]
        
        # 5. Search for recipe by ingredient
        search_response = client.get("/search?q=persistent_ingredient")
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) == 1
        assert search_results[0]["title"] == "Persistent Recipe"


class TestEdgeCasesAndErrorScenarios:
    """Test edge cases and error scenarios."""
    
    def test_large_ingredient_list(self, client: TestClient, db_session: Session):
        """Test creating recipe with large ingredient list."""
        large_ingredients = [f"ingredient_{i}" for i in range(100)]
        recipe_data = {
            "title": "Large Ingredient Recipe",
            "ingredients": large_ingredients
        }
        
        response = client.post("/recipes", json=recipe_data)
        assert response.status_code == 200
        
        created_recipe = response.json()
        assert len(created_recipe["ingredients"]) == 100
    
    def test_very_long_title(self, client: TestClient, db_session: Session):
        """Test creating recipe with very long title."""
        long_title = "A" * 1000
        recipe_data = {
            "title": long_title,
            "ingredients": ["ingredient"]
        }
        
        response = client.post("/recipes", json=recipe_data)
        assert response.status_code == 200
        
        created_recipe = response.json()
        assert created_recipe["title"] == long_title
    
    def test_special_characters_in_data(self, client: TestClient, db_session: Session):
        """Test handling of special characters in recipe data."""
        special_recipe_data = {
            "title": "Recipe with Special Chars: !@#$%^&*()_+-=[]{}|;:,.<>?",
            "description": "Description with unicode: ñáéíóú 测试 тест",
            "ingredients": ["ingredient-123", "ingredient_456", "ingredient+789"]
        }
        
        response = client.post("/recipes", json=special_recipe_data)
        assert response.status_code == 200
        
        created_recipe = response.json()
        assert created_recipe["title"] == special_recipe_data["title"]
        assert created_recipe["description"] == special_recipe_data["description"]
        assert len(created_recipe["ingredients"]) == 3
    
    def test_concurrent_operations(self, client: TestClient, db_session: Session):
        """Test concurrent operations on the same data."""
        # Create a recipe
        recipe_data = {"title": "Concurrent Recipe", "ingredients": ["ingredient"]}
        create_response = client.post("/recipes", json=recipe_data)
        assert create_response.status_code == 200
        created_recipe = create_response.json()
        
        # Simulate concurrent updates (though this is sequential in tests)
        update1_data = {"title": "Update 1", "ingredients": ["ingredient"]}
        update2_data = {"title": "Update 2", "ingredients": ["ingredient"]}
        
        # Both updates should succeed
        update1_response = client.put(f"/recipes/{created_recipe['id']}", json=update1_data)
        update2_response = client.put(f"/recipes/{created_recipe['id']}", json=update2_data)
        
        assert update1_response.status_code == 200
        assert update2_response.status_code == 200
        
        # Final state should be from the last update
        final_recipe = client.get(f"/recipes/{created_recipe['id']}").json()
        assert final_recipe["title"] == "Update 2"


class TestPerformanceAndScalability:
    """Test performance and scalability aspects."""
    
    def test_bulk_recipe_creation(self, client: TestClient, db_session: Session):
        """Test creating many recipes in sequence."""
        num_recipes = 50
        
        for i in range(num_recipes):
            recipe_data = {
                "title": f"Bulk Recipe {i+1}",
                "ingredients": [f"ingredient_{i+1}"]
            }
            
            response = client.post("/recipes", json=recipe_data)
            assert response.status_code == 200
        
        # Verify all recipes were created
        list_response = client.get("/recipes")
        assert list_response.status_code == 200
        recipes_list = list_response.json()
        assert len(recipes_list) == num_recipes
    
    def test_pagination_performance(self, client: TestClient, db_session: Session):
        """Test pagination performance with large datasets."""
        # Create many recipes
        num_recipes = 100
        for i in range(num_recipes):
            recipe_data = {
                "title": f"Pagination Recipe {i+1}",
                "ingredients": [f"ingredient_{i+1}"]
            }
            client.post("/recipes", json=recipe_data)
        
        # Test different pagination settings
        pagination_tests = [
            (0, 10),    # First page
            (10, 10),   # Second page
            (50, 25),   # Middle page with different limit
            (90, 10),   # Last page
            (95, 10),   # Beyond available data
        ]
        
        for skip, limit in pagination_tests:
            response = client.get(f"/recipes?skip={skip}&limit={limit}")
            assert response.status_code == 200
            
            recipes = response.json()
            if skip < num_recipes:
                assert len(recipes) > 0
                assert len(recipes) <= limit
            else:
                assert len(recipes) == 0
