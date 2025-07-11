#!/usr/bin/env python3
"""
Focused test for Walmart Integration Mock Data Removal
Tests specifically for the '10315' pattern mock product IDs filtering
"""

import requests
import json
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

class WalmartMockDataTester:
    def __init__(self, base_url="https://407d4e17-1478-4b87-bdc3-d8a695a6f09c.preview.emergentagent.com"):
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
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
            else:
                print(f"❌ Unsupported method: {method}")
                return False, {}
            
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
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_test_user(self):
        """Create and verify a test user"""
        print("\n" + "=" * 60)
        print("🔧 SETTING UP TEST USER")
        print("=" * 60)
        
        # Register user
        user_data = {
            "first_name": "Walmart",
            "last_name": "Tester",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": []
        }
        
        success, response = self.run_test(
            "Register Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not success:
            print("❌ Failed to register test user")
            return False
            
        self.user_id = response.get('user_id')
        print(f"✅ User registered with ID: {self.user_id}")
        
        # Get verification code
        code_success, code_response = self.run_test(
            "Get Verification Code",
            "GET",
            f"debug/verification-codes/{self.test_email}",
            200
        )
        
        if not code_success:
            print("❌ Failed to get verification code")
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
        
        if verify_success:
            print("✅ Email verified successfully")
            return True
        else:
            print("❌ Failed to verify email")
            return False

    def create_test_recipe(self):
        """Create a recipe with common ingredients like pasta, tomatoes, sugar"""
        print("\n" + "=" * 60)
        print("🍝 CREATING TEST RECIPE WITH COMMON INGREDIENTS")
        print("=" * 60)
        
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": "cuisine",
            "cuisine_type": "italian",
            "dietary_preferences": [],
            "ingredients_on_hand": ["pasta", "tomatoes", "sugar", "olive oil", "garlic"],
            "prep_time_max": 30,
            "servings": 4,
            "difficulty": "easy"
        }
        
        success, response = self.run_test(
            "Generate Test Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"✅ Recipe created with ID: {self.recipe_id}")
            print(f"Recipe title: {response.get('title', 'Unknown')}")
            
            # Show ingredients and shopping list
            if 'ingredients' in response:
                print(f"Ingredients: {response['ingredients'][:3]}...")  # Show first 3
            if 'shopping_list' in response:
                print(f"Shopping list: {response['shopping_list'][:5]}...")  # Show first 5
                
            return True
        else:
            print("❌ Failed to create test recipe")
            return False

    def test_cart_options_mock_filtering(self):
        """Test the /api/grocery/cart-options endpoint for mock data filtering"""
        print("\n" + "=" * 60)
        print("🛒 TESTING CART OPTIONS MOCK DATA FILTERING")
        print("=" * 60)
        
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available")
            return False
            
        success, response = self.run_test(
            "Cart Options with Mock Data Check",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": self.recipe_id, "user_id": self.user_id},
            timeout=45
        )
        
        if not success:
            print("❌ Cart options endpoint failed")
            return False
            
        print("✅ Cart options endpoint responded successfully")
        
        # Analyze the response for mock product IDs
        mock_ids_found = []
        real_ids_found = []
        total_products = 0
        
        if 'ingredient_options' in response:
            print(f"\n📊 ANALYZING {len(response['ingredient_options'])} INGREDIENT OPTIONS:")
            
            for i, ingredient_option in enumerate(response['ingredient_options']):
                ingredient_name = ingredient_option.get('ingredient_name', f'Ingredient {i+1}')
                options = ingredient_option.get('options', [])
                
                print(f"\n{i+1}. {ingredient_name}: {len(options)} product options")
                
                for j, product in enumerate(options):
                    product_id = product.get('product_id', '')
                    product_name = product.get('name', 'Unknown')
                    product_price = product.get('price', 0.0)
                    
                    total_products += 1
                    
                    # Check for mock product ID patterns
                    is_mock = False
                    mock_reason = ""
                    
                    if not product_id.isdigit():
                        is_mock = True
                        mock_reason = "Non-numeric ID"
                    elif len(product_id) < 6:
                        is_mock = True
                        mock_reason = "ID too short (< 6 digits)"
                    elif product_id.startswith('10315'):
                        is_mock = True
                        mock_reason = "Starts with '10315' (mock pattern)"
                    elif product_id.startswith('walmart-'):
                        is_mock = True
                        mock_reason = "Starts with 'walmart-'"
                    elif product_id.startswith('mock-'):
                        is_mock = True
                        mock_reason = "Starts with 'mock-'"
                    
                    if is_mock:
                        mock_ids_found.append({
                            'id': product_id,
                            'name': product_name,
                            'reason': mock_reason,
                            'ingredient': ingredient_name
                        })
                        print(f"   ❌ MOCK: {product_name} - ${product_price} (ID: {product_id}) - {mock_reason}")
                    else:
                        real_ids_found.append({
                            'id': product_id,
                            'name': product_name,
                            'ingredient': ingredient_name
                        })
                        print(f"   ✅ REAL: {product_name} - ${product_price} (ID: {product_id})")
        
        # Store results for final report
        self.mock_product_ids_found = mock_ids_found
        self.real_product_ids_found = real_ids_found
        
        # Print summary
        print(f"\n📈 SUMMARY:")
        print(f"Total products analyzed: {total_products}")
        print(f"Real Walmart products: {len(real_ids_found)}")
        print(f"Mock products found: {len(mock_ids_found)}")
        
        if mock_ids_found:
            print(f"\n❌ MOCK PRODUCTS DETECTED:")
            for mock in mock_ids_found:
                print(f"  - {mock['id']} ({mock['ingredient']}) - {mock['reason']}")
        else:
            print(f"\n✅ NO MOCK PRODUCTS FOUND - FILTERING IS WORKING!")
            
        return len(mock_ids_found) == 0  # Test passes if no mock IDs found

    def test_custom_cart_mock_rejection(self):
        """Test that custom cart endpoint rejects mock product IDs"""
        print("\n" + "=" * 60)
        print("🚫 TESTING CUSTOM CART MOCK ID REJECTION")
        print("=" * 60)
        
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available")
            return False
            
        # Test with mock product IDs that should be rejected
        mock_test_cases = [
            {
                "name": "10315 Pattern Mock ID",
                "products": [
                    {
                        "ingredient_name": "sugar",
                        "product_id": "10315162",  # Mock pattern
                        "name": "Mock Sugar Product",
                        "price": 2.99,
                        "quantity": 1
                    }
                ]
            },
            {
                "name": "Walmart- Prefix Mock ID",
                "products": [
                    {
                        "ingredient_name": "pasta",
                        "product_id": "walmart-123456",  # Mock pattern
                        "name": "Mock Pasta Product",
                        "price": 1.99,
                        "quantity": 1
                    }
                ]
            },
            {
                "name": "Mock- Prefix Mock ID",
                "products": [
                    {
                        "ingredient_name": "tomatoes",
                        "product_id": "mock-789123",  # Mock pattern
                        "name": "Mock Tomato Product",
                        "price": 3.49,
                        "quantity": 1
                    }
                ]
            },
            {
                "name": "Short ID Mock",
                "products": [
                    {
                        "ingredient_name": "oil",
                        "product_id": "12345",  # Too short
                        "name": "Mock Oil Product",
                        "price": 4.99,
                        "quantity": 1
                    }
                ]
            }
        ]
        
        all_rejected = True
        
        for test_case in mock_test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            
            custom_cart_data = {
                "user_id": self.user_id,
                "recipe_id": self.recipe_id,
                "products": test_case['products']
            }
            
            success, response = self.run_test(
                f"Custom Cart - {test_case['name']}",
                "POST",
                "grocery/custom-cart",
                400,  # Expect 400 error for mock IDs
                data=custom_cart_data
            )
            
            if success:
                print(f"✅ Mock ID correctly rejected: {test_case['products'][0]['product_id']}")
            else:
                print(f"❌ Mock ID was NOT rejected: {test_case['products'][0]['product_id']}")
                all_rejected = False
                
                # If it didn't return 400, check what it returned
                if 'walmart_url' in response:
                    print(f"⚠️ WARNING: Mock ID was included in Walmart URL: {response['walmart_url']}")
        
        # Test with valid product IDs (should succeed)
        print(f"\n🧪 Testing: Valid Product IDs")
        
        valid_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "products": [
                {
                    "ingredient_name": "pasta",
                    "product_id": "123456789",  # Valid format
                    "name": "Real Pasta Product",
                    "price": 1.99,
                    "quantity": 1
                },
                {
                    "ingredient_name": "tomatoes",
                    "product_id": "987654321",  # Valid format
                    "name": "Real Tomato Product",
                    "price": 2.49,
                    "quantity": 1
                }
            ]
        }
        
        valid_success, valid_response = self.run_test(
            "Custom Cart - Valid Product IDs",
            "POST",
            "grocery/custom-cart",
            200,  # Expect success for valid IDs
            data=valid_cart_data
        )
        
        if valid_success:
            print("✅ Valid product IDs accepted correctly")
            if 'walmart_url' in valid_response:
                print(f"✅ Walmart URL generated: {valid_response['walmart_url'][:50]}...")
        else:
            print("❌ Valid product IDs were rejected")
            all_rejected = False
            
        return all_rejected

    def run_comprehensive_test(self):
        """Run the complete Walmart mock data removal test"""
        print("\n" + "=" * 80)
        print("🎯 WALMART INTEGRATION MOCK DATA REMOVAL TEST")
        print("=" * 80)
        print("Testing specifically for '10315' pattern mock product ID filtering")
        print("=" * 80)
        
        # Step 1: Setup
        if not self.setup_test_user():
            print("\n❌ FAILED: Could not setup test user")
            return False
            
        # Step 2: Create recipe
        if not self.create_test_recipe():
            print("\n❌ FAILED: Could not create test recipe")
            return False
            
        # Step 3: Test cart options filtering
        cart_options_passed = self.test_cart_options_mock_filtering()
        
        # Step 4: Test custom cart rejection
        custom_cart_passed = self.test_custom_cart_mock_rejection()
        
        # Final Results
        print("\n" + "=" * 80)
        print("📊 FINAL TEST RESULTS")
        print("=" * 80)
        
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🔍 MOCK DATA ANALYSIS:")
        print(f"Mock product IDs found: {len(self.mock_product_ids_found)}")
        print(f"Real product IDs found: {len(self.real_product_ids_found)}")
        
        if self.mock_product_ids_found:
            print(f"\n❌ CRITICAL ISSUE: Mock product IDs detected!")
            for mock in self.mock_product_ids_found:
                print(f"  - {mock['id']} in {mock['ingredient']} - {mock['reason']}")
        else:
            print(f"\n✅ SUCCESS: No mock product IDs found!")
            
        print(f"\n🎯 VALIDATION CRITERIA RESULTS:")
        print(f"✅ Zero product IDs start with '10315': {'YES' if not any(m['id'].startswith('10315') for m in self.mock_product_ids_found) else 'NO'}")
        print(f"✅ Zero product IDs start with 'walmart-': {'YES' if not any(m['id'].startswith('walmart-') for m in self.mock_product_ids_found) else 'NO'}")
        print(f"✅ Zero product IDs start with 'mock-': {'YES' if not any(m['id'].startswith('mock-') for m in self.mock_product_ids_found) else 'NO'}")
        print(f"✅ All product IDs are numeric with 6+ digits: {'YES' if all(p['id'].isdigit() and len(p['id']) >= 6 for p in self.real_product_ids_found) else 'NO'}")
        print(f"✅ Custom cart rejects mock IDs: {'YES' if custom_cart_passed else 'NO'}")
        print(f"✅ Cart options filters mock data: {'YES' if cart_options_passed else 'NO'}")
        
        overall_success = cart_options_passed and custom_cart_passed and len(self.mock_product_ids_found) == 0
        
        print(f"\n🏆 OVERALL RESULT: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        
        if overall_success:
            print("The Walmart integration mock data filtering is working correctly!")
            print("Users will only see real Walmart products in their affiliate links.")
        else:
            print("CRITICAL: Mock data is still present in Walmart integration results!")
            print("This needs immediate attention before deployment.")
            
        return overall_success

if __name__ == "__main__":
    tester = WalmartMockDataTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)