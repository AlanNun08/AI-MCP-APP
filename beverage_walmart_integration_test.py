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

class BeverageWalmartIntegrationTester:
    def __init__(self, base_url="https://407d4e17-1478-4b87-bdc3-d8a695a6f09c.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.beverage_recipes = {}  # Store generated beverage recipes
        self.cart_options = {}  # Store cart options for each beverage
        self.custom_carts = {}  # Store custom carts for each beverage
        
        # Test user credentials
        self.test_email = f"beverage_test_{uuid.uuid4()}@example.com"
        self.test_password = "SecureP@ssw0rd123"
        
        # Beverage types to test
        self.beverage_types = ["coffee", "special lemonades", "thai tea", "boba tea"]
        
        # Expected clean ingredient patterns for beverages
        self.clean_ingredient_patterns = {
            "coffee": ["espresso beans", "coffee beans", "milk", "sugar", "vanilla syrup", "caramel", "cream"],
            "special lemonades": ["lemons", "honey", "mint", "herbs", "sugar", "water", "fruit"],
            "thai tea": ["thai tea", "tea", "condensed milk", "milk", "sugar", "spices", "coconut milk"],
            "boba tea": ["tapioca pearls", "tea", "milk", "brown sugar", "taro", "fruit", "syrup"]
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
            print(f"❌ Failed - Request timed out after {elapsed_time:.2f} seconds (timeout set to {timeout}s)")
            logger.error(f"Request timed out after {elapsed_time:.2f} seconds (timeout set to {timeout}s)")
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            logger.error(f"Connection error: Could not connect to {url}")
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            logger.error(f"Test failed with error: {str(e)}")
            return False, {}

    def setup_test_user(self):
        """Create and verify a test user for beverage testing"""
        print("\n" + "=" * 60)
        print("🔧 SETTING UP TEST USER FOR BEVERAGE TESTING")
        print("=" * 60)
        
        # Create user
        user_data = {
            "first_name": "Beverage",
            "last_name": "Tester",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": ["american"]
        }
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not success:
            print("❌ Failed to create test user")
            return False
        
        self.user_id = response.get('user_id')
        print(f"✅ Created test user with ID: {self.user_id}")
        
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
            print("✅ Test user setup complete")
            return True
        else:
            print("❌ Failed to verify test user")
            return False

    def test_beverage_recipe_generation(self):
        """Test beverage recipe generation for all beverage types"""
        print("\n" + "=" * 60)
        print("🧋 TESTING BEVERAGE RECIPE GENERATION")
        print("=" * 60)
        
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
        
        all_passed = True
        
        for beverage_type in self.beverage_types:
            print(f"\n--- Testing {beverage_type.title()} Recipe Generation ---")
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "beverage",
                "cuisine_type": beverage_type,
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 30,
                "servings": 2,
                "difficulty": "medium"
            }
            
            success, response = self.run_test(
                f"Generate {beverage_type.title()} Recipe",
                "POST",
                "recipes/generate",
                200,
                data=recipe_request,
                timeout=60
            )
            
            if success and 'id' in response:
                self.beverage_recipes[beverage_type] = response
                recipe_id = response['id']
                print(f"✅ Generated {beverage_type} recipe with ID: {recipe_id}")
                print(f"   Title: {response.get('title', 'N/A')}")
                
                # Analyze shopping list quality
                shopping_list = response.get('shopping_list', [])
                if shopping_list:
                    print(f"   Shopping List ({len(shopping_list)} items): {shopping_list}")
                    
                    # Check for clean ingredient names (no quantities/measurements)
                    clean_score = self.analyze_shopping_list_cleanliness(shopping_list, beverage_type)
                    print(f"   Shopping List Cleanliness Score: {clean_score:.1f}%")
                    
                    if clean_score >= 80:
                        print(f"   ✅ Shopping list is clean and suitable for Walmart search")
                    else:
                        print(f"   ⚠️ Shopping list may have issues with quantities/measurements")
                        all_passed = False
                else:
                    print("   ❌ No shopping list found in recipe")
                    all_passed = False
                    
            else:
                print(f"❌ Failed to generate {beverage_type} recipe")
                all_passed = False
        
        return all_passed

    def analyze_shopping_list_cleanliness(self, shopping_list, beverage_type):
        """Analyze how clean the shopping list is (no quantities, measurements, etc.)"""
        if not shopping_list:
            return 0.0
        
        clean_items = 0
        total_items = len(shopping_list)
        
        # Patterns that indicate unclean ingredients
        quantity_patterns = [
            r'\d+\s*(cups?|cup|tbsp|tablespoons?|tablespoon|tsp|teaspoons?|teaspoon)',
            r'\d+\s*(lbs?|pounds?|pound|oz|ounces?|ounce)',
            r'\d+\s*(cans?|can|jars?|jar|bottles?|bottle|packages?|package)',
            r'\d+\s*(shots?|shot)',
            r'\d+[\s\/\-]*\d*\s+',  # Numbers at the beginning
            r'^\d+',  # Starting with numbers
        ]
        
        measurement_patterns = [
            r'\b(fresh|dried|ground|chopped|sliced|diced|minced|cooked|raw)\b',
            r'\b(large|small|medium|extra)\b',
            r'\b(to taste|as needed)\b'
        ]
        
        for item in shopping_list:
            item_lower = item.lower().strip()
            is_clean = True
            
            # Check for quantity patterns
            for pattern in quantity_patterns:
                if re.search(pattern, item_lower):
                    print(f"     ⚠️ Found quantity pattern in '{item}': {pattern}")
                    is_clean = False
                    break
            
            # Check for measurement/preparation patterns
            if is_clean:
                for pattern in measurement_patterns:
                    if re.search(pattern, item_lower):
                        print(f"     ⚠️ Found measurement/prep pattern in '{item}': {pattern}")
                        is_clean = False
                        break
            
            if is_clean:
                clean_items += 1
                print(f"     ✅ Clean ingredient: '{item}'")
            else:
                print(f"     ❌ Unclean ingredient: '{item}'")
        
        return (clean_items / total_items) * 100

    def test_walmart_product_search_for_beverages(self):
        """Test Walmart API product search for beverage ingredients"""
        print("\n" + "=" * 60)
        print("🛒 TESTING WALMART PRODUCT SEARCH FOR BEVERAGES")
        print("=" * 60)
        
        if not self.beverage_recipes:
            print("❌ No beverage recipes available for testing")
            return False
        
        all_passed = True
        
        for beverage_type, recipe in self.beverage_recipes.items():
            print(f"\n--- Testing Walmart Search for {beverage_type.title()} Ingredients ---")
            
            recipe_id = recipe['id']
            shopping_list = recipe.get('shopping_list', [])
            
            if not shopping_list:
                print(f"❌ No shopping list found for {beverage_type}")
                all_passed = False
                continue
            
            success, response = self.run_test(
                f"Walmart Cart Options for {beverage_type.title()}",
                "POST",
                "grocery/cart-options",
                200,
                params={"recipe_id": recipe_id, "user_id": self.user_id},
                timeout=45
            )
            
            if success and 'ingredient_options' in response:
                self.cart_options[beverage_type] = response
                ingredient_options = response['ingredient_options']
                
                print(f"✅ Found product options for {len(ingredient_options)} ingredients")
                
                # Analyze product search results
                real_products = 0
                mock_products = 0
                total_products = 0
                
                for i, ingredient_option in enumerate(ingredient_options):
                    ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
                    original_ingredient = ingredient_option.get('original_ingredient', 'Unknown')
                    options = ingredient_option.get('options', [])
                    
                    print(f"   Ingredient {i+1}: '{ingredient_name}' (Original: '{original_ingredient}')")
                    print(f"     Found {len(options)} product options:")
                    
                    for j, product in enumerate(options):
                        product_id = product.get('product_id', 'N/A')
                        name = product.get('name', 'N/A')
                        price = product.get('price', 0.0)
                        
                        # Determine if this is a real or mock product
                        is_real = self.is_real_walmart_product(product_id, name)
                        if is_real:
                            real_products += 1
                            status = "✅ REAL"
                        else:
                            mock_products += 1
                            status = "🔧 MOCK"
                        
                        total_products += 1
                        print(f"       {j+1}. {status} - {name} - ${price:.2f} (ID: {product_id})")
                
                # Calculate real product percentage
                if total_products > 0:
                    real_percentage = (real_products / total_products) * 100
                    print(f"\n   📊 Product Analysis:")
                    print(f"     Real Walmart Products: {real_products}/{total_products} ({real_percentage:.1f}%)")
                    print(f"     Mock Products: {mock_products}/{total_products} ({100-real_percentage:.1f}%)")
                    
                    if real_percentage >= 50:
                        print(f"   ✅ Good real product rate for {beverage_type}")
                    else:
                        print(f"   ⚠️ Low real product rate for {beverage_type}")
                        
            else:
                print(f"❌ Failed to get Walmart product options for {beverage_type}")
                all_passed = False
        
        return all_passed

    def is_real_walmart_product(self, product_id, product_name):
        """Determine if a product is real or mock based on ID patterns and name"""
        # Real Walmart product IDs are typically 8-9 digits
        if not product_id or not product_id.isdigit():
            return False
        
        # Check for common mock product patterns
        mock_patterns = [
            "Great Value",
            "Mock Product",
            "Test Product"
        ]
        
        # Real product ID ranges (based on observed patterns)
        try:
            pid = int(product_id)
            # Real Walmart product IDs are typically in certain ranges
            if 10000000 <= pid <= 999999999:  # 8-9 digit range
                # Check if it's not a generated mock ID
                if not any(pattern in product_name for pattern in mock_patterns):
                    return True
        except:
            pass
        
        return False

    def test_cart_options_api_for_beverages(self):
        """Test the /api/grocery/cart-options endpoint specifically with beverage ingredients"""
        print("\n" + "=" * 60)
        print("🛒 TESTING CART OPTIONS API FOR BEVERAGES")
        print("=" * 60)
        
        if not self.beverage_recipes:
            print("❌ No beverage recipes available for testing")
            return False
        
        all_passed = True
        
        for beverage_type, recipe in self.beverage_recipes.items():
            print(f"\n--- Testing Cart Options API for {beverage_type.title()} ---")
            
            recipe_id = recipe['id']
            
            success, response = self.run_test(
                f"Cart Options API - {beverage_type.title()}",
                "POST",
                "grocery/cart-options",
                200,
                params={"recipe_id": recipe_id, "user_id": self.user_id},
                timeout=45
            )
            
            if success:
                # Verify response structure
                required_fields = ['id', 'user_id', 'recipe_id', 'ingredient_options']
                missing_fields = [field for field in required_fields if field not in response]
                
                if missing_fields:
                    print(f"❌ Missing required fields in response: {missing_fields}")
                    all_passed = False
                    continue
                
                print(f"✅ Cart options response has all required fields")
                
                # Verify ingredient options structure
                ingredient_options = response.get('ingredient_options', [])
                if not ingredient_options:
                    print(f"❌ No ingredient options found for {beverage_type}")
                    all_passed = False
                    continue
                
                print(f"✅ Found {len(ingredient_options)} ingredient options")
                
                # Check each ingredient option
                for i, ingredient_option in enumerate(ingredient_options):
                    required_option_fields = ['ingredient_name', 'original_ingredient', 'options']
                    missing_option_fields = [field for field in required_option_fields if field not in ingredient_option]
                    
                    if missing_option_fields:
                        print(f"❌ Ingredient {i+1} missing fields: {missing_option_fields}")
                        all_passed = False
                        continue
                    
                    # Check product options
                    options = ingredient_option.get('options', [])
                    if not options:
                        print(f"❌ No product options for ingredient: {ingredient_option.get('ingredient_name')}")
                        all_passed = False
                        continue
                    
                    # Verify product structure
                    for j, product in enumerate(options):
                        required_product_fields = ['product_id', 'name', 'price']
                        missing_product_fields = [field for field in required_product_fields if field not in product]
                        
                        if missing_product_fields:
                            print(f"❌ Product {j+1} missing fields: {missing_product_fields}")
                            all_passed = False
                        else:
                            print(f"   ✅ Product {j+1}: {product['name']} - ${product['price']:.2f}")
                
                # Store for custom cart testing
                self.cart_options[beverage_type] = response
                
            else:
                print(f"❌ Cart options API failed for {beverage_type}")
                all_passed = False
        
        return all_passed

    def test_product_id_collection(self):
        """Verify that Walmart product IDs are being correctly collected and stored for beverages"""
        print("\n" + "=" * 60)
        print("🔢 TESTING PRODUCT ID COLLECTION FOR BEVERAGES")
        print("=" * 60)
        
        if not self.cart_options:
            print("❌ No cart options available for testing")
            return False
        
        all_passed = True
        
        for beverage_type, cart_data in self.cart_options.items():
            print(f"\n--- Testing Product ID Collection for {beverage_type.title()} ---")
            
            ingredient_options = cart_data.get('ingredient_options', [])
            if not ingredient_options:
                print(f"❌ No ingredient options for {beverage_type}")
                all_passed = False
                continue
            
            total_products = 0
            valid_product_ids = 0
            product_ids = []
            
            for ingredient_option in ingredient_options:
                ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
                options = ingredient_option.get('options', [])
                
                print(f"   Ingredient: {ingredient_name}")
                
                for product in options:
                    product_id = product.get('product_id')
                    product_name = product.get('name', 'Unknown')
                    
                    total_products += 1
                    
                    if product_id and str(product_id).strip():
                        # Validate product ID format
                        if self.validate_product_id(product_id):
                            valid_product_ids += 1
                            product_ids.append(product_id)
                            print(f"     ✅ Valid Product ID: {product_id} - {product_name}")
                        else:
                            print(f"     ⚠️ Invalid Product ID format: {product_id} - {product_name}")
                    else:
                        print(f"     ❌ Missing Product ID for: {product_name}")
                        all_passed = False
            
            # Calculate validation rate
            if total_products > 0:
                validation_rate = (valid_product_ids / total_products) * 100
                print(f"\n   📊 Product ID Collection Analysis:")
                print(f"     Total Products: {total_products}")
                print(f"     Valid Product IDs: {valid_product_ids}")
                print(f"     Validation Rate: {validation_rate:.1f}%")
                print(f"     Collected Product IDs: {product_ids}")
                
                if validation_rate >= 90:
                    print(f"   ✅ Excellent product ID collection for {beverage_type}")
                elif validation_rate >= 75:
                    print(f"   ⚠️ Good product ID collection for {beverage_type}")
                else:
                    print(f"   ❌ Poor product ID collection for {beverage_type}")
                    all_passed = False
            else:
                print(f"   ❌ No products found for {beverage_type}")
                all_passed = False
        
        return all_passed

    def validate_product_id(self, product_id):
        """Validate if a product ID has the correct format"""
        if not product_id:
            return False
        
        # Convert to string and check
        pid_str = str(product_id).strip()
        
        # Should be numeric and reasonable length (6-12 digits for Walmart)
        if not pid_str.isdigit():
            return False
        
        if len(pid_str) < 6 or len(pid_str) > 12:
            return False
        
        return True

    def test_custom_cart_generation(self):
        """Test the /api/grocery/custom-cart endpoint with beverage product IDs"""
        print("\n" + "=" * 60)
        print("🛒 TESTING CUSTOM CART GENERATION FOR BEVERAGES")
        print("=" * 60)
        
        if not self.cart_options:
            print("❌ No cart options available for testing")
            return False
        
        all_passed = True
        
        for beverage_type, cart_data in self.cart_options.items():
            print(f"\n--- Testing Custom Cart Generation for {beverage_type.title()} ---")
            
            # Extract products from cart options
            ingredient_options = cart_data.get('ingredient_options', [])
            if not ingredient_options:
                print(f"❌ No ingredient options for {beverage_type}")
                all_passed = False
                continue
            
            # Select first product from each ingredient for the custom cart
            selected_products = []
            for ingredient_option in ingredient_options:
                ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
                options = ingredient_option.get('options', [])
                
                if options:
                    # Select the first product
                    product = options[0]
                    selected_products.append({
                        "ingredient_name": ingredient_name,
                        "product_id": product.get('product_id'),
                        "name": product.get('name'),
                        "price": product.get('price', 0.0),
                        "quantity": 1
                    })
            
            if not selected_products:
                print(f"❌ No products selected for {beverage_type}")
                all_passed = False
                continue
            
            # Create custom cart
            custom_cart_data = {
                "user_id": self.user_id,
                "recipe_id": self.beverage_recipes[beverage_type]['id'],
                "products": selected_products
            }
            
            success, response = self.run_test(
                f"Custom Cart Generation - {beverage_type.title()}",
                "POST",
                "grocery/custom-cart",
                200,
                data=custom_cart_data,
                timeout=30
            )
            
            if success:
                # Verify response structure
                required_fields = ['id', 'user_id', 'recipe_id', 'products', 'total_price', 'walmart_url']
                missing_fields = [field for field in required_fields if field not in response]
                
                if missing_fields:
                    print(f"❌ Missing required fields in custom cart response: {missing_fields}")
                    all_passed = False
                    continue
                
                print(f"✅ Custom cart created successfully")
                
                # Verify total price calculation
                expected_total = sum(p['price'] * p['quantity'] for p in selected_products)
                actual_total = response.get('total_price', 0.0)
                
                if abs(actual_total - expected_total) < 0.01:
                    print(f"✅ Total price calculated correctly: ${actual_total:.2f}")
                else:
                    print(f"❌ Total price calculation error: Expected ${expected_total:.2f}, got ${actual_total:.2f}")
                    all_passed = False
                
                # Verify Walmart URL
                walmart_url = response.get('walmart_url', '')
                if self.validate_walmart_url(walmart_url, selected_products):
                    print(f"✅ Walmart URL generated correctly")
                    print(f"   URL: {walmart_url}")
                else:
                    print(f"❌ Walmart URL validation failed")
                    print(f"   URL: {walmart_url}")
                    all_passed = False
                
                # Store for reference
                self.custom_carts[beverage_type] = response
                
            else:
                print(f"❌ Custom cart generation failed for {beverage_type}")
                all_passed = False
        
        return all_passed

    def validate_walmart_url(self, url, products):
        """Validate if the Walmart URL is correctly formatted"""
        if not url:
            return False
        
        # Check if URL contains the correct domain
        if 'affil.walmart.com' not in url:
            print(f"     ❌ URL doesn't contain 'affil.walmart.com'")
            return False
        
        # Check if URL contains items parameter
        if 'items=' not in url:
            print(f"     ❌ URL doesn't contain 'items=' parameter")
            return False
        
        # Check if all product IDs are in the URL
        product_ids = [str(p['product_id']) for p in products if p.get('product_id')]
        for product_id in product_ids:
            if product_id not in url:
                print(f"     ❌ Product ID {product_id} not found in URL")
                return False
        
        print(f"     ✅ All {len(product_ids)} product IDs found in URL")
        return True

    def run_comprehensive_beverage_walmart_integration_test(self):
        """Run the complete beverage Walmart integration test suite"""
        print("\n" + "=" * 80)
        print("🧋 COMPREHENSIVE BEVERAGE WALMART INTEGRATION TEST")
        print("=" * 80)
        print("Testing beverage Walmart integration to identify why link generation is not working")
        print("Focus areas:")
        print("1. Beverage Shopping List Generation (clean product names)")
        print("2. Walmart Product Search for Beverages")
        print("3. Cart Options API for Beverages")
        print("4. Product ID Collection")
        print("5. Custom Cart Generation")
        print("=" * 80)
        
        # Track test results
        test_results = {
            "User Setup": False,
            "Beverage Recipe Generation": False,
            "Walmart Product Search": False,
            "Cart Options API": False,
            "Product ID Collection": False,
            "Custom Cart Generation": False
        }
        
        # 1. Setup test user
        test_results["User Setup"] = self.setup_test_user()
        
        if not test_results["User Setup"]:
            print("\n❌ Cannot continue without test user setup")
            return self.generate_final_report(test_results)
        
        # 2. Test beverage recipe generation
        test_results["Beverage Recipe Generation"] = self.test_beverage_recipe_generation()
        
        # 3. Test Walmart product search
        test_results["Walmart Product Search"] = self.test_walmart_product_search_for_beverages()
        
        # 4. Test cart options API
        test_results["Cart Options API"] = self.test_cart_options_api_for_beverages()
        
        # 5. Test product ID collection
        test_results["Product ID Collection"] = self.test_product_id_collection()
        
        # 6. Test custom cart generation
        test_results["Custom Cart Generation"] = self.test_custom_cart_generation()
        
        # Generate final report
        return self.generate_final_report(test_results)

    def generate_final_report(self, test_results):
        """Generate a comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 BEVERAGE WALMART INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print(f"Total API Calls: {self.tests_run}")
        print(f"Successful API Calls: {self.tests_passed}")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        print("\n🔍 CRITICAL FINDINGS:")
        
        # Analyze beverage recipe generation
        if test_results["Beverage Recipe Generation"]:
            print("✅ Beverage recipe generation is working correctly")
            if self.beverage_recipes:
                print(f"   Generated {len(self.beverage_recipes)} beverage recipes:")
                for beverage_type, recipe in self.beverage_recipes.items():
                    shopping_list = recipe.get('shopping_list', [])
                    print(f"     - {beverage_type.title()}: {len(shopping_list)} ingredients in shopping list")
        else:
            print("❌ CRITICAL: Beverage recipe generation is failing")
            print("   This prevents all downstream Walmart integration testing")
        
        # Analyze shopping list quality
        if self.beverage_recipes:
            print("\n🛒 SHOPPING LIST ANALYSIS:")
            for beverage_type, recipe in self.beverage_recipes.items():
                shopping_list = recipe.get('shopping_list', [])
                if shopping_list:
                    cleanliness_score = self.analyze_shopping_list_cleanliness(shopping_list, beverage_type)
                    status = "✅" if cleanliness_score >= 80 else "⚠️" if cleanliness_score >= 60 else "❌"
                    print(f"   {status} {beverage_type.title()}: {cleanliness_score:.1f}% clean")
                    print(f"      Shopping List: {shopping_list}")
        
        # Analyze Walmart integration
        if test_results["Walmart Product Search"]:
            print("\n🛒 WALMART INTEGRATION ANALYSIS:")
            print("✅ Walmart API integration is working")
            if self.cart_options:
                for beverage_type, cart_data in self.cart_options.items():
                    ingredient_options = cart_data.get('ingredient_options', [])
                    total_products = sum(len(opt.get('options', [])) for opt in ingredient_options)
                    print(f"   {beverage_type.title()}: Found {total_products} total products for {len(ingredient_options)} ingredients")
        else:
            print("❌ CRITICAL: Walmart product search is failing")
            print("   This prevents cart generation and affiliate link creation")
        
        # Analyze custom cart generation
        if test_results["Custom Cart Generation"]:
            print("\n💰 CART GENERATION ANALYSIS:")
            print("✅ Custom cart generation is working")
            if self.custom_carts:
                total_cart_value = 0
                for beverage_type, cart in self.custom_carts.items():
                    cart_total = cart.get('total_price', 0.0)
                    total_cart_value += cart_total
                    print(f"   {beverage_type.title()}: ${cart_total:.2f}")
                print(f"   Total Test Cart Value: ${total_cart_value:.2f}")
        else:
            print("❌ CRITICAL: Custom cart generation is failing")
            print("   Users cannot create Walmart carts for beverage recipes")
        
        print("\n🎯 RECOMMENDATIONS:")
        
        if not test_results["Beverage Recipe Generation"]:
            print("1. 🔧 Fix beverage recipe generation - this is blocking all other functionality")
            print("   - Check OpenAI API integration for beverage category")
            print("   - Verify beverage-specific prompts are working")
        
        if test_results["Beverage Recipe Generation"] and not test_results["Walmart Product Search"]:
            print("2. 🔧 Fix Walmart API integration for beverage ingredients")
            print("   - Check Walmart API credentials and authentication")
            print("   - Verify ingredient name parsing for beverage items")
        
        if test_results["Walmart Product Search"] and not test_results["Custom Cart Generation"]:
            print("3. 🔧 Fix custom cart generation logic")
            print("   - Check product ID handling and URL generation")
            print("   - Verify cart total calculation")
        
        # Specific beverage issues
        if self.beverage_recipes:
            problematic_beverages = []
            for beverage_type, recipe in self.beverage_recipes.items():
                shopping_list = recipe.get('shopping_list', [])
                if shopping_list:
                    cleanliness_score = self.analyze_shopping_list_cleanliness(shopping_list, beverage_type)
                    if cleanliness_score < 80:
                        problematic_beverages.append(beverage_type)
            
            if problematic_beverages:
                print(f"4. 🔧 Improve shopping list generation for: {', '.join(problematic_beverages)}")
                print("   - Remove quantities and measurements from shopping lists")
                print("   - Use clean ingredient names suitable for Walmart search")
        
        print("\n" + "=" * 80)
        
        return success_rate >= 80  # Consider test suite passed if 80% or more tests pass

if __name__ == "__main__":
    print("🧋 Starting Beverage Walmart Integration Testing...")
    
    tester = BeverageWalmartIntegrationTester()
    success = tester.run_comprehensive_beverage_walmart_integration_test()
    
    if success:
        print("\n🎉 BEVERAGE WALMART INTEGRATION TEST SUITE PASSED")
        sys.exit(0)
    else:
        print("\n❌ BEVERAGE WALMART INTEGRATION TEST SUITE FAILED")
        sys.exit(1)