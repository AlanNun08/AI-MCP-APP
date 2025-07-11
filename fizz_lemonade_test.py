#!/usr/bin/env python3
"""
FIZZ LEMONADE SPECIFIC TEST
===========================

Testing the exact scenario the user reported: "fizz lemonade recipe"
This will test if there are any specific issues with fizzy/sparkling lemonade recipes.
"""

import requests
import json
import uuid
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FizzLemonadeSpecificTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.user_id = None
        self.recipe_id = None
        
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
            
        except Exception as e:
            logger.error(f"Request error for {method} {url}: {str(e)}")
            return 500, {"error": str(e)}
    
    def setup_test_user(self):
        """Create and verify a test user"""
        print("🔧 Setting up test user for fizz lemonade test...")
        
        test_email = f"fizz_lemonade_{uuid.uuid4()}@example.com"
        test_password = "SecureP@ssw0rd123"
        
        user_data = {
            "first_name": "Fizz",
            "last_name": "Lemonade",
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
            
        self.user_id = response['user_id']
        print(f"✅ User registered with ID: {self.user_id}")
        
        # Get verification code and verify
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
            print(f"❌ No verification code found")
            return False
            
        verify_data = {"email": test_email, "code": verification_code}
        status, verify_response = self.make_request("POST", "auth/verify", data=verify_data)
        if status != 200:
            print(f"❌ Failed to verify email: {verify_response}")
            return False
            
        print("✅ User verified successfully")
        return True
    
    def test_fizz_lemonade_variations(self):
        """Test different fizz lemonade recipe variations"""
        print("\n🥤 Testing Fizz Lemonade Recipe Variations...")
        
        variations = [
            {
                "name": "Fizz Lemonade (exact user term)",
                "request": {
                    "user_id": self.user_id,
                    "recipe_category": "beverage",
                    "cuisine_type": "special lemonades",
                    "ingredients_on_hand": ["sparkling water", "lemons", "sugar"],
                    "prep_time_max": 10,
                    "servings": 4,
                    "difficulty": "easy"
                }
            },
            {
                "name": "Sparkling Lemonade",
                "request": {
                    "user_id": self.user_id,
                    "recipe_category": "beverage", 
                    "cuisine_type": "special lemonades",
                    "ingredients_on_hand": ["soda water", "fresh lemons", "honey"],
                    "prep_time_max": 15,
                    "servings": 2,
                    "difficulty": "easy"
                }
            },
            {
                "name": "Carbonated Lemonade",
                "request": {
                    "user_id": self.user_id,
                    "recipe_category": "beverage",
                    "cuisine_type": "special lemonades", 
                    "ingredients_on_hand": ["carbonated water", "lemon juice", "simple syrup"],
                    "prep_time_max": 5,
                    "servings": 1,
                    "difficulty": "easy"
                }
            }
        ]
        
        results = []
        
        for variation in variations:
            print(f"\n   Testing: {variation['name']}")
            
            status, response = self.make_request(
                "POST", 
                "recipes/generate", 
                data=variation['request'],
                timeout=60
            )
            
            if status != 200:
                print(f"   ❌ Failed to generate {variation['name']}: {response}")
                results.append({
                    'name': variation['name'],
                    'success': False,
                    'error': response
                })
                continue
                
            if 'id' not in response:
                print(f"   ❌ No recipe ID in response for {variation['name']}")
                results.append({
                    'name': variation['name'],
                    'success': False,
                    'error': 'No recipe ID'
                })
                continue
                
            recipe_id = response['id']
            title = response.get('title', '')
            shopping_list = response.get('shopping_list', [])
            
            print(f"   ✅ Generated: {title}")
            print(f"   Recipe ID: {recipe_id}")
            print(f"   Shopping List: {shopping_list}")
            
            # Test Walmart integration for this recipe
            cart_status, cart_response = self.make_request(
                "POST",
                "grocery/cart-options",
                params={"recipe_id": recipe_id, "user_id": self.user_id}
            )
            
            if cart_status != 200:
                print(f"   ❌ Cart options failed: {cart_response}")
                results.append({
                    'name': variation['name'],
                    'success': False,
                    'recipe_id': recipe_id,
                    'title': title,
                    'cart_error': cart_response
                })
                continue
                
            # Analyze cart options
            ingredient_options = cart_response.get('ingredient_options', [])
            total_products = sum(len(opt.get('options', [])) for opt in ingredient_options)
            
            print(f"   ✅ Cart Options: {len(ingredient_options)} ingredients, {total_products} products")
            
            # Check for mock product IDs
            mock_ids = []
            valid_ids = []
            
            for ingredient_option in ingredient_options:
                for option in ingredient_option.get('options', []):
                    product_id = option.get('product_id', '')
                    if any(pattern in product_id for pattern in ['10315', 'walmart-', 'mock-']):
                        mock_ids.append(product_id)
                    elif product_id.isdigit() and len(product_id) >= 6:
                        valid_ids.append(product_id)
            
            if mock_ids:
                print(f"   🚨 MOCK IDs DETECTED: {mock_ids}")
            
            # Test custom cart creation
            if valid_ids:
                # Create a test custom cart
                test_products = []
                for ingredient_option in ingredient_options[:2]:  # Test with first 2 ingredients
                    for option in ingredient_option.get('options', [])[:1]:  # First option only
                        product_id = option.get('product_id', '')
                        if product_id in valid_ids:
                            test_products.append({
                                "ingredient_name": ingredient_option.get('ingredient_name', ''),
                                "product_id": product_id,
                                "name": option.get('name', ''),
                                "price": option.get('price', 0),
                                "quantity": 1
                            })
                
                if test_products:
                    custom_cart_data = {
                        "user_id": self.user_id,
                        "recipe_id": recipe_id,
                        "products": test_products
                    }
                    
                    custom_status, custom_response = self.make_request(
                        "POST",
                        "grocery/custom-cart",
                        data=custom_cart_data
                    )
                    
                    if custom_status == 200:
                        walmart_url = custom_response.get('walmart_url', '')
                        print(f"   ✅ Custom Cart Created")
                        print(f"   Walmart URL: {walmart_url}")
                        
                        # Validate URL
                        url_valid = (
                            'affil.walmart.com' in walmart_url and
                            'items=' in walmart_url and
                            walmart_url.startswith('https://')
                        )
                        
                        if not url_valid:
                            print(f"   ❌ Invalid Walmart URL format")
                        
                        results.append({
                            'name': variation['name'],
                            'success': True,
                            'recipe_id': recipe_id,
                            'title': title,
                            'shopping_list': shopping_list,
                            'total_products': total_products,
                            'mock_ids': mock_ids,
                            'valid_ids': len(valid_ids),
                            'walmart_url': walmart_url,
                            'url_valid': url_valid
                        })
                    else:
                        print(f"   ❌ Custom cart failed: {custom_response}")
                        results.append({
                            'name': variation['name'],
                            'success': False,
                            'recipe_id': recipe_id,
                            'title': title,
                            'custom_cart_error': custom_response
                        })
                else:
                    print(f"   ⚠️ No valid products for custom cart")
                    results.append({
                        'name': variation['name'],
                        'success': False,
                        'recipe_id': recipe_id,
                        'title': title,
                        'error': 'No valid products for custom cart'
                    })
            else:
                print(f"   ❌ No valid product IDs found")
                results.append({
                    'name': variation['name'],
                    'success': False,
                    'recipe_id': recipe_id,
                    'title': title,
                    'error': 'No valid product IDs'
                })
        
        return results
    
    def run_test(self):
        """Run the fizz lemonade specific test"""
        print("=" * 80)
        print("🥤 FIZZ LEMONADE SPECIFIC TEST")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.setup_test_user():
            print("❌ Failed to setup test user")
            return False
            
        results = self.test_fizz_lemonade_variations()
        
        # Final analysis
        print("\n" + "=" * 80)
        print("🎯 FIZZ LEMONADE TEST RESULTS")
        print("=" * 80)
        
        successful_tests = [r for r in results if r.get('success', False)]
        failed_tests = [r for r in results if not r.get('success', False)]
        
        print(f"Successful Tests: {len(successful_tests)}/{len(results)}")
        print(f"Failed Tests: {len(failed_tests)}/{len(results)}")
        
        if successful_tests:
            print("\n✅ SUCCESSFUL FIZZ LEMONADE TESTS:")
            for result in successful_tests:
                print(f"   - {result['name']}: {result['title']}")
                print(f"     Products: {result.get('total_products', 0)}, Valid IDs: {result.get('valid_ids', 0)}")
                if result.get('mock_ids'):
                    print(f"     🚨 Mock IDs: {result['mock_ids']}")
                if result.get('walmart_url'):
                    url_status = "✅ Valid" if result.get('url_valid', False) else "❌ Invalid"
                    print(f"     Walmart URL: {url_status}")
        
        if failed_tests:
            print("\n❌ FAILED FIZZ LEMONADE TESTS:")
            for result in failed_tests:
                print(f"   - {result['name']}: {result.get('error', 'Unknown error')}")
        
        # Overall assessment
        print("\n" + "=" * 80)
        print("🔍 FIZZ LEMONADE ISSUE ANALYSIS")
        print("=" * 80)
        
        if len(successful_tests) == len(results):
            print("✅ ALL FIZZ LEMONADE VARIATIONS WORKING CORRECTLY")
            print("The user's reported issue may be resolved or was a temporary problem.")
        elif len(successful_tests) > 0:
            print("⚠️ PARTIAL SUCCESS - Some fizz lemonade variations work, others don't")
            print("This suggests intermittent issues or specific recipe combinations causing problems.")
        else:
            print("❌ ALL FIZZ LEMONADE TESTS FAILED")
            print("This confirms the user's reported issue with fizz lemonade recipes.")
        
        # Check for mock ID contamination
        mock_id_issues = [r for r in successful_tests if r.get('mock_ids')]
        if mock_id_issues:
            print(f"\n🚨 MOCK ID CONTAMINATION DETECTED in {len(mock_id_issues)} tests")
            print("This could cause 'invalid item or quantity' errors in Walmart!")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return len(successful_tests) == len(results)

if __name__ == "__main__":
    tester = FizzLemonadeSpecificTester()
    success = tester.run_test()
    exit(0 if success else 1)