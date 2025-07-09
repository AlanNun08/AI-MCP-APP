import requests
import json
import time
import sys
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackendAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.recipe_id = None
        self.cart_options_id = None
        self.custom_cart_id = None
        # Test user credentials - using the provided test user
        self.test_email = "Alan.nunez0310@icloud.com"
        self.test_password = "testpassword"  # This is a placeholder, we'll need the actual password

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

    def test_login(self):
        """Test login with the test user"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "Login with Test User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'user' in response and 'id' in response['user']:
            self.user_id = response['user']['id']
            print(f"Logged in as user with ID: {self.user_id}")
            return True
        return False

    def test_get_user_recipes(self):
        """Test getting all recipes for the test user"""
        if not self.user_id:
            print("❌ No user ID available for testing - trying with a test ID")
            # Use a test user ID for testing
            self.user_id = "test_user_id"
            
        success, response = self.run_test(
            "Get User Recipes",
            "GET",
            f"users/{self.user_id}/recipes",
            200
        )
        
        if success:
            print(f"✅ Successfully retrieved {len(response)} recipes for user")
            # Check if we have any recipes
            if len(response) > 0:
                print(f"Recipe titles: {[recipe.get('title', 'Untitled') for recipe in response]}")
                # Store the first recipe ID for further testing
                self.recipe_id = response[0].get('id')
                print(f"Using recipe ID: {self.recipe_id} for further testing")
            else:
                print("No recipes found for this user")
        
        return success

    def test_generate_recipe(self):
        """Test recipe generation"""
        if not self.user_id:
            print("❌ No user ID available for testing - trying with a test ID")
            # Use a test user ID for testing
            self.user_id = "test_user_id"
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "italian",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["pasta", "tomatoes", "garlic"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "easy"
        }
        
        print("Testing recipe generation with 60 second timeout...")
        success, response = self.run_test(
            "Generate Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60  # Set timeout to 60 seconds to check for timeout issues
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"Generated recipe with ID: {self.recipe_id}")
            return True
        return False

    def test_cart_options_endpoint(self):
        """Test the cart-options endpoint with recipe_id and user_id parameters"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing - trying with test IDs")
            # Use test IDs for testing
            if not self.recipe_id:
                self.recipe_id = "test_recipe_id"
            if not self.user_id:
                self.user_id = "test_user_id"
            
        success, response = self.run_test(
            "Cart Options Endpoint",
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

    def test_custom_cart_creation(self):
        """Test creating a custom cart with selected products"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing - trying with test IDs")
            # Use test IDs for testing
            if not self.recipe_id:
                self.recipe_id = "test_recipe_id"
            if not self.user_id:
                self.user_id = "test_user_id"
            
        # Create a custom cart with selected products
        custom_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "products": [
                {
                    "ingredient_name": "pasta",
                    "product_id": "123456789",
                    "name": "Barilla Pasta Penne 16oz",
                    "price": 1.99,
                    "quantity": 2
                },
                {
                    "ingredient_name": "tomatoes",
                    "product_id": "987654321",
                    "name": "Fresh Roma Tomatoes 2lb",
                    "price": 2.49,
                    "quantity": 1
                },
                {
                    "ingredient_name": "garlic",
                    "product_id": "789123456",
                    "name": "Fresh Garlic Bulb 3oz",
                    "price": 0.98,
                    "quantity": 3
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Custom Cart",
            "POST",
            "grocery/custom-cart",
            200,
            data=custom_cart_data
        )
        
        if success and 'id' in response:
            self.custom_cart_id = response['id']
            print(f"Created custom cart with ID: {self.custom_cart_id}")
            
            # Verify the response structure
            if 'products' in response:
                products_count = len(response['products'])
                print(f"Cart contains {products_count} products")
                
                # Check if total price is calculated correctly
                if 'total_price' in response:
                    expected_total = sum(p['price'] * p['quantity'] for p in custom_cart_data['products'])
                    actual_total = response['total_price']
                    print(f"Total price: ${actual_total:.2f} (Expected: ${expected_total:.2f})")
                    
                    if abs(actual_total - expected_total) < 0.01:  # Allow for small floating-point differences
                        print("✅ Total price calculated correctly")
                    else:
                        print("❌ Total price calculation error")
                
                # Check if Walmart URL is generated correctly
                if 'walmart_url' in response:
                    walmart_url = response['walmart_url']
                    print(f"Walmart URL: {walmart_url}")
                    
                    if 'affil.walmart.com' in walmart_url and 'items=' in walmart_url:
                        print("✅ Walmart URL correctly formatted")
                        
                        # Check if all product IDs are in the URL
                        product_ids = [p['product_id'] for p in custom_cart_data['products']]
                        all_ids_in_url = all(pid in walmart_url for pid in product_ids)
                        if all_ids_in_url:
                            print("✅ All product IDs included in Walmart URL")
                        else:
                            print("❌ Not all product IDs found in Walmart URL")
                    else:
                        print("❌ Walmart URL format may be incorrect")
            
            return True
        return False

def main():
    print("=" * 80)
    print("AI Recipe & Grocery App - Backend API Testing")
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
    
    tester = BackendAPITester(backend_url)
    
    # Test API root
    tester.test_api_root()
    
    # Test login (optional - may not work without correct password)
    print("\n" + "=" * 50)
    print("Testing User Authentication")
    print("=" * 50)
    print("Note: Login test may fail if we don't have the correct password for the test user.")
    print("This won't prevent other tests from running.")
    tester.test_login()
    
    # Test recipe history retrieval
    print("\n" + "=" * 50)
    print("Testing Recipe History Retrieval")
    print("=" * 50)
    tester.test_get_user_recipes()
    
    # Test recipe generation
    print("\n" + "=" * 50)
    print("Testing Recipe Generation")
    print("=" * 50)
    tester.test_generate_recipe()
    
    # Test Walmart cart options
    print("\n" + "=" * 50)
    print("Testing Walmart Cart Options")
    print("=" * 50)
    tester.test_cart_options_endpoint()
    
    # Test custom cart creation
    print("\n" + "=" * 50)
    print("Testing Custom Cart Creation")
    print("=" * 50)
    tester.test_custom_cart_creation()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())