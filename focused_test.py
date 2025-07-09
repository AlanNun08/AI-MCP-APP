import requests
import json
import time
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

class FocusedTester:
    def __init__(self, base_url="https://1896460c-1fcb-418f-bf8d-0da71d07a349.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = {}
        
        # Test user data
        self.random_id = random.randint(10000, 99999)
        self.test_email = f"test.user.{self.random_id}@example.com"
        self.test_password = "SecureP@ssw0rd123"
        self.user_id = None
        self.verification_code = None
        self.recipe_id = None
        
        # Performance tracking
        self.response_times = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a single API test with configurable timeout and performance tracking"""
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
                self.test_results[name] = False
                return False, {}
            
            elapsed_time = time.time() - start_time
            self.response_times[name] = elapsed_time
            
            print(f"⏱️ Request completed in {elapsed_time:.2f} seconds")
            logger.info(f"Request completed in {elapsed_time:.2f} seconds")
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                self.test_results[name] = True
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                self.test_results[name] = False
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
            logger.error(f"Request timed out after {elapsed_time:.2f} seconds (timeout set to {timeout}s)")
            self.test_results[name] = False
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            logger.error(f"Connection error: Could not connect to {url}")
            self.test_results[name] = False
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            logger.error(f"Test failed with error: {str(e)}")
            self.test_results[name] = False
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

    def test_user_registration(self):
        """Test user registration with email verification"""
        print("\n" + "=" * 50)
        print("Testing User Registration with Email Verification")
        print("=" * 50)
        
        # Test valid registration
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": ["vegetarian"],
            "allergies": ["nuts"],
            "favorite_cuisines": ["italian", "mexican"]
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'user_id' in response:
            self.user_id = response['user_id']
            print(f"✅ User registered with ID: {self.user_id}")
            return True
        return False
    
    def test_get_verification_code(self):
        """Test getting verification code from debug endpoint"""
        if not self.test_email:
            print("❌ No test email provided")
            return False
            
        success, response = self.run_test(
            "Get Verification Code",
            "GET",
            f"debug/verification-codes/{self.test_email}",
            200
        )
        
        if success and 'codes' in response and len(response['codes']) > 0:
            self.verification_code = response['codes'][0]['code']
            print(f"✅ Retrieved verification code: {self.verification_code}")
            return True
        elif success and 'last_test_code' in response and response['last_test_code']:
            self.verification_code = response['last_test_code']
            print(f"✅ Retrieved last test verification code: {self.verification_code}")
            return True
        else:
            print("❌ No verification code found")
            return False
    
    def test_email_verification(self):
        """Test email verification with code"""
        if not self.test_email or not self.verification_code:
            print("❌ No test email or verification code available")
            return False
            
        verify_data = {
            "email": self.test_email,
            "code": self.verification_code
        }
        
        success, response = self.run_test(
            "Email Verification",
            "POST",
            "auth/verify",
            200,
            data=verify_data
        )
        
        if success and 'message' in response:
            if 'verified' in response['message'].lower():
                print("✅ Email verified successfully")
                return True
        
        return success
    
    def test_login(self):
        """Test login with verified user"""
        if not self.test_email:
            print("❌ No test email available")
            return False
            
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'status' in response:
            if response['status'] == 'success':
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Unexpected response for login: {response}")
                return False
        
        return success
    
    def test_password_reset_request(self):
        """Test password reset request"""
        if not self.test_email:
            print("❌ No test email available")
            return False
            
        reset_request = {
            "email": self.test_email
        }
        
        success, response = self.run_test(
            "Password Reset Request",
            "POST",
            "auth/forgot-password",
            200,
            data=reset_request
        )
        
        if success and 'message' in response:
            print("✅ Password reset request successful")
            return True
        
        return success
    
    def test_generate_recipe(self):
        """Test recipe generation with realistic ingredients"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "italian",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["pasta", "tomatoes", "garlic", "olive oil", "basil"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "medium"
        }
        
        print("Testing recipe generation with 60 second timeout...")
        success, response = self.run_test(
            "Generate Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60  # Set timeout to 60 seconds to check for timeout issues
        )
        
        if success and 'id' in response:
            self.recipe_id = response['id']
            print(f"Generated recipe with ID: {self.recipe_id}")
            print(f"Recipe title: {response.get('title', 'Unknown')}")
            print(f"Recipe ingredients: {len(response.get('ingredients', []))} ingredients")
            return True
        return False
    
    def test_generate_healthy_recipe(self):
        """Test healthy recipe generation with calorie limits"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        recipe_request = {
            "user_id": self.user_id,
            "cuisine_type": "mediterranean",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["chickpeas", "olive oil", "tomatoes", "cucumber", "feta"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "medium",
            "is_healthy": True,
            "max_calories_per_serving": 400
        }
        
        print("Testing healthy recipe generation with 60 second timeout...")
        success, response = self.run_test(
            "Generate Healthy Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60
        )
        
        if success and 'id' in response:
            healthy_recipe_id = response['id']
            print(f"Generated healthy recipe with ID: {healthy_recipe_id}")
            
            # Verify calorie information is present
            if 'calories_per_serving' in response and response['calories_per_serving']:
                print(f"✅ Calorie information present: {response['calories_per_serving']} calories per serving")
                if response['calories_per_serving'] <= recipe_request['max_calories_per_serving']:
                    print(f"✅ Calorie limit respected: {response['calories_per_serving']} <= {recipe_request['max_calories_per_serving']}")
                else:
                    print(f"⚠️ Calorie limit exceeded: {response['calories_per_serving']} > {recipe_request['max_calories_per_serving']}")
            else:
                print("⚠️ No calorie information in the response")
                
            return True
        return False
    
    def test_create_grocery_cart(self):
        """Test grocery cart generation with actual product data"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        success, response = self.run_test(
            "Create Grocery Cart with Options",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": self.recipe_id, "user_id": self.user_id}
        )
        
        if success and 'id' in response:
            cart_options_id = response['id']
            print(f"Created grocery cart with options, ID: {cart_options_id}")
            
            # Verify multiple options per ingredient
            if 'ingredient_options' in response:
                options_count = len(response['ingredient_options'])
                print(f"Found {options_count} ingredients with options")
                
                # Check if each ingredient has multiple options
                for i, ingredient_option in enumerate(response['ingredient_options']):
                    if 'options' in ingredient_option:
                        product_count = len(ingredient_option['options'])
                        print(f"  Ingredient {i+1}: {ingredient_option.get('ingredient_name', 'Unknown')} - {product_count} product options")
                        
                        # Check if we have product options with prices
                        if product_count > 0:
                            prices = [product.get('price', 0) for product in ingredient_option['options']]
                            if prices:
                                print(f"    Price range: ${min(prices):.2f} - ${max(prices):.2f}")
            
            return True
        return False
    
    def test_create_custom_cart(self):
        """Test creating custom cart from selected options"""
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available for testing")
            return False
            
        # Create a custom cart directly
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
        
        success, response = self.run_test(
            "Create Custom Cart",
            "POST",
            "grocery/custom-cart",
            200,
            data=custom_cart_data
        )
        
        if success and 'id' in response:
            print(f"Created custom cart with ID: {response['id']}")
            print(f"Total price: ${response.get('total_price', 0):.2f}")
            print(f"Walmart URL: {response.get('walmart_url', 'N/A')}")
            
            # Verify Walmart URL format
            if 'walmart_url' in response:
                walmart_url = response['walmart_url']
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
        return False
    
    def test_email_service_with_mailjet(self):
        """Test if the email service is using Mailjet API with the new keys"""
        print("\n" + "=" * 50)
        print("Testing Email Service with Mailjet API")
        print("=" * 50)
        
        # We'll use the password reset endpoint to trigger an email
        reset_email = f"alan.nunez0310+test{self.random_id}@icloud.com"
        
        # First, create a user to reset password for
        user_data = {
            "first_name": "Mailjet",
            "last_name": "Test",
            "email": reset_email,
            "password": "SecureP@ssw0rd123",
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": []
        }
        
        # Register the user
        reg_success, _ = self.run_test(
            "Register User for Mailjet Test",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not reg_success:
            print("❌ Failed to register user for Mailjet test")
            return False
        
        # Request password reset to trigger email
        reset_request = {
            "email": reset_email
        }
        
        reset_success, _ = self.run_test(
            "Request Password Reset for Mailjet Test",
            "POST",
            "auth/forgot-password",
            200,
            data=reset_request
        )
        
        if not reset_success:
            print("❌ Failed to request password reset for Mailjet test")
            return False
        
        print("✅ Password reset request sent successfully")
        print("✅ Email should have been sent via Mailjet API")
        print("NOTE: Check the real email inbox to confirm receipt")
        
        return True
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("🚀 COMPREHENSIVE BACKEND TESTING FOR AI RECIPE + GROCERY DELIVERY APP 🚀")
        print("=" * 80)
        
        # Test API root
        self.test_api_root()
        
        # Test Email Service with Mailjet
        self.test_email_service_with_mailjet()
        
        # Test Complete User Flow
        print("\n" + "=" * 50)
        print("Testing Complete User Flow")
        print("=" * 50)
        
        self.test_user_registration()
        self.test_get_verification_code()
        self.test_email_verification()
        self.test_login()
        self.test_password_reset_request()
        
        # Test Recipe Generation
        print("\n" + "=" * 50)
        print("Testing Recipe Generation")
        print("=" * 50)
        
        self.test_generate_recipe()
        self.test_generate_healthy_recipe()
        
        # Test Grocery Cart
        print("\n" + "=" * 50)
        print("Testing Grocery Cart")
        print("=" * 50)
        
        self.test_create_grocery_cart()
        self.test_create_custom_cart()
        
        # Print results
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"Tests passed: {self.tests_passed}/{self.tests_run} ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Print performance results
        print("\n" + "=" * 50)
        print("⏱️ API PERFORMANCE RESULTS")
        print("=" * 50)
        
        for name, time in sorted(self.response_times.items(), key=lambda x: x[1], reverse=True):
            status = "✅" if self.test_results.get(name, False) else "❌"
            print(f"{status} {name}: {time:.2f} seconds")
        
        # Check if all endpoints respond under 5 seconds
        slow_endpoints = [name for name, time in self.response_times.items() if time > 5.0]
        if slow_endpoints:
            print("\n⚠️ Endpoints with response time over 5 seconds:")
            for name in slow_endpoints:
                print(f"  - {name}: {self.response_times[name]:.2f} seconds")
        else:
            print("\n✅ All endpoints respond in under 5 seconds")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = FocusedTester()
    tester.run_all_tests()