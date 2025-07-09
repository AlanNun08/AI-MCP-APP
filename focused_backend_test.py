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

class FocusedBackendTester:
    def __init__(self, base_url="https://1896460c-1fcb-418f-bf8d-0da71d07a349.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.recipe_id = None
        self.cart_options_id = None
        self.custom_cart_id = None
        self.test_email = f"test_{uuid.uuid4()}@example.com"
        self.test_password = "SecureP@ssw0rd123"

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
        """Create a test user for recipe generation and grocery cart testing"""
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "favorite_cuisines": ["italian", "mexican"]
        }
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'user_id' in response:
            self.user_id = response['user_id']
            print(f"Created user with ID: {self.user_id}")
            
            # Get verification code
            code_success, code_response = self.run_test(
                "Get Verification Code",
                "GET",
                f"debug/verification-codes/{self.test_email}",
                200
            )
            
            if code_success and 'codes' in code_response and len(code_response['codes']) > 0:
                verification_code = code_response['codes'][0]['code']
                
                # Verify the user
                verify_data = {
                    "email": self.test_email,
                    "code": verification_code
                }
                
                verify_success, _ = self.run_test(
                    "Verify User",
                    "POST",
                    "auth/verify",
                    200,
                    data=verify_data
                )
                
                if verify_success:
                    print(f"✅ User verified successfully")
                    return True
        
        return False

    def test_recipe_generation(self):
        """Test recipe generation with OpenAI"""
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
            data=recipe_request,
            timeout=60  # Set timeout to 60 seconds for OpenAI API
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"Generated recipe with ID: {self.recipe_id}")
            
            # Verify recipe structure
            required_fields = ['title', 'description', 'ingredients', 'instructions', 'prep_time', 'cook_time']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"⚠️ Recipe is missing required fields: {', '.join(missing_fields)}")
                return False
            
            print(f"✅ Recipe generated successfully with title: {response['title']}")
            print(f"✅ Recipe has {len(response['ingredients'])} ingredients and {len(response['instructions'])} instructions")
            return True
        
        return False

    def test_grocery_cart_options(self):
        """Test grocery cart options endpoint"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Grocery Cart Options",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": self.recipe_id, "user_id": self.user_id}
        )
        
        if success and 'id' in response:
            self.cart_options_id = response['id']
            print(f"Created grocery cart options with ID: {self.cart_options_id}")
            
            # Verify cart options structure
            if 'ingredient_options' not in response:
                print("⚠️ Response is missing ingredient_options field")
                return False
            
            ingredient_options = response['ingredient_options']
            print(f"✅ Cart options include {len(ingredient_options)} ingredients")
            
            # Check if each ingredient has product options with prices
            for i, ingredient_option in enumerate(ingredient_options):
                if 'options' not in ingredient_option:
                    print(f"⚠️ Ingredient {i+1} is missing options field")
                    continue
                
                options = ingredient_option['options']
                print(f"  Ingredient: {ingredient_option.get('ingredient_name', 'Unknown')} - {len(options)} product options")
                
                # Check if each product has a price
                for j, product in enumerate(options):
                    if 'price' not in product:
                        print(f"  ⚠️ Product {j+1} is missing price field")
                    else:
                        print(f"  ✅ Product: {product.get('name', 'Unknown')} - Price: ${product['price']}")
            
            return True
        
        return False

    def test_custom_cart(self):
        """Test creating a custom cart with selected products"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        # Create a custom cart directly
        custom_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "products": [
                {
                    "ingredient_name": "pasta",
                    "product_id": "123456789",
                    "name": "Barilla Pasta Penne 16oz",
                    "price": 1.99,
                    "quantity": 1
                },
                {
                    "ingredient_name": "tomatoes",
                    "product_id": "987654321",
                    "name": "Fresh Roma Tomatoes 2lb",
                    "price": 2.49,
                    "quantity": 2
                },
                {
                    "ingredient_name": "garlic",
                    "product_id": "789123456",
                    "name": "Fresh Garlic Bulb 3oz",
                    "price": 0.98,
                    "quantity": 1
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
            
            # Verify custom cart structure
            if 'products' not in response:
                print("⚠️ Response is missing products field")
                return False
            
            if 'total_price' not in response:
                print("⚠️ Response is missing total_price field")
                return False
            
            if 'walmart_url' not in response:
                print("⚠️ Response is missing walmart_url field")
                return False
            
            products = response['products']
            total_price = response['total_price']
            walmart_url = response['walmart_url']
            
            print(f"✅ Custom cart includes {len(products)} products")
            print(f"✅ Total price: ${total_price}")
            print(f"✅ Walmart URL: {walmart_url}")
            
            # Check if all product IDs are in the Walmart URL
            product_ids = [p['product_id'] for p in custom_cart_data['products']]
            all_ids_in_url = all(pid in walmart_url for pid in product_ids)
            
            if all_ids_in_url:
                print("✅ All product IDs included in Walmart URL")
            else:
                print("⚠️ Not all product IDs found in Walmart URL")
            
            # Check if the URL is properly formatted
            if 'affil.walmart.com' in walmart_url and 'items=' in walmart_url:
                print("✅ Walmart URL correctly formatted")
            else:
                print("⚠️ Walmart URL format may be incorrect")
            
            return True
        
        return False

def main():
    print("=" * 50)
    print("Focused Backend API Test for Grocery Cart Functionality")
    print("=" * 50)
    
    tester = FocusedBackendTester()
    
    # Test API root
    tester.test_api_root()
    
    # Create test user
    user_created = tester.create_test_user()
    if not user_created:
        print("❌ Failed to create test user - cannot continue testing")
        return 1
    
    # Test recipe generation
    recipe_generated = tester.test_recipe_generation()
    if not recipe_generated:
        print("❌ Failed to generate recipe - cannot continue testing")
        return 1
    
    # Test grocery cart options
    tester.test_grocery_cart_options()
    
    # Test custom cart
    tester.test_custom_cart()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())