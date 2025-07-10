#!/usr/bin/env python3
"""
Beverage Type Selection Fix Testing
==================================

This test specifically validates that when a user selects a specific beverage type 
(like "Coffee"), the OpenAI API only generates a recipe for that specific type, 
not all four beverage types (Coffee, Lemonade, Thai Tea, Boba).

Test Requirements:
1. Test the /api/generate-recipe endpoint with beverage category
2. Verify that when beverage_type is "Coffee", only a coffee recipe is generated
3. Verify that when beverage_type is "Lemonade", only a lemonade recipe is generated
4. Verify that when beverage_type is "Thai Tea", only a Thai tea recipe is generated
5. Verify that when beverage_type is "Boba", only a boba recipe is generated
6. Check that the OpenAI prompt is correctly constructed to request only the selected beverage type
7. Verify the response structure matches single recipe format (not 4-recipe collection)
8. Test with both healthy and budget mode combinations
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

class BeverageTypeSelectionTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.test_results = []
        
        # Test user credentials
        self.test_email = f"beverage_test_{uuid.uuid4()}@example.com"
        self.test_password = "SecureP@ssw0rd123"
        
        # Beverage types to test
        self.beverage_types = {
            "coffee": "Coffee",
            "special lemonades": "Lemonade", 
            "thai tea": "Thai Tea",
            "boba tea": "Boba"
        }

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
            
        if 'user_id' in response:
            self.user_id = response['user_id']
            print(f"✅ Created user with ID: {self.user_id}")
        else:
            print("❌ No user_id in response")
            return False
            
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
            print("✅ User setup complete")
            return True
        else:
            print("❌ Failed to verify user")
            return False

    def analyze_recipe_response(self, response, expected_beverage_type, test_name):
        """Analyze the recipe response to ensure it contains only the expected beverage type"""
        analysis = {
            "is_single_recipe": False,
            "contains_expected_type": False,
            "contains_other_types": False,
            "has_proper_structure": False,
            "shopping_list_clean": False,
            "details": []
        }
        
        # Check if response has single recipe structure
        required_fields = ['title', 'description', 'ingredients', 'instructions', 'shopping_list']
        has_all_fields = all(field in response for field in required_fields)
        
        if has_all_fields:
            analysis["has_proper_structure"] = True
            analysis["details"].append("✅ Has proper single recipe structure")
        else:
            missing_fields = [field for field in required_fields if field not in response]
            analysis["details"].append(f"❌ Missing fields: {missing_fields}")
            
        # Check if it's a single recipe (not a collection of 4 recipes)
        title = response.get('title', '').lower()
        description = response.get('description', '').lower()
        ingredients = ' '.join(response.get('ingredients', [])).lower()
        instructions = ' '.join(response.get('instructions', [])).lower()
        
        # Combine all text for analysis
        full_text = f"{title} {description} {ingredients} {instructions}"
        
        # Check if response contains multiple beverage types (indicating 4-recipe format)
        beverage_indicators = {
            'coffee': ['coffee', 'espresso', 'latte', 'cappuccino', 'macchiato', 'americano'],
            'lemonade': ['lemonade', 'lemon', 'citrus', 'lime'],
            'thai tea': ['thai tea', 'thai', 'orange tea', 'condensed milk'],
            'boba': ['boba', 'bubble tea', 'tapioca', 'pearl', 'milk tea']
        }
        
        # Count how many different beverage types are mentioned
        mentioned_types = []
        for bev_type, indicators in beverage_indicators.items():
            if any(indicator in full_text for indicator in indicators):
                mentioned_types.append(bev_type)
                
        if len(mentioned_types) == 1:
            analysis["is_single_recipe"] = True
            analysis["details"].append("✅ Contains only one beverage type")
        else:
            analysis["is_single_recipe"] = False
            analysis["details"].append(f"❌ Contains multiple beverage types: {mentioned_types}")
            
        # Check if the expected beverage type is present
        expected_indicators = beverage_indicators.get(expected_beverage_type.lower(), [])
        if any(indicator in full_text for indicator in expected_indicators):
            analysis["contains_expected_type"] = True
            analysis["details"].append(f"✅ Contains expected beverage type: {expected_beverage_type}")
        else:
            analysis["contains_expected_type"] = False
            analysis["details"].append(f"❌ Does not contain expected beverage type: {expected_beverage_type}")
            
        # Check if other beverage types are present (should not be)
        other_types = [bev_type for bev_type in beverage_indicators.keys() 
                      if bev_type != expected_beverage_type.lower()]
        found_other_types = []
        
        for other_type in other_types:
            other_indicators = beverage_indicators[other_type]
            if any(indicator in full_text for indicator in other_indicators):
                found_other_types.append(other_type)
                
        if not found_other_types:
            analysis["contains_other_types"] = False
            analysis["details"].append("✅ Does not contain other beverage types")
        else:
            analysis["contains_other_types"] = True
            analysis["details"].append(f"❌ Contains other beverage types: {found_other_types}")
            
        # Check shopping list cleanliness
        shopping_list = response.get('shopping_list', [])
        if shopping_list:
            # Check for quantities and measurements in shopping list
            quantity_patterns = [
                r'\d+\s*(cups?|tbsp|tsp|oz|lbs?|cans?|bottles?|packages?)',
                r'\d+/\d+\s*(cup|tbsp|tsp)',
                r'\d+\s+(shots?|pieces?|slices?)',
                r'^\d+\s+',  # Numbers at start
            ]
            
            clean_items = 0
            total_items = len(shopping_list)
            
            for item in shopping_list:
                item_str = str(item).lower()
                has_quantity = any(re.search(pattern, item_str) for pattern in quantity_patterns)
                if not has_quantity:
                    clean_items += 1
                    
            cleanliness_ratio = clean_items / total_items if total_items > 0 else 0
            
            if cleanliness_ratio >= 0.8:  # 80% or more items are clean
                analysis["shopping_list_clean"] = True
                analysis["details"].append(f"✅ Shopping list is clean ({clean_items}/{total_items} items)")
            else:
                analysis["shopping_list_clean"] = False
                analysis["details"].append(f"❌ Shopping list contains quantities ({clean_items}/{total_items} clean)")
        else:
            analysis["details"].append("⚠️ No shopping list found")
            
        return analysis

    def test_beverage_type_selection(self, beverage_type, display_name, mode_config=None):
        """Test generation of a specific beverage type"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        # Build recipe request
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": "beverage",
            "cuisine_type": beverage_type,  # This is the key field that specifies the beverage type
            "dietary_preferences": [],
            "ingredients_on_hand": [],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "medium"
        }
        
        # Add mode configurations if provided
        if mode_config:
            recipe_request.update(mode_config)
            
        mode_description = ""
        if mode_config:
            if mode_config.get('is_healthy'):
                mode_description += f" (Healthy: {mode_config.get('max_calories_per_serving', 'N/A')} cal)"
            if mode_config.get('is_budget_friendly'):
                mode_description += f" (Budget: ${mode_config.get('max_budget', 'N/A')})"
                
        test_name = f"Generate {display_name} Recipe{mode_description}"
        
        print(f"\n🧪 Testing: {test_name}")
        print(f"Request payload: {json.dumps(recipe_request, indent=2)}")
        
        success, response = self.run_test(
            test_name,
            "POST",
            "recipes/generate",
            200,
            data=recipe_request,
            timeout=60
        )
        
        if not success:
            print(f"❌ Failed to generate {display_name} recipe")
            self.test_results.append({
                "test": test_name,
                "success": False,
                "error": "API call failed",
                "analysis": None
            })
            return False
            
        # Analyze the response
        analysis = self.analyze_recipe_response(response, display_name, test_name)
        
        # Print analysis results
        print(f"\n📊 Analysis for {test_name}:")
        for detail in analysis["details"]:
            print(f"   {detail}")
            
        # Determine overall success
        overall_success = (
            analysis["has_proper_structure"] and
            analysis["is_single_recipe"] and
            analysis["contains_expected_type"] and
            not analysis["contains_other_types"]
        )
        
        if overall_success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
            
        # Store results
        self.test_results.append({
            "test": test_name,
            "success": overall_success,
            "response": response,
            "analysis": analysis
        })
        
        return overall_success

    def test_all_beverage_types(self):
        """Test all beverage types with different mode combinations"""
        print("\n" + "=" * 80)
        print("🧋 BEVERAGE TYPE SELECTION TESTING")
        print("=" * 80)
        
        if not self.setup_test_user():
            print("❌ Failed to setup test user - cannot continue")
            return False
            
        # Test configurations
        test_configs = [
            {"name": "Basic", "config": None},
            {"name": "Healthy", "config": {"is_healthy": True, "max_calories_per_serving": 300}},
            {"name": "Budget", "config": {"is_budget_friendly": True, "max_budget": 10.0}},
            {"name": "Healthy + Budget", "config": {
                "is_healthy": True, 
                "max_calories_per_serving": 350,
                "is_budget_friendly": True, 
                "max_budget": 12.0
            }}
        ]
        
        all_tests_passed = True
        
        # Test each beverage type with each configuration
        for beverage_type, display_name in self.beverage_types.items():
            print(f"\n" + "=" * 60)
            print(f"🧋 Testing {display_name} Recipes")
            print("=" * 60)
            
            for test_config in test_configs:
                config_name = test_config["name"]
                config_data = test_config["config"]
                
                success = self.test_beverage_type_selection(
                    beverage_type, 
                    display_name, 
                    config_data
                )
                
                if not success:
                    all_tests_passed = False
                    
                # Add a small delay between tests to avoid rate limiting
                time.sleep(2)
                
        return all_tests_passed

    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 BEVERAGE TYPE SELECTION TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📈 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
        
        # Group results by beverage type
        beverage_results = {}
        for result in self.test_results:
            test_name = result["test"]
            for beverage_type, display_name in self.beverage_types.items():
                if display_name in test_name:
                    if display_name not in beverage_results:
                        beverage_results[display_name] = []
                    beverage_results[display_name].append(result)
                    break
                    
        # Print detailed results by beverage type
        print(f"\n📋 Detailed Results by Beverage Type:")
        for beverage_name, results in beverage_results.items():
            print(f"\n🧋 {beverage_name}:")
            beverage_passed = sum(1 for r in results if r["success"])
            beverage_total = len(results)
            print(f"   Success Rate: {beverage_passed}/{beverage_total} ({(beverage_passed/beverage_total*100):.1f}%)")
            
            for result in results:
                status = "✅ PASSED" if result["success"] else "❌ FAILED"
                print(f"   {status} - {result['test']}")
                
                if not result["success"] and result.get("analysis"):
                    analysis = result["analysis"]
                    print(f"      Issues:")
                    if not analysis["has_proper_structure"]:
                        print(f"        - Missing proper recipe structure")
                    if not analysis["is_single_recipe"]:
                        print(f"        - Contains multiple beverage types (should be single)")
                    if not analysis["contains_expected_type"]:
                        print(f"        - Does not contain expected beverage type")
                    if analysis["contains_other_types"]:
                        print(f"        - Contains other beverage types (should not)")
                        
        # Critical issues summary
        print(f"\n🚨 Critical Issues Found:")
        critical_issues = []
        
        for result in self.test_results:
            if not result["success"] and result.get("analysis"):
                analysis = result["analysis"]
                if not analysis["is_single_recipe"]:
                    critical_issues.append("Multiple beverage types in single recipe response")
                if analysis["contains_other_types"]:
                    critical_issues.append("Wrong beverage types generated")
                    
        if critical_issues:
            unique_issues = list(set(critical_issues))
            for issue in unique_issues:
                print(f"   ❌ {issue}")
        else:
            print(f"   ✅ No critical issues found")
            
        # Recommendations
        print(f"\n💡 Recommendations:")
        if failed_tests > 0:
            print(f"   1. Review OpenAI prompt construction for beverage category")
            print(f"   2. Ensure cuisine_type parameter correctly filters beverage types")
            print(f"   3. Verify response parsing handles single recipe format")
            print(f"   4. Check that shopping_list generation is clean for beverages")
        else:
            print(f"   ✅ All tests passed - beverage type selection is working correctly!")
            
        return passed_tests == total_tests

def main():
    """Main test execution"""
    print("🧋 Starting Beverage Type Selection Fix Testing")
    print("=" * 80)
    
    # Initialize tester
    tester = BeverageTypeSelectionTester()
    
    try:
        # Run all tests
        all_passed = tester.test_all_beverage_types()
        
        # Generate report
        report_success = tester.generate_test_report()
        
        # Final summary
        print(f"\n" + "=" * 80)
        print("🏁 FINAL SUMMARY")
        print("=" * 80)
        
        if all_passed and report_success:
            print("✅ ALL BEVERAGE TYPE SELECTION TESTS PASSED")
            print("✅ The beverage type selection fix is working correctly")
            print("✅ Users will receive only the specific beverage type they select")
            return True
        else:
            print("❌ SOME BEVERAGE TYPE SELECTION TESTS FAILED")
            print("❌ The beverage type selection fix needs attention")
            print("❌ Users may receive multiple beverage types instead of their selection")
            return False
            
    except Exception as e:
        print(f"❌ Testing failed with error: {str(e)}")
        logger.error(f"Testing failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)