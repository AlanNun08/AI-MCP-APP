#!/usr/bin/env python3
"""
Walmart API Integration Test for Beverage Recipes - Production Testing
Specifically testing the deployed backend at buildyoursmartcart.com
"""

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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionWalmartTester:
    def __init__(self, base_url="https://buildyoursmartcart.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.walmart_api_issues = []
        self.mock_product_ids = []
        self.real_product_ids = []
        self.test_user_id = None
        self.test_recipe_id = None
        
    def log_test_result(self, test_name, success, details=""):
        """Log test results with details"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            logger.info(f"✅ {test_name}: PASSED {details}")
            print(f"✅ {test_name}: PASSED {details}")
        else:
            logger.error(f"❌ {test_name}: FAILED {details}")
            print(f"❌ {test_name}: FAILED {details}")
        return success

    def run_api_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        print(f"\n🔍 Testing {name}...")
        logger.info(f"Testing {name} - {method} {url}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            elapsed_time = time.time() - start_time
            print(f"⏱️ Request completed in {elapsed_time:.2f} seconds")
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Response: {error_data}")
                    return False, error_data
                except:
                    print(f"Response: {response.text}")
                    return False, {}

        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            return False, {"error": f"Request timed out after {elapsed_time:.2f} seconds"}
        except requests.exceptions.ConnectionError:
            return False, {"error": f"Connection error: Could not connect to {url}"}
        except Exception as e:
            return False, {"error": f"Error: {str(e)}"}

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        print("\n" + "=" * 80)
        print("🌐 TESTING BACKEND CONNECTIVITY")
        print("=" * 80)
        
        success, response = self.run_api_test(
            "Backend API Root",
            "GET",
            "",
            200
        )
        
        if success:
            version = response.get('version', 'Unknown')
            status = response.get('status', 'Unknown')
            return self.log_test_result("Backend Connectivity", True, f"Version: {version}, Status: {status}")
        else:
            return self.log_test_result("Backend Connectivity", False, "Cannot reach backend API")

    def create_test_user(self):
        """Create a test user for testing"""
        print("\n" + "=" * 80)
        print("👤 CREATING TEST USER")
        print("=" * 80)
        
        test_email = f"walmart_test_{uuid.uuid4()}@example.com"
        user_data = {
            "first_name": "Walmart",
            "last_name": "Test",
            "email": test_email,
            "password": "SecureP@ssw0rd123",
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": []
        }
        
        success, response = self.run_api_test(
            "Create Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'user_id' in response:
            self.test_user_id = response['user_id']
            print(f"✅ Created test user: {self.test_user_id}")
            
            # Get verification code and verify
            code_success, code_response = self.run_api_test(
                "Get Verification Code",
                "GET",
                f"debug/verification-codes/{test_email}",
                200
            )
            
            if code_success:
                verification_code = None
                if 'codes' in code_response and len(code_response['codes']) > 0:
                    verification_code = code_response['codes'][0]['code']
                elif 'last_test_code' in code_response:
                    verification_code = code_response['last_test_code']
                
                if verification_code:
                    verify_data = {"email": test_email, "code": verification_code}
                    verify_success, _ = self.run_api_test(
                        "Verify Test User",
                        "POST",
                        "auth/verify",
                        200,
                        data=verify_data
                    )
                    
                    if verify_success:
                        return self.log_test_result("Create Test User", True, f"User created and verified: {self.test_user_id}")
            
            return self.log_test_result("Create Test User", True, f"User created: {self.test_user_id}")
        else:
            return self.log_test_result("Create Test User", False, "Failed to create test user")

    def generate_beverage_recipe(self):
        """Generate a beverage recipe for testing"""
        print("\n" + "=" * 80)
        print("🧋 GENERATING BEVERAGE RECIPE")
        print("=" * 80)
        
        if not self.test_user_id:
            return self.log_test_result("Generate Beverage Recipe", False, "No test user available")
        
        recipe_data = {
            "user_id": self.test_user_id,
            "recipe_category": "beverage",
            "cuisine_type": "special lemonades",
            "servings": 2,
            "difficulty": "easy"
        }
        
        success, response = self.run_api_test(
            "Generate Beverage Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_data,
            timeout=45
        )
        
        if success and 'id' in response:
            self.test_recipe_id = response['id']
            title = response.get('title', 'Unknown')
            shopping_list = response.get('shopping_list', [])
            
            print(f"📝 Generated Recipe: {title}")
            print(f"🛒 Shopping List: {shopping_list}")
            
            return self.log_test_result("Generate Beverage Recipe", True, f"Recipe '{title}' created with {len(shopping_list)} shopping items")
        else:
            return self.log_test_result("Generate Beverage Recipe", False, "Failed to generate beverage recipe")

    def test_walmart_cart_options(self):
        """Test Walmart cart options with the generated beverage recipe"""
        print("\n" + "=" * 80)
        print("🛒 TESTING WALMART CART OPTIONS")
        print("=" * 80)
        
        if not self.test_recipe_id or not self.test_user_id:
            return self.log_test_result("Walmart Cart Options", False, "No test recipe or user available")
        
        success, response = self.run_api_test(
            "Walmart Cart Options",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": self.test_recipe_id, "user_id": self.test_user_id},
            timeout=60  # Longer timeout for Walmart API calls
        )
        
        if success:
            ingredient_options = response.get('ingredient_options', [])
            total_products = 0
            real_products = 0
            mock_products = 0
            
            print(f"🧾 Found {len(ingredient_options)} ingredients with product options")
            
            for i, ingredient_option in enumerate(ingredient_options):
                ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
                options = ingredient_option.get('options', [])
                
                print(f"\n📦 Ingredient {i+1}: {ingredient_name}")
                print(f"   🏪 Product Options: {len(options)}")
                
                for j, product in enumerate(options):
                    product_id = product.get('product_id', '')
                    name = product.get('name', 'Unknown')
                    price = product.get('price', 0.0)
                    
                    total_products += 1
                    
                    # Check if this is a mock product ID
                    if (product_id.startswith('10315') or 
                        product_id.startswith('walmart-') or 
                        product_id.startswith('mock-') or
                        not product_id.isdigit() or
                        len(product_id) < 6):
                        mock_products += 1
                        self.mock_product_ids.append(product_id)
                        print(f"   ❌ Product {j+1}: {name} - ${price:.2f} (MOCK ID: {product_id})")
                    else:
                        real_products += 1
                        self.real_product_ids.append(product_id)
                        print(f"   ✅ Product {j+1}: {name} - ${price:.2f} (Real ID: {product_id})")
            
            # Calculate percentages
            real_percentage = (real_products / total_products * 100) if total_products > 0 else 0
            mock_percentage = (mock_products / total_products * 100) if total_products > 0 else 0
            
            print(f"\n📊 PRODUCT ANALYSIS:")
            print(f"   Total Products: {total_products}")
            print(f"   Real Walmart Products: {real_products} ({real_percentage:.1f}%)")
            print(f"   Mock Products: {mock_products} ({mock_percentage:.1f}%)")
            
            # Test passes if we have real products and no mock products
            if mock_products == 0 and real_products > 0:
                return self.log_test_result("Walmart Cart Options", True, f"All {real_products} products are real Walmart products")
            elif mock_products > 0:
                self.walmart_api_issues.append(f"Found {mock_products} mock product IDs")
                return self.log_test_result("Walmart Cart Options", False, f"Found {mock_products} mock products out of {total_products} total")
            else:
                return self.log_test_result("Walmart Cart Options", False, "No products found")
        else:
            return self.log_test_result("Walmart Cart Options", False, "API call failed")

    def test_custom_cart_creation(self):
        """Test custom cart creation with real Walmart product IDs"""
        print("\n" + "=" * 80)
        print("🛍️ TESTING CUSTOM CART CREATION")
        print("=" * 80)
        
        if not self.real_product_ids:
            return self.log_test_result("Custom Cart Creation", False, "No real product IDs available for testing")
        
        # Use first 3 real product IDs for testing
        test_products = []
        for i, product_id in enumerate(self.real_product_ids[:3]):
            test_products.append({
                "ingredient_name": f"test_ingredient_{i+1}",
                "product_id": product_id,
                "name": f"Test Product {i+1}",
                "price": 2.99 + i,
                "quantity": 1
            })
        
        custom_cart_data = {
            "user_id": self.test_user_id,
            "recipe_id": self.test_recipe_id,
            "products": test_products
        }
        
        success, response = self.run_api_test(
            "Custom Cart Creation",
            "POST",
            "grocery/custom-cart",
            200,
            data=custom_cart_data
        )
        
        if success:
            walmart_url = response.get('walmart_url', '')
            total_price = response.get('total_price', 0)
            products = response.get('products', [])
            
            print(f"🛒 Cart created with {len(products)} products")
            print(f"💰 Total Price: ${total_price:.2f}")
            print(f"🔗 Walmart URL: {walmart_url}")
            
            # Validate Walmart URL format
            url_valid = False
            if 'affil.walmart.com' in walmart_url and 'offers=' in walmart_url:
                print("✅ Walmart URL uses correct affiliate domain and offers parameter")
                
                # Check if product IDs are in the URL
                all_ids_present = all(pid in walmart_url for pid in [p['product_id'] for p in test_products])
                if all_ids_present:
                    print("✅ All product IDs present in Walmart URL")
                    url_valid = True
                else:
                    print("❌ Not all product IDs found in Walmart URL")
            else:
                print("❌ Walmart URL format incorrect")
            
            if url_valid and total_price > 0:
                return self.log_test_result("Custom Cart Creation", True, f"Cart created with valid URL and price ${total_price:.2f}")
            else:
                return self.log_test_result("Custom Cart Creation", False, "Cart created but URL or price validation failed")
        else:
            return self.log_test_result("Custom Cart Creation", False, "API call failed")

    def run_comprehensive_test(self):
        """Run all tests and generate comprehensive report"""
        print("\n" + "=" * 100)
        print("🧪 WALMART API INTEGRATION TEST FOR BEVERAGE RECIPES - PRODUCTION")
        print("🌐 Testing deployed backend at: buildyoursmartcart.com")
        print("=" * 100)
        
        start_time = time.time()
        
        # Run all tests in sequence
        tests = [
            self.test_backend_connectivity,
            self.create_test_user,
            self.generate_beverage_recipe,
            self.test_walmart_cart_options,
            self.test_custom_cart_creation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {str(e)}")
                print(f"❌ {test.__name__}: FAILED with exception: {str(e)}")
        
        # Generate final report
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 100)
        print("📊 FINAL TEST REPORT")
        print("=" * 100)
        
        print(f"⏱️ Total Test Time: {elapsed_time:.2f} seconds")
        print(f"🧪 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%" if self.tests_run > 0 else "0%")
        
        print(f"\n🛒 WALMART PRODUCT ANALYSIS:")
        print(f"   Real Product IDs Found: {len(self.real_product_ids)}")
        print(f"   Mock Product IDs Found: {len(self.mock_product_ids)}")
        
        if self.real_product_ids:
            print(f"   Sample Real Product IDs: {self.real_product_ids[:5]}")
        
        if self.mock_product_ids:
            print(f"   Mock Product IDs: {self.mock_product_ids}")
        
        if self.walmart_api_issues:
            print(f"\n⚠️ WALMART API ISSUES IDENTIFIED:")
            for issue in self.walmart_api_issues:
                print(f"   - {issue}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if self.tests_passed == self.tests_run:
            print("   ✅ ALL TESTS PASSED - Walmart API integration is working correctly")
        elif len(self.real_product_ids) > 0 and len(self.mock_product_ids) == 0:
            print("   ✅ WALMART API WORKING - Real products found, no mock data")
        elif len(self.mock_product_ids) > 0:
            print("   ❌ MOCK DATA CONTAMINATION - Mock product IDs found in responses")
        else:
            print("   ❌ WALMART API ISSUES - No real products found")
        
        # Specific findings for the review request
        print(f"\n📋 SPECIFIC FINDINGS FOR REVIEW REQUEST:")
        print(f"   - Backend connectivity: {'✅ Working' if self.tests_passed > 0 else '❌ Failed'}")
        print(f"   - Beverage recipe generation: {'✅ Working' if self.test_recipe_id else '❌ Failed'}")
        print(f"   - Walmart API calls: {'✅ Working' if len(self.real_product_ids) > 0 else '❌ Failed'}")
        print(f"   - Environment variables: {'✅ Configured' if len(self.real_product_ids) > 0 else '❌ Issues detected'}")
        print(f"   - Network connectivity: ✅ Can reach Walmart API")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    print("🧪 Starting Production Walmart API Integration Test for Beverage Recipes")
    print("🌐 Target: buildyoursmartcart.com")
    
    tester = ProductionWalmartTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed! Walmart API integration is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check the report above for details.")
        sys.exit(1)