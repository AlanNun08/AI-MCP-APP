#!/usr/bin/env python3
"""
Walmart Integration Test - Verify No Mock Data Usage
This test specifically validates that the Walmart integration only returns real product IDs
and no mock data is used in affiliate links.
"""

import requests
import json
import time
import uuid
import logging
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WalmartIntegrationTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.recipe_id = None
        self.mock_product_ids_found = []
        self.real_product_ids_found = []
        
        # Test user credentials
        self.test_email = f"walmart_test_{uuid.uuid4()}@example.com"
        self.test_password = "SecureP@ssw0rd123"

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a single API test"""
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
            else:
                print(f"❌ Unsupported method: {method}")
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
            print(f"❌ Failed - Request timed out after {elapsed_time:.2f} seconds")
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def validate_product_id(self, product_id, ingredient_name="unknown"):
        """Validate that a product ID is from real Walmart API (not mock data)"""
        if not product_id:
            print(f"    ❌ Empty product ID for {ingredient_name}")
            return False
            
        # Convert to string for validation
        product_id_str = str(product_id)
        
        # Check for mock patterns
        mock_patterns = [
            'walmart-',
            'mock-',
            '10315',  # Common mock ID pattern
            'test-',
            'demo-'
        ]
        
        for pattern in mock_patterns:
            if product_id_str.startswith(pattern):
                print(f"    ❌ MOCK PRODUCT ID DETECTED: {product_id_str} for {ingredient_name} (pattern: {pattern})")
                self.mock_product_ids_found.append({
                    'product_id': product_id_str,
                    'ingredient': ingredient_name,
                    'pattern': pattern
                })
                return False
        
        # Check if product ID is numeric and at least 6 digits (real Walmart format)
        if not product_id_str.isdigit():
            print(f"    ❌ Non-numeric product ID: {product_id_str} for {ingredient_name}")
            return False
            
        if len(product_id_str) < 6:
            print(f"    ❌ Product ID too short: {product_id_str} for {ingredient_name} (less than 6 digits)")
            return False
        
        print(f"    ✅ Valid real product ID: {product_id_str} for {ingredient_name}")
        self.real_product_ids_found.append({
            'product_id': product_id_str,
            'ingredient': ingredient_name
        })
        return True

    def setup_test_user(self):
        """Create and verify a test user for testing"""
        print("\n" + "=" * 60)
        print("Setting up test user for Walmart integration testing")
        print("=" * 60)
        
        # Register user
        user_data = {
            "first_name": "Walmart",
            "last_name": "Tester",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": ["italian"]
        }
        
        success, response = self.run_test(
            "Register Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not success:
            return False
            
        self.user_id = response.get('user_id')
        if not self.user_id:
            print("❌ No user_id in registration response")
            return False
            
        # Get verification code
        code_success, code_response = self.run_test(
            "Get Verification Code",
            "GET",
            f"debug/verification-codes/{self.test_email}",
            200
        )
        
        if not code_success:
            return False
            
        verification_code = None
        if 'codes' in code_response and len(code_response['codes']) > 0:
            verification_code = code_response['codes'][0]['code']
        elif 'last_test_code' in code_response:
            verification_code = code_response['last_test_code']
            
        if not verification_code:
            print("❌ No verification code found")
            return False
            
        # Verify email
        verify_data = {
            "email": self.test_email,
            "code": verification_code
        }
        
        verify_success, _ = self.run_test(
            "Verify Email",
            "POST",
            "auth/verify",
            200,
            data=verify_data
        )
        
        return verify_success

    def create_test_recipe(self, recipe_type="pasta", ingredients=None):
        """Create a test recipe with common ingredients"""
        if not self.user_id:
            print("❌ No user ID available")
            return False
            
        if ingredients is None:
            if recipe_type == "pasta":
                ingredients = ["pasta", "tomatoes", "garlic", "olive oil", "cheese"]
            elif recipe_type == "coffee":
                ingredients = ["coffee beans", "milk", "sugar"]
            else:
                ingredients = ["chicken", "rice", "vegetables"]
        
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": "cuisine" if recipe_type != "coffee" else "beverage",
            "cuisine_type": "italian" if recipe_type == "pasta" else recipe_type,
            "dietary_preferences": [],
            "ingredients_on_hand": ingredients,
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "easy"
        }
        
        success, response = self.run_test(
            f"Generate {recipe_type.title()} Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"✅ Created recipe with ID: {self.recipe_id}")
            
            # Validate shopping list exists and is clean
            if 'shopping_list' in response:
                shopping_list = response['shopping_list']
                print(f"✅ Recipe has shopping list with {len(shopping_list)} items: {shopping_list}")
                
                # Check for quantities/measurements in shopping list (should be clean)
                for item in shopping_list:
                    if re.search(r'\d+\s*(cup|tbsp|tsp|oz|lb|can|jar)', item.lower()):
                        print(f"    ⚠️ Shopping list item contains measurements: '{item}'")
                    else:
                        print(f"    ✅ Clean shopping list item: '{item}'")
            else:
                print("⚠️ Recipe missing shopping_list field")
                
            return True
        return False

    def test_cart_options_real_products_only(self):
        """Test that cart-options endpoint only returns real Walmart product IDs"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available")
            return False
            
        print("\n" + "=" * 60)
        print("Testing Cart Options - Real Products Only")
        print("=" * 60)
        
        success, response = self.run_test(
            "Cart Options with Real Products Check",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": self.recipe_id, "user_id": self.user_id},
            timeout=45
        )
        
        if not success:
            return False
            
        if 'ingredient_options' not in response:
            print("❌ No ingredient_options in response")
            return False
            
        ingredient_options = response['ingredient_options']
        print(f"Found {len(ingredient_options)} ingredients with product options")
        
        total_products = 0
        valid_products = 0
        
        for ingredient_option in ingredient_options:
            ingredient_name = ingredient_option.get('ingredient_name', 'unknown')
            options = ingredient_option.get('options', [])
            
            print(f"\n🔍 Checking ingredient: {ingredient_name}")
            print(f"   Found {len(options)} product options")
            
            if len(options) == 0:
                print(f"   ✅ No products found for '{ingredient_name}' - correctly returning empty list instead of mock data")
                continue
                
            for i, product in enumerate(options):
                total_products += 1
                product_id = product.get('product_id', '')
                product_name = product.get('name', 'Unknown')
                product_price = product.get('price', 0)
                
                print(f"   Product {i+1}: {product_name} - ${product_price} (ID: {product_id})")
                
                if self.validate_product_id(product_id, ingredient_name):
                    valid_products += 1
        
        print(f"\n📊 WALMART PRODUCT VALIDATION RESULTS:")
        print(f"   Total products found: {total_products}")
        print(f"   Valid real products: {valid_products}")
        print(f"   Mock products detected: {len(self.mock_product_ids_found)}")
        
        if len(self.mock_product_ids_found) > 0:
            print(f"\n❌ MOCK PRODUCTS DETECTED:")
            for mock_product in self.mock_product_ids_found:
                print(f"   - {mock_product['product_id']} for {mock_product['ingredient']} (pattern: {mock_product['pattern']})")
            return False
        else:
            print(f"✅ NO MOCK PRODUCTS DETECTED - All product IDs are real Walmart products")
            return True

    def test_custom_cart_real_products_only(self):
        """Test that custom-cart endpoint only accepts real product IDs and generates clean affiliate URLs"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available")
            return False
            
        print("\n" + "=" * 60)
        print("Testing Custom Cart - Real Products Only")
        print("=" * 60)
        
        # Test with real product IDs
        real_products = [
            {
                "ingredient_name": "pasta",
                "product_id": "123456789",  # Real format: numeric, 9 digits
                "name": "Barilla Pasta Penne 16oz",
                "price": 1.99,
                "quantity": 1
            },
            {
                "ingredient_name": "tomatoes",
                "product_id": "987654321",  # Real format: numeric, 9 digits
                "name": "Fresh Roma Tomatoes 2lb",
                "price": 2.49,
                "quantity": 1
            }
        ]
        
        custom_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "products": real_products
        }
        
        success, response = self.run_test(
            "Custom Cart with Real Product IDs",
            "POST",
            "grocery/custom-cart",
            200,
            data=custom_cart_data
        )
        
        if not success:
            return False
            
        # Validate response
        if 'walmart_url' not in response:
            print("❌ No walmart_url in response")
            return False
            
        walmart_url = response['walmart_url']
        print(f"Generated Walmart URL: {walmart_url}")
        
        # Validate URL format
        if not walmart_url.startswith('https://affil.walmart.com/cart/addToCart?items='):
            print(f"❌ Invalid Walmart URL format: {walmart_url}")
            return False
            
        # Extract product IDs from URL
        url_product_ids = walmart_url.split('items=')[1].split(',')
        print(f"Product IDs in URL: {url_product_ids}")
        
        # Validate all product IDs in URL are real
        for product_id in url_product_ids:
            if not self.validate_product_id(product_id, "URL"):
                return False
                
        print("✅ Custom cart successfully created with real product IDs only")
        
        # Test with mock product IDs (should be rejected)
        print("\n🔍 Testing rejection of mock product IDs...")
        
        mock_products = [
            {
                "ingredient_name": "pasta",
                "product_id": "walmart-123456",  # Mock format
                "name": "Mock Pasta",
                "price": 1.99,
                "quantity": 1
            },
            {
                "ingredient_name": "tomatoes",
                "product_id": "mock-789",  # Mock format
                "name": "Mock Tomatoes",
                "price": 2.49,
                "quantity": 1
            }
        ]
        
        mock_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "products": mock_products
        }
        
        mock_success, mock_response = self.run_test(
            "Custom Cart with Mock Product IDs (Should Fail)",
            "POST",
            "grocery/custom-cart",
            400,  # Should fail with 400 error
            data=mock_cart_data
        )
        
        if mock_success:
            print("✅ Mock product IDs correctly rejected")
            return True
        else:
            # If it doesn't return 400, check if it created a cart with no products
            if 'products' in mock_response and len(mock_response['products']) == 0:
                print("✅ Mock product IDs filtered out, empty cart returned")
                return True
            else:
                print("❌ Mock product IDs were not properly rejected")
                return False

    def test_beverage_walmart_integration(self):
        """Test Walmart integration specifically for beverages"""
        print("\n" + "=" * 60)
        print("Testing Beverage Walmart Integration")
        print("=" * 60)
        
        # Create a coffee recipe
        if not self.create_test_recipe("coffee"):
            return False
            
        # Test cart options for beverage
        return self.test_cart_options_real_products_only()

    def test_ingredient_parsing_edge_cases(self):
        """Test ingredient parsing with complex recipe descriptions"""
        print("\n" + "=" * 60)
        print("Testing Ingredient Parsing Edge Cases")
        print("=" * 60)
        
        # Create recipe with complex ingredient descriptions
        complex_ingredients = [
            "1 can chickpeas, drained and rinsed",
            "1/2 cup BBQ sauce",
            "1 cup cooked quinoa",
            "1 cup mixed vegetables (bell peppers, zucchini, onions)",
            "1 avocado, sliced",
            "2 tbsp olive oil",
            "Salt and pepper to taste"
        ]
        
        if not self.create_test_recipe("complex", complex_ingredients):
            return False
            
        # Test that cart options can handle complex ingredients
        return self.test_cart_options_real_products_only()

    def run_comprehensive_walmart_test(self):
        """Run comprehensive Walmart integration test"""
        print("\n" + "=" * 80)
        print("🛒 COMPREHENSIVE WALMART INTEGRATION TEST - NO MOCK DATA")
        print("=" * 80)
        print("This test verifies that the Walmart integration only uses real product IDs")
        print("and never returns mock data in affiliate links.")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user")
            return False
            
        # Test scenarios
        test_scenarios = [
            ("Pasta Recipe Walmart Integration", lambda: self.create_test_recipe("pasta") and self.test_cart_options_real_products_only()),
            ("Coffee Recipe Walmart Integration", self.test_beverage_walmart_integration),
            ("Complex Ingredients Parsing", self.test_ingredient_parsing_edge_cases),
            ("Custom Cart Real Products Only", self.test_custom_cart_real_products_only)
        ]
        
        passed_tests = 0
        
        for test_name, test_func in test_scenarios:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    print(f"✅ {test_name} PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
        
        # Final report
        print("\n" + "=" * 80)
        print("🏁 FINAL WALMART INTEGRATION TEST REPORT")
        print("=" * 80)
        print(f"Tests run: {len(test_scenarios)}")
        print(f"Tests passed: {passed_tests}")
        print(f"Tests failed: {len(test_scenarios) - passed_tests}")
        print(f"Success rate: {(passed_tests/len(test_scenarios)*100):.1f}%")
        
        print(f"\n📊 PRODUCT ID ANALYSIS:")
        print(f"Real Walmart product IDs found: {len(self.real_product_ids_found)}")
        print(f"Mock product IDs detected: {len(self.mock_product_ids_found)}")
        
        if len(self.mock_product_ids_found) > 0:
            print(f"\n❌ CRITICAL ISSUE: Mock product IDs detected!")
            for mock_product in self.mock_product_ids_found:
                print(f"   - {mock_product['product_id']} for {mock_product['ingredient']}")
            print("\n🚨 RECOMMENDATION: Fix the Walmart integration to remove all mock data")
            return False
        else:
            print(f"\n✅ SUCCESS: No mock product IDs detected!")
            print("✅ All product IDs are real Walmart products")
            print("✅ Affiliate links will only contain authentic Walmart product IDs")
            
        if passed_tests == len(test_scenarios):
            print(f"\n🎉 ALL WALMART INTEGRATION TESTS PASSED!")
            print("✅ The system is ready for production with clean Walmart integration")
            return True
        else:
            print(f"\n⚠️ Some tests failed - review issues above")
            return False

if __name__ == "__main__":
    tester = WalmartIntegrationTester()
    success = tester.run_comprehensive_walmart_test()
    exit(0 if success else 1)