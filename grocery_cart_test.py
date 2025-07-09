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

class GroceryCartTester:
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

    def test_recipe_generation_with_user_ingredients(self):
        """Test recipe generation with the user's reported ingredients"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        # Using the ingredients from the user's report
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "mexican",
            "dietary_preferences": [],
            "ingredients_on_hand": [
                "bell pepper",
                "cumin",
                "chili powder",
                "tortillas",
                "avocado",
                "cheese",
                "cilantro",
                "lime",
                "salt",
                "pepper",
                "chicken"
            ],
            "prep_time_max": 30,
            "servings": 4,
            "difficulty": "medium"
        }
        
        success, response = self.run_test(
            "Generate Recipe with User's Ingredients",
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
            
            # Print the ingredients to verify they match what we expect
            print("\nRecipe Ingredients:")
            for i, ingredient in enumerate(response['ingredients']):
                print(f"  {i+1}. {ingredient}")
                
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
            
        # Create a custom cart with products matching the user's ingredients
        custom_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "products": [
                {
                    "ingredient_name": "bell pepper",
                    "product_id": "999123456",
                    "name": "Fresh Bell Pepper",
                    "price": 0.99,
                    "quantity": 1
                },
                {
                    "ingredient_name": "cumin",
                    "product_id": "999654321",
                    "name": "Ground Cumin",
                    "price": 2.49,
                    "quantity": 1
                },
                {
                    "ingredient_name": "chili powder",
                    "product_id": "999789123",
                    "name": "Chili Powder",
                    "price": 1.99,
                    "quantity": 1
                },
                {
                    "ingredient_name": "tortillas",
                    "product_id": "445566778",
                    "name": "Mission Corn Tortillas 30ct",
                    "price": 2.98,
                    "quantity": 1
                },
                {
                    "ingredient_name": "avocado",
                    "product_id": "999456789",
                    "name": "Fresh Avocado",
                    "price": 1.49,
                    "quantity": 1
                },
                {
                    "ingredient_name": "cheese",
                    "product_id": "456789123",
                    "name": "Great Value Shredded Cheddar Cheese 8oz",
                    "price": 2.84,
                    "quantity": 1
                },
                {
                    "ingredient_name": "cilantro",
                    "product_id": "999321654",
                    "name": "Fresh Cilantro Bunch",
                    "price": 0.99,
                    "quantity": 1
                },
                {
                    "ingredient_name": "lime",
                    "product_id": "999987654",
                    "name": "Fresh Lime",
                    "price": 0.50,
                    "quantity": 1
                },
                {
                    "ingredient_name": "salt",
                    "product_id": "147258369",
                    "name": "Morton Salt 26oz",
                    "price": 1.24,
                    "quantity": 1
                },
                {
                    "ingredient_name": "pepper",
                    "product_id": "147258370",
                    "name": "Black Pepper Ground 3oz",
                    "price": 2.68,
                    "quantity": 1
                },
                {
                    "ingredient_name": "chicken",
                    "product_id": "556677889",
                    "name": "Great Value Chicken Breast 2.5lb",
                    "price": 8.99,
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
    print("=" * 80)
    print("Grocery Cart Functionality Test with User's Reported Ingredients")
    print("=" * 80)
    
    tester = GroceryCartTester()
    
    # Test API root
    tester.test_api_root()
    
    # Create test user
    user_created = tester.create_test_user()
    if not user_created:
        print("❌ Failed to create test user - cannot continue testing")
        return 1
    
    # Test recipe generation with user's ingredients
    recipe_generated = tester.test_recipe_generation_with_user_ingredients()
    if not recipe_generated:
        print("❌ Failed to generate recipe - cannot continue testing")
        return 1
    
    # Test grocery cart options
    cart_options_success = tester.test_grocery_cart_options()
    
    # Test custom cart
    custom_cart_success = tester.test_custom_cart()
    
    # Print results
    print("\n" + "=" * 80)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 80)
    
    if cart_options_success and custom_cart_success:
        print("✅ GROCERY CART FUNCTIONALITY IS WORKING CORRECTLY")
        print("The 'Generate Walmart Shopping Cart' button should be working properly.")
    else:
        print("❌ GROCERY CART FUNCTIONALITY HAS ISSUES")
        if not cart_options_success:
            print("- The cart-options endpoint is not working correctly")
        if not custom_cart_success:
            print("- The custom-cart endpoint is not working correctly")
        print("This explains why the 'Generate Walmart Shopping Cart' button is not working.")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())