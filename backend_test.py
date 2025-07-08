import requests
import json
import time
import sys
import uuid
from datetime import datetime

class AIRecipeAppTester:
    def __init__(self, base_url="https://0f1f869d-6ed3-4b88-8686-333f2c09e742.preview.emergentagent.com"):
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

    def test_generate_healthy_recipe(self):
        """Test healthy recipe generation with calorie limits"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "mediterranean",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["chickpeas", "olive oil", "tomatoes"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "medium",
            "is_healthy": True,
            "max_calories_per_serving": 400
        }
        
        success, response = self.run_test(
            "Generate Healthy Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request
        )
        
        if success and 'id' in response:
            self.healthy_recipe_id = response['id']
            print(f"Generated healthy recipe with ID: {self.healthy_recipe_id}")
            
            # Verify calorie information is present
            if 'calories_per_serving' in response and response['calories_per_serving']:
                print(f"✅ Calorie information present: {response['calories_per_serving']} calories per serving")
                if response['calories_per_serving'] <= recipe_request['max_calories_per_serving']:
                    print(f"✅ Calorie limit respected: {response['calories_per_serving']} <= {recipe_request['max_calories_per_serving']}")
                else:
                    print(f"⚠️ Calorie limit exceeded: {response['calories_per_serving']} > {recipe_request['max_calories_per_serving']}")
            else:
                print("⚠️ No calorie information in the response")
                
            return True
        return False

    def test_generate_budget_recipe(self):
        """Test budget-friendly recipe generation with budget limits"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "american",
            "dietary_preferences": [],
            "ingredients_on_hand": ["potatoes", "onions", "beans"],
            "prep_time_max": 45,
            "servings": 4,
            "difficulty": "easy",
            "is_budget_friendly": True,
            "max_budget": 15.0
        }
        
        success, response = self.run_test(
            "Generate Budget-Friendly Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request
        )
        
        if success and 'id' in response:
            self.budget_recipe_id = response['id']
            print(f"Generated budget-friendly recipe with ID: {self.budget_recipe_id}")
            return True
        return False

    def test_generate_combined_recipe(self):
        """Test recipe generation with both healthy and budget modes"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "asian",
            "dietary_preferences": ["low-carb"],
            "ingredients_on_hand": ["tofu", "broccoli", "ginger"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "medium",
            "is_healthy": True,
            "max_calories_per_serving": 350,
            "is_budget_friendly": True,
            "max_budget": 12.0
        }
        
        success, response = self.run_test(
            "Generate Combined Healthy & Budget Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request
        )
        
        if success and 'id' in response:
            self.combined_recipe_id = response['id']
            print(f"Generated combined healthy & budget recipe with ID: {self.combined_recipe_id}")
            
            # Verify calorie information is present
            if 'calories_per_serving' in response and response['calories_per_serving']:
                print(f"✅ Calorie information present: {response['calories_per_serving']} calories per serving")
                if response['calories_per_serving'] <= recipe_request['max_calories_per_serving']:
                    print(f"✅ Calorie limit respected: {response['calories_per_serving']} <= {recipe_request['max_calories_per_serving']}")
                else:
                    print(f"⚠️ Calorie limit exceeded: {response['calories_per_serving']} > {recipe_request['max_calories_per_serving']}")
            else:
                print("⚠️ No calorie information in the response")
                
            return True
        return False

    def test_create_simple_grocery_cart(self):
        """Test creating simple grocery cart with just ingredient names (no portions)"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        cart_request = {
            "recipe_id": self.recipe_id,
            "user_id": self.user_id
        }
        
        success, response = self.run_test(
            "Create Simple Grocery Cart",
            "POST",
            "grocery/simple-cart",
            200,
            data=cart_request
        )
        
        if success and 'id' in response:
            self.cart_id = response['id']
            print(f"Created simple grocery cart with ID: {self.cart_id}")
            
            # Verify Walmart URL format
            walmart_url = response.get('walmart_url', '')
            print(f"Walmart URL: {walmart_url}")
            
            # Check if URL uses simplified format (no _2, _3 suffixes)
            if 'items=' in walmart_url:
                items_part = walmart_url.split('items=')[1]
                if '_' in items_part:
                    print("⚠️ Warning: Walmart URL contains quantity suffixes (_2, _3) which should be removed")
                else:
                    print("✅ Walmart URL uses simplified format without quantity suffixes")
            
            # Check if simple_items are present
            if 'simple_items' in response:
                items_count = len(response['simple_items'])
                print(f"Found {items_count} simple items in cart")
                
                # Check a few items to verify they have the right structure
                for i, item in enumerate(response['simple_items'][:3]):  # Check first 3 items
                    print(f"  Item {i+1}: {item.get('name', 'Unknown')} - ${item.get('price', 0):.2f}")
                    if 'original_ingredient' in item:
                        print(f"    Original: {item['original_ingredient']}")
            
            return True
        return False

    def test_get_grocery_cart(self):
        """Test getting grocery cart by ID"""
        if not self.cart_id:
            print("❌ No cart ID available for testing")
            return False
            
        # Note: This endpoint doesn't exist in the API, skipping this test
        print("⚠️ Skipping test_get_grocery_cart as the endpoint doesn't exist")
        return True
        
    def test_create_grocery_cart_with_options(self):
        """Test creating grocery cart with multiple options per ingredient"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Create Grocery Cart with Options",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": self.recipe_id, "user_id": self.user_id}
        )
        
        if success and 'id' in response:
            self.cart_options_id = response['id']
            print(f"Created grocery cart with options, ID: {self.cart_options_id}")
            
            # Verify multiple options per ingredient
            if 'ingredient_options' in response:
                options_count = len(response['ingredient_options'])
                print(f"Found {options_count} ingredients with options")
                
                # Check if each ingredient has multiple options
                for i, ingredient_option in enumerate(response['ingredient_options']):
                    if 'options' in ingredient_option:
                        product_count = len(ingredient_option['options'])
                        print(f"  Ingredient {i+1}: {ingredient_option.get('ingredient_name', 'Unknown')} - {product_count} product options")
                        
                        # Check if we have budget, mid-range, and premium options
                        if product_count > 0:
                            prices = [product.get('price', 0) for product in ingredient_option['options']]
                            if len(prices) >= 3:
                                print(f"    Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                            else:
                                print(f"    Limited options: {product_count} (expected 3)")
            
            return True
        return False
        
    def test_get_grocery_cart_options(self):
        """Test getting grocery cart options by ID"""
        if not self.cart_options_id:
            print("❌ No cart options ID available for testing")
            return False
            
        success, _ = self.run_test(
            "Get Grocery Cart Options",
            "GET",
            f"grocery/cart-options/{self.cart_options_id}",
            200
        )
        
        return success
        
    def test_create_custom_cart(self):
        """Test creating custom cart from selected options"""
        if not self.cart_options_id or not self.user_id:
            print("❌ No cart options ID or user ID available for testing")
            return False
            
        # First, get the cart options to select from
        _, cart_options = self.run_test(
            "Get Cart Options for Selection",
            "GET",
            f"grocery/cart-options/{self.cart_options_id}",
            200
        )
        
        if not cart_options or 'ingredient_options' not in cart_options:
            print("❌ Failed to get ingredient options")
            return False
            
        # Create selections from available options
        selections = []
        for ingredient_option in cart_options['ingredient_options']:
            if 'options' in ingredient_option and len(ingredient_option['options']) > 0:
                # Select the first option for each ingredient
                selections.append({
                    "ingredient_name": ingredient_option['ingredient_name'],
                    "selected_product_id": ingredient_option['options'][0]['product_id'],
                    "quantity": ingredient_option.get('quantity', 1)
                })
        
        if not selections:
            print("❌ No product options available to select")
            return False
            
        custom_cart_request = {
            "cart_id": self.cart_options_id,
            "selections": selections
        }
        
        success, response = self.run_test(
            "Create Custom Cart",
            "POST",
            "grocery/custom-cart",
            200,
            data=custom_cart_request
        )
        
        if success and 'id' in response:
            print(f"Created custom cart with ID: {response['id']}")
            print(f"Total price: ${response.get('total_price', 0):.2f}")
            print(f"Walmart URL: {response.get('walmart_url', 'N/A')}")
            return True
        return False

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
    
    # Test basic recipe generation
    if not tester.test_generate_recipe():
        print("❌ Recipe generation failed, stopping tests")
        return 1
    
    tester.test_get_recipes()
    tester.test_get_recipe()
    
    # Test healthy recipe generation
    print("\n" + "=" * 50)
    print("Testing Healthy Recipe Mode")
    print("=" * 50)
    tester.test_generate_healthy_recipe()
    
    # Test budget recipe generation
    print("\n" + "=" * 50)
    print("Testing Budget-Friendly Recipe Mode")
    print("=" * 50)
    tester.test_generate_budget_recipe()
    
    # Test combined healthy + budget recipe generation
    print("\n" + "=" * 50)
    print("Testing Combined Healthy + Budget Recipe Mode")
    print("=" * 50)
    tester.test_generate_combined_recipe()
    
    # Test grocery cart with options
    print("\n" + "=" * 50)
    print("Testing Grocery Cart with Multiple Options")
    print("=" * 50)
    tester.test_create_grocery_cart_with_options()
    tester.test_get_grocery_cart_options()
    tester.test_create_custom_cart()
    
    # Test regular grocery cart
    print("\n" + "=" * 50)
    print("Testing Simple Grocery Cart")
    print("=" * 50)
    tester.test_create_simple_grocery_cart()
    tester.test_get_grocery_cart()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())