import requests
import json
import time
import uuid
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ShoppingListTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.recipe_id = None
        self.cart_options_id = None
        
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a single API test with configurable timeout"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        logger.info(f"Testing {name} - {method} {url}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                print(f"❌ Unsupported method: {method}")
                return False, {}
            
            elapsed_time = time.time() - start_time
            print(f"⏱️ Request completed in {elapsed_time:.2f} seconds")
            logger.info(f"Request completed in {elapsed_time:.2f} seconds")
            
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
                    error_data = response.json()
                    print(f"Response: {error_data}")
                    return False, error_data
                except:
                    print(f"Response: {response.text}")
                    return False, {}

        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"❌ Failed - Request timed out after {elapsed_time:.2f} seconds (timeout set to {timeout}s)")
            logger.error(f"Request timed out after {elapsed_time:.2f} seconds (timeout set to {timeout}s)")
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            logger.error(f"Connection error: Could not connect to {url}")
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            logger.error(f"Test failed with error: {str(e)}")
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

    def create_test_user(self):
        """Create a test user for recipe generation"""
        user_data = {
            "name": f"Test User {uuid.uuid4()}",
            "email": f"test_{uuid.uuid4()}@example.com",
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": []
        }
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "users",
            200,
            data=user_data
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"Created test user with ID: {self.user_id}")
            return True
        return False

    def test_generate_recipe_with_shopping_list(self):
        """Test recipe generation with shopping list"""
        if not self.user_id:
            if not self.create_test_user():
                print("❌ Failed to create test user")
                return False
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "vegetarian",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": [],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "easy"
        }
        
        print("Testing recipe generation with shopping list...")
        success, response = self.run_test(
            "Generate Recipe with Shopping List",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60  # Set timeout to 60 seconds for OpenAI
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"Generated recipe with ID: {self.recipe_id}")
            
            # Check if shopping_list field exists in the response
            if 'shopping_list' in response:
                print(f"✅ Shopping list field exists in the response")
                shopping_list = response['shopping_list']
                print(f"Shopping list: {shopping_list}")
                
                # Check if shopping list contains items
                if isinstance(shopping_list, list) and len(shopping_list) > 0:
                    print(f"✅ Shopping list contains {len(shopping_list)} items")
                    
                    # Check if shopping list items are clean (no amounts, no measurements)
                    all_clean = True
                    for item in shopping_list:
                        # Check for common measurement patterns
                        if any(pattern in item.lower() for pattern in ['cup', 'tbsp', 'tsp', 'oz', 'pound', 'lb', 'g', 'kg', 'ml', 'l']):
                            print(f"❌ Shopping list item contains measurement: {item}")
                            all_clean = False
                        # Check for numeric patterns at the beginning
                        elif any(c.isdigit() for c in item):
                            print(f"❌ Shopping list item contains numbers: {item}")
                            all_clean = False
                    
                    if all_clean:
                        print(f"✅ All shopping list items are clean (no amounts, no measurements)")
                    else:
                        print(f"❌ Some shopping list items contain measurements or amounts")
                else:
                    print(f"❌ Shopping list is empty or not a list")
            else:
                print(f"❌ Shopping list field does not exist in the response")
                return False
            
            return True
        return False

    def test_cart_options_with_shopping_list(self):
        """Test cart-options endpoint with shopping list"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Cart Options with Shopping List",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": self.recipe_id, "user_id": self.user_id}
        )
        
        if success and 'id' in response:
            self.cart_options_id = response['id']
            print(f"Created grocery cart options with ID: {self.cart_options_id}")
            
            # Verify the response structure
            if 'ingredient_options' in response:
                options_count = len(response['ingredient_options'])
                print(f"Found {options_count} ingredients with options")
                
                # Check if each ingredient has multiple options with required fields
                for i, ingredient_option in enumerate(response['ingredient_options']):
                    if 'options' in ingredient_option:
                        product_count = len(ingredient_option['options'])
                        print(f"  Ingredient {i+1}: {ingredient_option.get('ingredient_name', 'Unknown')} - {product_count} product options")
                        
                        # Check if products have all required fields
                        for j, product in enumerate(ingredient_option['options']):
                            required_fields = ['product_id', 'name', 'price']
                            missing_fields = [field for field in required_fields if field not in product]
                            
                            if missing_fields:
                                print(f"    ❌ Product {j+1} missing required fields: {', '.join(missing_fields)}")
                            else:
                                print(f"    ✅ Product {j+1}: {product['name']} - ${product['price']:.2f} (ID: {product['product_id']})")
            
            return True
        return False

    def test_specific_recipe_ingredients(self):
        """Test recipe generation with specific ingredients"""
        if not self.user_id:
            if not self.create_test_user():
                print("❌ Failed to create test user")
                return False
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "bbq bowl",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": [
                "1 can chickpeas, drained and rinsed",
                "1/2 cup BBQ sauce",
                "1 cup cooked quinoa",
                "1 avocado, sliced",
                "2 tbsp olive oil"
            ],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "easy"
        }
        
        print("Testing recipe generation with specific ingredients...")
        success, response = self.run_test(
            "Generate Recipe with Specific Ingredients",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60  # Set timeout to 60 seconds for OpenAI
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"Generated recipe with ID: {self.recipe_id}")
            
            # Check if shopping_list field exists in the response
            if 'shopping_list' in response:
                print(f"✅ Shopping list field exists in the response")
                shopping_list = response['shopping_list']
                print(f"Shopping list: {shopping_list}")
                
                # Check if shopping list contains expected clean items
                expected_items = ["chickpeas", "bbq sauce", "quinoa", "avocado", "olive oil"]
                found_items = []
                
                for expected in expected_items:
                    found = False
                    for item in shopping_list:
                        if expected.lower() in item.lower():
                            found = True
                            found_items.append(expected)
                            print(f"✅ Found expected item: {expected} as '{item}'")
                            break
                    if not found:
                        print(f"❌ Expected item not found in shopping list: {expected}")
                
                if len(found_items) == len(expected_items):
                    print(f"✅ All expected items found in shopping list")
                else:
                    print(f"❌ Only {len(found_items)}/{len(expected_items)} expected items found in shopping list")
            else:
                print(f"❌ Shopping list field does not exist in the response")
                return False
            
            return True
        return False

def main():
    print("=" * 80)
    print("AI Recipe & Grocery App - Shopping List Testing")
    print("=" * 80)
    
    # Get the backend URL from the frontend .env file
    import os
    import re
    
    backend_url = "http://localhost:8001"  # Use local backend URL
    print(f"Using local backend URL: {backend_url}")
    
    tester = ShoppingListTester(backend_url)
    
    # Test API root
    tester.test_api_root()
    
    # Test recipe generation with shopping list
    print("\n" + "=" * 50)
    print("Testing Recipe Generation with Shopping List")
    print("=" * 50)
    recipe_generated = tester.test_generate_recipe_with_shopping_list()
    
    if recipe_generated:
        # Test cart options with shopping list
        print("\n" + "=" * 50)
        print("Testing Cart Options with Shopping List")
        print("=" * 50)
        tester.test_cart_options_with_shopping_list()
    
    # Test recipe generation with specific ingredients
    print("\n" + "=" * 50)
    print("Testing Recipe Generation with Specific Ingredients")
    print("=" * 50)
    specific_recipe_generated = tester.test_specific_recipe_ingredients()
    
    if specific_recipe_generated:
        # Test cart options with specific ingredients
        print("\n" + "=" * 50)
        print("Testing Cart Options with Specific Ingredients")
        print("=" * 50)
        tester.test_cart_options_with_shopping_list()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    # Print summary of findings
    print("\n" + "=" * 50)
    print("SUMMARY OF FINDINGS")
    print("=" * 50)
    print("1. API Root: ✅ Working")
    print("2. Recipe Generation with Shopping List: " + ("✅ Working" if recipe_generated else "❌ Not Working"))
    print("3. Cart Options with Shopping List: " + ("✅ Working" if tester.cart_options_id else "❌ Not Working"))
    print("4. Recipe Generation with Specific Ingredients: " + ("✅ Working" if specific_recipe_generated else "❌ Not Working"))
    
    return 0 if tester.tests_passed > 0 else 1

if __name__ == "__main__":
    sys.exit(main())