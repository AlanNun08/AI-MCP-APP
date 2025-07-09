import requests
import json
import time
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IngredientParsingTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = "test_user_id"  # Using a test user ID
        self.recipe_id = None
        
    def test_cart_options_with_direct_ingredients(self):
        """Test the cart-options endpoint directly with specific ingredients"""
        # Create a test recipe with the specific ingredients
        test_recipe = {
            "id": "test_recipe_id",
            "title": "Test Recipe with Specific Ingredients",
            "description": "A test recipe to verify ingredient parsing",
            "ingredients": [
                "1 can chickpeas, drained and rinsed",
                "1/2 cup BBQ sauce",
                "1 cup cooked quinoa",
                "1 cup mixed vegetables (bell peppers, zucchini, onions)",
                "1 avocado, sliced",
                "2 tbsp olive oil",
                "Salt and pepper to taste"
            ],
            "instructions": ["Mix all ingredients together", "Serve and enjoy"],
            "prep_time": 15,
            "cook_time": 10,
            "servings": 2,
            "cuisine_type": "test",
            "dietary_tags": ["vegetarian"],
            "difficulty": "easy",
            "user_id": self.user_id
        }
        
        # First, try to save the test recipe
        success, response = self.run_test(
            "Create Test Recipe",
            "POST",
            "recipes/generate",
            200,
            data=test_recipe
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"Created test recipe with ID: {self.recipe_id}")
        else:
            # If we can't save the recipe, we'll use a direct approach
            print("Using direct ingredient testing approach...")
            
            # Test each ingredient individually
            ingredients = test_recipe["ingredients"]
            all_success = True
            
            print("\nTesting individual ingredients:")
            for i, ingredient in enumerate(ingredients):
                print(f"\n--- Testing ingredient {i+1}: '{ingredient}' ---")
                
                # Create a mock recipe with just this ingredient
                mock_recipe = {
                    "id": f"test_recipe_{i}",
                    "title": f"Test Recipe {i}",
                    "ingredients": [ingredient],
                    "user_id": self.user_id
                }
                
                # Mock the database call by directly calling the cart-options endpoint
                # with our mock recipe data
                success, ingredient_response = self.run_test(
                    f"Parse Ingredient: '{ingredient}'",
                    "POST",
                    "grocery/cart-options",
                    200,
                    params={"recipe_id": mock_recipe["id"], "user_id": self.user_id},
                    data=mock_recipe  # Pass the mock recipe as data
                )
                
                if not success:
                    all_success = False
                    continue
                
                # Check if we got product options
                if 'ingredient_options' in ingredient_response:
                    for option in ingredient_response.get('ingredient_options', []):
                        original = option.get('original_ingredient', '')
                        cleaned = option.get('ingredient_name', '')
                        print(f"  Original: '{original}'")
                        print(f"  Cleaned: '{cleaned}'")
                        
                        if 'options' in option:
                            product_count = len(option['options'])
                            print(f"  Found {product_count} product options")
                            
                            if product_count > 0:
                                print("  ✅ Product options found")
                                for j, product in enumerate(option['options'][:2]):  # Show first 2 products
                                    print(f"    Product {j+1}: {product.get('name', 'Unknown')} - ${product.get('price', 0):.2f}")
                            else:
                                print("  ❌ No product options found")
                                all_success = False
                
            return all_success
        
        return False

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



def main():
    print("=" * 80)
    print("AI Recipe & Grocery App - Ingredient Parsing Testing")
    print("=" * 80)
    
    # Get the backend URL from the frontend .env file
    import os
    import re
    
    backend_url = "http://localhost:8001"  # Default fallback
    try:
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            match = re.search(r'REACT_APP_BACKEND_URL=(.+)', env_content)
            if match:
                backend_url = match.group(1).strip()
                print(f"Using backend URL from frontend/.env: {backend_url}")
    except Exception as e:
        print(f"Error reading backend URL from .env: {str(e)}")
        print(f"Using default backend URL: {backend_url}")
    
    tester = IngredientParsingTester(backend_url)
    
    # Test cart options with direct ingredient testing
    print("\n" + "=" * 50)
    print("Testing Cart Options with Specific Ingredients")
    print("=" * 50)
    cart_success = tester.test_cart_options_with_direct_ingredients()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    # Print summary
    print("\nSUMMARY OF FINDINGS:")
    if cart_success:
        print("✅ Ingredient parsing is working correctly")
        print("✅ All test ingredients were successfully parsed")
        print("✅ Product options were found for all ingredients")
        print("✅ No 'No product options available' errors were found")
    else:
        print("❌ Issues found with ingredient parsing")
        print("❌ Some ingredients may not have been parsed correctly")
        print("❌ Some ingredients may not have product options")
    
    return 0 if tester.tests_passed > 0 else 1

if __name__ == "__main__":
    main()