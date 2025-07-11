#!/usr/bin/env python3
"""
Focused test for beverage shopping list fix verification.
Tests that the grocery cart options endpoint returns clean ingredient names.
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BeverageCartTester:
    def __init__(self, base_url="https://d0aaf224-cbee-4960-9af5-9ebe32591c28.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.user_id = None
        self.recipe_id = None
        self.test_email = f"beverage_test_{uuid.uuid4()}@example.com"
        self.test_password = "SecureP@ssw0rd123"
        
    def log_test_result(self, test_name, success, details=""):
        """Log test results with consistent formatting"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status} - {test_name}")
        if details:
            print(f"Details: {details}")
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
            logger.error(f"Request timed out: {method} {url}")
            return 408, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {method} {url}")
            return 503, {"error": "Connection error"}
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            return 500, {"error": str(e)}
    
    def setup_test_user(self):
        """Create and verify a test user"""
        print("\n" + "=" * 60)
        print("🔧 SETTING UP TEST USER")
        print("=" * 60)
        
        # Register user
        user_data = {
            "first_name": "Beverage",
            "last_name": "Tester",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": ["american"]
        }
        
        status_code, response = self.make_request("POST", "auth/register", data=user_data)
        
        if status_code != 200:
            self.log_test_result("User Registration", False, f"Status: {status_code}, Response: {response}")
            return False
            
        if 'user_id' not in response:
            self.log_test_result("User Registration", False, "No user_id in response")
            return False
            
        self.user_id = response['user_id']
        self.log_test_result("User Registration", True, f"User ID: {self.user_id}")
        
        # Get verification code
        status_code, code_response = self.make_request("GET", f"debug/verification-codes/{self.test_email}")
        
        if status_code != 200:
            self.log_test_result("Get Verification Code", False, f"Status: {status_code}")
            return False
            
        verification_code = None
        if 'codes' in code_response and len(code_response['codes']) > 0:
            verification_code = code_response['codes'][0]['code']
        elif 'last_test_code' in code_response and code_response['last_test_code']:
            verification_code = code_response['last_test_code']
            
        if not verification_code:
            self.log_test_result("Get Verification Code", False, "No verification code found")
            return False
            
        self.log_test_result("Get Verification Code", True, f"Code: {verification_code}")
        
        # Verify email
        verify_data = {
            "email": self.test_email,
            "code": verification_code
        }
        
        status_code, response = self.make_request("POST", "auth/verify", data=verify_data)
        
        if status_code != 200:
            self.log_test_result("Email Verification", False, f"Status: {status_code}")
            return False
            
        self.log_test_result("Email Verification", True, "User verified successfully")
        return True
    
    def generate_beverage_recipe(self):
        """Generate a new beverage recipe for testing"""
        print("\n" + "=" * 60)
        print("🧋 GENERATING BEVERAGE RECIPE")
        print("=" * 60)
        
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": "beverage",
            "cuisine_type": "mixed beverages",
            "dietary_preferences": [],
            "ingredients_on_hand": [],
            "prep_time_max": 30,
            "servings": 4,
            "difficulty": "easy"
        }
        
        status_code, response = self.make_request("POST", "recipes/generate", data=recipe_request, timeout=60)
        
        if status_code != 200:
            self.log_test_result("Beverage Recipe Generation", False, f"Status: {status_code}, Response: {response}")
            return False
            
        if 'id' not in response:
            self.log_test_result("Beverage Recipe Generation", False, "No recipe ID in response")
            return False
            
        self.recipe_id = response['id']
        
        # Log recipe details
        recipe_title = response.get('title', 'Unknown')
        shopping_list = response.get('shopping_list', [])
        ingredients = response.get('ingredients', [])
        
        print(f"📋 Recipe Title: {recipe_title}")
        print(f"🛒 Shopping List ({len(shopping_list)} items): {shopping_list}")
        print(f"🥤 Ingredients ({len(ingredients)} items): {ingredients[:3]}..." if len(ingredients) > 3 else f"🥤 Ingredients: {ingredients}")
        
        self.log_test_result("Beverage Recipe Generation", True, f"Recipe ID: {self.recipe_id}, Title: {recipe_title}")
        
        # Store recipe data for analysis
        self.recipe_data = response
        return True
    
    def test_cart_options_endpoint(self):
        """Test the grocery cart options endpoint and verify clean ingredient names"""
        print("\n" + "=" * 60)
        print("🛒 TESTING CART OPTIONS ENDPOINT")
        print("=" * 60)
        
        if not self.recipe_id or not self.user_id:
            self.log_test_result("Cart Options Test", False, "Missing recipe_id or user_id")
            return False
            
        # Call cart-options endpoint
        status_code, response = self.make_request(
            "POST", 
            "grocery/cart-options",
            params={"recipe_id": self.recipe_id, "user_id": self.user_id},
            timeout=30
        )
        
        if status_code != 200:
            self.log_test_result("Cart Options API Call", False, f"Status: {status_code}, Response: {response}")
            return False
            
        self.log_test_result("Cart Options API Call", True, f"Status: {status_code}")
        
        # Analyze the response structure
        if 'ingredient_options' not in response:
            self.log_test_result("Cart Options Response Structure", False, "Missing 'ingredient_options' field")
            return False
            
        ingredient_options = response['ingredient_options']
        print(f"\n📊 Found {len(ingredient_options)} ingredient options")
        
        # Store cart options data for analysis
        self.cart_options_data = response
        return True
    
    def analyze_ingredient_cleanliness(self):
        """Analyze ingredient names for cleanliness (no quantities, measurements, etc.)"""
        print("\n" + "=" * 60)
        print("🔍 ANALYZING INGREDIENT NAME CLEANLINESS")
        print("=" * 60)
        
        if not hasattr(self, 'cart_options_data'):
            self.log_test_result("Ingredient Cleanliness Analysis", False, "No cart options data available")
            return False
            
        ingredient_options = self.cart_options_data.get('ingredient_options', [])
        
        # Patterns that indicate unclean ingredient names
        quantity_patterns = [
            r'^\d+\s',           # Numbers at start (e.g., "4 lemons")
            r'^\d+/\d+\s',       # Fractions at start (e.g., "1/2 cup")
            r'^\d+\.\d+\s',      # Decimals at start (e.g., "1.5 cups")
        ]
        
        measurement_patterns = [
            r'\b(cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons)\b',
            r'\b(oz|ounce|ounces|lb|lbs|pound|pounds)\b',
            r'\b(can|cans|jar|jars|bottle|bottles|package|packages)\b',
            r'\b(slice|slices|piece|pieces|clove|cloves)\b'
        ]
        
        preparation_patterns = [
            r'\b(fresh|dried|chopped|sliced|diced|minced|cooked|raw)\b',
            r'\b(drained|rinsed|peeled|grated|shredded)\b'
        ]
        
        all_patterns = quantity_patterns + measurement_patterns + preparation_patterns
        
        clean_count = 0
        total_count = len(ingredient_options)
        issues_found = []
        
        print(f"\n🔍 Analyzing {total_count} ingredients:")
        
        for i, ingredient_option in enumerate(ingredient_options, 1):
            ingredient_name = ingredient_option.get('ingredient_name', '')
            original_ingredient = ingredient_option.get('original_ingredient', '')
            
            print(f"\n{i}. Ingredient Analysis:")
            print(f"   ingredient_name: '{ingredient_name}'")
            print(f"   original_ingredient: '{original_ingredient}'")
            
            # Check ingredient_name for cleanliness
            ingredient_issues = []
            for pattern in all_patterns:
                if re.search(pattern, ingredient_name, re.IGNORECASE):
                    match = re.search(pattern, ingredient_name, re.IGNORECASE)
                    ingredient_issues.append(f"Found '{match.group()}' in ingredient_name")
            
            # Check original_ingredient for cleanliness
            original_issues = []
            for pattern in all_patterns:
                if re.search(pattern, original_ingredient, re.IGNORECASE):
                    match = re.search(pattern, original_ingredient, re.IGNORECASE)
                    original_issues.append(f"Found '{match.group()}' in original_ingredient")
            
            if not ingredient_issues and not original_issues:
                print(f"   ✅ CLEAN - No quantities, measurements, or preparation words found")
                clean_count += 1
            else:
                print(f"   ❌ ISSUES FOUND:")
                for issue in ingredient_issues + original_issues:
                    print(f"      - {issue}")
                issues_found.extend(ingredient_issues + original_issues)
        
        # Calculate cleanliness score
        cleanliness_score = (clean_count / total_count * 100) if total_count > 0 else 0
        
        print(f"\n📊 CLEANLINESS ANALYSIS RESULTS:")
        print(f"   Clean ingredients: {clean_count}/{total_count}")
        print(f"   Cleanliness score: {cleanliness_score:.1f}%")
        print(f"   Total issues found: {len(issues_found)}")
        
        # Determine if the fix is working
        is_fix_working = cleanliness_score >= 80  # 80% threshold for "good"
        
        if is_fix_working:
            rating = "EXCELLENT" if cleanliness_score >= 95 else "GOOD" if cleanliness_score >= 80 else "FAIR"
            self.log_test_result("Ingredient Cleanliness", True, f"Score: {cleanliness_score:.1f}% ({rating})")
        else:
            self.log_test_result("Ingredient Cleanliness", False, f"Score: {cleanliness_score:.1f}% (Below 80% threshold)")
        
        return is_fix_working, cleanliness_score, issues_found
    
    def verify_frontend_impact(self):
        """Verify that the productOptions keys will be clean ingredient names"""
        print("\n" + "=" * 60)
        print("🖥️ VERIFYING FRONTEND IMPACT")
        print("=" * 60)
        
        if not hasattr(self, 'cart_options_data'):
            self.log_test_result("Frontend Impact Verification", False, "No cart options data available")
            return False
            
        ingredient_options = self.cart_options_data.get('ingredient_options', [])
        
        print("🔍 Checking productOptions keys that frontend will use:")
        
        clean_keys = []
        problematic_keys = []
        
        for i, ingredient_option in enumerate(ingredient_options, 1):
            ingredient_name = ingredient_option.get('ingredient_name', '')
            
            # This is what the frontend will use as productOptions key
            print(f"{i}. productOptions['{ingredient_name}'] = [product options...]")
            
            # Check if this key would be problematic for frontend
            if re.search(r'^\d+\s|cup|tbsp|tsp|oz|lb|fresh|chopped|diced', ingredient_name, re.IGNORECASE):
                problematic_keys.append(ingredient_name)
                print(f"   ❌ Problematic key: Contains quantities/measurements/preparation words")
            else:
                clean_keys.append(ingredient_name)
                print(f"   ✅ Clean key: Suitable for frontend use")
        
        frontend_success = len(clean_keys) > len(problematic_keys)
        
        print(f"\n📊 FRONTEND IMPACT ANALYSIS:")
        print(f"   Clean keys: {len(clean_keys)}")
        print(f"   Problematic keys: {len(problematic_keys)}")
        print(f"   Frontend compatibility: {'✅ GOOD' if frontend_success else '❌ NEEDS IMPROVEMENT'}")
        
        self.log_test_result("Frontend Impact Verification", frontend_success, 
                           f"Clean keys: {len(clean_keys)}, Problematic: {len(problematic_keys)}")
        
        return frontend_success
    
    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("\n" + "=" * 80)
        print("🧪 BEVERAGE CART OPTIONS CLEANLINESS TEST")
        print("=" * 80)
        print(f"Testing backend fix for clean ingredient names in grocery cart")
        print(f"Base URL: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test steps
        test_results = {}
        
        # Step 1: Setup test user
        test_results['user_setup'] = self.setup_test_user()
        if not test_results['user_setup']:
            print("\n❌ CRITICAL FAILURE: Could not setup test user")
            return False
            
        # Step 2: Generate beverage recipe
        test_results['recipe_generation'] = self.generate_beverage_recipe()
        if not test_results['recipe_generation']:
            print("\n❌ CRITICAL FAILURE: Could not generate beverage recipe")
            return False
            
        # Step 3: Test cart options endpoint
        test_results['cart_options'] = self.test_cart_options_endpoint()
        if not test_results['cart_options']:
            print("\n❌ CRITICAL FAILURE: Cart options endpoint failed")
            return False
            
        # Step 4: Analyze ingredient cleanliness
        cleanliness_result, cleanliness_score, issues = self.analyze_ingredient_cleanliness()
        test_results['cleanliness'] = cleanliness_result
        
        # Step 5: Verify frontend impact
        test_results['frontend_impact'] = self.verify_frontend_impact()
        
        # Final summary
        print("\n" + "=" * 80)
        print("📋 FINAL TEST RESULTS")
        print("=" * 80)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests passed: {passed_tests}/{total_tests}")
        print(f"   Success rate: {(passed_tests/total_tests*100):.1f}%")
        
        if hasattr(self, 'cart_options_data'):
            ingredient_count = len(self.cart_options_data.get('ingredient_options', []))
            print(f"   Ingredients tested: {ingredient_count}")
            print(f"   Cleanliness score: {cleanliness_score:.1f}%")
        
        # Determine overall success
        overall_success = test_results['cleanliness'] and test_results['frontend_impact']
        
        print(f"\n🎯 BEVERAGE SHOPPING LIST FIX STATUS:")
        if overall_success:
            print("✅ WORKING - Ingredient names are clean and suitable for frontend use")
        else:
            print("❌ NEEDS ATTENTION - Issues found with ingredient name cleanliness")
            if issues:
                print(f"   Issues found: {len(issues)}")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"   - {issue}")
                if len(issues) > 5:
                    print(f"   ... and {len(issues) - 5} more issues")
        
        return overall_success

def main():
    """Main test execution"""
    tester = BeverageCartTester()
    success = tester.run_comprehensive_test()
    
    print(f"\n{'='*80}")
    print(f"🏁 TEST EXECUTION COMPLETED")
    print(f"{'='*80}")
    print(f"Overall result: {'✅ SUCCESS' if success else '❌ FAILURE'}")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())