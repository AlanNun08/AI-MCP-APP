#!/usr/bin/env python3
"""
URGENT LEMONADE WALMART INTEGRATION TEST
========================================

This test specifically addresses the user's reported issue:
"invalid item or quantity" error when clicking Walmart link for fizz lemonade recipe.

Focus Areas:
1. Generate a lemonade beverage recipe specifically
2. Test the /api/grocery/cart-options endpoint with the lemonade recipe
3. Examine the product IDs returned - check if ANY are mock data or invalid
4. Test the /api/grocery/custom-cart endpoint with the lemonade products
5. Verify the exact Walmart affiliate URL format being generated
6. Check if the URL contains invalid product IDs or incorrect quantity parameters

Looking for:
- '10315' pattern IDs that might be passing through
- Verify all product IDs are valid Walmart format (numeric, 6+ digits)
- Check affiliate URL format: https://affil.walmart.com/cart/addToCart?items=ID1,ID2,ID3
"""

import requests
import json
import uuid
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LemonadeWalmartTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.user_id = None
        self.recipe_id = None
        self.cart_options_id = None
        self.test_results = {
            'lemonade_recipe_generation': False,
            'cart_options_api': False,
            'product_id_validation': False,
            'custom_cart_api': False,
            'walmart_url_format': False,
            'mock_data_detection': False
        }
        self.mock_product_ids = []
        self.real_product_ids = []
        self.walmart_url = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results with details"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
        logger.info(f"{test_name}: {'PASSED' if success else 'FAILED'} - {details}")
        
    def make_request(self, method, endpoint, data=None, params=None, timeout=30):
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
            logger.error(f"Request timeout for {method} {url}")
            return 408, {"error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {method} {url}")
            return 503, {"error": "Connection error"}
        except Exception as e:
            logger.error(f"Request error for {method} {url}: {str(e)}")
            return 500, {"error": str(e)}
    
    def setup_test_user(self):
        """Create and verify a test user for testing"""
        print("\n🔧 Setting up test user...")
        
        # Create unique test user
        test_email = f"lemonade_test_{uuid.uuid4()}@example.com"
        test_password = "SecureP@ssw0rd123"
        
        user_data = {
            "first_name": "Lemonade",
            "last_name": "Tester",
            "email": test_email,
            "password": test_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": ["american"]
        }
        
        # Register user
        status, response = self.make_request("POST", "auth/register", data=user_data)
        if status != 200:
            print(f"❌ Failed to register user: {response}")
            return False
            
        if 'user_id' not in response:
            print(f"❌ No user_id in registration response: {response}")
            return False
            
        self.user_id = response['user_id']
        print(f"✅ User registered with ID: {self.user_id}")
        
        # Get verification code
        status, code_response = self.make_request("GET", f"debug/verification-codes/{test_email}")
        if status != 200:
            print(f"❌ Failed to get verification code: {code_response}")
            return False
            
        verification_code = None
        if 'codes' in code_response and len(code_response['codes']) > 0:
            verification_code = code_response['codes'][0]['code']
        elif 'last_test_code' in code_response:
            verification_code = code_response['last_test_code']
            
        if not verification_code:
            print(f"❌ No verification code found: {code_response}")
            return False
            
        # Verify email
        verify_data = {"email": test_email, "code": verification_code}
        status, verify_response = self.make_request("POST", "auth/verify", data=verify_data)
        if status != 200:
            print(f"❌ Failed to verify email: {verify_response}")
            return False
            
        print("✅ User verified successfully")
        return True
    
    def test_lemonade_recipe_generation(self):
        """Test generating a specific lemonade beverage recipe"""
        print("\n🍋 Testing Lemonade Recipe Generation...")
        
        if not self.user_id:
            self.log_test("Lemonade Recipe Generation", False, "No user ID available")
            return False
            
        # Generate lemonade recipe specifically
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": "beverage",
            "cuisine_type": "special lemonades",  # This should trigger lemonade generation
            "dietary_preferences": [],
            "ingredients_on_hand": [],
            "prep_time_max": 15,
            "servings": 4,
            "difficulty": "easy"
        }
        
        print(f"Requesting lemonade recipe with data: {json.dumps(recipe_request, indent=2)}")
        
        status, response = self.make_request("POST", "recipes/generate", data=recipe_request, timeout=60)
        
        if status != 200:
            self.log_test("Lemonade Recipe Generation", False, f"API returned status {status}: {response}")
            return False
            
        if 'id' not in response:
            self.log_test("Lemonade Recipe Generation", False, f"No recipe ID in response: {response}")
            return False
            
        self.recipe_id = response['id']
        
        # Verify it's actually a lemonade recipe
        title = response.get('title', '').lower()
        description = response.get('description', '').lower()
        ingredients = [ing.lower() for ing in response.get('ingredients', [])]
        shopping_list = [item.lower() for item in response.get('shopping_list', [])]
        
        lemonade_keywords = ['lemon', 'lemonade', 'citrus', 'lime']
        has_lemonade_content = any(keyword in title or keyword in description for keyword in lemonade_keywords)
        has_lemon_ingredients = any(keyword in ' '.join(ingredients) for keyword in lemonade_keywords)
        has_lemon_shopping = any(keyword in ' '.join(shopping_list) for keyword in lemonade_keywords)
        
        if not (has_lemonade_content or has_lemon_ingredients or has_lemon_shopping):
            self.log_test("Lemonade Recipe Generation", False, f"Generated recipe doesn't appear to be lemonade-related. Title: {response.get('title')}")
            return False
            
        # Check shopping list quality
        shopping_list_clean = True
        problematic_items = []
        
        for item in response.get('shopping_list', []):
            # Check for quantities or measurements
            if re.search(r'\d+\s*(cup|tbsp|tsp|oz|lb|can|jar|bottle)', item.lower()):
                shopping_list_clean = False
                problematic_items.append(item)
                
        details = f"Recipe ID: {self.recipe_id}, Title: {response.get('title')}"
        if not shopping_list_clean:
            details += f", Problematic shopping list items: {problematic_items}"
        else:
            details += f", Shopping list clean: {response.get('shopping_list')}"
            
        self.test_results['lemonade_recipe_generation'] = True
        self.log_test("Lemonade Recipe Generation", True, details)
        return True
    
    def test_cart_options_api(self):
        """Test the /api/grocery/cart-options endpoint with lemonade recipe"""
        print("\n🛒 Testing Cart Options API...")
        
        if not self.recipe_id or not self.user_id:
            self.log_test("Cart Options API", False, "No recipe ID or user ID available")
            return False
            
        status, response = self.make_request(
            "POST", 
            "grocery/cart-options",
            params={"recipe_id": self.recipe_id, "user_id": self.user_id},
            timeout=30
        )
        
        if status != 200:
            self.log_test("Cart Options API", False, f"API returned status {status}: {response}")
            return False
            
        if 'id' not in response:
            self.log_test("Cart Options API", False, f"No cart options ID in response: {response}")
            return False
            
        self.cart_options_id = response['id']
        
        # Analyze ingredient options
        ingredient_options = response.get('ingredient_options', [])
        if not ingredient_options:
            self.log_test("Cart Options API", False, "No ingredient options returned")
            return False
            
        total_products = 0
        for ingredient_option in ingredient_options:
            options = ingredient_option.get('options', [])
            total_products += len(options)
            
            ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
            print(f"   Ingredient: {ingredient_name} - {len(options)} product options")
            
            for option in options:
                product_id = option.get('product_id', '')
                name = option.get('name', '')
                price = option.get('price', 0)
                print(f"     Product ID: {product_id}, Name: {name}, Price: ${price}")
        
        details = f"Cart Options ID: {self.cart_options_id}, Total ingredients: {len(ingredient_options)}, Total products: {total_products}"
        self.test_results['cart_options_api'] = True
        self.log_test("Cart Options API", True, details)
        return True
    
    def test_product_id_validation(self):
        """Examine product IDs for mock data and invalid formats"""
        print("\n🔍 Testing Product ID Validation...")
        
        if not self.cart_options_id:
            self.log_test("Product ID Validation", False, "No cart options available")
            return False
            
        # Get cart options data
        status, response = self.make_request("GET", f"grocery/cart-options/{self.cart_options_id}")
        if status == 404:
            # If direct GET doesn't work, we'll use the data from previous test
            # This is expected since the endpoint might not support GET
            print("   Note: Using cart options data from previous test")
            
        # Re-fetch cart options to get fresh data
        status, response = self.make_request(
            "POST", 
            "grocery/cart-options",
            params={"recipe_id": self.recipe_id, "user_id": self.user_id}
        )
        
        if status != 200:
            self.log_test("Product ID Validation", False, f"Failed to get cart options: {response}")
            return False
            
        # Analyze all product IDs
        all_product_ids = []
        mock_patterns = ['10315', 'walmart-', 'mock-']
        
        for ingredient_option in response.get('ingredient_options', []):
            for option in ingredient_option.get('options', []):
                product_id = option.get('product_id', '')
                all_product_ids.append({
                    'id': product_id,
                    'name': option.get('name', ''),
                    'price': option.get('price', 0),
                    'ingredient': ingredient_option.get('ingredient_name', '')
                })
        
        # Validate each product ID
        valid_ids = []
        invalid_ids = []
        mock_ids = []
        
        for product in all_product_ids:
            product_id = product['id']
            
            # Check for mock patterns
            is_mock = any(pattern in product_id for pattern in mock_patterns)
            if is_mock:
                mock_ids.append(product)
                self.mock_product_ids.append(product_id)
                continue
                
            # Check if it's a valid Walmart product ID format
            # Real Walmart IDs are numeric and at least 6 digits
            if product_id.isdigit() and len(product_id) >= 6:
                valid_ids.append(product)
                self.real_product_ids.append(product_id)
            else:
                invalid_ids.append(product)
        
        # Report findings
        print(f"   Total Product IDs Analyzed: {len(all_product_ids)}")
        print(f"   Valid Walmart IDs: {len(valid_ids)}")
        print(f"   Mock/Test IDs: {len(mock_ids)}")
        print(f"   Invalid Format IDs: {len(invalid_ids)}")
        
        if mock_ids:
            print("\n   🚨 MOCK PRODUCT IDs DETECTED:")
            for mock_product in mock_ids:
                print(f"     ID: {mock_product['id']}, Name: {mock_product['name']}, Ingredient: {mock_product['ingredient']}")
        
        if invalid_ids:
            print("\n   ⚠️ INVALID FORMAT IDs DETECTED:")
            for invalid_product in invalid_ids:
                print(f"     ID: {invalid_product['id']}, Name: {invalid_product['name']}, Ingredient: {invalid_product['ingredient']}")
        
        # Test passes if we have some valid IDs and no mock IDs
        has_valid_ids = len(valid_ids) > 0
        has_no_mock_ids = len(mock_ids) == 0
        
        success = has_valid_ids and has_no_mock_ids
        details = f"Valid: {len(valid_ids)}, Mock: {len(mock_ids)}, Invalid: {len(invalid_ids)}"
        
        self.test_results['product_id_validation'] = success
        self.test_results['mock_data_detection'] = len(mock_ids) == 0
        
        self.log_test("Product ID Validation", success, details)
        return success
    
    def test_custom_cart_api(self):
        """Test the /api/grocery/custom-cart endpoint with lemonade products"""
        print("\n🛍️ Testing Custom Cart API...")
        
        if not self.real_product_ids:
            self.log_test("Custom Cart API", False, "No valid product IDs available for testing")
            return False
            
        # Create custom cart with real product IDs
        # Use first few real product IDs for testing
        test_products = []
        
        # Re-fetch cart options to get product details
        status, response = self.make_request(
            "POST", 
            "grocery/cart-options",
            params={"recipe_id": self.recipe_id, "user_id": self.user_id}
        )
        
        if status != 200:
            self.log_test("Custom Cart API", False, f"Failed to get cart options for custom cart: {response}")
            return False
            
        # Build test products from real product IDs
        for ingredient_option in response.get('ingredient_options', []):
            for option in ingredient_option.get('options', []):
                product_id = option.get('product_id', '')
                if product_id in self.real_product_ids:
                    test_products.append({
                        "ingredient_name": ingredient_option.get('ingredient_name', ''),
                        "product_id": product_id,
                        "name": option.get('name', ''),
                        "price": option.get('price', 0),
                        "quantity": 1
                    })
                    
                    # Limit to 3 products for testing
                    if len(test_products) >= 3:
                        break
            if len(test_products) >= 3:
                break
        
        if not test_products:
            self.log_test("Custom Cart API", False, "No valid products available for custom cart")
            return False
            
        custom_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "products": test_products
        }
        
        print(f"   Creating custom cart with {len(test_products)} products:")
        for product in test_products:
            print(f"     {product['ingredient_name']}: {product['name']} (ID: {product['product_id']}) - ${product['price']}")
        
        status, response = self.make_request("POST", "grocery/custom-cart", data=custom_cart_data)
        
        if status != 200:
            self.log_test("Custom Cart API", False, f"API returned status {status}: {response}")
            return False
            
        if 'id' not in response:
            self.log_test("Custom Cart API", False, f"No custom cart ID in response: {response}")
            return False
            
        # Verify response structure
        cart_id = response['id']
        products = response.get('products', [])
        total_price = response.get('total_price', 0)
        walmart_url = response.get('walmart_url', '')
        
        # Calculate expected total
        expected_total = sum(p['price'] * p['quantity'] for p in test_products)
        price_correct = abs(total_price - expected_total) < 0.01
        
        self.walmart_url = walmart_url
        
        details = f"Cart ID: {cart_id}, Products: {len(products)}, Total: ${total_price:.2f} (Expected: ${expected_total:.2f}), Price Correct: {price_correct}"
        
        self.test_results['custom_cart_api'] = True
        self.log_test("Custom Cart API", True, details)
        return True
    
    def test_walmart_url_format(self):
        """Verify the Walmart affiliate URL format and content"""
        print("\n🔗 Testing Walmart URL Format...")
        
        if not self.walmart_url:
            self.log_test("Walmart URL Format", False, "No Walmart URL available")
            return False
            
        print(f"   Walmart URL: {self.walmart_url}")
        
        # Check URL format
        expected_domain = "affil.walmart.com"
        expected_path = "/cart/addToCart"
        expected_param = "items="
        
        format_checks = {
            'has_correct_domain': expected_domain in self.walmart_url,
            'has_correct_path': expected_path in self.walmart_url,
            'has_items_param': expected_param in self.walmart_url,
            'is_https': self.walmart_url.startswith('https://'),
        }
        
        print(f"   Format Checks:")
        for check, result in format_checks.items():
            print(f"     {check}: {'✅' if result else '❌'}")
        
        # Extract product IDs from URL
        url_product_ids = []
        if 'items=' in self.walmart_url:
            items_part = self.walmart_url.split('items=')[1]
            # Remove any additional parameters
            if '&' in items_part:
                items_part = items_part.split('&')[0]
            url_product_ids = items_part.split(',')
        
        print(f"   Product IDs in URL: {url_product_ids}")
        
        # Verify product IDs in URL are valid
        invalid_url_ids = []
        mock_url_ids = []
        
        for product_id in url_product_ids:
            # Check for mock patterns
            if any(pattern in product_id for pattern in ['10315', 'walmart-', 'mock-']):
                mock_url_ids.append(product_id)
            # Check if it's a valid format
            elif not (product_id.isdigit() and len(product_id) >= 6):
                invalid_url_ids.append(product_id)
        
        id_checks = {
            'no_mock_ids_in_url': len(mock_url_ids) == 0,
            'no_invalid_ids_in_url': len(invalid_url_ids) == 0,
            'has_product_ids': len(url_product_ids) > 0
        }
        
        print(f"   Product ID Checks:")
        for check, result in id_checks.items():
            print(f"     {check}: {'✅' if result else '❌'}")
            
        if mock_url_ids:
            print(f"   🚨 MOCK IDs IN URL: {mock_url_ids}")
        if invalid_url_ids:
            print(f"   ⚠️ INVALID IDs IN URL: {invalid_url_ids}")
        
        # Overall success
        all_format_checks_pass = all(format_checks.values())
        all_id_checks_pass = all(id_checks.values())
        success = all_format_checks_pass and all_id_checks_pass
        
        details = f"Format OK: {all_format_checks_pass}, IDs OK: {all_id_checks_pass}, URL: {self.walmart_url[:100]}..."
        
        self.test_results['walmart_url_format'] = success
        self.log_test("Walmart URL Format", success, details)
        return success
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("🍋 LEMONADE WALMART INTEGRATION COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests in sequence
        tests = [
            ("Setup Test User", self.setup_test_user),
            ("Lemonade Recipe Generation", self.test_lemonade_recipe_generation),
            ("Cart Options API", self.test_cart_options_api),
            ("Product ID Validation", self.test_product_id_validation),
            ("Custom Cart API", self.test_custom_cart_api),
            ("Walmart URL Format", self.test_walmart_url_format),
        ]
        
        results = {}
        for test_name, test_method in tests:
            try:
                results[test_name] = test_method()
            except Exception as e:
                print(f"\n❌ EXCEPTION in {test_name}: {str(e)}")
                logger.error(f"Exception in {test_name}: {str(e)}")
                results[test_name] = False
        
        # Final report
        print("\n" + "=" * 80)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 80)
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        # Critical issue analysis
        print("\n" + "=" * 80)
        print("🚨 CRITICAL ISSUE ANALYSIS")
        print("=" * 80)
        
        critical_issues = []
        
        if len(self.mock_product_ids) > 0:
            critical_issues.append(f"MOCK PRODUCT IDs DETECTED: {self.mock_product_ids}")
            
        if not self.test_results.get('walmart_url_format', False):
            critical_issues.append("WALMART URL FORMAT INVALID")
            
        if not self.test_results.get('product_id_validation', False):
            critical_issues.append("PRODUCT ID VALIDATION FAILED")
            
        if critical_issues:
            print("🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   - {issue}")
            print("\nThese issues could cause 'invalid item or quantity' errors in Walmart!")
        else:
            print("✅ NO CRITICAL ISSUES DETECTED")
            print("The lemonade Walmart integration appears to be working correctly.")
        
        # Recommendations
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        
        if len(self.mock_product_ids) > 0:
            print("1. Remove all mock product IDs from the system")
            print("2. Ensure product ID filtering is working correctly")
            
        if not self.walmart_url:
            print("3. Fix Walmart URL generation")
        elif self.walmart_url and not self.test_results.get('walmart_url_format', False):
            print("3. Fix Walmart URL format issues")
            
        if self.test_results.get('lemonade_recipe_generation', False):
            print("4. ✅ Lemonade recipe generation is working correctly")
        else:
            print("4. Fix lemonade recipe generation")
            
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results

if __name__ == "__main__":
    tester = LemonadeWalmartTester()
    results = tester.run_comprehensive_test()