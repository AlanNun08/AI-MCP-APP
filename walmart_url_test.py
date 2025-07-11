#!/usr/bin/env python3
"""
WALMART URL VALIDATION TEST
===========================

This test validates the actual Walmart URLs generated to see if they would cause
"invalid item or quantity" errors when clicked.
"""

import requests
import json
import uuid
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WalmartURLValidator:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.user_id = None
        self.test_urls = []
        
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
        print("🔧 Setting up test user for URL validation...")
        
        test_email = f"url_test_{uuid.uuid4()}@example.com"
        test_password = "SecureP@ssw0rd123"
        
        user_data = {
            "first_name": "URL",
            "last_name": "Tester",
            "email": test_email,
            "password": test_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": ["american"]
        }
        
        # Register and verify user
        status, response = self.make_request("POST", "auth/register", data=user_data)
        if status != 200:
            return False
            
        self.user_id = response['user_id']
        
        status, code_response = self.make_request("GET", f"debug/verification-codes/{test_email}")
        if status != 200:
            return False
            
        verification_code = code_response.get('codes', [{}])[0].get('code') or code_response.get('last_test_code')
        if not verification_code:
            return False
            
        verify_data = {"email": test_email, "code": verification_code}
        status, verify_response = self.make_request("POST", "auth/verify", data=verify_data)
        
        return status == 200
    
    def generate_test_walmart_urls(self):
        """Generate multiple Walmart URLs for different recipe types"""
        print("\n🔗 Generating Test Walmart URLs...")
        
        test_recipes = [
            {
                "name": "Lemonade Recipe",
                "request": {
                    "user_id": self.user_id,
                    "recipe_category": "beverage",
                    "cuisine_type": "special lemonades",
                    "ingredients_on_hand": ["lemons", "sugar", "water"],
                    "servings": 4,
                    "difficulty": "easy"
                }
            },
            {
                "name": "Italian Pasta Recipe",
                "request": {
                    "user_id": self.user_id,
                    "recipe_category": "cuisine",
                    "cuisine_type": "italian",
                    "ingredients_on_hand": ["pasta", "tomatoes", "garlic"],
                    "servings": 2,
                    "difficulty": "medium"
                }
            },
            {
                "name": "Healthy Snack Recipe",
                "request": {
                    "user_id": self.user_id,
                    "recipe_category": "snack",
                    "cuisine_type": "acai bowls",
                    "ingredients_on_hand": ["acai", "berries", "granola"],
                    "servings": 1,
                    "difficulty": "easy"
                }
            }
        ]
        
        for recipe_test in test_recipes:
            print(f"\n   Generating {recipe_test['name']}...")
            
            # Generate recipe
            status, response = self.make_request("POST", "recipes/generate", data=recipe_test['request'], timeout=60)
            if status != 200:
                print(f"   ❌ Failed to generate recipe: {response}")
                continue
                
            recipe_id = response.get('id')
            if not recipe_id:
                print(f"   ❌ No recipe ID returned")
                continue
                
            print(f"   ✅ Generated: {response.get('title', 'Unknown')}")
            
            # Get cart options
            status, cart_response = self.make_request(
                "POST",
                "grocery/cart-options", 
                params={"recipe_id": recipe_id, "user_id": self.user_id}
            )
            
            if status != 200:
                print(f"   ❌ Failed to get cart options: {cart_response}")
                continue
                
            # Create custom cart with first few products
            ingredient_options = cart_response.get('ingredient_options', [])
            if not ingredient_options:
                print(f"   ❌ No ingredient options available")
                continue
                
            # Select products for custom cart
            test_products = []
            for ingredient_option in ingredient_options[:3]:  # First 3 ingredients
                options = ingredient_option.get('options', [])
                if options:
                    option = options[0]  # First option
                    product_id = option.get('product_id', '')
                    
                    # Validate product ID format
                    if product_id.isdigit() and len(product_id) >= 6:
                        test_products.append({
                            "ingredient_name": ingredient_option.get('ingredient_name', ''),
                            "product_id": product_id,
                            "name": option.get('name', ''),
                            "price": option.get('price', 0),
                            "quantity": 1
                        })
            
            if not test_products:
                print(f"   ❌ No valid products for custom cart")
                continue
                
            # Create custom cart
            custom_cart_data = {
                "user_id": self.user_id,
                "recipe_id": recipe_id,
                "products": test_products
            }
            
            status, custom_response = self.make_request("POST", "grocery/custom-cart", data=custom_cart_data)
            if status != 200:
                print(f"   ❌ Failed to create custom cart: {custom_response}")
                continue
                
            walmart_url = custom_response.get('walmart_url', '')
            if not walmart_url:
                print(f"   ❌ No Walmart URL generated")
                continue
                
            print(f"   ✅ Walmart URL Generated: {walmart_url}")
            
            # Store for validation
            self.test_urls.append({
                'recipe_name': recipe_test['name'],
                'recipe_title': response.get('title', 'Unknown'),
                'recipe_id': recipe_id,
                'walmart_url': walmart_url,
                'product_ids': [p['product_id'] for p in test_products],
                'total_price': custom_response.get('total_price', 0)
            })
    
    def validate_walmart_urls(self):
        """Validate the generated Walmart URLs"""
        print(f"\n🔍 Validating {len(self.test_urls)} Walmart URLs...")
        
        validation_results = []
        
        for url_data in self.test_urls:
            print(f"\n   Validating: {url_data['recipe_name']}")
            walmart_url = url_data['walmart_url']
            
            # URL Format Validation
            format_checks = {
                'has_https': walmart_url.startswith('https://'),
                'has_walmart_domain': 'affil.walmart.com' in walmart_url,
                'has_cart_path': '/cart/addToCart' in walmart_url,
                'has_items_param': 'items=' in walmart_url,
                'no_spaces': ' ' not in walmart_url,
                'no_special_chars': all(c.isalnum() or c in ':/?.=,-' for c in walmart_url)
            }
            
            # Product ID Validation
            product_ids = url_data['product_ids']
            id_checks = {
                'has_product_ids': len(product_ids) > 0,
                'all_numeric': all(pid.isdigit() for pid in product_ids),
                'all_valid_length': all(len(pid) >= 6 for pid in product_ids),
                'no_mock_patterns': not any(any(pattern in pid for pattern in ['10315', 'walmart-', 'mock-']) for pid in product_ids)
            }
            
            # Extract IDs from URL for cross-validation
            url_ids = []
            if 'items=' in walmart_url:
                items_part = walmart_url.split('items=')[1].split('&')[0]
                url_ids = items_part.split(',')
            
            url_id_checks = {
                'ids_match_products': set(url_ids) == set(product_ids),
                'url_ids_valid_format': all(uid.isdigit() and len(uid) >= 6 for uid in url_ids),
                'no_duplicate_ids': len(url_ids) == len(set(url_ids))
            }
            
            # Overall validation
            all_format_valid = all(format_checks.values())
            all_ids_valid = all(id_checks.values())
            all_url_ids_valid = all(url_id_checks.values())
            
            overall_valid = all_format_valid and all_ids_valid and all_url_ids_valid
            
            print(f"     Format Valid: {'✅' if all_format_valid else '❌'}")
            print(f"     Product IDs Valid: {'✅' if all_ids_valid else '❌'}")
            print(f"     URL IDs Valid: {'✅' if all_url_ids_valid else '❌'}")
            print(f"     Overall Valid: {'✅' if overall_valid else '❌'}")
            
            if not all_format_valid:
                failed_format = [k for k, v in format_checks.items() if not v]
                print(f"     Failed Format Checks: {failed_format}")
                
            if not all_ids_valid:
                failed_ids = [k for k, v in id_checks.items() if not v]
                print(f"     Failed ID Checks: {failed_ids}")
                
            if not all_url_ids_valid:
                failed_url_ids = [k for k, v in url_id_checks.items() if not v]
                print(f"     Failed URL ID Checks: {failed_url_ids}")
            
            validation_results.append({
                'recipe_name': url_data['recipe_name'],
                'recipe_title': url_data['recipe_title'],
                'walmart_url': walmart_url,
                'product_ids': product_ids,
                'url_ids': url_ids,
                'format_valid': all_format_valid,
                'ids_valid': all_ids_valid,
                'url_ids_valid': all_url_ids_valid,
                'overall_valid': overall_valid,
                'format_checks': format_checks,
                'id_checks': id_checks,
                'url_id_checks': url_id_checks
            })
        
        return validation_results
    
    def test_url_accessibility(self, validation_results):
        """Test if the URLs are accessible (without actually adding to cart)"""
        print(f"\n🌐 Testing URL Accessibility...")
        
        for result in validation_results:
            if not result['overall_valid']:
                print(f"   Skipping {result['recipe_name']} - Invalid URL format")
                continue
                
            walmart_url = result['walmart_url']
            print(f"\n   Testing: {result['recipe_name']}")
            print(f"   URL: {walmart_url}")
            
            try:
                # Make a HEAD request to check if URL is accessible
                # We don't want to actually add items to cart, just check if URL is valid
                response = requests.head(walmart_url, timeout=10, allow_redirects=True)
                
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ URL is accessible")
                elif response.status_code in [301, 302, 307, 308]:
                    print(f"   ✅ URL redirects (normal for affiliate links)")
                elif response.status_code == 404:
                    print(f"   ❌ URL not found - may indicate invalid product IDs")
                elif response.status_code == 400:
                    print(f"   ❌ Bad request - may indicate invalid parameters")
                else:
                    print(f"   ⚠️ Unexpected status code: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⚠️ Request timed out")
            except requests.exceptions.ConnectionError:
                print(f"   ⚠️ Connection error")
            except Exception as e:
                print(f"   ⚠️ Error testing URL: {str(e)}")
    
    def run_validation(self):
        """Run the complete Walmart URL validation"""
        print("=" * 80)
        print("🔗 WALMART URL VALIDATION TEST")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.setup_test_user():
            print("❌ Failed to setup test user")
            return False
            
        self.generate_test_walmart_urls()
        
        if not self.test_urls:
            print("❌ No Walmart URLs generated for testing")
            return False
            
        validation_results = self.validate_walmart_urls()
        
        # Test URL accessibility
        self.test_url_accessibility(validation_results)
        
        # Final analysis
        print("\n" + "=" * 80)
        print("🎯 WALMART URL VALIDATION RESULTS")
        print("=" * 80)
        
        valid_urls = [r for r in validation_results if r['overall_valid']]
        invalid_urls = [r for r in validation_results if not r['overall_valid']]
        
        print(f"Valid URLs: {len(valid_urls)}/{len(validation_results)}")
        print(f"Invalid URLs: {len(invalid_urls)}/{len(validation_results)}")
        
        if valid_urls:
            print("\n✅ VALID WALMART URLS:")
            for result in valid_urls:
                print(f"   - {result['recipe_name']}: {result['recipe_title']}")
                print(f"     Product IDs: {result['product_ids']}")
                print(f"     URL: {result['walmart_url']}")
        
        if invalid_urls:
            print("\n❌ INVALID WALMART URLS:")
            for result in invalid_urls:
                print(f"   - {result['recipe_name']}: {result['recipe_title']}")
                issues = []
                if not result['format_valid']:
                    issues.append("Format issues")
                if not result['ids_valid']:
                    issues.append("Product ID issues")
                if not result['url_ids_valid']:
                    issues.append("URL ID issues")
                print(f"     Issues: {', '.join(issues)}")
        
        # Overall assessment
        print("\n" + "=" * 80)
        print("🔍 ISSUE ANALYSIS")
        print("=" * 80)
        
        if len(valid_urls) == len(validation_results):
            print("✅ ALL WALMART URLS ARE VALID")
            print("The user's 'invalid item or quantity' error is likely not due to URL format issues.")
        elif len(valid_urls) > 0:
            print("⚠️ SOME WALMART URLS ARE INVALID")
            print("This could cause intermittent 'invalid item or quantity' errors.")
        else:
            print("❌ ALL WALMART URLS ARE INVALID")
            print("This would definitely cause 'invalid item or quantity' errors.")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return len(invalid_urls) == 0

if __name__ == "__main__":
    validator = WalmartURLValidator()
    success = validator.run_validation()
    exit(0 if success else 1)