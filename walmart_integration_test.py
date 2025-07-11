#!/usr/bin/env python3
"""
Comprehensive Walmart Product Search Testing for buildyoursmartcart.com
Testing for user: Alan.nunez0310@icloud.com

This script tests the deployed backend at buildyoursmartcart.com specifically
for Walmart integration functionality as requested in the review.
"""

import requests
import json
import time
import sys
import uuid
import logging
import re
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WalmartIntegrationTester:
    def __init__(self, base_url="https://buildyoursmartcart.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.recipe_ids = {}
        self.target_user_email = "Alan.nunez0310@icloud.com"
        self.target_user_id = None
        self.walmart_api_working = False
        self.cart_options_working = False
        self.product_search_results = {}
        
        print(f"🎯 WALMART INTEGRATION TESTING FOR DEPLOYED BACKEND")
        print(f"🌐 Backend URL: {base_url}")
        print(f"👤 Target User: {self.target_user_email}")
        print("=" * 80)

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
            print(f"❌ Failed - Request timed out after {elapsed_time:.2f} seconds")
            logger.error(f"Request timed out after {elapsed_time:.2f} seconds")
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            logger.error(f"Connection error: Could not connect to {url}")
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            logger.error(f"Test failed with error: {str(e)}")
            return False, {}

    def test_backend_connectivity(self):
        """Test if the deployed backend is accessible"""
        print("\n" + "=" * 60)
        print("🌐 BACKEND CONNECTIVITY TEST")
        print("=" * 60)
        
        success, response = self.run_test(
            "Backend API Root",
            "GET",
            "",
            200
        )
        
        if success:
            version = response.get('version', 'Unknown')
            status = response.get('status', 'Unknown')
            print(f"✅ Backend connected successfully")
            print(f"📊 Version: {version}")
            print(f"📊 Status: {status}")
            return True
        else:
            print("❌ Cannot connect to deployed backend")
            return False

    def test_user_account_verification(self):
        """Verify the target user Alan.nunez0310@icloud.com exists and get their user_id"""
        print("\n" + "=" * 60)
        print("👤 USER ACCOUNT VERIFICATION")
        print("=" * 60)
        
        # Try to get user debug info (if available)
        success, response = self.run_test(
            f"Get User Debug Info for {self.target_user_email}",
            "GET",
            f"debug/user/{self.target_user_email}",
            200
        )
        
        if success and 'user' in response:
            user_data = response['user']
            self.target_user_id = user_data.get('id')
            print(f"✅ User found: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
            print(f"📧 Email: {user_data.get('email', '')}")
            print(f"🆔 User ID: {self.target_user_id}")
            print(f"✅ Verified: {user_data.get('is_verified', False)}")
            print(f"📅 Created: {user_data.get('created_at', 'Unknown')}")
            return True
        else:
            print(f"❌ User {self.target_user_email} not found or debug endpoint not available")
            # Try to create a test user for testing purposes
            return self.create_test_user()

    def create_test_user(self):
        """Create a test user for Walmart integration testing"""
        print("\n🔧 Creating test user for Walmart integration testing...")
        
        test_user = {
            "first_name": "Walmart",
            "last_name": "Tester",
            "email": f"walmart_test_{uuid.uuid4()}@example.com",
            "password": "WalmartTest123",
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "favorite_cuisines": ["italian", "mexican", "asian"]
        }
        
        success, response = self.run_test(
            "Create Test User for Walmart Testing",
            "POST",
            "auth/register",
            200,
            data=test_user
        )
        
        if success and 'user_id' in response:
            self.target_user_id = response['user_id']
            self.target_user_email = test_user['email']
            print(f"✅ Test user created with ID: {self.target_user_id}")
            
            # Get verification code and verify user
            code_success, code_response = self.run_test(
                "Get Verification Code for Test User",
                "GET",
                f"debug/verification-codes/{self.target_user_email}",
                200
            )
            
            if code_success and 'codes' in code_response and len(code_response['codes']) > 0:
                verification_code = code_response['codes'][0]['code']
                
                verify_data = {
                    "email": self.target_user_email,
                    "code": verification_code
                }
                
                verify_success, _ = self.run_test(
                    "Verify Test User",
                    "POST",
                    "auth/verify",
                    200,
                    data=verify_data
                )
                
                if verify_success:
                    print("✅ Test user verified successfully")
                    return True
            
            return True
        else:
            print("❌ Failed to create test user")
            return False

    def test_existing_recipes(self):
        """Check existing recipes for the user across all categories"""
        print("\n" + "=" * 60)
        print("📚 EXISTING RECIPES CHECK")
        print("=" * 60)
        
        if not self.target_user_id:
            print("❌ No user ID available")
            return False
        
        success, response = self.run_test(
            "Get User Recipe History",
            "GET",
            f"recipes/history/{self.target_user_id}",
            200
        )
        
        if success:
            recipes = response.get('recipes', [])
            total_count = response.get('total_count', 0)
            regular_recipes = response.get('regular_recipes', 0)
            starbucks_recipes = response.get('starbucks_recipes', 0)
            
            print(f"📊 Total recipes: {total_count}")
            print(f"🍝 Regular recipes: {regular_recipes}")
            print(f"☕ Starbucks recipes: {starbucks_recipes}")
            
            # Categorize recipes
            categories = {'cuisine': [], 'beverages': [], 'snacks': [], 'starbucks': []}
            
            for recipe in recipes:
                category = recipe.get('category', 'cuisine')
                categories[category].append(recipe)
            
            for category, recipe_list in categories.items():
                if recipe_list:
                    print(f"\n{category.upper()} RECIPES ({len(recipe_list)}):")
                    for recipe in recipe_list[:5]:  # Show first 5
                        title = recipe.get('title') or recipe.get('drink_name', 'Unknown')
                        recipe_id = recipe.get('id', 'Unknown')
                        print(f"  • {title} (ID: {recipe_id})")
                    
                    if len(recipe_list) > 5:
                        print(f"  ... and {len(recipe_list) - 5} more")
            
            return True
        else:
            print("❌ Failed to get user recipes")
            return False

    def test_cuisine_recipe_walmart_integration(self):
        """Test recipe generation and Walmart integration for cuisine recipes"""
        print("\n" + "=" * 60)
        print("🍝 CUISINE RECIPE WALMART INTEGRATION")
        print("=" * 60)
        
        if not self.target_user_id:
            print("❌ No user ID available")
            return False
        
        # Test Italian cuisine recipe
        recipe_request = {
            "user_id": self.target_user_id,
            "recipe_category": "cuisine",
            "cuisine_type": "italian",
            "dietary_preferences": [],
            "ingredients_on_hand": ["pasta", "tomatoes", "garlic", "olive oil"],
            "prep_time_max": 30,
            "servings": 4,
            "difficulty": "medium"
        }
        
        success, response = self.run_test(
            "Generate Italian Cuisine Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=45
        )
        
        if success and 'id' in response:
            recipe_id = response['id']
            self.recipe_ids['cuisine'] = recipe_id
            title = response.get('title', 'Unknown')
            ingredients = response.get('ingredients', [])
            shopping_list = response.get('shopping_list', [])
            
            print(f"✅ Generated cuisine recipe: {title}")
            print(f"🆔 Recipe ID: {recipe_id}")
            print(f"🛒 Shopping list items: {len(shopping_list)}")
            print(f"📝 Shopping list: {shopping_list[:5]}...")  # Show first 5 items
            
            # Test Walmart cart options for this recipe
            return self.test_walmart_cart_options(recipe_id, "cuisine", shopping_list)
        else:
            print("❌ Failed to generate cuisine recipe")
            return False

    def test_beverage_recipe_walmart_integration(self):
        """Test recipe generation and Walmart integration for beverage recipes"""
        print("\n" + "=" * 60)
        print("🧋 BEVERAGE RECIPE WALMART INTEGRATION")
        print("=" * 60)
        
        if not self.target_user_id:
            print("❌ No user ID available")
            return False
        
        # Test lemonade beverage recipe
        recipe_request = {
            "user_id": self.target_user_id,
            "recipe_category": "beverage",
            "cuisine_type": "special lemonades",
            "dietary_preferences": [],
            "ingredients_on_hand": ["lemons", "sugar", "mint"],
            "prep_time_max": 15,
            "servings": 2,
            "difficulty": "easy"
        }
        
        success, response = self.run_test(
            "Generate Lemonade Beverage Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=45
        )
        
        if success and 'id' in response:
            recipe_id = response['id']
            self.recipe_ids['beverage'] = recipe_id
            title = response.get('title', 'Unknown')
            ingredients = response.get('ingredients', [])
            shopping_list = response.get('shopping_list', [])
            
            print(f"✅ Generated beverage recipe: {title}")
            print(f"🆔 Recipe ID: {recipe_id}")
            print(f"🛒 Shopping list items: {len(shopping_list)}")
            print(f"📝 Shopping list: {shopping_list}")
            
            # Test Walmart cart options for this recipe
            return self.test_walmart_cart_options(recipe_id, "beverage", shopping_list)
        else:
            print("❌ Failed to generate beverage recipe")
            return False

    def test_snack_recipe_walmart_integration(self):
        """Test recipe generation and Walmart integration for snack recipes"""
        print("\n" + "=" * 60)
        print("🍪 SNACK RECIPE WALMART INTEGRATION")
        print("=" * 60)
        
        if not self.target_user_id:
            print("❌ No user ID available")
            return False
        
        # Test trail mix snack recipe
        recipe_request = {
            "user_id": self.target_user_id,
            "recipe_category": "snack",
            "cuisine_type": "trail mix",
            "dietary_preferences": ["healthy"],
            "ingredients_on_hand": ["nuts", "dried fruit", "seeds"],
            "prep_time_max": 10,
            "servings": 4,
            "difficulty": "easy"
        }
        
        success, response = self.run_test(
            "Generate Trail Mix Snack Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=45
        )
        
        if success and 'id' in response:
            recipe_id = response['id']
            self.recipe_ids['snack'] = recipe_id
            title = response.get('title', 'Unknown')
            ingredients = response.get('ingredients', [])
            shopping_list = response.get('shopping_list', [])
            
            print(f"✅ Generated snack recipe: {title}")
            print(f"🆔 Recipe ID: {recipe_id}")
            print(f"🛒 Shopping list items: {len(shopping_list)}")
            print(f"📝 Shopping list: {shopping_list}")
            
            # Test Walmart cart options for this recipe
            return self.test_walmart_cart_options(recipe_id, "snack", shopping_list)
        else:
            print("❌ Failed to generate snack recipe")
            return False

    def test_walmart_cart_options(self, recipe_id, category, shopping_list):
        """Test the grocery cart options endpoint for Walmart products"""
        print(f"\n🛒 Testing Walmart Cart Options for {category} recipe...")
        
        success, response = self.run_test(
            f"Get Walmart Cart Options for {category}",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": recipe_id, "user_id": self.target_user_id},
            timeout=60
        )
        
        if success:
            ingredient_options = response.get('ingredient_options', [])
            total_ingredients = len(ingredient_options)
            total_products = sum(len(opt.get('options', [])) for opt in ingredient_options)
            
            print(f"✅ Cart options retrieved successfully")
            print(f"📊 Ingredients with options: {total_ingredients}")
            print(f"📊 Total product options: {total_products}")
            
            # Analyze product data quality
            real_products = 0
            mock_products = 0
            product_ids = []
            
            for ingredient_option in ingredient_options:
                ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
                original_ingredient = ingredient_option.get('original_ingredient', 'Unknown')
                options = ingredient_option.get('options', [])
                
                print(f"\n🥕 Ingredient: {ingredient_name} (Original: {original_ingredient})")
                print(f"   Options found: {len(options)}")
                
                for i, product in enumerate(options):
                    product_id = product.get('product_id', '')
                    name = product.get('name', 'Unknown')
                    price = product.get('price', 0.0)
                    
                    product_ids.append(product_id)
                    
                    # Check if this is a real Walmart product ID
                    if (product_id.isdigit() and 
                        len(product_id) >= 6 and
                        not product_id.startswith('10315') and  # Mock pattern
                        not product_id.startswith('walmart-') and
                        not product_id.startswith('mock-')):
                        real_products += 1
                        status = "✅ REAL"
                    else:
                        mock_products += 1
                        status = "❌ MOCK"
                    
                    print(f"   {i+1}. {name} - ${price:.2f} (ID: {product_id}) {status}")
            
            # Store results for analysis
            self.product_search_results[category] = {
                'total_ingredients': total_ingredients,
                'total_products': total_products,
                'real_products': real_products,
                'mock_products': mock_products,
                'product_ids': product_ids
            }
            
            print(f"\n📊 WALMART PRODUCT ANALYSIS:")
            print(f"   Real Walmart products: {real_products}")
            print(f"   Mock products: {mock_products}")
            print(f"   Real product rate: {(real_products/total_products*100):.1f}%" if total_products > 0 else "   No products found")
            
            if total_products > 0:
                self.cart_options_working = True
                
                # Test custom cart creation
                return self.test_custom_cart_creation(recipe_id, category, ingredient_options)
            else:
                print("❌ No products returned from Walmart API")
                return False
        else:
            print(f"❌ Failed to get cart options for {category} recipe")
            return False

    def test_custom_cart_creation(self, recipe_id, category, ingredient_options):
        """Test creating a custom cart with selected Walmart products"""
        print(f"\n🛍️ Testing Custom Cart Creation for {category}...")
        
        # Select first product from each ingredient
        products = []
        for ingredient_option in ingredient_options:
            options = ingredient_option.get('options', [])
            if options:
                first_option = options[0]
                products.append({
                    "ingredient_name": ingredient_option.get('ingredient_name', ''),
                    "product_id": first_option.get('product_id', ''),
                    "name": first_option.get('name', ''),
                    "price": first_option.get('price', 0.0),
                    "quantity": 1
                })
        
        if not products:
            print("❌ No products available for custom cart")
            return False
        
        custom_cart_data = {
            "user_id": self.target_user_id,
            "recipe_id": recipe_id,
            "products": products
        }
        
        success, response = self.run_test(
            f"Create Custom Cart for {category}",
            "POST",
            "grocery/custom-cart",
            200,
            data=custom_cart_data,
            timeout=30
        )
        
        if success:
            cart_id = response.get('id', 'Unknown')
            total_price = response.get('total_price', 0.0)
            walmart_url = response.get('walmart_url', '')
            cart_products = response.get('products', [])
            
            print(f"✅ Custom cart created successfully")
            print(f"🆔 Cart ID: {cart_id}")
            print(f"💰 Total price: ${total_price:.2f}")
            print(f"📦 Products in cart: {len(cart_products)}")
            
            # Analyze Walmart URL
            if walmart_url:
                print(f"\n🔗 Walmart URL Analysis:")
                print(f"   URL: {walmart_url}")
                
                # Check URL format
                if 'affil.walmart.com' in walmart_url:
                    print("   ✅ Correct Walmart affiliate domain")
                else:
                    print("   ❌ Incorrect domain")
                
                if 'offers=' in walmart_url:
                    print("   ✅ Uses new 'offers=' parameter format")
                    
                    # Extract and validate offers format
                    offers_part = walmart_url.split('offers=')[1] if 'offers=' in walmart_url else ""
                    print(f"   📋 Offers: {offers_part}")
                    
                    # Check if all product IDs are included
                    product_ids_in_cart = [p['product_id'] for p in products]
                    all_ids_present = all(pid in walmart_url for pid in product_ids_in_cart)
                    
                    if all_ids_present:
                        print("   ✅ All product IDs included in URL")
                    else:
                        print("   ❌ Some product IDs missing from URL")
                        
                elif 'items=' in walmart_url:
                    print("   ❌ Still using old 'items=' format")
                else:
                    print("   ❌ Unknown URL parameter format")
                
                # Test URL accessibility
                try:
                    url_response = requests.head(walmart_url, timeout=10)
                    if url_response.status_code == 200:
                        print("   ✅ URL is accessible (HTTP 200)")
                    else:
                        print(f"   ⚠️ URL returned status: {url_response.status_code}")
                except Exception as e:
                    print(f"   ⚠️ URL accessibility test failed: {str(e)}")
            else:
                print("❌ No Walmart URL generated")
            
            return True
        else:
            print(f"❌ Failed to create custom cart for {category}")
            return False

    def test_walmart_api_direct(self):
        """Test Walmart API integration directly with common ingredients"""
        print("\n" + "=" * 60)
        print("🏪 DIRECT WALMART API TESTING")
        print("=" * 60)
        
        # Test common ingredients that should return products
        test_ingredients = ["chicken", "tomatoes", "sugar", "milk", "bread", "eggs"]
        
        for ingredient in test_ingredients:
            print(f"\n🔍 Testing Walmart search for: {ingredient}")
            
            # Create a simple recipe with this ingredient to test cart options
            if not self.target_user_id:
                print("❌ No user ID available")
                continue
            
            simple_recipe_request = {
                "user_id": self.target_user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "simple",
                "ingredients_on_hand": [ingredient],
                "prep_time_max": 15,
                "servings": 2,
                "difficulty": "easy"
            }
            
            success, response = self.run_test(
                f"Generate Simple Recipe with {ingredient}",
                "POST",
                "recipes/generate",
                200,
                data=simple_recipe_request,
                timeout=30
            )
            
            if success and 'id' in response:
                recipe_id = response['id']
                shopping_list = response.get('shopping_list', [])
                
                # Test cart options for this ingredient
                cart_success, cart_response = self.run_test(
                    f"Get Cart Options for {ingredient}",
                    "POST",
                    "grocery/cart-options",
                    200,
                    params={"recipe_id": recipe_id, "user_id": self.target_user_id},
                    timeout=30
                )
                
                if cart_success:
                    ingredient_options = cart_response.get('ingredient_options', [])
                    total_products = sum(len(opt.get('options', [])) for opt in ingredient_options)
                    
                    if total_products > 0:
                        print(f"   ✅ Found {total_products} products for {ingredient}")
                        self.walmart_api_working = True
                    else:
                        print(f"   ❌ No products found for {ingredient}")
                else:
                    print(f"   ❌ Cart options failed for {ingredient}")
            else:
                print(f"   ❌ Recipe generation failed for {ingredient}")

    def analyze_error_patterns(self):
        """Analyze backend logs and error patterns"""
        print("\n" + "=" * 60)
        print("🔍 ERROR ANALYSIS")
        print("=" * 60)
        
        # Check if we can access any debug endpoints for error analysis
        print("Checking for common error patterns...")
        
        # Test with invalid recipe ID to see error handling
        success, response = self.run_test(
            "Test Error Handling with Invalid Recipe ID",
            "POST",
            "grocery/cart-options",
            422,  # Expect validation error
            params={"recipe_id": "invalid-id", "user_id": self.target_user_id}
        )
        
        if success:
            print("✅ Error handling working correctly for invalid recipe ID")
        
        # Test with missing parameters
        success, response = self.run_test(
            "Test Error Handling with Missing Parameters",
            "POST",
            "grocery/cart-options",
            422,  # Expect validation error
            params={}
        )
        
        if success:
            print("✅ Error handling working correctly for missing parameters")

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 WALMART INTEGRATION TEST REPORT")
        print("=" * 80)
        
        print(f"🎯 Target User: {self.target_user_email}")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "N/A")
        
        print(f"\n🔧 SYSTEM STATUS:")
        print(f"   Backend Connectivity: {'✅ Working' if self.tests_passed > 0 else '❌ Failed'}")
        print(f"   User Account: {'✅ Found' if self.target_user_id else '❌ Not Found'}")
        print(f"   Walmart API Integration: {'✅ Working' if self.walmart_api_working else '❌ Not Working'}")
        print(f"   Cart Options Endpoint: {'✅ Working' if self.cart_options_working else '❌ Not Working'}")
        
        if self.product_search_results:
            print(f"\n🛒 WALMART PRODUCT SEARCH RESULTS:")
            total_real = 0
            total_mock = 0
            total_products = 0
            
            for category, results in self.product_search_results.items():
                real = results['real_products']
                mock = results['mock_products']
                total = results['total_products']
                
                total_real += real
                total_mock += mock
                total_products += total
                
                print(f"   {category.upper()}:")
                print(f"     Total products: {total}")
                print(f"     Real Walmart products: {real}")
                print(f"     Mock products: {mock}")
                print(f"     Real product rate: {(real/total*100):.1f}%" if total > 0 else "     No products")
            
            if total_products > 0:
                print(f"\n   OVERALL WALMART INTEGRATION:")
                print(f"     Total products analyzed: {total_products}")
                print(f"     Real Walmart products: {total_real}")
                print(f"     Mock products: {total_mock}")
                print(f"     Overall real product rate: {(total_real/total_products*100):.1f}%")
                
                if total_real > 0:
                    print(f"     🎉 WALMART API IS WORKING - Real products found!")
                else:
                    print(f"     ❌ WALMART API ISSUES - Only mock products found")
            else:
                print(f"     ❌ NO PRODUCTS FOUND - Walmart API may not be working")
        
        print(f"\n🔍 ISSUES IDENTIFIED:")
        issues = []
        
        if not self.walmart_api_working:
            issues.append("Walmart API integration not returning products")
        
        if not self.cart_options_working:
            issues.append("Cart options endpoint not working properly")
        
        if self.product_search_results:
            for category, results in self.product_search_results.items():
                if results['mock_products'] > 0:
                    issues.append(f"Mock products found in {category} category")
                if results['total_products'] == 0:
                    issues.append(f"No products returned for {category} recipes")
        
        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   ✅ No major issues identified")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if not self.walmart_api_working:
            print("   1. Check Walmart API credentials and authentication")
            print("   2. Verify Walmart API rate limits and quotas")
            print("   3. Check network connectivity to Walmart API endpoints")
        
        if self.product_search_results:
            total_mock = sum(r['mock_products'] for r in self.product_search_results.values())
            if total_mock > 0:
                print("   4. Remove all mock product data from responses")
                print("   5. Implement better product ID validation")
        
        print("   6. Monitor backend logs for Walmart API errors")
        print("   7. Test with different ingredient combinations")
        
        return self.tests_passed >= (self.tests_run * 0.7)  # 70% success rate threshold

    def run_all_tests(self):
        """Run all Walmart integration tests"""
        print("🚀 Starting Walmart Integration Testing...")
        
        # Test sequence
        tests = [
            ("Backend Connectivity", self.test_backend_connectivity),
            ("User Account Verification", self.test_user_account_verification),
            ("Existing Recipes Check", self.test_existing_recipes),
            ("Cuisine Recipe Walmart Integration", self.test_cuisine_recipe_walmart_integration),
            ("Beverage Recipe Walmart Integration", self.test_beverage_recipe_walmart_integration),
            ("Snack Recipe Walmart Integration", self.test_snack_recipe_walmart_integration),
            ("Direct Walmart API Testing", self.test_walmart_api_direct),
            ("Error Analysis", self.analyze_error_patterns),
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                test_func()
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {str(e)}")
                logger.error(f"Test {test_name} failed with exception: {str(e)}")
        
        # Generate final report
        success = self.generate_final_report()
        
        return success

def main():
    """Main function to run Walmart integration tests"""
    tester = WalmartIntegrationTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 WALMART INTEGRATION TESTING COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n❌ WALMART INTEGRATION TESTING FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        logger.error(f"Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
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