import requests
import json
import time
import sys
import uuid
import logging
import random
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIRecipeAppTester:
    def __init__(self, base_url="https://1896460c-1fcb-418f-bf8d-0da71d07a349.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.recipe_id = None
        self.cart_id = None
        self.test_email = f"test_{uuid.uuid4()}@example.com"
        self.test_password = "SecureP@ssw0rd123"
        self.verification_code = None
        self.reset_code = None
        self.results = {
            "Authentication": {
                "Registration": False,
                "Verification": False,
                "Login": False,
                "Password Reset": False
            },
            "Recipe Generation": {
                "Basic Recipe": False,
                "Healthy Mode": False,
                "Budget Mode": False
            },
            "Grocery Cart": {
                "Cart Options": False,
                "Custom Cart": False
            },
            "Database Operations": {
                "User Storage": False,
                "Recipe Storage": False
            },
            "Email Service": {
                "Verification Email": False,
                "Reset Email": False
            }
        }

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
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
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

    def test_authentication_system(self):
        """Test complete authentication flow"""
        print("\n" + "=" * 50)
        print("Testing Authentication System")
        print("=" * 50)
        
        # Step 1: Register user
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "favorite_cuisines": ["italian", "mexican"]
        }
        
        register_success, register_response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not register_success:
            print("❌ User registration failed - cannot continue authentication flow test")
            return False
        
        self.results["Authentication"]["Registration"] = True
        print("✅ User registration successful")
        
        # Step 2: Get verification code
        code_success, code_response = self.run_test(
            "Get Verification Code",
            "GET",
            f"debug/verification-codes/{self.test_email}",
            200
        )
        
        if not code_success:
            print("❌ Failed to get verification code")
            return False
        
        if 'codes' in code_response and len(code_response['codes']) > 0:
            self.verification_code = code_response['codes'][0]['code']
            print(f"✅ Retrieved verification code: {self.verification_code}")
        elif 'last_test_code' in code_response and code_response['last_test_code']:
            self.verification_code = code_response['last_test_code']
            print(f"✅ Retrieved last test verification code: {self.verification_code}")
        else:
            print("❌ No verification code found")
            return False
        
        # Step 3: Verify email
        verify_data = {
            "email": self.test_email,
            "code": self.verification_code
        }
        
        verify_success, _ = self.run_test(
            "Email Verification",
            "POST",
            "auth/verify",
            200,
            data=verify_data
        )
        
        if not verify_success:
            print("❌ Email verification failed")
            return False
        
        self.results["Authentication"]["Verification"] = True
        self.results["Email Service"]["Verification Email"] = True
        print("✅ Email verification successful")
        
        # Step 4: Login with verified user
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        login_success, login_response = self.run_test(
            "Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if not login_success or 'status' not in login_response or login_response['status'] != 'success':
            print("❌ Login failed")
            return False
        
        self.results["Authentication"]["Login"] = True
        print("✅ Login successful")
        
        # Step 5: Test password reset flow
        reset_request = {
            "email": self.test_email
        }
        
        reset_success, _ = self.run_test(
            "Request Password Reset",
            "POST",
            "auth/forgot-password",
            200,
            data=reset_request
        )
        
        if not reset_success:
            print("❌ Password reset request failed")
            return False
        
        print("✅ Password reset request successful")
        
        # Get reset code
        reset_code_success, reset_code_response = self.run_test(
            "Get Reset Code",
            "GET",
            f"debug/verification-codes/{self.test_email}",
            200
        )
        
        if not reset_code_success:
            print("❌ Failed to get reset code")
            return False
        
        if 'codes' in reset_code_response and len(reset_code_response['codes']) > 0:
            self.reset_code = reset_code_response['codes'][0]['code']
            print(f"✅ Retrieved reset code: {self.reset_code}")
        elif 'last_test_code' in reset_code_response and reset_code_response['last_test_code']:
            self.reset_code = reset_code_response['last_test_code']
            print(f"✅ Retrieved last test reset code: {self.reset_code}")
        else:
            print("❌ No reset code found")
            return False
        
        # Reset password
        new_password = "NewSecureP@ssw0rd456"
        reset_data = {
            "email": self.test_email,
            "reset_code": self.reset_code,
            "new_password": new_password
        }
        
        reset_verify_success, _ = self.run_test(
            "Reset Password",
            "POST",
            "auth/reset-password",
            200,
            data=reset_data
        )
        
        if not reset_verify_success:
            print("❌ Password reset failed")
            return False
        
        self.results["Authentication"]["Password Reset"] = True
        self.results["Email Service"]["Reset Email"] = True
        print("✅ Password reset successful")
        
        # Login with new password
        new_login_data = {
            "email": self.test_email,
            "password": new_password
        }
        
        new_login_success, new_login_response = self.run_test(
            "Login with New Password",
            "POST",
            "auth/login",
            200,
            data=new_login_data
        )
        
        if not new_login_success or 'status' not in new_login_response or new_login_response['status'] != 'success':
            print("❌ Login with new password failed")
            return False
        
        print("✅ Login with new password successful")
        
        # Save user ID for other tests
        if 'user' in new_login_response and 'id' in new_login_response['user']:
            self.user_id = new_login_response['user']['id']
            print(f"✅ User ID saved: {self.user_id}")
            self.results["Database Operations"]["User Storage"] = True
        
        return True

    def test_recipe_generation(self):
        """Test recipe generation with different modes"""
        print("\n" + "=" * 50)
        print("Testing Recipe Generation")
        print("=" * 50)
        
        if not self.user_id:
            print("❌ No user ID available - creating a test user")
            test_user = {
                "name": f"Test User {uuid.uuid4()}",
                "email": f"recipe_test_{uuid.uuid4()}@example.com",
                "dietary_preferences": ["vegetarian"],
                "allergies": ["nuts"],
                "favorite_cuisines": ["italian", "mexican"]
            }
            
            success, response = self.run_test(
                "Create Test User for Recipe Generation",
                "POST",
                "users",
                200,
                data=test_user
            )
            
            if success and 'id' in response:
                self.user_id = response['id']
                print(f"✅ Created test user with ID: {self.user_id}")
            else:
                print("❌ Failed to create test user")
                return False
        
        # Test basic recipe generation
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "italian",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["pasta", "tomatoes", "garlic"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "easy"
        }
        
        print("Testing basic recipe generation with 60 second timeout...")
        success, response = self.run_test(
            "Generate Basic Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60
        )
        
        if not success:
            print("❌ Basic recipe generation failed")
            return False
        
        if 'id' in response:
            self.recipe_id = response['id']
            print(f"✅ Generated recipe with ID: {self.recipe_id}")
            self.results["Recipe Generation"]["Basic Recipe"] = True
            self.results["Database Operations"]["Recipe Storage"] = True
        
        # Test healthy recipe generation
        healthy_recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "mediterranean",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["chickpeas", "olive oil", "tomatoes"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "medium",
            "is_healthy": True,
            "max_calories_per_serving": 400
        }
        
        print("Testing healthy recipe generation with 60 second timeout...")
        healthy_success, healthy_response = self.run_test(
            "Generate Healthy Recipe",
            "POST",
            "recipes/generate",
            200,
            data=healthy_recipe_request,
            timeout=60
        )
        
        if healthy_success and 'id' in healthy_response:
            print(f"✅ Generated healthy recipe with ID: {healthy_response['id']}")
            
            # Verify calorie information is present
            if 'calories_per_serving' in healthy_response and healthy_response['calories_per_serving']:
                print(f"✅ Calorie information present: {healthy_response['calories_per_serving']} calories per serving")
                if healthy_response['calories_per_serving'] <= healthy_recipe_request['max_calories_per_serving']:
                    print(f"✅ Calorie limit respected: {healthy_response['calories_per_serving']} <= {healthy_recipe_request['max_calories_per_serving']}")
                    self.results["Recipe Generation"]["Healthy Mode"] = True
                else:
                    print(f"⚠️ Calorie limit exceeded: {healthy_response['calories_per_serving']} > {healthy_recipe_request['max_calories_per_serving']}")
            else:
                print("⚠️ No calorie information in the response")
        
        # Test budget recipe generation
        budget_recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "american",
            "dietary_preferences": [],
            "ingredients_on_hand": ["potatoes", "onions", "beans"],
            "prep_time_max": 45,
            "servings": 4,
            "difficulty": "easy",
            "is_budget_friendly": True,
            "max_budget": 15.0
        }
        
        print("Testing budget recipe generation with 60 second timeout...")
        budget_success, budget_response = self.run_test(
            "Generate Budget-Friendly Recipe",
            "POST",
            "recipes/generate",
            200,
            data=budget_recipe_request,
            timeout=60
        )
        
        if budget_success and 'id' in budget_response:
            print(f"✅ Generated budget-friendly recipe with ID: {budget_response['id']}")
            self.results["Recipe Generation"]["Budget Mode"] = True
        
        return True

    def test_grocery_cart(self):
        """Test grocery cart functionality"""
        print("\n" + "=" * 50)
        print("Testing Grocery Cart Functionality")
        print("=" * 50)
        
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
        
        # Test cart options
        success, response = self.run_test(
            "Create Grocery Cart with Options",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": self.recipe_id, "user_id": self.user_id}
        )
        
        if not success:
            print("❌ Failed to create grocery cart with options")
            return False
        
        if 'id' in response:
            cart_options_id = response['id']
            print(f"✅ Created grocery cart with options, ID: {cart_options_id}")
            self.results["Grocery Cart"]["Cart Options"] = True
            
            # Verify multiple options per ingredient
            if 'ingredient_options' in response:
                options_count = len(response['ingredient_options'])
                print(f"Found {options_count} ingredients with options")
                
                # Check if each ingredient has multiple options
                for i, ingredient_option in enumerate(response['ingredient_options']):
                    if 'options' in ingredient_option:
                        product_count = len(ingredient_option['options'])
                        print(f"  Ingredient {i+1}: {ingredient_option.get('ingredient_name', 'Unknown')} - {product_count} product options")
        
        # Test custom cart
        custom_cart_data = {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "products": [
                {
                    "ingredient_name": "pasta",
                    "product_id": "12345",
                    "name": "Barilla Pasta",
                    "price": 2.99,
                    "quantity": 1
                },
                {
                    "ingredient_name": "tomatoes",
                    "product_id": "67890",
                    "name": "Roma Tomatoes",
                    "price": 1.99,
                    "quantity": 2
                },
                {
                    "ingredient_name": "garlic",
                    "product_id": "54321",
                    "name": "Fresh Garlic",
                    "price": 0.99,
                    "quantity": 1
                }
            ]
        }
        
        custom_success, custom_response = self.run_test(
            "Create Custom Cart",
            "POST",
            "grocery/custom-cart",
            200,
            data=custom_cart_data
        )
        
        if not custom_success:
            print("❌ Failed to create custom cart")
            return False
        
        if 'id' in custom_response:
            self.cart_id = custom_response['id']
            print(f"✅ Created custom cart with ID: {self.cart_id}")
            print(f"Total price: ${custom_response.get('total_price', 0):.2f}")
            print(f"Walmart URL: {custom_response.get('walmart_url', 'N/A')}")
            self.results["Grocery Cart"]["Custom Cart"] = True
            
            # Verify Walmart URL format
            if 'walmart_url' in custom_response:
                walmart_url = custom_response['walmart_url']
                if 'affil.walmart.com' in walmart_url and 'items=' in walmart_url:
                    print("✅ Walmart URL correctly formatted")
                    
                    # Check if all product IDs are in the URL
                    product_ids = [p['product_id'] for p in custom_cart_data['products']]
                    all_ids_in_url = all(pid in walmart_url for pid in product_ids)
                    if all_ids_in_url:
                        print("✅ All product IDs included in Walmart URL")
                    else:
                        print("⚠️ Not all product IDs found in Walmart URL")
                else:
                    print("⚠️ Walmart URL format may be incorrect")
        
        return True

    def run_comprehensive_test(self):
        """Run all tests and provide a comprehensive report"""
        print("\n" + "=" * 80)
        print("🚀 COMPREHENSIVE DEPLOYMENT READINESS TESTING 🚀")
        print("=" * 80)
        
        # Test API root
        api_root = self.test_api_root()
        if not api_root:
            print("❌ API root test failed - cannot continue")
            return False
        
        # Test authentication system
        auth_success = self.test_authentication_system()
        
        # Test recipe generation
        recipe_success = self.test_recipe_generation()
        
        # Test grocery cart
        cart_success = self.test_grocery_cart()
        
        # Print comprehensive report
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        for category, tests in self.results.items():
            print(f"\n{category}:")
            for test, result in tests.items():
                print(f"  {test}: {'✅ PASSED' if result else '❌ FAILED'}")
        
        # Calculate overall readiness
        auth_ready = all(self.results["Authentication"].values())
        recipe_ready = all(self.results["Recipe Generation"].values())
        cart_ready = all(self.results["Grocery Cart"].values())
        db_ready = all(self.results["Database Operations"].values())
        email_ready = all(self.results["Email Service"].values())
        
        critical_ready = auth_ready and recipe_ready and db_ready
        overall_ready = critical_ready and cart_ready and email_ready
        
        print("\n" + "=" * 50)
        if overall_ready:
            print("✅ OVERALL ASSESSMENT: READY FOR DEPLOYMENT")
            print("All systems are functioning correctly.")
        elif critical_ready:
            print("⚠️ OVERALL ASSESSMENT: PARTIALLY READY FOR DEPLOYMENT")
            print("Critical systems are working, but some non-critical systems have issues.")
        else:
            print("❌ OVERALL ASSESSMENT: NOT READY FOR DEPLOYMENT")
            print("Critical systems have issues that need to be addressed before deployment.")
        
        print("=" * 50)
        
        return overall_ready

def main():
    print("=" * 50)
    print("AI Recipe & Grocery App Comprehensive API Test")
    print("=" * 50)
    
    tester = AIRecipeAppTester()
    deployment_ready = tester.run_comprehensive_test()
    
    return 0 if deployment_ready else 1

if __name__ == "__main__":
    sys.exit(main())