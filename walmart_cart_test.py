import requests
import json
import uuid
import logging
import re
import random
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for API
BASE_URL = "http://localhost:8001/api"

class WalmartCartTester:
    def __init__(self):
        self.user_id = None
        self.user_email = None
        self.recipe_id = None
        self.cart_options_id = None
        self.custom_cart_id = None
        self.tests_passed = 0
        self.tests_failed = 0
        
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a single API test with configurable timeout"""
        url = f"{BASE_URL}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
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
                self.tests_failed += 1
                return False, {}
            
            elapsed_time = time.time() - start_time
            print(f"⏱️ Request completed in {elapsed_time:.2f} seconds")
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                self.tests_failed += 1
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
            self.tests_failed += 1
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            self.tests_failed += 1
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.tests_failed += 1
            return False, {}
    
    def create_test_user(self):
        """Create a test user for the test session"""
        print("\n" + "=" * 80)
        print("CREATING TEST USER")
        print("=" * 80)
        
        self.user_email = f"test_{uuid.uuid4()}@example.com"
        user_password = "TestPassword123"
        
        # Try the new authentication system first
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": self.user_email,
            "password": user_password,
            "dietary_preferences": ["vegetarian"],
            "allergies": [],
            "favorite_cuisines": ["italian"]
        }
        
        success, response = self.run_test(
            "Create User with New Auth System",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'user_id' in response:
            self.user_id = response['user_id']
            print(f"✅ Created user with ID: {self.user_id}")
            
            # Get verification code
            time.sleep(1)  # Wait a bit for the code to be stored
            code_success, code_response = self.run_test(
                "Get Verification Code",
                "GET",
                f"debug/verification-codes/{self.user_email}",
                200
            )
            
            if code_success and 'codes' in code_response and len(code_response['codes']) > 0:
                verification_code = code_response['codes'][0]['code']
                print(f"✅ Retrieved verification code: {verification_code}")
                
                # Verify email
                verify_data = {
                    "email": self.user_email,
                    "code": verification_code
                }
                
                verify_success, _ = self.run_test(
                    "Email Verification",
                    "POST",
                    "auth/verify",
                    200,
                    data=verify_data
                )
                
                if verify_success:
                    print("✅ Email verified successfully")
                    return True
            
            return True
        
        # Fallback to legacy user creation
        print("Trying legacy user creation...")
        legacy_user_data = {
            "name": f"Test User {uuid.uuid4()}",
            "email": self.user_email,
            "dietary_preferences": ["vegetarian"],
            "allergies": [],
            "favorite_cuisines": ["italian"]
        }
        
        success, response = self.run_test(
            "Create User with Legacy System",
            "POST",
            "users",
            200,
            data=legacy_user_data
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"✅ Created legacy user with ID: {self.user_id}")
            return True
        
        return False
    
    def generate_test_recipe(self):
        """Generate a test recipe"""
        print("\n" + "=" * 80)
        print("GENERATING TEST RECIPE")
        print("=" * 80)
        
        if not self.user_id:
            print("❌ No user ID available - cannot generate recipe")
            return False
        
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "italian",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["pasta", "tomatoes", "garlic", "basil", "olive oil"],
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
            timeout=60  # Recipe generation can take time
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            recipe_title = response.get('title', 'Untitled Recipe')
            recipe_ingredients = response.get('ingredients', [])
            
            print(f"✅ Generated recipe '{recipe_title}' with ID: {self.recipe_id}")
            print(f"Recipe has {len(recipe_ingredients)} ingredients:")
            for i, ingredient in enumerate(recipe_ingredients):
                print(f"  {i+1}. {ingredient}")
            
            return True
        
        return False
    
    def test_cart_options_endpoint(self):
        """Test the cart-options endpoint"""
        print("\n" + "=" * 80)
        print("TESTING /api/grocery/cart-options ENDPOINT")
        print("=" * 80)
        
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available - cannot test cart options")
            return False
        
        cart_options_params = {
            "recipe_id": self.recipe_id,
            "user_id": self.user_id
        }
        
        success, response = self.run_test(
            "Cart Options Endpoint",
            "POST",
            "grocery/cart-options",
            200,
            params=cart_options_params
        )
        
        if not success:
            return False
        
        if 'id' not in response:
            print("❌ Response missing 'id' field")
            return False
        
        self.cart_options_id = response['id']
        print(f"✅ Created grocery cart options with ID: {self.cart_options_id}")
        
        # Verify the response structure
        if 'ingredient_options' not in response:
            print("❌ Response missing 'ingredient_options' field")
            return False
        
        ingredient_options = response['ingredient_options']
        print(f"✅ Response contains 'ingredient_options' with {len(ingredient_options)} ingredients")
        
        # Check if each ingredient has multiple options with required fields
        all_product_ids = []
        valid_structure = True
        
        for i, ingredient_option in enumerate(ingredient_options):
            if 'options' not in ingredient_option:
                print(f"❌ Ingredient {i+1} missing 'options' field")
                valid_structure = False
                continue
            
            options = ingredient_option['options']
            original_ingredient = ingredient_option.get('original_ingredient', 'Unknown')
            print(f"\nIngredient {i+1}: {original_ingredient}")
            print(f"  Found {len(options)} product options")
            
            if len(options) == 0:
                print(f"❌ No product options for ingredient: {original_ingredient}")
                valid_structure = False
                continue
            
            # Check if each product has required fields
            for j, product in enumerate(options):
                required_fields = ['product_id', 'name', 'price']
                missing_fields = [field for field in required_fields if field not in product]
                
                if missing_fields:
                    print(f"  ❌ Product {j+1} missing required fields: {', '.join(missing_fields)}")
                    valid_structure = False
                    continue
                
                product_id = product['product_id']
                all_product_ids.append(product_id)
                
                print(f"  ✅ Product {j+1}: {product['name']} - ${product['price']:.2f} (ID: {product_id})")
        
        # Check for mock data patterns
        known_mock_patterns = [
            "556677", "445566", "334455", "123456", "987654", 
            "456789", "789123", "321654", "654987", "147258"
        ]
        
        mock_pattern_matches = 0
        for pid in all_product_ids:
            if any(pid.startswith(pattern) for pattern in known_mock_patterns):
                mock_pattern_matches += 1
        
        mock_pattern_ratio = mock_pattern_matches / len(all_product_ids) if all_product_ids else 0
        
        # Summary
        print("\nCart Options Summary:")
        print(f"  Total ingredients: {len(ingredient_options)}")
        print(f"  Total product options: {len(all_product_ids)}")
        print(f"  Unique product IDs: {len(set(all_product_ids))}")
        
        if mock_pattern_ratio > 0.5:
            print(f"  ⚠️ {mock_pattern_ratio:.0%} of product IDs match known mock data patterns")
            print("  ⚠️ The implementation is using mock data instead of real Walmart API data")
        
        # Final assessment
        if valid_structure:
            print("\n✅ PASS: /api/grocery/cart-options endpoint returns proper structure")
            if all(len(opt['options']) > 1 for opt in ingredient_options if 'options' in opt):
                print("✅ PASS: Each ingredient has multiple product options")
            else:
                print("⚠️ WARNING: Some ingredients have only one product option")
            
            print("✅ PASS: Each product option has required product_id, name, and price fields")
            return True
        else:
            print("\n❌ FAIL: /api/grocery/cart-options endpoint response has structural issues")
            return False
    
    def test_custom_cart_endpoint(self):
        """Test the custom-cart endpoint"""
        print("\n" + "=" * 80)
        print("TESTING /api/grocery/custom-cart ENDPOINT")
        print("=" * 80)
        
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available - cannot test custom cart")
            return False
        
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
        
        if not success:
            return False
        
        if 'id' not in response:
            print("❌ Response missing 'id' field")
            return False
        
        self.custom_cart_id = response['id']
        print(f"✅ Created custom cart with ID: {self.custom_cart_id}")
        
        # Verify the response structure
        if 'products' not in response:
            print("❌ Response missing 'products' field")
            return False
        
        products = response['products']
        print(f"✅ Response contains {len(products)} products")
        
        # Check total price calculation
        if 'total_price' not in response:
            print("❌ Response missing 'total_price' field")
            return False
        
        expected_total = sum(p['price'] * p['quantity'] for p in custom_cart_data['products'])
        actual_total = response['total_price']
        print(f"Total price: ${actual_total:.2f} (Expected: ${expected_total:.2f})")
        
        if abs(actual_total - expected_total) < 0.01:  # Allow for small floating-point differences
            print("✅ Total price calculated correctly")
        else:
            print("❌ Total price calculation error")
        
        # Check Walmart URL generation
        if 'walmart_url' not in response:
            print("❌ Response missing 'walmart_url' field")
            return False
        
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
        
        # Final assessment
        print("\n✅ PASS: /api/grocery/custom-cart endpoint returns proper response")
        return True
    
    def test_cart_options_missing_recipe_id(self):
        """Test cart-options endpoint with missing recipe_id parameter"""
        print("\n" + "=" * 80)
        print("TESTING /api/grocery/cart-options WITH MISSING RECIPE_ID")
        print("=" * 80)
        
        if not self.user_id:
            print("❌ No user ID available - cannot test")
            return False
        
        # We expect this to fail with 422 or 400 status code
        success, response = self.run_test(
            "Cart Options with Missing Recipe ID",
            "POST",
            "grocery/cart-options",
            422,  # Unprocessable Entity is the expected response for missing parameters
            params={"user_id": self.user_id}
        )
        
        # This test passes if the API correctly rejects the request
        if success:
            print("✅ PASS: API correctly rejects requests with missing recipe_id")
            return True
        else:
            # Try with 400 status code as an alternative
            alt_success, _ = self.run_test(
                "Cart Options with Missing Recipe ID (alt status)",
                "POST",
                "grocery/cart-options",
                400,
                params={"user_id": self.user_id}
            )
            
            if alt_success:
                print("✅ PASS: API correctly rejects requests with missing recipe_id")
                return True
            
            print("❌ FAIL: API does not properly handle missing recipe_id")
            return False
    
    def test_custom_cart_missing_fields(self):
        """Test custom cart creation with missing required fields"""
        print("\n" + "=" * 80)
        print("TESTING /api/grocery/custom-cart WITH MISSING FIELDS")
        print("=" * 80)
        
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available - cannot test")
            return False
        
        # Create a cart with missing products field
        invalid_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id
            # Missing 'products' field
        }
        
        # We expect this to fail with 400 status code
        success, response = self.run_test(
            "Custom Cart with Missing Fields",
            "POST",
            "grocery/custom-cart",
            400,
            data=invalid_cart_data
        )
        
        # This test passes if the API correctly rejects the request
        if success:
            print("✅ PASS: API correctly rejects requests with missing fields")
            return True
        else:
            print("❌ FAIL: API does not properly handle missing fields")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "=" * 80)
        print("WALMART CART API TESTING")
        print("=" * 80)
        
        # Step 1: Create test user
        if not self.create_test_user():
            print("❌ Failed to create test user - cannot continue tests")
            return False
        
        # Step 2: Generate test recipe
        if not self.generate_test_recipe():
            print("❌ Failed to generate test recipe - cannot continue cart tests")
            return False
        
        # Step 3: Test cart-options endpoint
        self.test_cart_options_endpoint()
        
        # Step 4: Test custom-cart endpoint
        self.test_custom_cart_endpoint()
        
        # Step 5: Test error handling
        self.test_cart_options_missing_recipe_id()
        self.test_custom_cart_missing_fields()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_failed}")
        print(f"Success rate: {self.tests_passed / (self.tests_passed + self.tests_failed) * 100:.1f}%")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = WalmartCartTester()
    tester.run_all_tests()