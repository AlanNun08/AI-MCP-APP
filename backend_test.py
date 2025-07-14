#!/usr/bin/env python3
"""
Backend API Testing Script for Walmart Integration
Tests the /api/grocery/cart-options endpoint and related functionality
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

class WalmartIntegrationTester:
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
        """Test demo user login to get user_id"""
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
                        f"Login response missing expected fields",
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
        """Generate a test recipe for Walmart integration testing"""
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
                            "shopping_list": data.get("shopping_list", [])
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

    async def test_cart_options_endpoint(self):
        """Test the main /api/grocery/cart-options endpoint"""
        try:
            response = await self.client.post(f"{API_BASE}/grocery/cart-options?recipe_id={self.test_recipe_id}&user_id={self.demo_user_id}")
            
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                success = True
                issues = []
                
                # Check for ingredient_options field (not ingredients)
                if "ingredient_options" not in data:
                    success = False
                    issues.append("Missing 'ingredient_options' field in response")
                elif not isinstance(data["ingredient_options"], list):
                    success = False
                    issues.append("'ingredient_options' should be a list")
                else:
                    # Check each ingredient option
                    for i, ingredient_option in enumerate(data["ingredient_options"]):
                        if "ingredient_name" not in ingredient_option:
                            success = False
                            issues.append(f"Ingredient option {i} missing 'ingredient_name'")
                        
                        # Check for 'options' field (not 'products')
                        if "options" not in ingredient_option:
                            success = False
                            issues.append(f"Ingredient option {i} missing 'options' field")
                        elif not isinstance(ingredient_option["options"], list):
                            success = False
                            issues.append(f"Ingredient option {i} 'options' should be a list")
                        else:
                            # Check each product in options
                            for j, product in enumerate(ingredient_option["options"]):
                                required_fields = ["product_id", "name", "price", "image_url", "available"]
                                for field in required_fields:
                                    if field not in product:
                                        success = False
                                        issues.append(f"Product {j} in ingredient {i} missing '{field}' field")
                
                await self.log_result(
                    "Cart Options Endpoint Structure", 
                    success, 
                    "Response structure validation" if success else f"Structure issues: {'; '.join(issues)}",
                    {
                        "response_keys": list(data.keys()),
                        "ingredient_count": len(data.get("ingredient_options", [])),
                        "issues": issues,
                        "sample_response": data
                    }
                )
                
                return success, data
            else:
                await self.log_result(
                    "Cart Options Endpoint", 
                    False, 
                    f"Request failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False, None
                
        except Exception as e:
            await self.log_result("Cart Options Endpoint", False, f"Exception: {str(e)}")
            return False, None

    async def test_cart_options_invalid_recipe_id(self):
        """Test cart options with invalid recipe_id"""
        try:
            response = await self.client.post(f"{API_BASE}/grocery/cart-options?recipe_id=invalid-recipe-id-12345&user_id={self.demo_user_id}")
            
            
            # Should return 404 or appropriate error
            if response.status_code in [404, 422, 400]:
                await self.log_result(
                    "Invalid Recipe ID Test", 
                    True, 
                    f"Correctly handled invalid recipe_id with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return True
            else:
                await self.log_result(
                    "Invalid Recipe ID Test", 
                    False, 
                    f"Unexpected status code {response.status_code} for invalid recipe_id",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Invalid Recipe ID Test", False, f"Exception: {str(e)}")
            return False

    async def test_cart_options_invalid_user_id(self):
        """Test cart options with invalid user_id"""
        try:
            response = await self.client.post(f"{API_BASE}/grocery/cart-options?recipe_id={self.test_recipe_id}&user_id=invalid-user-id-12345")
            
            
            # Should return 404 or appropriate error
            if response.status_code in [404, 422, 400]:
                await self.log_result(
                    "Invalid User ID Test", 
                    True, 
                    f"Correctly handled invalid user_id with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return True
            else:
                await self.log_result(
                    "Invalid User ID Test", 
                    False, 
                    f"Unexpected status code {response.status_code} for invalid user_id",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Invalid User ID Test", False, f"Exception: {str(e)}")
            return False

    async def test_product_authenticity(self, cart_data: Dict):
        """Test that returned products are authentic Walmart products"""
        try:
            if not cart_data or "ingredient_options" not in cart_data:
                await self.log_result("Product Authenticity", False, "No cart data to test")
                return False
            
            total_products = 0
            authentic_products = 0
            product_samples = []
            
            for ingredient_option in cart_data["ingredient_options"]:
                for product in ingredient_option.get("options", []):
                    total_products += 1
                    
                    # Check product_id format (Walmart IDs can be 6-11 digits)
                    product_id = str(product.get("product_id", ""))
                    product_name = product.get("name", "").lower()
                    product_price = product.get("price", 0)
                    
                    is_authentic = (
                        product_id.isdigit() and 
                        len(product_id) >= 6 and 
                        len(product_id) <= 11 and
                        not product_id.startswith("10315") and  # Avoid mock data pattern
                        not product_id.startswith("12345") and  # Avoid test data pattern
                        product_price > 0 and  # Has valid price
                        len(product_name) > 0 and  # Has valid name
                        not "mock" in product_name and  # Not mock data
                        not "test" in product_name      # Not test data
                    )
                    
                    if is_authentic:
                        authentic_products += 1
                    
                    # Collect sample for analysis
                    if len(product_samples) < 5:
                        product_samples.append({
                            "product_id": product_id,
                            "name": product.get("name", ""),
                            "price": product.get("price", 0),
                            "is_authentic": is_authentic,
                            "id_length": len(product_id)
                        })
            
            authenticity_rate = (authentic_products / total_products * 100) if total_products > 0 else 0
            
            await self.log_result(
                "Product Authenticity", 
                authenticity_rate >= 80,  # At least 80% should be authentic
                f"Authenticity rate: {authenticity_rate:.1f}% ({authentic_products}/{total_products})",
                {
                    "total_products": total_products,
                    "authentic_products": authentic_products,
                    "authenticity_rate": authenticity_rate,
                    "product_samples": product_samples
                }
            )
            
            return authenticity_rate >= 80
            
        except Exception as e:
            await self.log_result("Product Authenticity", False, f"Exception: {str(e)}")
            return False

    async def test_response_format_consistency(self, cart_data: Dict):
        """Test that response format is consistent and matches frontend expectations"""
        try:
            if not cart_data:
                await self.log_result("Response Format Consistency", False, "No cart data to test")
                return False
            
            issues = []
            
            # Check top-level structure
            expected_top_fields = ["ingredient_options"]
            for field in expected_top_fields:
                if field not in cart_data:
                    issues.append(f"Missing top-level field: {field}")
            
            # Check ingredient options structure
            if "ingredient_options" in cart_data:
                for i, ingredient_option in enumerate(cart_data["ingredient_options"]):
                    # Check ingredient option fields
                    expected_ingredient_fields = ["ingredient_name", "options"]
                    for field in expected_ingredient_fields:
                        if field not in ingredient_option:
                            issues.append(f"Ingredient {i} missing field: {field}")
                    
                    # Check product structure
                    if "options" in ingredient_option:
                        for j, product in enumerate(ingredient_option["options"]):
                            expected_product_fields = ["product_id", "name", "price", "image_url", "available"]
                            for field in expected_product_fields:
                                if field not in product:
                                    issues.append(f"Product {j} in ingredient {i} missing field: {field}")
                            
                            # Check field types
                            if "price" in product and not isinstance(product["price"], (int, float)):
                                issues.append(f"Product {j} price should be numeric")
                            
                            if "available" in product and not isinstance(product["available"], (bool, str)):
                                issues.append(f"Product {j} available should be boolean or string")
            
            success = len(issues) == 0
            
            await self.log_result(
                "Response Format Consistency", 
                success, 
                "Response format is consistent" if success else f"Format issues: {'; '.join(issues[:5])}",
                {
                    "total_issues": len(issues),
                    "issues": issues[:10],  # Limit to first 10 issues
                    "response_structure": self._analyze_structure(cart_data)
                }
            )
            
            return success
            
        except Exception as e:
            await self.log_result("Response Format Consistency", False, f"Exception: {str(e)}")
            return False

    async def test_specific_field_requirements(self):
        """Test specific field requirements from review request"""
        try:
            response = await self.client.post(f"{API_BASE}/grocery/cart-options?recipe_id={self.test_recipe_id}&user_id={self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                issues = []
                
                # 1. Verify response contains 'ingredient_options' (not 'ingredients')
                if "ingredients" in data:
                    issues.append("Response contains 'ingredients' field - should be 'ingredient_options'")
                if "ingredient_options" not in data:
                    issues.append("Response missing 'ingredient_options' field")
                
                # 2. Verify each ingredient option contains 'options' field (not 'products')
                if "ingredient_options" in data:
                    for i, ingredient_option in enumerate(data["ingredient_options"]):
                        if "products" in ingredient_option:
                            issues.append(f"Ingredient {i} contains 'products' field - should be 'options'")
                        if "options" not in ingredient_option:
                            issues.append(f"Ingredient {i} missing 'options' field")
                        
                        # 3. Verify each product has correct fields
                        if "options" in ingredient_option:
                            for j, product in enumerate(ingredient_option["options"]):
                                required_fields = ["product_id", "name", "price", "image_url", "available"]
                                for field in required_fields:
                                    if field not in product:
                                        issues.append(f"Product {j} in ingredient {i} missing required field '{field}'")
                
                success = len(issues) == 0
                
                await self.log_result(
                    "Specific Field Requirements", 
                    success, 
                    "All field requirements met" if success else f"Field issues: {'; '.join(issues[:3])}",
                    {
                        "total_issues": len(issues),
                        "issues": issues,
                        "has_ingredient_options": "ingredient_options" in data,
                        "has_ingredients": "ingredients" in data,
                        "sample_structure": self._get_field_structure(data)
                    }
                )
                
                return success
            else:
                await self.log_result(
                    "Specific Field Requirements", 
                    False, 
                    f"Request failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Specific Field Requirements", False, f"Exception: {str(e)}")
            return False

    def _get_field_structure(self, data: Dict) -> Dict:
        """Get field structure for analysis"""
        structure = {
            "top_level_fields": list(data.keys()) if isinstance(data, dict) else [],
            "ingredient_structure": {},
            "product_structure": {}
        }
        
        if "ingredient_options" in data and isinstance(data["ingredient_options"], list) and len(data["ingredient_options"]) > 0:
            first_ingredient = data["ingredient_options"][0]
            structure["ingredient_structure"] = list(first_ingredient.keys()) if isinstance(first_ingredient, dict) else []
            
            if "options" in first_ingredient and isinstance(first_ingredient["options"], list) and len(first_ingredient["options"]) > 0:
                first_product = first_ingredient["options"][0]
                structure["product_structure"] = list(first_product.keys()) if isinstance(first_product, dict) else []
        
        return structure

    def _analyze_structure(self, data: Any, max_depth: int = 3) -> Dict:
        """Analyze data structure for debugging"""
        if max_depth <= 0:
            return {"type": type(data).__name__, "truncated": True}
        
        if isinstance(data, dict):
            return {
                "type": "dict",
                "keys": list(data.keys()),
                "sample_values": {k: self._analyze_structure(v, max_depth - 1) for k, v in list(data.items())[:3]}
            }
        elif isinstance(data, list):
            return {
                "type": "list",
                "length": len(data),
                "sample_items": [self._analyze_structure(item, max_depth - 1) for item in data[:2]]
            }
        else:
            return {"type": type(data).__name__, "value": str(data)[:100]}

    async def run_all_tests(self):
        """Run all Walmart integration tests"""
        print("🎯 Starting Walmart Integration API Testing")
        print("=" * 60)
        
        # Test 1: Demo user login
        if not await self.test_demo_user_login():
            print("❌ Cannot proceed without demo user login")
            return False
        
        # Test 2: Generate test recipe
        if not await self.test_recipe_generation():
            print("❌ Cannot proceed without test recipe")
            return False
        
        # Test 3: Main cart options endpoint
        success, cart_data = await self.test_cart_options_endpoint()
        if not success:
            print("❌ Main endpoint test failed")
            return False
        
        # Test 4: Specific field requirements from review request
        await self.test_specific_field_requirements()
        
        # Test 5: Product authenticity
        await self.test_product_authenticity(cart_data)
        
        # Test 6: Response format consistency
        await self.test_response_format_consistency(cart_data)
        
        # Test 7: Edge cases
        await self.test_cart_options_invalid_recipe_id()
        await self.test_cart_options_invalid_user_id()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 WALMART INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
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
        
        # Print exact response format for review
        if cart_data:
            print("\n" + "=" * 60)
            print("🔍 EXACT RESPONSE FORMAT FOR REVIEW")
            print("=" * 60)
            print("Sample cart-options response structure:")
            print(json.dumps(self._get_response_sample(cart_data), indent=2))
        
        await self.client.aclose()
        return passed == total

    def _get_response_sample(self, cart_data: Dict) -> Dict:
        """Get a clean sample of the response for review"""
        if not cart_data or "ingredient_options" not in cart_data:
            return {}
        
        sample = {
            "ingredient_options": []
        }
        
        # Take first 2 ingredients as sample
        for ingredient_option in cart_data["ingredient_options"][:2]:
            ingredient_sample = {
                "ingredient_name": ingredient_option.get("ingredient_name", ""),
                "options": []
            }
            
            # Take first 2 products as sample
            for product in ingredient_option.get("options", [])[:2]:
                product_sample = {
                    "product_id": product.get("product_id", ""),
                    "name": product.get("name", ""),
                    "price": product.get("price", 0),
                    "image_url": product.get("image_url", ""),
                    "available": product.get("available", True)
                }
                ingredient_sample["options"].append(product_sample)
            
            sample["ingredient_options"].append(ingredient_sample)
        
        return sample

async def main():
    """Main test runner"""
    tester = WalmartIntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Walmart integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the results above.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())