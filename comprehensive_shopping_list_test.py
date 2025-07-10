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

class ShoppingListConsistencyTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.test_results = []
        
        # Test user credentials
        self.test_email = f"shopping_test_{uuid.uuid4()}@example.com"
        self.test_password = "SecureP@ssw0rd123"

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=60):
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

    def setup_test_user(self):
        """Create and verify a test user for recipe generation"""
        print("\n" + "=" * 50)
        print("Setting up test user for shopping list testing")
        print("=" * 50)
        
        # Create user
        user_data = {
            "first_name": "Shopping",
            "last_name": "Tester",
            "email": self.test_email,
            "password": self.test_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": []
        }
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not success:
            return False
            
        self.user_id = response.get('user_id')
        
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

    def validate_shopping_list(self, recipe_data, category, recipe_type):
        """Validate shopping list format and consistency"""
        validation_results = {
            "has_shopping_list": False,
            "shopping_list_format_valid": False,
            "no_quantities": True,
            "no_measurements": True,
            "individual_spices": True,
            "shopping_list_items": [],
            "issues": []
        }
        
        # Check if shopping_list field exists
        if 'shopping_list' not in recipe_data:
            validation_results["issues"].append("Missing shopping_list field")
            return validation_results
            
        validation_results["has_shopping_list"] = True
        shopping_list = recipe_data['shopping_list']
        
        # Check if shopping_list is a list
        if not isinstance(shopping_list, list):
            validation_results["issues"].append("shopping_list is not a list")
            return validation_results
            
        validation_results["shopping_list_format_valid"] = True
        validation_results["shopping_list_items"] = shopping_list
        
        # Validate each item in shopping list
        quantity_pattern = r'\b\d+[\s\/\-]*\d*\s*(cups?|cup|tbsp|tablespoons?|tablespoon|tsp|teaspoons?|teaspoon|lbs?|pounds?|pound|oz|ounces?|ounce|cans?|can|jars?|jar|bottles?|bottle|packages?|package|bags?|bag|cloves?|clove|slices?|slice|pieces?|piece|pinch|dash)\b'
        measurement_pattern = r'\b(cups?|cup|tbsp|tablespoons?|tablespoon|tsp|teaspoons?|teaspoon|lbs?|pounds?|pound|oz|ounces?|ounce|cans?|can|jars?|jar|bottles?|bottle|packages?|package|bags?|bag|cloves?|clove|slices?|slice|pieces?|piece|pinch|dash)\b'
        
        for item in shopping_list:
            # Check for quantities and measurements
            if re.search(quantity_pattern, item, re.IGNORECASE):
                validation_results["no_quantities"] = False
                validation_results["issues"].append(f"Item contains quantity/measurement: '{item}'")
                
            if re.search(measurement_pattern, item, re.IGNORECASE):
                validation_results["no_measurements"] = False
                validation_results["issues"].append(f"Item contains measurement unit: '{item}'")
        
        # Check for generic spice terms
        generic_spice_terms = ['spices', 'seasoning', 'mixed spices', 'herbs and spices']
        for item in shopping_list:
            if any(term in item.lower() for term in generic_spice_terms):
                validation_results["individual_spices"] = False
                validation_results["issues"].append(f"Generic spice term found: '{item}'")
        
        return validation_results

    def test_cuisine_category_shopping_list(self):
        """Test shopping list consistency for Cuisine category"""
        print("\n" + "=" * 60)
        print("🍝 TESTING CUISINE CATEGORY SHOPPING LIST CONSISTENCY")
        print("=" * 60)
        
        cuisine_tests = [
            {"cuisine_type": "Italian", "expected_ingredients": ["pasta", "tomatoes", "garlic", "olive oil"]},
            {"cuisine_type": "Mexican", "expected_ingredients": ["beans", "rice", "peppers", "onions"]},
            {"cuisine_type": "Japanese", "expected_ingredients": ["rice", "soy sauce", "ginger", "seaweed"]}
        ]
        
        cuisine_results = []
        
        for test_case in cuisine_tests:
            print(f"\n--- Testing {test_case['cuisine_type']} Cuisine ---")
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "cuisine",
                "cuisine_type": test_case['cuisine_type'],
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 45,
                "servings": 4,
                "difficulty": "medium"
            }
            
            success, response = self.run_test(
                f"Generate {test_case['cuisine_type']} Recipe",
                "POST",
                "recipes/generate",
                200,
                data=recipe_request,
                timeout=60
            )
            
            if success:
                validation = self.validate_shopping_list(response, "cuisine", test_case['cuisine_type'])
                validation['recipe_title'] = response.get('title', 'Unknown')
                validation['cuisine_type'] = test_case['cuisine_type']
                cuisine_results.append(validation)
                
                print(f"Recipe: {validation['recipe_title']}")
                print(f"Shopping List: {validation['shopping_list_items']}")
                print(f"Has Shopping List: {'✅' if validation['has_shopping_list'] else '❌'}")
                print(f"Format Valid: {'✅' if validation['shopping_list_format_valid'] else '❌'}")
                print(f"No Quantities: {'✅' if validation['no_quantities'] else '❌'}")
                print(f"No Measurements: {'✅' if validation['no_measurements'] else '❌'}")
                print(f"Individual Spices: {'✅' if validation['individual_spices'] else '❌'}")
                
                if validation['issues']:
                    print(f"Issues found: {validation['issues']}")
            else:
                print(f"❌ Failed to generate {test_case['cuisine_type']} recipe")
                
        return cuisine_results

    def test_snack_category_shopping_list(self):
        """Test shopping list consistency for Snack category"""
        print("\n" + "=" * 60)
        print("🥗 TESTING SNACK CATEGORY SHOPPING LIST CONSISTENCY")
        print("=" * 60)
        
        snack_tests = [
            {"recipe_type": "acai bowls", "expected_ingredients": ["acai", "granola", "berries", "honey"]},
            {"recipe_type": "fruit lemon slices chili", "expected_ingredients": ["fruits", "lemon", "chili powder", "lime"]},
            {"recipe_type": "frozen yogurt berry bites", "expected_ingredients": ["yogurt", "berries", "sweetener"]}
        ]
        
        snack_results = []
        
        for test_case in snack_tests:
            print(f"\n--- Testing {test_case['recipe_type']} Snack ---")
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "snack",
                "cuisine_type": test_case['recipe_type'],
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 30,
                "servings": 2,
                "difficulty": "easy"
            }
            
            success, response = self.run_test(
                f"Generate {test_case['recipe_type']} Snack",
                "POST",
                "recipes/generate",
                200,
                data=recipe_request,
                timeout=60
            )
            
            if success:
                validation = self.validate_shopping_list(response, "snack", test_case['recipe_type'])
                validation['recipe_title'] = response.get('title', 'Unknown')
                validation['recipe_type'] = test_case['recipe_type']
                snack_results.append(validation)
                
                print(f"Recipe: {validation['recipe_title']}")
                print(f"Shopping List: {validation['shopping_list_items']}")
                print(f"Has Shopping List: {'✅' if validation['has_shopping_list'] else '❌'}")
                print(f"Format Valid: {'✅' if validation['shopping_list_format_valid'] else '❌'}")
                print(f"No Quantities: {'✅' if validation['no_quantities'] else '❌'}")
                print(f"No Measurements: {'✅' if validation['no_measurements'] else '❌'}")
                print(f"Individual Spices: {'✅' if validation['individual_spices'] else '❌'}")
                
                if validation['issues']:
                    print(f"Issues found: {validation['issues']}")
            else:
                print(f"❌ Failed to generate {test_case['recipe_type']} snack")
                
        return snack_results

    def test_beverage_category_shopping_list(self):
        """Test shopping list consistency for Beverage category"""
        print("\n" + "=" * 60)
        print("☕ TESTING BEVERAGE CATEGORY SHOPPING LIST CONSISTENCY")
        print("=" * 60)
        
        beverage_tests = [
            {"recipe_type": "coffee", "expected_ingredients": ["espresso beans", "milk", "sugar"]},
            {"recipe_type": "boba tea", "expected_ingredients": ["tea", "tapioca pearls", "brown sugar", "milk"]},
            {"recipe_type": "thai tea", "expected_ingredients": ["thai tea", "condensed milk", "sugar"]},
            {"recipe_type": "special lemonades", "expected_ingredients": ["lemons", "sugar", "water"]}
        ]
        
        beverage_results = []
        
        for test_case in beverage_tests:
            print(f"\n--- Testing {test_case['recipe_type']} Beverage ---")
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "beverage",
                "cuisine_type": test_case['recipe_type'],
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 20,
                "servings": 2,
                "difficulty": "easy"
            }
            
            success, response = self.run_test(
                f"Generate {test_case['recipe_type']} Beverage",
                "POST",
                "recipes/generate",
                200,
                data=recipe_request,
                timeout=60
            )
            
            if success:
                validation = self.validate_shopping_list(response, "beverage", test_case['recipe_type'])
                validation['recipe_title'] = response.get('title', 'Unknown')
                validation['recipe_type'] = test_case['recipe_type']
                beverage_results.append(validation)
                
                print(f"Recipe: {validation['recipe_title']}")
                print(f"Shopping List: {validation['shopping_list_items']}")
                print(f"Has Shopping List: {'✅' if validation['has_shopping_list'] else '❌'}")
                print(f"Format Valid: {'✅' if validation['shopping_list_format_valid'] else '❌'}")
                print(f"No Quantities: {'✅' if validation['no_quantities'] else '❌'}")
                print(f"No Measurements: {'✅' if validation['no_measurements'] else '❌'}")
                print(f"Individual Spices: {'✅' if validation['individual_spices'] else '❌'}")
                
                if validation['issues']:
                    print(f"Issues found: {validation['issues']}")
                    
                # Special validation for beverages - check for "secret recipe" format
                if 'ingredients' in response:
                    ingredients = response['ingredients']
                    has_measurements = any(re.search(r'\d+.*\b(shots?|cups?|tbsp|tsp|oz|ml)\b', ing, re.IGNORECASE) for ing in ingredients)
                    if has_measurements:
                        print("✅ Beverage has detailed measurements in ingredients (secret recipe format)")
                    else:
                        print("⚠️ Beverage may lack detailed measurements in ingredients")
            else:
                print(f"❌ Failed to generate {test_case['recipe_type']} beverage")
                
        return beverage_results

    def analyze_consistency_across_categories(self, cuisine_results, snack_results, beverage_results):
        """Analyze consistency of shopping list format across all categories"""
        print("\n" + "=" * 70)
        print("📊 SHOPPING LIST CONSISTENCY ANALYSIS ACROSS CATEGORIES")
        print("=" * 70)
        
        all_results = cuisine_results + snack_results + beverage_results
        
        # Count successes for each validation criteria
        total_tests = len(all_results)
        has_shopping_list_count = sum(1 for r in all_results if r['has_shopping_list'])
        format_valid_count = sum(1 for r in all_results if r['shopping_list_format_valid'])
        no_quantities_count = sum(1 for r in all_results if r['no_quantities'])
        no_measurements_count = sum(1 for r in all_results if r['no_measurements'])
        individual_spices_count = sum(1 for r in all_results if r['individual_spices'])
        
        print(f"\nTotal recipes tested: {total_tests}")
        print(f"Has shopping_list field: {has_shopping_list_count}/{total_tests} ({has_shopping_list_count/total_tests*100:.1f}%)")
        print(f"Shopping list format valid: {format_valid_count}/{total_tests} ({format_valid_count/total_tests*100:.1f}%)")
        print(f"No quantities in shopping list: {no_quantities_count}/{total_tests} ({no_quantities_count/total_tests*100:.1f}%)")
        print(f"No measurements in shopping list: {no_measurements_count}/{total_tests} ({no_measurements_count/total_tests*100:.1f}%)")
        print(f"Individual spices listed: {individual_spices_count}/{total_tests} ({individual_spices_count/total_tests*100:.1f}%)")
        
        # Category-specific analysis
        print(f"\n--- Category Breakdown ---")
        
        categories = [
            ("Cuisine", cuisine_results),
            ("Snack", snack_results),
            ("Beverage", beverage_results)
        ]
        
        for category_name, results in categories:
            if results:
                category_total = len(results)
                category_has_list = sum(1 for r in results if r['has_shopping_list'])
                category_format_valid = sum(1 for r in results if r['shopping_list_format_valid'])
                category_no_quantities = sum(1 for r in results if r['no_quantities'])
                category_no_measurements = sum(1 for r in results if r['no_measurements'])
                category_individual_spices = sum(1 for r in results if r['individual_spices'])
                
                print(f"\n{category_name} Category ({category_total} tests):")
                print(f"  Has shopping_list: {category_has_list}/{category_total} ({category_has_list/category_total*100:.1f}%)")
                print(f"  Format valid: {category_format_valid}/{category_total} ({category_format_valid/category_total*100:.1f}%)")
                print(f"  No quantities: {category_no_quantities}/{category_total} ({category_no_quantities/category_total*100:.1f}%)")
                print(f"  No measurements: {category_no_measurements}/{category_total} ({category_no_measurements/category_total*100:.1f}%)")
                print(f"  Individual spices: {category_individual_spices}/{category_total} ({category_individual_spices/category_total*100:.1f}%)")
        
        # Overall consistency assessment
        consistency_score = (has_shopping_list_count + format_valid_count + no_quantities_count + no_measurements_count + individual_spices_count) / (total_tests * 5) * 100
        
        print(f"\n--- Overall Consistency Score ---")
        print(f"Shopping List Consistency: {consistency_score:.1f}%")
        
        if consistency_score >= 90:
            print("✅ EXCELLENT: Shopping list consistency is excellent across all categories")
        elif consistency_score >= 75:
            print("✅ GOOD: Shopping list consistency is good with minor issues")
        elif consistency_score >= 60:
            print("⚠️ FAIR: Shopping list consistency needs improvement")
        else:
            print("❌ POOR: Shopping list consistency has significant issues")
            
        return consistency_score

    def run_comprehensive_shopping_list_test(self):
        """Run comprehensive shopping list consistency test"""
        print("\n" + "=" * 80)
        print("🛒 COMPREHENSIVE SHOPPING LIST CONSISTENCY TEST")
        print("=" * 80)
        
        # Setup test user
        if not self.setup_test_user():
            print("❌ Failed to setup test user - cannot continue")
            return False
            
        # Test all categories
        cuisine_results = self.test_cuisine_category_shopping_list()
        snack_results = self.test_snack_category_shopping_list()
        beverage_results = self.test_beverage_category_shopping_list()
        
        # Analyze consistency
        consistency_score = self.analyze_consistency_across_categories(cuisine_results, snack_results, beverage_results)
        
        # Final summary
        print(f"\n" + "=" * 80)
        print("📋 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"Total API calls made: {self.tests_run}")
        print(f"Successful API calls: {self.tests_passed}")
        print(f"API success rate: {self.tests_passed/self.tests_run*100:.1f}%")
        print(f"Shopping list consistency score: {consistency_score:.1f}%")
        
        # Determine overall result
        overall_success = (self.tests_passed/self.tests_run >= 0.8) and (consistency_score >= 75)
        
        if overall_success:
            print("\n✅ OVERALL RESULT: SHOPPING LIST CONSISTENCY TEST PASSED")
            print("The shopping_list field is consistently implemented across all three categories.")
        else:
            print("\n❌ OVERALL RESULT: SHOPPING LIST CONSISTENCY TEST FAILED")
            print("Shopping list implementation needs improvement for consistency across categories.")
            
        return overall_success

def main():
    """Main function to run the shopping list consistency test"""
    print("Starting OpenAI Shopping List Consistency Test...")
    
    # Use the backend URL from environment
    backend_url = "http://localhost:8001"
    
    tester = ShoppingListConsistencyTester(backend_url)
    success = tester.run_comprehensive_shopping_list_test()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)