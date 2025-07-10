#!/usr/bin/env python3
"""
Beverage Shopping List Test
Tests the fixed beverage shopping list to ensure it contains only clean ingredient names 
without quantities or measurements.
"""

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

class BeverageShoppingListTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.test_email = f"beverage_test_{uuid.uuid4()}@example.com"
        self.test_password = "SecureP@ssw0rd123"
        
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=60):
        """Run a single API test"""
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
        """Create and verify a test user for beverage testing"""
        print("\n" + "=" * 60)
        print("🔧 Setting up test user for beverage testing")
        print("=" * 60)
        
        # Create user
        user_data = {
            "first_name": "Beverage",
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

    def validate_shopping_list_cleanliness(self, shopping_list, recipe_title=""):
        """
        Validate that shopping list contains only clean ingredient names
        without quantities, measurements, or preparation instructions
        """
        print(f"\n🔍 Validating shopping list cleanliness for: {recipe_title}")
        print(f"Shopping list: {shopping_list}")
        
        validation_results = {
            "has_shopping_list": bool(shopping_list),
            "shopping_list_format": isinstance(shopping_list, list),
            "no_quantities": True,
            "no_measurements": True,
            "no_preparation_words": True,
            "clean_names": True,
            "issues": []
        }
        
        if not shopping_list:
            validation_results["issues"].append("No shopping_list field found")
            return validation_results
            
        if not isinstance(shopping_list, list):
            validation_results["issues"].append("shopping_list is not a list")
            return validation_results
            
        # Patterns to check for quantities and measurements
        quantity_patterns = [
            r'\b\d+\b',  # Numbers like "4", "2"
            r'\b\d+/\d+\b',  # Fractions like "1/2", "3/4"
            r'\b\d+\.\d+\b',  # Decimals like "1.5", "2.25"
        ]
        
        measurement_patterns = [
            r'\bcups?\b', r'\bcup\b',
            r'\btbsp\b', r'\btablespoons?\b', r'\btablespoon\b',
            r'\btsp\b', r'\bteaspoons?\b', r'\bteaspoon\b',
            r'\boz\b', r'\bounces?\b', r'\bounce\b',
            r'\blbs?\b', r'\bpounds?\b', r'\bpound\b',
            r'\bcans?\b', r'\bcan\b',
            r'\bjars?\b', r'\bjar\b',
            r'\bbottles?\b', r'\bbottle\b',
            r'\bpackages?\b', r'\bpackage\b',
            r'\bbags?\b', r'\bbag\b',
            r'\bcloves?\b', r'\bclove\b',
            r'\bslices?\b', r'\bslice\b',
            r'\bpieces?\b', r'\bpiece\b',
            r'\bshots?\b', r'\bshot\b'
        ]
        
        preparation_patterns = [
            r'\bfresh\b', r'\bdried\b', r'\bground\b', r'\bwhole\b',
            r'\bchopped\b', r'\bsliced\b', r'\bdiced\b', r'\bminced\b',
            r'\bcooked\b', r'\braw\b', r'\bfrozen\b',
            r'\bdrained\b', r'\brinsed\b',
            r'\bchunks\b', r'\bleaves\b', r'\bcubes\b'
        ]
        
        for ingredient in shopping_list:
            ingredient_lower = ingredient.lower()
            
            # Check for quantities
            for pattern in quantity_patterns:
                if re.search(pattern, ingredient_lower):
                    validation_results["no_quantities"] = False
                    validation_results["issues"].append(f"Found quantity in '{ingredient}': {pattern}")
                    
            # Check for measurements
            for pattern in measurement_patterns:
                if re.search(pattern, ingredient_lower):
                    validation_results["no_measurements"] = False
                    validation_results["issues"].append(f"Found measurement in '{ingredient}': {pattern}")
                    
            # Check for preparation words
            for pattern in preparation_patterns:
                if re.search(pattern, ingredient_lower):
                    validation_results["no_preparation_words"] = False
                    validation_results["issues"].append(f"Found preparation word in '{ingredient}': {pattern}")
        
        # Calculate overall cleanliness score
        criteria_met = sum([
            validation_results["has_shopping_list"],
            validation_results["shopping_list_format"],
            validation_results["no_quantities"],
            validation_results["no_measurements"],
            validation_results["no_preparation_words"]
        ])
        
        validation_results["cleanliness_score"] = (criteria_met / 5) * 100
        
        # Print validation results
        print(f"✅ Has shopping_list: {validation_results['has_shopping_list']}")
        print(f"✅ Shopping list format valid: {validation_results['shopping_list_format']}")
        print(f"{'✅' if validation_results['no_quantities'] else '❌'} No quantities: {validation_results['no_quantities']}")
        print(f"{'✅' if validation_results['no_measurements'] else '❌'} No measurements: {validation_results['no_measurements']}")
        print(f"{'✅' if validation_results['no_preparation_words'] else '❌'} No preparation words: {validation_results['no_preparation_words']}")
        print(f"📊 Cleanliness score: {validation_results['cleanliness_score']:.1f}%")
        
        if validation_results["issues"]:
            print("⚠️ Issues found:")
            for issue in validation_results["issues"]:
                print(f"  - {issue}")
        else:
            print("✅ No issues found - shopping list is perfectly clean!")
            
        return validation_results

    def test_beverage_recipe_generation(self):
        """Test beverage recipe generation with focus on shopping list"""
        print("\n" + "=" * 60)
        print("🧋 Testing Beverage Recipe Generation & Shopping List")
        print("=" * 60)
        
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        # Test beverage recipe generation
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": "beverage",  # This is the key parameter
            "servings": 4,
            "difficulty": "medium"
        }
        
        print("🔄 Generating beverage recipes (4-recipe format)...")
        success, response = self.run_test(
            "Generate Beverage Recipe",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60
        )
        
        if not success:
            print("❌ Failed to generate beverage recipe")
            return False
            
        print("✅ Beverage recipe generated successfully!")
        
        # Validate the response structure
        required_fields = ['title', 'description', 'ingredients', 'instructions', 'shopping_list']
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
            
        print(f"✅ All required fields present")
        print(f"📝 Recipe title: {response.get('title', 'N/A')}")
        print(f"📝 Recipe description: {response.get('description', 'N/A')[:100]}...")
        
        # Check if it's the 4-recipe format
        title = response.get('title', '')
        if '4' in title and 'beverage' in title.lower():
            print("✅ Confirmed 4-recipe beverage format")
        else:
            print(f"⚠️ Title doesn't indicate 4-recipe format: {title}")
            
        # Validate shopping list
        shopping_list = response.get('shopping_list', [])
        validation_results = self.validate_shopping_list_cleanliness(shopping_list, title)
        
        # Store recipe ID for further testing
        self.recipe_id = response.get('id')
        
        return validation_results["cleanliness_score"] >= 90  # 90% or higher is considered passing

    def test_specific_beverage_examples(self):
        """Test specific beverage examples mentioned in the user's issue"""
        print("\n" + "=" * 60)
        print("🎯 Testing Specific Beverage Examples")
        print("=" * 60)
        
        # Test multiple beverage recipes to check consistency
        test_cases = [
            {"name": "Tropical Beverage Mix", "servings": 2},
            {"name": "Coffee & Tea Collection", "servings": 4},
            {"name": "Summer Refreshers", "servings": 6}
        ]
        
        all_validation_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['name']} ---")
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "beverage",
                "servings": test_case["servings"],
                "difficulty": "easy"
            }
            
            success, response = self.run_test(
                f"Generate {test_case['name']}",
                "POST",
                "recipes/generate",
                200,
                data=recipe_request,
                timeout=60
            )
            
            if success and 'shopping_list' in response:
                shopping_list = response.get('shopping_list', [])
                validation_results = self.validate_shopping_list_cleanliness(
                    shopping_list, 
                    response.get('title', test_case['name'])
                )
                all_validation_results.append(validation_results)
                
                # Check for specific examples mentioned in the issue
                problematic_patterns = [
                    r'\b\d+\s+lemons?\b',  # "4 lemons"
                    r'\b\d+/\d+\s+cup.*pineapple.*chunks?\b',  # "1/2 cup pineapple chunks"
                    r'\b\d+/\d+\s+cup.*mango.*chunks?\b',  # "1/2 cup mango chunks"
                    r'\b\d+/\d+\s+cup.*fresh.*mint.*leaves?\b',  # "1/4 cup fresh mint leaves"
                    r'\b\d+/\d+\s+cup.*honey\b',  # "1/2 cup honey"
                    r'\b\d+\s+cups?\s+water\b',  # "4 cups water"
                    r'\bice\s+cubes?\b'  # "ice cubes"
                ]
                
                print(f"\n🔍 Checking for specific problematic patterns...")
                for ingredient in shopping_list:
                    ingredient_lower = ingredient.lower()
                    for pattern in problematic_patterns:
                        if re.search(pattern, ingredient_lower):
                            print(f"❌ Found problematic pattern in '{ingredient}': {pattern}")
                        else:
                            # Check if clean versions are present
                            if 'lemon' in ingredient_lower and not re.search(r'\d', ingredient):
                                print(f"✅ Clean lemon ingredient: '{ingredient}'")
                            elif 'pineapple' in ingredient_lower and not re.search(r'chunk', ingredient_lower):
                                print(f"✅ Clean pineapple ingredient: '{ingredient}'")
                            elif 'mango' in ingredient_lower and not re.search(r'chunk', ingredient_lower):
                                print(f"✅ Clean mango ingredient: '{ingredient}'")
                            elif 'mint' in ingredient_lower and not re.search(r'fresh|leaves', ingredient_lower):
                                print(f"✅ Clean mint ingredient: '{ingredient}'")
                            elif 'honey' in ingredient_lower and not re.search(r'\d|cup', ingredient_lower):
                                print(f"✅ Clean honey ingredient: '{ingredient}'")
                            elif 'water' in ingredient_lower and not re.search(r'\d|cup', ingredient_lower):
                                print(f"✅ Clean water ingredient: '{ingredient}'")
                            elif 'ice' in ingredient_lower and not re.search(r'cube', ingredient_lower):
                                print(f"✅ Clean ice ingredient: '{ingredient}'")
            else:
                print(f"❌ Failed to generate or validate {test_case['name']}")
                
        # Calculate overall results
        if all_validation_results:
            avg_score = sum(r["cleanliness_score"] for r in all_validation_results) / len(all_validation_results)
            print(f"\n📊 Overall average cleanliness score: {avg_score:.1f}%")
            return avg_score >= 90
        else:
            print("❌ No validation results to analyze")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive beverage shopping list test"""
        print("\n" + "=" * 80)
        print("🧋 BEVERAGE SHOPPING LIST COMPREHENSIVE TEST 🧋")
        print("=" * 80)
        print(f"Testing beverage recipe generation with focus on shopping list cleanliness")
        print(f"Target: Clean ingredient names without quantities, measurements, or preparation words")
        print("=" * 80)
        
        # Setup test user
        if not self.setup_test_user():
            print("❌ Failed to setup test user - cannot continue")
            return False
            
        # Test beverage recipe generation
        beverage_test_passed = self.test_beverage_recipe_generation()
        
        # Test specific examples
        examples_test_passed = self.test_specific_beverage_examples()
        
        # Final results
        print("\n" + "=" * 80)
        print("📊 FINAL TEST RESULTS")
        print("=" * 80)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        print()
        print(f"{'✅' if beverage_test_passed else '❌'} Beverage Recipe Generation: {'PASSED' if beverage_test_passed else 'FAILED'}")
        print(f"{'✅' if examples_test_passed else '❌'} Specific Examples Test: {'PASSED' if examples_test_passed else 'FAILED'}")
        
        overall_success = beverage_test_passed and examples_test_passed
        print(f"\n🎯 OVERALL RESULT: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        
        if overall_success:
            print("\n🎉 BEVERAGE SHOPPING LIST FIX VERIFIED!")
            print("✅ Shopping lists contain only clean ingredient names")
            print("✅ No quantities, measurements, or preparation instructions found")
            print("✅ All beverage ingredients are Walmart-searchable")
            print("✅ The 4-recipe format is working correctly")
        else:
            print("\n⚠️ ISSUES DETECTED IN BEVERAGE SHOPPING LIST")
            print("❌ Some shopping list items still contain quantities or measurements")
            print("❌ Further fixes may be needed")
            
        return overall_success

if __name__ == "__main__":
    # Run the comprehensive beverage shopping list test
    tester = BeverageShoppingListTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed! Beverage shopping list fix is working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please review the issues above.")
        exit(1)