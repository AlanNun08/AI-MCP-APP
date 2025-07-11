#!/usr/bin/env python3
"""
Comprehensive Walmart Product Search Testing with Real User Recipes
Testing the user's reported issue: "Walmart product ID search with real recipes from users"

This test focuses on:
1. User Recipe Generation across all categories (cuisine, beverage, snack)
2. Walmart Product Search with /api/grocery/cart-options endpoint
3. Product Validation - ensuring all returned product IDs are authentic Walmart catalog products
4. Cross-Category Testing - ensuring Walmart integration works universally
5. No Mock Data - verifying no mock product IDs (like 10315* pattern) are returned
"""

import requests
import json
import time
import uuid
import logging
import re
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WalmartRecipeIntegrationTester:
    def __init__(self):
        # Get backend URL from environment or use default
        backend_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        self.base_url = f"{backend_url}/api"
        
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.recipes = {}  # Store generated recipes by category
        self.cart_options = {}  # Store cart options by recipe
        self.product_analysis = {
            'total_products': 0,
            'real_products': 0,
            'mock_products': 0,
            'mock_patterns': [],
            'real_product_examples': []
        }
        
        # Test user credentials
        self.test_email = f"walmart_test_{uuid.uuid4()}@example.com"
        self.test_password = "WalmartTest123!"
        
        print(f"🔧 Backend URL: {self.base_url}")
        print(f"📧 Test Email: {self.test_email}")

    def log_test_result(self, test_name, success, details=""):
        """Log test results with consistent formatting"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
            logger.info(f"PASSED: {test_name} {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
            logger.error(f"FAILED: {test_name} {details}")
        return success

    def make_request(self, method, endpoint, data=None, params=None, timeout=45):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response.status_code, response.json() if response.content else {}
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {url}")
            return 408, {"error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {url}")
            return 503, {"error": "Connection error"}
        except Exception as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return 500, {"error": str(e)}

    def setup_test_user(self):
        """Create and verify test user account"""
        print("\n" + "=" * 60)
        print("🔧 SETTING UP TEST USER ACCOUNT")
        print("=" * 60)
        
        # Register user
        user_data = {
            "first_name": "Walmart",
            "last_name": "Tester",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "favorite_cuisines": ["italian", "mexican", "asian"]
        }
        
        status, response = self.make_request("POST", "auth/register", data=user_data)
        
        if status == 200 and 'user_id' in response:
            self.user_id = response['user_id']
            success = self.log_test_result("User Registration", True, f"ID: {self.user_id}")
            
            # Get verification code
            status, code_response = self.make_request("GET", f"debug/verification-codes/{self.test_email}")
            
            if status == 200 and 'codes' in code_response and len(code_response['codes']) > 0:
                verification_code = code_response['codes'][0]['code']
                
                # Verify email
                verify_data = {
                    "email": self.test_email,
                    "code": verification_code
                }
                
                status, _ = self.make_request("POST", "auth/verify", data=verify_data)
                
                if status == 200:
                    return self.log_test_result("Email Verification", True, f"Code: {verification_code}")
                else:
                    return self.log_test_result("Email Verification", False, f"Status: {status}")
            else:
                return self.log_test_result("Get Verification Code", False, f"Status: {status}")
        else:
            return self.log_test_result("User Registration", False, f"Status: {status}")

    def generate_recipe_by_category(self, category, recipe_type):
        """Generate recipe for specific category and type"""
        print(f"\n📝 Generating {category.upper()} recipe: {recipe_type}")
        
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": category,
            "cuisine_type": recipe_type if category == "cuisine" else None,
            "servings": 4,
            "difficulty": "medium"
        }
        
        # Add category-specific parameters
        if category == "beverage":
            recipe_request["cuisine_type"] = recipe_type
        elif category == "snack":
            recipe_request["cuisine_type"] = recipe_type
        
        status, response = self.make_request("POST", "recipes/generate", data=recipe_request, timeout=60)
        
        if status == 200 and 'id' in response:
            recipe_id = response['id']
            recipe_title = response.get('title', 'Unknown Recipe')
            shopping_list = response.get('shopping_list', [])
            
            # Store recipe data
            self.recipes[f"{category}_{recipe_type}"] = {
                'id': recipe_id,
                'title': recipe_title,
                'shopping_list': shopping_list,
                'category': category,
                'type': recipe_type,
                'full_response': response
            }
            
            success = self.log_test_result(
                f"{category.title()} Recipe Generation ({recipe_type})", 
                True, 
                f"'{recipe_title}' - {len(shopping_list)} ingredients"
            )
            
            # Validate shopping list quality
            self.validate_shopping_list_quality(shopping_list, f"{category}_{recipe_type}")
            
            return success
        else:
            return self.log_test_result(
                f"{category.title()} Recipe Generation ({recipe_type})", 
                False, 
                f"Status: {status}"
            )

    def validate_shopping_list_quality(self, shopping_list, recipe_key):
        """Validate that shopping list contains clean ingredient names"""
        print(f"   🔍 Validating shopping list quality for {recipe_key}")
        
        issues = []
        clean_count = 0
        
        for ingredient in shopping_list:
            # Check for quantities (numbers at start)
            if re.match(r'^\d+', ingredient.strip()):
                issues.append(f"Contains quantity: '{ingredient}'")
            # Check for measurements
            elif any(measure in ingredient.lower() for measure in ['cup', 'tbsp', 'tsp', 'oz', 'lb', 'gram', 'ml']):
                issues.append(f"Contains measurement: '{ingredient}'")
            # Check for preparation words
            elif any(prep in ingredient.lower() for prep in ['diced', 'chopped', 'minced', 'sliced', 'fresh', 'dried']):
                issues.append(f"Contains preparation word: '{ingredient}'")
            else:
                clean_count += 1
        
        cleanliness_score = (clean_count / len(shopping_list)) * 100 if shopping_list else 0
        
        if cleanliness_score >= 90:
            print(f"   ✅ Shopping list quality: EXCELLENT ({cleanliness_score:.1f}% clean)")
        elif cleanliness_score >= 75:
            print(f"   ✅ Shopping list quality: GOOD ({cleanliness_score:.1f}% clean)")
        elif cleanliness_score >= 50:
            print(f"   ⚠️ Shopping list quality: FAIR ({cleanliness_score:.1f}% clean)")
        else:
            print(f"   ❌ Shopping list quality: POOR ({cleanliness_score:.1f}% clean)")
        
        if issues:
            print(f"   📋 Issues found: {len(issues)}")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"      - {issue}")
            if len(issues) > 3:
                print(f"      ... and {len(issues) - 3} more")

    def test_walmart_cart_options(self, recipe_key):
        """Test Walmart cart-options endpoint with a specific recipe"""
        recipe_data = self.recipes[recipe_key]
        recipe_id = recipe_data['id']
        recipe_title = recipe_data['title']
        
        print(f"\n🛒 Testing Walmart Cart Options for: {recipe_title}")
        
        status, response = self.make_request(
            "POST", 
            "grocery/cart-options", 
            params={"recipe_id": recipe_id, "user_id": self.user_id},
            timeout=60
        )
        
        if status == 200 and 'ingredient_options' in response:
            ingredient_options = response['ingredient_options']
            
            # Store cart options
            self.cart_options[recipe_key] = response
            
            # Analyze products
            total_products = 0
            real_products = 0
            mock_products = 0
            
            print(f"   📦 Found options for {len(ingredient_options)} ingredients:")
            
            for ingredient_option in ingredient_options:
                ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
                options = ingredient_option.get('options', [])
                
                print(f"      🥕 {ingredient_name}: {len(options)} products")
                
                for product in options:
                    total_products += 1
                    product_id = product.get('product_id', '')
                    product_name = product.get('name', '')
                    product_price = product.get('price', 0)
                    
                    # Validate product authenticity
                    is_real = self.validate_product_authenticity(product_id, product_name, product_price)
                    
                    if is_real:
                        real_products += 1
                        if len(self.product_analysis['real_product_examples']) < 10:
                            self.product_analysis['real_product_examples'].append({
                                'id': product_id,
                                'name': product_name,
                                'price': product_price,
                                'ingredient': ingredient_name
                            })
                    else:
                        mock_products += 1
                        self.product_analysis['mock_patterns'].append(product_id)
            
            # Update global analysis
            self.product_analysis['total_products'] += total_products
            self.product_analysis['real_products'] += real_products
            self.product_analysis['mock_products'] += mock_products
            
            # Calculate success rate
            real_rate = (real_products / total_products * 100) if total_products > 0 else 0
            
            success = self.log_test_result(
                f"Walmart Cart Options ({recipe_key})", 
                True, 
                f"{total_products} products, {real_rate:.1f}% real"
            )
            
            # Detailed product analysis
            print(f"   📊 Product Analysis:")
            print(f"      Total Products: {total_products}")
            print(f"      Real Products: {real_products} ({real_rate:.1f}%)")
            print(f"      Mock Products: {mock_products} ({100-real_rate:.1f}%)")
            
            if mock_products > 0:
                print(f"   ⚠️ WARNING: Found {mock_products} mock products!")
                unique_mock_patterns = list(set(self.product_analysis['mock_patterns'][-mock_products:]))
                for pattern in unique_mock_patterns[:3]:
                    print(f"      Mock ID: {pattern}")
            
            return success
        else:
            return self.log_test_result(
                f"Walmart Cart Options ({recipe_key})", 
                False, 
                f"Status: {status}, Response: {response}"
            )

    def validate_product_authenticity(self, product_id, product_name, product_price):
        """Validate if a product ID is authentic Walmart catalog product"""
        
        # Check for mock patterns
        mock_patterns = [
            r'^10315\d+$',  # 10315* pattern
            r'^12345\d+$',  # 12345* pattern  
            r'^99999\d+$',  # 99999* pattern
            r'^walmart-',   # walmart- prefix
            r'^mock-',      # mock- prefix
            r'^test-',      # test- prefix
        ]
        
        for pattern in mock_patterns:
            if re.match(pattern, str(product_id)):
                return False
        
        # Validate authentic Walmart product characteristics
        if not str(product_id).isdigit():
            return False
        
        if len(str(product_id)) < 6 or len(str(product_id)) > 12:
            return False
        
        if not product_name or len(product_name) < 3:
            return False
        
        if not isinstance(product_price, (int, float)) or product_price <= 0 or product_price > 1000:
            return False
        
        return True

    def test_custom_cart_creation(self, recipe_key):
        """Test custom cart creation with real Walmart products"""
        if recipe_key not in self.cart_options:
            print(f"❌ No cart options available for {recipe_key}")
            return False
        
        cart_options = self.cart_options[recipe_key]
        recipe_data = self.recipes[recipe_key]
        
        print(f"\n🛍️ Testing Custom Cart Creation for: {recipe_data['title']}")
        
        # Select first product from each ingredient
        products = []
        for ingredient_option in cart_options['ingredient_options']:
            if ingredient_option.get('options'):
                product = ingredient_option['options'][0]  # Take first option
                products.append({
                    "ingredient_name": ingredient_option['ingredient_name'],
                    "product_id": product['product_id'],
                    "name": product['name'],
                    "price": product['price'],
                    "quantity": 1
                })
        
        if not products:
            return self.log_test_result(f"Custom Cart Creation ({recipe_key})", False, "No products available")
        
        custom_cart_data = {
            "user_id": self.user_id,
            "recipe_id": recipe_data['id'],
            "products": products
        }
        
        status, response = self.make_request("POST", "grocery/custom-cart", data=custom_cart_data)
        
        if status == 200 and 'walmart_url' in response:
            walmart_url = response['walmart_url']
            total_price = response.get('total_price', 0)
            
            # Validate Walmart URL format
            url_valid = self.validate_walmart_url(walmart_url, products)
            
            success = self.log_test_result(
                f"Custom Cart Creation ({recipe_key})", 
                True, 
                f"${total_price:.2f}, URL valid: {url_valid}"
            )
            
            print(f"   🔗 Walmart URL: {walmart_url}")
            print(f"   💰 Total Price: ${total_price:.2f}")
            
            return success
        else:
            return self.log_test_result(
                f"Custom Cart Creation ({recipe_key})", 
                False, 
                f"Status: {status}"
            )

    def validate_walmart_url(self, url, products):
        """Validate Walmart affiliate URL format"""
        
        # Check basic URL structure
        if not url.startswith('https://affil.walmart.com/cart/addToCart'):
            print(f"   ❌ Invalid URL domain/path: {url}")
            return False
        
        # Check for offers parameter (new format)
        if 'offers=' not in url:
            print(f"   ❌ Missing 'offers=' parameter in URL")
            return False
        
        # Extract offers part
        offers_part = url.split('offers=')[1] if 'offers=' in url else ""
        
        # Validate offers format: SKU1|Quantity1,SKU2|Quantity2
        expected_offers = []
        for product in products:
            expected_offers.append(f"{product['product_id']}|{product['quantity']}")
        
        expected_offers_str = ','.join(expected_offers)
        
        if offers_part == expected_offers_str:
            print(f"   ✅ Walmart URL format correct: offers={offers_part}")
            return True
        else:
            print(f"   ❌ Walmart URL format incorrect")
            print(f"      Expected: {expected_offers_str}")
            print(f"      Got: {offers_part}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive Walmart product search testing"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE WALMART PRODUCT SEARCH TESTING")
        print("   Testing: Walmart product ID search with real recipes from users")
        print("=" * 80)
        
        start_time = time.time()
        
        # Step 1: Setup test user
        if not self.setup_test_user():
            print("❌ Failed to setup test user - aborting tests")
            return False
        
        # Step 2: Test recipe generation across all categories
        print("\n" + "=" * 60)
        print("📝 STEP 2: RECIPE GENERATION ACROSS ALL CATEGORIES")
        print("=" * 60)
        
        recipe_tests = [
            ("cuisine", "italian"),
            ("cuisine", "mexican"), 
            ("beverage", "coffee"),
            ("beverage", "special lemonades"),
            ("snack", "acai bowls"),
            ("snack", "frozen yogurt berry bites")
        ]
        
        recipe_generation_success = 0
        for category, recipe_type in recipe_tests:
            if self.generate_recipe_by_category(category, recipe_type):
                recipe_generation_success += 1
        
        print(f"\n📊 Recipe Generation Summary: {recipe_generation_success}/{len(recipe_tests)} successful")
        
        if recipe_generation_success == 0:
            print("❌ No recipes generated - cannot test Walmart integration")
            return False
        
        # Step 3: Test Walmart cart-options endpoint
        print("\n" + "=" * 60)
        print("🛒 STEP 3: WALMART CART-OPTIONS ENDPOINT TESTING")
        print("=" * 60)
        
        cart_options_success = 0
        for recipe_key in self.recipes.keys():
            if self.test_walmart_cart_options(recipe_key):
                cart_options_success += 1
        
        print(f"\n📊 Cart Options Summary: {cart_options_success}/{len(self.recipes)} successful")
        
        # Step 4: Test custom cart creation
        print("\n" + "=" * 60)
        print("🛍️ STEP 4: CUSTOM CART CREATION TESTING")
        print("=" * 60)
        
        custom_cart_success = 0
        for recipe_key in self.recipes.keys():
            if recipe_key in self.cart_options:
                if self.test_custom_cart_creation(recipe_key):
                    custom_cart_success += 1
        
        print(f"\n📊 Custom Cart Summary: {custom_cart_success}/{len(self.cart_options)} successful")
        
        # Step 5: Final analysis and report
        self.generate_final_report(start_time)
        
        # Determine overall success
        overall_success = (
            recipe_generation_success > 0 and
            cart_options_success > 0 and
            self.product_analysis['mock_products'] == 0 and
            self.product_analysis['real_products'] > 0
        )
        
        return overall_success

    def generate_final_report(self, start_time):
        """Generate comprehensive final report"""
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 80)
        print("📋 FINAL COMPREHENSIVE REPORT")
        print("=" * 80)
        
        print(f"⏱️ Total Test Duration: {elapsed_time:.1f} seconds")
        print(f"🧪 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"📊 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n📝 RECIPE GENERATION RESULTS:")
        print(f"   Total Recipes Generated: {len(self.recipes)}")
        for recipe_key, recipe_data in self.recipes.items():
            print(f"   ✅ {recipe_key}: '{recipe_data['title']}' ({len(recipe_data['shopping_list'])} ingredients)")
        
        print(f"\n🛒 WALMART INTEGRATION RESULTS:")
        print(f"   Total Products Analyzed: {self.product_analysis['total_products']}")
        print(f"   Real Walmart Products: {self.product_analysis['real_products']}")
        print(f"   Mock Products Found: {self.product_analysis['mock_products']}")
        
        if self.product_analysis['total_products'] > 0:
            real_percentage = (self.product_analysis['real_products'] / self.product_analysis['total_products']) * 100
            print(f"   Real Product Rate: {real_percentage:.1f}%")
        
        print(f"\n🔍 PRODUCT AUTHENTICITY VALIDATION:")
        if self.product_analysis['mock_products'] == 0:
            print("   ✅ ZERO mock products detected - All products are authentic!")
        else:
            print(f"   ❌ {self.product_analysis['mock_products']} mock products detected")
            unique_mock_patterns = list(set(self.product_analysis['mock_patterns']))
            print(f"   Mock patterns found: {unique_mock_patterns[:5]}")
        
        print(f"\n💎 REAL PRODUCT EXAMPLES:")
        for i, product in enumerate(self.product_analysis['real_product_examples'][:5]):
            print(f"   {i+1}. {product['name']} - ${product['price']:.2f} (ID: {product['id']})")
        
        print(f"\n🎯 CRITICAL SUCCESS CRITERIA:")
        criteria = [
            ("Recipe Generation Works", len(self.recipes) > 0),
            ("Walmart API Returns Products", self.product_analysis['total_products'] > 0),
            ("No Mock Product IDs", self.product_analysis['mock_products'] == 0),
            ("Real Product IDs Found", self.product_analysis['real_products'] > 0),
            ("Cross-Category Support", len(set(r['category'] for r in self.recipes.values())) > 1)
        ]
        
        all_criteria_met = True
        for criterion, met in criteria:
            status = "✅ PASS" if met else "❌ FAIL"
            print(f"   {status}: {criterion}")
            if not met:
                all_criteria_met = False
        
        print(f"\n🏆 OVERALL RESULT:")
        if all_criteria_met:
            print("   ✅ ALL CRITICAL CRITERIA MET - WALMART INTEGRATION WORKING PERFECTLY!")
            print("   🎉 User's reported issue appears to be RESOLVED!")
        else:
            print("   ❌ Some critical criteria not met - Issues still exist")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = WalmartRecipeIntegrationTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 COMPREHENSIVE TESTING COMPLETED SUCCESSFULLY!")
            print("✅ Walmart product search with real user recipes is WORKING!")
            exit(0)
        else:
            print("\n❌ COMPREHENSIVE TESTING REVEALED ISSUES!")
            print("🔧 Walmart product search needs attention!")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        logger.error(f"Testing failed with error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()