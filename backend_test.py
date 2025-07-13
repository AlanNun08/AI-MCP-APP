#!/usr/bin/env python3
"""
Backend Testing Script for Walmart Integration Workflow
Tests the specific requirements from the review request:
1. Demo user login (demo@test.com / password123)
2. Recipe generation for demo user
3. Cart-options endpoint with authentic Walmart products
4. Verify relevance filtering is disabled
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://142302c8-79a4-4ce9-afcd-9780360c7f94.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class WalmartIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.demo_user_id = None
        self.recipe_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_backend_health(self):
        """Test if backend is accessible"""
        try:
            response = self.session.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                self.log_result("Backend Health Check", True, "Backend is accessible")
                return True
            else:
                self.log_result("Backend Health Check", False, f"Backend returned {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Backend not accessible: {str(e)}")
            return False
    
    def test_demo_user_login(self):
        """Test demo user login as specified in review request"""
        try:
            login_data = {
                "email": "demo@test.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.demo_user_id = data.get("user", {}).get("id") or data.get("user_id")
                    user_info = data.get("user", {})
                    self.log_result(
                        "Demo User Login", 
                        True, 
                        f"Successfully logged in as {user_info.get('first_name', 'Demo')} {user_info.get('last_name', 'User')}",
                        {"user_id": self.demo_user_id, "email": user_info.get("email")}
                    )
                    return True
                else:
                    self.log_result("Demo User Login", False, f"Login failed: {data.get('message', 'Unknown error')}", data)
                    return False
            else:
                self.log_result("Demo User Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Demo User Login", False, f"Login request failed: {str(e)}")
            return False
    
    def test_recipe_generation(self):
        """Test Italian cuisine recipe generation for demo user"""
        if not self.demo_user_id:
            self.log_result("Recipe Generation", False, "No demo user ID available")
            return False
            
        try:
            recipe_data = {
                "user_id": self.demo_user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "Italian",
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 60,
                "servings": 4,
                "difficulty": "medium"
            }
            
            response = self.session.post(f"{API_BASE}/recipes/generate", json=recipe_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.recipe_id = data.get("id")
                shopping_list = data.get("shopping_list", [])
                
                self.log_result(
                    "Recipe Generation", 
                    True, 
                    f"Generated Italian recipe: {data.get('title', 'Unknown')} with {len(shopping_list)} shopping items",
                    {
                        "recipe_id": self.recipe_id,
                        "title": data.get("title"),
                        "shopping_list_count": len(shopping_list),
                        "shopping_list": shopping_list[:5]  # First 5 items for brevity
                    }
                )
                return True
            else:
                self.log_result("Recipe Generation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Recipe Generation", False, f"Recipe generation failed: {str(e)}")
            return False
    
    def test_walmart_cart_options(self):
        """Test the critical Walmart cart-options endpoint"""
        if not self.demo_user_id or not self.recipe_id:
            self.log_result("Walmart Cart Options", False, "Missing demo user ID or recipe ID")
            return False
            
        try:
            params = {
                "user_id": self.demo_user_id,
                "recipe_id": self.recipe_id
            }
            
            response = self.session.post(f"{API_BASE}/grocery/cart-options", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                ingredient_options = data.get("ingredient_options", [])
                
                # Analyze the products for authenticity
                total_products = 0
                authentic_products = 0
                product_details = []
                
                for ingredient in ingredient_options:
                    ingredient_name = ingredient.get("ingredient_name", "Unknown")
                    options = ingredient.get("options", [])
                    total_products += len(options)
                    
                    for product in options:
                        product_id = product.get("product_id", "")
                        name = product.get("name", "")
                        price = product.get("price", 0)
                        
                        # Check if product looks authentic (real Walmart product IDs are typically 8-11 digits)
                        is_authentic = (
                            len(product_id) >= 8 and 
                            product_id.isdigit() and 
                            price > 0 and 
                            len(name) > 5 and
                            not product_id.startswith("10315")  # Avoid mock data pattern
                        )
                        
                        if is_authentic:
                            authentic_products += 1
                            
                        product_details.append({
                            "ingredient": ingredient_name,
                            "product_id": product_id,
                            "name": name,
                            "price": price,
                            "authentic": is_authentic
                        })
                
                authenticity_rate = (authentic_products / total_products * 100) if total_products > 0 else 0
                
                success = total_products > 0 and authenticity_rate >= 80  # At least 80% authentic products
                
                self.log_result(
                    "Walmart Cart Options", 
                    success, 
                    f"Found {total_products} products across {len(ingredient_options)} ingredients. Authenticity rate: {authenticity_rate:.1f}%",
                    {
                        "total_ingredients": len(ingredient_options),
                        "total_products": total_products,
                        "authentic_products": authentic_products,
                        "authenticity_rate": f"{authenticity_rate:.1f}%",
                        "sample_products": product_details[:5]  # First 5 for brevity
                    }
                )
                
                # Additional check for "No Walmart products found" error
                if total_products == 0:
                    self.log_result(
                        "Walmart Products Availability", 
                        False, 
                        "No Walmart products found - this indicates the relevance filtering issue may still exist"
                    )
                
                return success
                
            elif response.status_code == 404:
                self.log_result("Walmart Cart Options", False, "Recipe not found for Walmart integration")
                return False
            else:
                self.log_result("Walmart Cart Options", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Walmart Cart Options", False, f"Cart options request failed: {str(e)}")
            return False
    
    def test_relevance_filtering_disabled(self):
        """Verify that relevance filtering is disabled by checking for debug logs"""
        # This is more of a code verification since we can't directly access backend logs
        # But we can infer from the success of the cart-options test
        if len([r for r in self.test_results if r["test"] == "Walmart Cart Options" and "✅" in r["status"]]) > 0:
            self.log_result(
                "Relevance Filtering Check", 
                True, 
                "Relevance filtering appears to be disabled (products were found successfully)"
            )
            return True
        else:
            self.log_result(
                "Relevance Filtering Check", 
                False, 
                "Relevance filtering may still be active (no products found)"
            )
            return False
    
    def test_multiple_ingredients_processing(self):
        """Test that the system processes multiple ingredients correctly"""
        # This is verified by checking if we got products for multiple ingredients
        cart_options_results = [r for r in self.test_results if r["test"] == "Walmart Cart Options"]
        
        if cart_options_results and cart_options_results[0]["details"].get("total_ingredients", 0) > 1:
            ingredient_count = cart_options_results[0]["details"]["total_ingredients"]
            self.log_result(
                "Multiple Ingredients Processing", 
                True, 
                f"Successfully processed {ingredient_count} ingredients"
            )
            return True
        else:
            self.log_result(
                "Multiple Ingredients Processing", 
                False, 
                "Failed to process multiple ingredients or only found 1 ingredient"
            )
            return False
    
    def run_all_tests(self):
        """Run all tests in the specified order"""
        print("🎯 Starting Walmart Integration Testing as per Review Request")
        print("=" * 70)
        
        # Test sequence as specified in review request
        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("Demo User Login", self.test_demo_user_login),
            ("Recipe Generation", self.test_recipe_generation),
            ("Walmart Cart Options", self.test_walmart_cart_options),
            ("Relevance Filtering Check", self.test_relevance_filtering_disabled),
            ("Multiple Ingredients Processing", self.test_multiple_ingredients_processing)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {str(e)}")
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 WALMART INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details'] and "✅" not in result['status']:
                print(f"   → {result['message']}")
        
        print(f"\n📊 OVERALL RESULT: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Specific review request validation
        critical_tests = ["Demo User Login", "Recipe Generation", "Walmart Cart Options"]
        critical_passed = len([r for r in self.test_results if r["test"] in critical_tests and "✅" in r["status"]])
        
        if critical_passed == len(critical_tests):
            print("✅ CRITICAL REVIEW REQUIREMENTS: ALL PASSED")
            print("   - Demo user authentication working")
            print("   - Recipe generation working")
            print("   - Walmart integration returning authentic products")
        else:
            print("❌ CRITICAL REVIEW REQUIREMENTS: FAILED")
            print(f"   - Only {critical_passed}/{len(critical_tests)} critical tests passed")
        
        return success_rate >= 80 and critical_passed == len(critical_tests)

def main():
    """Main test execution"""
    print("🚀 Walmart Integration Backend Testing")
    print("Testing the specific workflow from the review request:")
    print("1. Demo user login (demo@test.com / password123)")
    print("2. Recipe generation for Italian cuisine")
    print("3. Walmart cart-options with authentic products")
    print("4. Verification of relevance filtering disabled")
    print()
    
    tester = WalmartIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL CRITICAL TESTS PASSED - Walmart integration is working correctly!")
        sys.exit(0)
    else:
        print("\n🚨 SOME TESTS FAILED - Review the issues above")
        sys.exit(1)

if __name__ == "__main__":
    main()