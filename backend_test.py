import requests
import json
import time
import sys
import uuid
from datetime import datetime

class AIRecipeAppTester:
    def __init__(self, base_url="https://ae98d8a0-e0fa-4434-aadf-fe1df1f1101d.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.recipe_id = None
        self.healthy_recipe_id = None
        self.budget_recipe_id = None
        self.combined_recipe_id = None
        self.cart_id = None
        self.cart_options_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        success, _ = self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        return success

    def test_create_user(self):
        """Test user creation"""
        test_user = {
            "name": f"Test User {uuid.uuid4()}",
            "email": f"test_{uuid.uuid4()}@example.com",
            "dietary_preferences": ["vegetarian", "gluten-free"],
            "allergies": ["nuts", "dairy"],
            "favorite_cuisines": ["italian", "mexican"]
        }
        
        success, response = self.run_test(
            "Create User",
            "POST",
            "users",
            200,
            data=test_user
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"Created user with ID: {self.user_id}")
            return True
        return False

    def test_get_user(self):
        """Test getting user by ID"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get User",
            "GET",
            f"users/{self.user_id}",
            200
        )
        
        return success

    def test_update_user(self):
        """Test updating user"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        update_data = {
            "name": f"Updated User {uuid.uuid4()}",
            "email": f"updated_{uuid.uuid4()}@example.com",
            "dietary_preferences": ["vegan", "keto"],
            "allergies": ["soy", "eggs"],
            "favorite_cuisines": ["indian", "mediterranean"]
        }
        
        success, _ = self.run_test(
            "Update User",
            "PUT",
            f"users/{self.user_id}",
            200,
            data=update_data
        )
        
        return success

    def test_generate_recipe(self):
        """Test recipe generation"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "italian",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["pasta", "tomatoes", "garlic"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "easy"
        }
        
        success, response = self.run_test(
            "Generate Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"Generated recipe with ID: {self.recipe_id}")
            return True
        return False

    def test_get_recipes(self):
        """Test getting recipes"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Recipes",
            "GET",
            "recipes",
            200,
            params={"user_id": self.user_id}
        )
        
        return success

    def test_get_recipe(self):
        """Test getting recipe by ID"""
        if not self.recipe_id:
            print("❌ No recipe ID available for testing")
            return False
            
        success, _ = self.run_test(
            "Get Recipe",
            "GET",
            f"recipes/{self.recipe_id}",
            200
        )
        
        return success

    def test_save_recipe(self):
        """Test saving recipe"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        success, _ = self.run_test(
            "Save Recipe",
            "POST",
            f"recipes/{self.recipe_id}/save",
            200,
            params={"user_id": self.user_id}
        )
        
        return success

    def test_create_grocery_cart(self):
        """Test creating grocery cart"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Create Grocery Cart",
            "POST",
            "grocery/cart",
            200,
            params={"recipe_id": self.recipe_id, "user_id": self.user_id}
        )
        
        if success and 'id' in response:
            self.cart_id = response['id']
            print(f"Created grocery cart with ID: {self.cart_id}")
            print(f"Walmart URL: {response.get('walmart_url', 'N/A')}")
            return True
        return False

    def test_get_grocery_cart(self):
        """Test getting grocery cart by ID"""
        if not self.cart_id:
            print("❌ No cart ID available for testing")
            return False
            
        success, _ = self.run_test(
            "Get Grocery Cart",
            "GET",
            f"grocery/cart/{self.cart_id}",
            200
        )
        
        return success

def main():
    print("=" * 50)
    print("AI Recipe & Grocery App API Test")
    print("=" * 50)
    
    tester = AIRecipeAppTester()
    
    # Test API root
    tester.test_api_root()
    
    # Test user management
    if not tester.test_create_user():
        print("❌ User creation failed, stopping tests")
        return 1
    
    tester.test_get_user()
    tester.test_update_user()
    
    # Test recipe generation
    if not tester.test_generate_recipe():
        print("❌ Recipe generation failed, stopping tests")
        return 1
    
    tester.test_get_recipes()
    tester.test_get_recipe()
    tester.test_save_recipe()
    
    # Test grocery cart
    tester.test_create_grocery_cart()
    tester.test_get_grocery_cart()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())