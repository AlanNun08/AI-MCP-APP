#!/usr/bin/env python3
"""
Backend API Testing Script for Walmart Integration - Mock Data Removal Testing
Tests that mock data has been removed and system returns appropriate empty responses
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Get backend URL from frontend .env file
BACKEND_URL = "https://9e62e04a-638f-4447-9e5b-339823cf6f32.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class WalmartMockDataRemovalTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.demo_user_email = "demo@test.com"
        self.demo_user_password = "password123"
        self.demo_user_id = None
        self.test_recipe_id = None
        self.results = []

    async def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {json.dumps(details, indent=2)}")

    async def test_demo_user_login(self):
        """Test demo user login with demo@test.com / password123"""
        try:
            response = await self.client.post(f"{API_BASE}/auth/login", json={
                "email": self.demo_user_email,
                "password": self.demo_user_password
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "user" in data:
                    self.demo_user_id = data["user"]["id"]
                    await self.log_result(
                        "Demo User Login", 
                        True, 
                        f"Successfully logged in demo user: {self.demo_user_email}",
                        {"user_id": self.demo_user_id, "user_data": data["user"]}
                    )
                    return True
                else:
                    await self.log_result(
                        "Demo User Login", 
                        False, 
                        f"Login response missing expected fields or status not success",
                        {"response": data}
                    )
                    return False
            else:
                await self.log_result(
                    "Demo User Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Demo User Login", False, f"Exception: {str(e)}")
            return False

    async def test_recipe_generation(self):
        """Generate a new recipe for testing"""
        try:
            response = await self.client.post(f"{API_BASE}/recipes/generate", json={
                "user_id": self.demo_user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "Italian",
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 30,
                "servings": 4,
                "difficulty": "medium"
            })
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "shopping_list" in data:
                    self.test_recipe_id = data["id"]
                    await self.log_result(
                        "Recipe Generation", 
                        True, 
                        f"Generated test recipe: {data.get('title', 'Unknown')}",
                        {
                            "recipe_id": self.test_recipe_id,
                            "title": data.get("title"),
                            "shopping_list": data.get("shopping_list", []),
                            "shopping_list_count": len(data.get("shopping_list", []))
                        }
                    )
                    return True
                else:
                    await self.log_result(
                        "Recipe Generation", 
                        False, 
                        "Recipe response missing required fields",
                        {"response": data}
                    )
                    return False
            else:
                await self.log_result(
                    "Recipe Generation", 
                    False, 
                    f"Recipe generation failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Recipe Generation", False, f"Exception: {str(e)}")
            return False

    async def test_cart_options_empty_response(self):
        """Test that /api/grocery/cart-options returns empty ingredient_options"""
        try:
            response = await self.client.post(f"{API_BASE}/grocery/cart-options?recipe_id={self.test_recipe_id}&user_id={self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for empty ingredient_options
                ingredient_options = data.get("ingredient_options", None)
                total_products = data.get("total_products", None)
                message = data.get("message", "")
                
                # Verify empty response
                is_empty = (
                    isinstance(ingredient_options, list) and 
                    len(ingredient_options) == 0 and
                    total_products == 0
                )
                
                # Check for appropriate message
                expected_message = "No Walmart products found for this recipe's ingredients. Real Walmart API integration needed."
                has_correct_message = expected_message in message
                
                success = is_empty and has_correct_message
                
                await self.log_result(
                    "Empty Cart Options Response", 
                    success, 
                    f"Empty response verification: {'✓' if is_empty else '✗'} Empty, {'✓' if has_correct_message else '✗'} Correct message",
                    {
                        "ingredient_options_empty": len(ingredient_options) == 0 if isinstance(ingredient_options, list) else False,
                        "total_products": total_products,
                        "message": message,
                        "expected_message": expected_message,
                        "has_correct_message": has_correct_message,
                        "full_response": data
                    }
                )
                
                return success, data
            else:
                await self.log_result(
                    "Empty Cart Options Response", 
                    False, 
                    f"Request failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False, None
                
        except Exception as e:
            await self.log_result("Empty Cart Options Response", False, f"Exception: {str(e)}")
            return False, None

    async def test_no_fake_product_ids(self, cart_data: Dict):
        """Verify that no fake product IDs are generated"""
        try:
            if not cart_data:
                await self.log_result("No Fake Product IDs", True, "No cart data to check - as expected")
                return True
            
            ingredient_options = cart_data.get("ingredient_options", [])
            
            # Should be empty, but let's check if any products exist
            fake_product_patterns = [
                "10315",  # Mock data pattern
                "12345",  # Test data pattern
                "99999",  # Common fake pattern
                "00000",  # Zero pattern
            ]
            
            fake_products_found = []
            total_products_found = 0
            
            for ingredient_option in ingredient_options:
                for product in ingredient_option.get("options", []):
                    total_products_found += 1
                    product_id = str(product.get("product_id", ""))
                    product_name = product.get("name", "").lower()
                    
                    # Check for fake patterns
                    is_fake = (
                        any(pattern in product_id for pattern in fake_product_patterns) or
                        "mock" in product_name or
                        "test" in product_name or
                        "fake" in product_name
                    )
                    
                    if is_fake:
                        fake_products_found.append({
                            "product_id": product_id,
                            "name": product.get("name", ""),
                            "reason": "Contains fake pattern"
                        })
            
            success = len(fake_products_found) == 0
            
            await self.log_result(
                "No Fake Product IDs", 
                success, 
                f"Found {len(fake_products_found)} fake products out of {total_products_found} total products",
                {
                    "total_products": total_products_found,
                    "fake_products_count": len(fake_products_found),
                    "fake_products": fake_products_found,
                    "expected_total": 0  # Should be 0 since mock data removed
                }
            )
            
            return success
            
        except Exception as e:
            await self.log_result("No Fake Product IDs", False, f"Exception: {str(e)}")
            return False

    async def test_response_structure_compliance(self, cart_data: Dict):
        """Test that response structure matches frontend expectations"""
        try:
            if not cart_data:
                await self.log_result("Response Structure", False, "No cart data to test")
                return False
            
            issues = []
            
            # Check required fields
            required_fields = ["recipe_id", "user_id", "ingredient_options", "total_products"]
            for field in required_fields:
                if field not in cart_data:
                    issues.append(f"Missing required field: {field}")
            
            # Check ingredient_options is list
            ingredient_options = cart_data.get("ingredient_options")
            if not isinstance(ingredient_options, list):
                issues.append("ingredient_options should be a list")
            
            # Check total_products is 0
            total_products = cart_data.get("total_products")
            if total_products != 0:
                issues.append(f"total_products should be 0, got {total_products}")
            
            # Check message field exists and has correct content
            message = cart_data.get("message", "")
            expected_message = "No Walmart products found for this recipe's ingredients. Real Walmart API integration needed."
            if expected_message not in message:
                issues.append(f"Message should contain expected text about real API integration needed")
            
            success = len(issues) == 0
            
            await self.log_result(
                "Response Structure Compliance", 
                success, 
                "Response structure is compliant" if success else f"Structure issues: {'; '.join(issues[:3])}",
                {
                    "total_issues": len(issues),
                    "issues": issues,
                    "response_keys": list(cart_data.keys()),
                    "ingredient_options_type": type(ingredient_options).__name__,
                    "ingredient_options_length": len(ingredient_options) if isinstance(ingredient_options, list) else "N/A",
                    "total_products": total_products,
                    "message_present": "message" in cart_data
                }
            )
            
            return success
            
        except Exception as e:
            await self.log_result("Response Structure Compliance", False, f"Exception: {str(e)}")
            return False

    async def test_existing_recipe_empty_response(self):
        """Test cart options with existing recipe also returns empty"""
        try:
            # Get demo user's recipe history
            response = await self.client.get(f"{API_BASE}/recipes/history/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                recipes = data.get("recipes", [])
                
                if not recipes:
                    await self.log_result(
                        "Existing Recipe Empty Response", 
                        True, 
                        "No existing recipes found - skipping test",
                        {"response": data}
                    )
                    return True
                
                # Use the first recipe from history
                existing_recipe = recipes[0]
                existing_recipe_id = existing_recipe.get("id")
                
                if not existing_recipe_id:
                    await self.log_result(
                        "Existing Recipe Empty Response", 
                        False, 
                        "Recipe from history missing ID",
                        {"recipe": existing_recipe}
                    )
                    return False
                
                # Test cart options with existing recipe
                cart_response = await self.client.post(f"{API_BASE}/grocery/cart-options?recipe_id={existing_recipe_id}&user_id={self.demo_user_id}")
                
                if cart_response.status_code == 200:
                    cart_data = cart_response.json()
                    
                    # Verify empty response
                    ingredient_options = cart_data.get("ingredient_options", [])
                    total_products = cart_data.get("total_products", -1)
                    message = cart_data.get("message", "")
                    
                    is_empty = len(ingredient_options) == 0 and total_products == 0
                    expected_message = "No Walmart products found for this recipe's ingredients. Real Walmart API integration needed."
                    has_correct_message = expected_message in message
                    
                    success = is_empty and has_correct_message
                    
                    await self.log_result(
                        "Existing Recipe Empty Response", 
                        success, 
                        f"Existing recipe also returns empty: {'✓' if is_empty else '✗'} Empty, {'✓' if has_correct_message else '✗'} Correct message",
                        {
                            "recipe_id": existing_recipe_id,
                            "recipe_title": existing_recipe.get("title"),
                            "ingredient_options_count": len(ingredient_options),
                            "total_products": total_products,
                            "message": message,
                            "has_correct_message": has_correct_message
                        }
                    )
                    
                    return success
                else:
                    await self.log_result(
                        "Existing Recipe Empty Response", 
                        False, 
                        f"Cart options failed for existing recipe with status {cart_response.status_code}",
                        {"response": cart_response.text}
                    )
                    return False
            else:
                await self.log_result(
                    "Existing Recipe Empty Response", 
                    False, 
                    f"Failed to get recipe history with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Existing Recipe Empty Response", False, f"Exception: {str(e)}")
            return False

    async def test_error_handling_edge_cases(self):
        """Test error handling for edge cases"""
        try:
            test_cases = [
                {
                    "name": "Invalid Recipe ID",
                    "recipe_id": "invalid-recipe-id-12345",
                    "user_id": self.demo_user_id,
                    "expected_status": [404, 422, 400]
                },
                {
                    "name": "Invalid User ID", 
                    "recipe_id": self.test_recipe_id,
                    "user_id": "invalid-user-id-12345",
                    "expected_status": [404, 422, 400]
                }
            ]
            
            all_passed = True
            
            for test_case in test_cases:
                response = await self.client.post(f"{API_BASE}/grocery/cart-options?recipe_id={test_case['recipe_id']}&user_id={test_case['user_id']}")
                
                success = response.status_code in test_case["expected_status"]
                if not success:
                    all_passed = False
                
                await self.log_result(
                    f"Error Handling - {test_case['name']}", 
                    success, 
                    f"Status {response.status_code} {'✓' if success else '✗'} Expected {test_case['expected_status']}",
                    {
                        "status_code": response.status_code,
                        "expected_status": test_case["expected_status"],
                        "response": response.text[:200]
                    }
                )
            
            return all_passed
            
        except Exception as e:
            await self.log_result("Error Handling Edge Cases", False, f"Exception: {str(e)}")
            return False

    async def test_frontend_graceful_handling_simulation(self):
        """Simulate how frontend should handle empty responses gracefully"""
        try:
            response = await self.client.post(f"{API_BASE}/grocery/cart-options?recipe_id={self.test_recipe_id}&user_id={self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Simulate frontend processing
                ingredient_options = data.get("ingredient_options", [])
                message = data.get("message", "")
                
                # Frontend should be able to handle:
                # 1. Empty ingredient_options list
                # 2. Display appropriate message to user
                # 3. Not crash or show errors
                
                frontend_can_handle = (
                    isinstance(ingredient_options, list) and  # Can iterate over list
                    len(ingredient_options) == 0 and          # Empty list is handled
                    isinstance(message, str) and              # Message is displayable
                    len(message) > 0                          # Message has content
                )
                
                await self.log_result(
                    "Frontend Graceful Handling", 
                    frontend_can_handle, 
                    f"Frontend can handle response gracefully: {'✓' if frontend_can_handle else '✗'}",
                    {
                        "ingredient_options_is_list": isinstance(ingredient_options, list),
                        "ingredient_options_empty": len(ingredient_options) == 0,
                        "message_is_string": isinstance(message, str),
                        "message_has_content": len(message) > 0,
                        "message_preview": message[:100]
                    }
                )
                
                return frontend_can_handle
            else:
                await self.log_result(
                    "Frontend Graceful Handling", 
                    False, 
                    f"Request failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Frontend Graceful Handling", False, f"Exception: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all mock data removal tests"""
        print("🎯 Starting Walmart Integration Mock Data Removal Testing")
        print("=" * 70)
        print("Testing that mock data has been removed and system returns appropriate empty responses")
        print("=" * 70)
        
        # Test 1: Demo user login
        if not await self.test_demo_user_login():
            print("❌ Cannot proceed without demo user login")
            return False
        
        # Test 2: Generate test recipe
        if not await self.test_recipe_generation():
            print("❌ Cannot proceed without test recipe")
            return False
        
        # Test 3: Main test - empty cart options response
        success, cart_data = await self.test_cart_options_empty_response()
        if not success:
            print("❌ Main empty response test failed")
            return False
        
        # Test 4: Verify no fake product IDs
        await self.test_no_fake_product_ids(cart_data)
        
        # Test 5: Response structure compliance
        await self.test_response_structure_compliance(cart_data)
        
        # Test 6: Test with existing recipe
        await self.test_existing_recipe_empty_response()
        
        # Test 7: Error handling edge cases
        await self.test_error_handling_edge_cases()
        
        # Test 8: Frontend graceful handling simulation
        await self.test_frontend_graceful_handling_simulation()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎯 WALMART MOCK DATA REMOVAL TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        # Print detailed results
        print("\nDetailed Results:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Print key findings
        print("\n" + "=" * 70)
        print("🔍 KEY FINDINGS FOR REVIEW REQUEST")
        print("=" * 70)
        
        if cart_data:
            print("✅ Mock data removal verification:")
            print(f"   - ingredient_options: {cart_data.get('ingredient_options', [])} (empty as expected)")
            print(f"   - total_products: {cart_data.get('total_products', 'N/A')} (0 as expected)")
            print(f"   - message: {cart_data.get('message', 'N/A')}")
            print(f"   - No fake product IDs generated: ✓")
            print(f"   - Frontend can handle gracefully: ✓")
        
        await self.client.aclose()
        return passed == total

async def main():
    """Main test runner"""
    tester = WalmartMockDataRemovalTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Mock data removal verified successfully.")
    else:
        print("\n⚠️ Some tests failed. Please review the results above.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())