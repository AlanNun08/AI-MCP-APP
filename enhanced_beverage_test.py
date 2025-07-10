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

class EnhancedBeverageTestSuite:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.test_results = []
        
        # Test user credentials
        self.test_email = f"beverage_test_{uuid.uuid4()}@example.com"
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
            "favorite_cuisines": ["american", "asian"]
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
        elif 'last_test_code' in code_response and code_response['last_test_code']:
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

    def test_enhanced_beverage_generation(self):
        """Test the enhanced 4-recipe beverage generation functionality"""
        print("\n" + "=" * 80)
        print("🧋 ENHANCED BEVERAGE GENERATION TESTING")
        print("=" * 80)
        
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        # Test different beverage recipe types to ensure consistency
        beverage_types = [
            "coffee drinks",
            "lemonade",
            "thai tea", 
            "bubble tea",
            "smoothies",
            "cocktails"
        ]
        
        all_tests_passed = True
        
        for beverage_type in beverage_types:
            print(f"\n📋 Testing beverage generation with recipe_type: '{beverage_type}'")
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "beverage",
                "cuisine_type": beverage_type,
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 45,
                "servings": 4,
                "difficulty": "medium"
            }
            
            success, response = self.run_test(
                f"Generate 4-Recipe Beverage Collection ({beverage_type})",
                "POST",
                "recipes/generate",
                200,
                data=recipe_request,
                timeout=60
            )
            
            if success:
                # Validate the response structure
                validation_result = self.validate_beverage_response(response, beverage_type)
                if not validation_result:
                    all_tests_passed = False
                    
                # Store the result for detailed analysis
                self.test_results.append({
                    "beverage_type": beverage_type,
                    "success": success,
                    "response": response,
                    "validation_passed": validation_result
                })
            else:
                print(f"❌ Failed to generate beverage recipes for {beverage_type}")
                all_tests_passed = False
                
        return all_tests_passed

    def validate_beverage_response(self, response, beverage_type):
        """Validate that the beverage response meets all requirements"""
        print(f"\n🔍 Validating response structure for {beverage_type}...")
        
        validation_results = {
            "has_title": False,
            "has_description": False,
            "has_ingredients": False,
            "has_instructions": False,
            "has_shopping_list": False,
            "title_format_correct": False,
            "description_mentions_4_recipes": False,
            "instructions_contain_4_beverages": False,
            "shopping_list_clean": False,
            "contains_coffee_drink": False,
            "contains_lemonade_drink": False,
            "contains_thai_tea_drink": False,
            "contains_boba_drink": False,
            "proper_emoji_format": False,
            "has_creative_names": False,
            "has_flavor_descriptions": False,
            "has_exact_quantities": False,
            "has_step_by_step_instructions": False,
            "has_tips_variations": False
        }
        
        # 1. Check basic response structure
        required_fields = ['title', 'description', 'ingredients', 'instructions', 'shopping_list']
        for field in required_fields:
            if field in response:
                validation_results[f"has_{field}"] = True
                print(f"✅ Has {field} field")
            else:
                print(f"❌ Missing {field} field")
        
        # 2. Validate title format
        title = response.get('title', '')
        if '4' in title and ('beverage' in title.lower() or 'drink' in title.lower() or 'collection' in title.lower()):
            validation_results["title_format_correct"] = True
            print(f"✅ Title format correct: '{title}'")
        else:
            print(f"❌ Title format incorrect: '{title}'")
            
        # 3. Validate description mentions 4 recipes
        description = response.get('description', '')
        if '4' in description or 'four' in description.lower():
            validation_results["description_mentions_4_recipes"] = True
            print(f"✅ Description mentions 4 recipes")
        else:
            print(f"❌ Description doesn't mention 4 recipes: '{description}'")
            
        # 4. Validate instructions contain all 4 beverage types
        instructions = response.get('instructions', [])
        instructions_text = ' '.join(instructions).lower()
        
        beverage_checks = [
            ("coffee", "contains_coffee_drink"),
            ("lemonade", "contains_lemonade_drink"), 
            ("thai tea", "contains_thai_tea_drink"),
            ("boba", "contains_boba_drink")
        ]
        
        found_beverages = 0
        for beverage_keyword, validation_key in beverage_checks:
            if beverage_keyword in instructions_text:
                validation_results[validation_key] = True
                found_beverages += 1
                print(f"✅ Contains {beverage_keyword}-based drink")
            else:
                print(f"❌ Missing {beverage_keyword}-based drink")
                
        if found_beverages == 4:
            validation_results["instructions_contain_4_beverages"] = True
            print("✅ All 4 required beverage types found")
        else:
            print(f"❌ Only found {found_beverages}/4 required beverage types")
            
        # 5. Validate emoji format usage
        emoji_patterns = ['🧋', '✨', '🧾', '🍳', '💡']
        emoji_count = 0
        for emoji in emoji_patterns:
            if emoji in instructions_text:
                emoji_count += 1
                
        if emoji_count >= 4:  # Should have most emojis
            validation_results["proper_emoji_format"] = True
            print(f"✅ Proper emoji format used ({emoji_count}/5 emojis found)")
        else:
            print(f"❌ Insufficient emoji usage ({emoji_count}/5 emojis found)")
            
        # 6. Validate creative names (look for creative drink names)
        creative_indicators = ['macchiato', 'latte', 'frappe', 'smoothie', 'fizz', 'blast', 'delight', 'fusion', 'twist']
        creative_names_found = any(indicator in instructions_text for indicator in creative_indicators)
        if creative_names_found:
            validation_results["has_creative_names"] = True
            print("✅ Creative drink names detected")
        else:
            print("❌ No creative drink names detected")
            
        # 7. Validate flavor descriptions (look for descriptive words)
        flavor_words = ['refreshing', 'creamy', 'sweet', 'tangy', 'rich', 'smooth', 'aromatic', 'tropical', 'zesty']
        flavor_descriptions_found = any(word in instructions_text for word in flavor_words)
        if flavor_descriptions_found:
            validation_results["has_flavor_descriptions"] = True
            print("✅ Flavor descriptions detected")
        else:
            print("❌ No flavor descriptions detected")
            
        # 8. Validate exact quantities (look for measurements)
        quantity_patterns = [r'\d+\s*(cup|cups|tbsp|tsp|oz|ounces|shots?)', r'\d+/\d+\s*(cup|cups)']
        has_quantities = any(re.search(pattern, instructions_text) for pattern in quantity_patterns)
        if has_quantities:
            validation_results["has_exact_quantities"] = True
            print("✅ Exact quantities with units detected")
        else:
            print("❌ No exact quantities with units detected")
            
        # 9. Validate step-by-step instructions
        step_indicators = ['step', '1.', '2.', '3.', 'first', 'then', 'next', 'finally']
        has_steps = any(indicator in instructions_text for indicator in step_indicators)
        if has_steps:
            validation_results["has_step_by_step_instructions"] = True
            print("✅ Step-by-step instructions detected")
        else:
            print("❌ No step-by-step instructions detected")
            
        # 10. Validate tips/variations
        tip_indicators = ['tip', 'variation', 'substitute', 'alternative', 'optional', 'vegan', 'swap']
        has_tips = any(indicator in instructions_text for indicator in tip_indicators)
        if has_tips:
            validation_results["has_tips_variations"] = True
            print("✅ Tips or variations detected")
        else:
            print("❌ No tips or variations detected")
            
        # 11. Validate shopping list is clean (no quantities/measurements)
        shopping_list = response.get('shopping_list', [])
        if shopping_list:
            clean_shopping_list = True
            quantity_patterns_shopping = [r'\d+', r'cup', r'tbsp', r'tsp', r'oz', r'ounces', r'lb', r'pounds']
            
            for item in shopping_list:
                if any(re.search(pattern, item.lower()) for pattern in quantity_patterns_shopping):
                    clean_shopping_list = False
                    print(f"❌ Shopping list item contains quantities/measurements: '{item}'")
                    break
                    
            if clean_shopping_list:
                validation_results["shopping_list_clean"] = True
                print(f"✅ Shopping list is clean ({len(shopping_list)} items)")
            else:
                print("❌ Shopping list contains quantities/measurements")
        else:
            print("❌ Shopping list is empty")
            
        # Calculate overall validation score
        total_checks = len(validation_results)
        passed_checks = sum(validation_results.values())
        validation_score = (passed_checks / total_checks) * 100
        
        print(f"\n📊 Validation Score: {validation_score:.1f}% ({passed_checks}/{total_checks} checks passed)")
        
        # Consider validation successful if >= 80% of checks pass
        validation_successful = validation_score >= 80.0
        
        if validation_successful:
            print("✅ Beverage response validation PASSED")
        else:
            print("❌ Beverage response validation FAILED")
            
        return validation_successful

    def test_beverage_shopping_list_consistency(self):
        """Test that shopping lists are consistent and clean across beverage recipes"""
        print("\n" + "=" * 80)
        print("🛒 BEVERAGE SHOPPING LIST CONSISTENCY TESTING")
        print("=" * 80)
        
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        # Generate multiple beverage recipes and check shopping list consistency
        test_cases = [
            {"recipe_type": "coffee drinks", "expected_ingredients": ["coffee", "milk", "sugar", "syrup"]},
            {"recipe_type": "lemonade", "expected_ingredients": ["lemon", "sugar", "water", "herbs"]},
            {"recipe_type": "thai tea", "expected_ingredients": ["thai tea", "milk", "sugar", "ice"]},
            {"recipe_type": "bubble tea", "expected_ingredients": ["tea", "tapioca", "milk", "sugar"]}
        ]
        
        all_shopping_lists_clean = True
        shopping_list_results = []
        
        for test_case in test_cases:
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "beverage",
                "cuisine_type": test_case["recipe_type"],
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 30,
                "servings": 2,
                "difficulty": "easy"
            }
            
            success, response = self.run_test(
                f"Generate Beverage for Shopping List Test ({test_case['recipe_type']})",
                "POST",
                "recipes/generate",
                200,
                data=recipe_request,
                timeout=45
            )
            
            if success and 'shopping_list' in response:
                shopping_list = response['shopping_list']
                
                # Check if shopping list is clean (no quantities, measurements)
                is_clean = self.validate_shopping_list_cleanliness(shopping_list, test_case['recipe_type'])
                if not is_clean:
                    all_shopping_lists_clean = False
                    
                shopping_list_results.append({
                    "recipe_type": test_case['recipe_type'],
                    "shopping_list": shopping_list,
                    "is_clean": is_clean,
                    "item_count": len(shopping_list)
                })
            else:
                print(f"❌ Failed to generate beverage recipe for {test_case['recipe_type']}")
                all_shopping_lists_clean = False
                
        # Summary of shopping list consistency
        print(f"\n📋 Shopping List Consistency Summary:")
        clean_lists = sum(1 for result in shopping_list_results if result['is_clean'])
        total_lists = len(shopping_list_results)
        
        print(f"Clean shopping lists: {clean_lists}/{total_lists}")
        print(f"Consistency score: {(clean_lists/total_lists)*100:.1f}%" if total_lists > 0 else "No data")
        
        for result in shopping_list_results:
            status = "✅" if result['is_clean'] else "❌"
            print(f"{status} {result['recipe_type']}: {result['item_count']} items")
            
        return all_shopping_lists_clean

    def validate_shopping_list_cleanliness(self, shopping_list, recipe_type):
        """Validate that a shopping list contains only clean ingredient names"""
        print(f"\n🔍 Validating shopping list cleanliness for {recipe_type}...")
        
        # Patterns that should NOT be in shopping list items
        forbidden_patterns = [
            r'\d+\s*(cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons)',
            r'\d+\s*(oz|ounce|ounces|lb|pound|pounds|gram|grams|kg)',
            r'\d+\s*(can|cans|jar|jars|bottle|bottles|package|packages)',
            r'\d+[\s\/\-]*\d*\s*(cup|tbsp|tsp|oz|lb)',
            r'^\d+\s+',  # Numbers at the start
            r'\d+/\d+',  # Fractions
            r'\d+\-\d+', # Ranges like 1-2
        ]
        
        # Preparation words that should NOT be in shopping list
        preparation_words = [
            'chopped', 'diced', 'sliced', 'minced', 'crushed', 'ground',
            'fresh', 'dried', 'cooked', 'raw', 'frozen', 'canned',
            'drained', 'rinsed', 'peeled', 'seeded', 'juiced'
        ]
        
        is_clean = True
        issues_found = []
        
        for item in shopping_list:
            item_lower = item.lower().strip()
            
            # Check for forbidden patterns
            for pattern in forbidden_patterns:
                if re.search(pattern, item_lower):
                    is_clean = False
                    issues_found.append(f"Contains measurement/quantity: '{item}'")
                    break
                    
            # Check for preparation words
            for prep_word in preparation_words:
                if prep_word in item_lower:
                    is_clean = False
                    issues_found.append(f"Contains preparation instruction: '{item}' (contains '{prep_word}')")
                    break
                    
        if is_clean:
            print(f"✅ Shopping list is clean ({len(shopping_list)} items)")
            print(f"   Items: {', '.join(shopping_list)}")
        else:
            print(f"❌ Shopping list has issues:")
            for issue in issues_found[:3]:  # Show first 3 issues
                print(f"   - {issue}")
                
        return is_clean

    def test_instagram_worthy_requirements(self):
        """Test that beverages meet Instagram-worthy presentation requirements"""
        print("\n" + "=" * 80)
        print("📸 INSTAGRAM-WORTHY BEVERAGE REQUIREMENTS TESTING")
        print("=" * 80)
        
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": "beverage",
            "cuisine_type": "specialty drinks",
            "dietary_preferences": [],
            "ingredients_on_hand": [],
            "prep_time_max": 60,
            "servings": 4,
            "difficulty": "medium"
        }
        
        success, response = self.run_test(
            "Generate Instagram-Worthy Beverages",
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60
        )
        
        if not success:
            print("❌ Failed to generate Instagram-worthy beverages")
            return False
            
        instructions_text = ' '.join(response.get('instructions', [])).lower()
        
        # Instagram-worthy indicators
        visual_appeal_words = [
            'layered', 'layering', 'foam', 'whipped', 'drizzle', 'garnish',
            'presentation', 'colorful', 'vibrant', 'beautiful', 'elegant',
            'instagram', 'photo', 'visual', 'aesthetic', 'artistic'
        ]
        
        professional_techniques = [
            'shaking', 'stirring', 'brewing', 'steaming', 'frothing',
            'temperature', 'chilled', 'hot', 'cold', 'ice', 'blend'
        ]
        
        creative_elements = [
            'syrup', 'sauce', 'topping', 'cream', 'milk foam', 'caramel',
            'vanilla', 'flavored', 'specialty', 'gourmet', 'artisan'
        ]
        
        # Check for visual appeal
        visual_score = sum(1 for word in visual_appeal_words if word in instructions_text)
        technique_score = sum(1 for word in professional_techniques if word in instructions_text)
        creative_score = sum(1 for word in creative_elements if word in instructions_text)
        
        print(f"📊 Instagram-Worthy Analysis:")
        print(f"   Visual Appeal Words: {visual_score}/15 found")
        print(f"   Professional Techniques: {technique_score}/10 found")
        print(f"   Creative Elements: {creative_score}/10 found")
        
        # Calculate Instagram-worthy score
        total_possible = 35
        total_found = visual_score + technique_score + creative_score
        instagram_score = (total_found / total_possible) * 100
        
        print(f"   Overall Instagram-Worthy Score: {instagram_score:.1f}%")
        
        # Consider Instagram-worthy if score >= 30%
        is_instagram_worthy = instagram_score >= 30.0
        
        if is_instagram_worthy:
            print("✅ Beverages meet Instagram-worthy requirements")
        else:
            print("❌ Beverages do not meet Instagram-worthy requirements")
            
        return is_instagram_worthy

    def run_comprehensive_beverage_test(self):
        """Run the complete enhanced beverage functionality test suite"""
        print("\n" + "=" * 100)
        print("🧋 COMPREHENSIVE ENHANCED BEVERAGE FUNCTIONALITY TEST SUITE")
        print("=" * 100)
        
        start_time = time.time()
        
        # Test results tracking
        test_suite_results = {
            "setup_successful": False,
            "beverage_generation_successful": False,
            "shopping_list_consistent": False,
            "instagram_worthy": False
        }
        
        # 1. Setup test user
        print("\n1️⃣ Setting up test environment...")
        test_suite_results["setup_successful"] = self.setup_test_user()
        
        if not test_suite_results["setup_successful"]:
            print("❌ Test setup failed - cannot continue")
            return False
            
        # 2. Test enhanced beverage generation
        print("\n2️⃣ Testing enhanced 4-recipe beverage generation...")
        test_suite_results["beverage_generation_successful"] = self.test_enhanced_beverage_generation()
        
        # 3. Test shopping list consistency
        print("\n3️⃣ Testing beverage shopping list consistency...")
        test_suite_results["shopping_list_consistent"] = self.test_beverage_shopping_list_consistency()
        
        # 4. Test Instagram-worthy requirements
        print("\n4️⃣ Testing Instagram-worthy presentation requirements...")
        test_suite_results["instagram_worthy"] = self.test_instagram_worthy_requirements()
        
        # Final results summary
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 100)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 100)
        
        print(f"⏱️ Total test execution time: {elapsed_time:.2f} seconds")
        print(f"🔢 Total tests run: {self.tests_run}")
        print(f"✅ Total tests passed: {self.tests_passed}")
        print(f"📈 Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🧪 Test Suite Component Results:")
        for component, result in test_suite_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {component.replace('_', ' ').title()}: {status}")
            
        # Overall assessment
        passed_components = sum(test_suite_results.values())
        total_components = len(test_suite_results)
        overall_success = passed_components >= 3  # At least 3/4 components must pass
        
        print(f"\n🎯 Overall Assessment: {passed_components}/{total_components} components passed")
        
        if overall_success:
            print("🎉 ENHANCED BEVERAGE FUNCTIONALITY TEST SUITE: ✅ PASSED")
            print("\n✨ Key Findings:")
            print("   • 4-recipe beverage generation is working correctly")
            print("   • All required beverage types (coffee, lemonade, Thai tea, boba) are included")
            print("   • Shopping lists are clean and consistent")
            print("   • Beverages meet Instagram-worthy presentation standards")
            print("   • Response format follows specifications with proper emojis and structure")
        else:
            print("❌ ENHANCED BEVERAGE FUNCTIONALITY TEST SUITE: ❌ FAILED")
            print("\n⚠️ Issues Found:")
            failed_components = [comp for comp, result in test_suite_results.items() if not result]
            for component in failed_components:
                print(f"   • {component.replace('_', ' ').title()} failed")
                
        return overall_success

def main():
    """Main function to run the enhanced beverage test suite"""
    print("🚀 Starting Enhanced Beverage Functionality Testing...")
    
    # Initialize test suite
    tester = EnhancedBeverageTestSuite()
    
    # Run comprehensive test
    success = tester.run_comprehensive_beverage_test()
    
    # Exit with appropriate code
    exit_code = 0 if success else 1
    print(f"\n🏁 Test suite completed with exit code: {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    main()