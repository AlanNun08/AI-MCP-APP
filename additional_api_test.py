#!/usr/bin/env python3
"""
Additional API Testing Script for Recipe APIs
Tests recipe generation, recipe history, and individual recipe details APIs
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

class AdditionalAPITester:
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

    async def test_recipe_generation_api(self):
        """Test recipe generation API with different categories"""
        try:
            # Test cuisine recipe generation
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
                if "id" in data and "title" in data and "shopping_list" in data:
                    self.test_recipe_id = data["id"]
                    await self.log_result(
                        "Recipe Generation API - Cuisine", 
                        True, 
                        f"Generated cuisine recipe: {data.get('title', 'Unknown')}",
                        {
                            "recipe_id": self.test_recipe_id,
                            "title": data.get("title"),
                            "shopping_list_count": len(data.get("shopping_list", [])),
                            "cuisine_type": data.get("cuisine_type"),
                            "category": "cuisine"
                        }
                    )
                    
                    # Test snack recipe generation
                    snack_response = await self.client.post(f"{API_BASE}/recipes/generate", json={
                        "user_id": self.demo_user_id,
                        "recipe_category": "snack",
                        "dietary_preferences": ["healthy"],
                        "servings": 2,
                        "difficulty": "easy"
                    })
                    
                    if snack_response.status_code == 200:
                        snack_data = snack_response.json()
                        await self.log_result(
                            "Recipe Generation API - Snack", 
                            True, 
                            f"Generated snack recipe: {snack_data.get('title', 'Unknown')}",
                            {
                                "recipe_id": snack_data.get("id"),
                                "title": snack_data.get("title"),
                                "shopping_list_count": len(snack_data.get("shopping_list", [])),
                                "category": "snack"
                            }
                        )
                    else:
                        await self.log_result(
                            "Recipe Generation API - Snack", 
                            False, 
                            f"Snack recipe generation failed with status {snack_response.status_code}",
                            {"response": snack_response.text}
                        )
                    
                    # Test beverage recipe generation
                    beverage_response = await self.client.post(f"{API_BASE}/recipes/generate", json={
                        "user_id": self.demo_user_id,
                        "recipe_category": "beverage",
                        "servings": 1,
                        "difficulty": "easy"
                    })
                    
                    if beverage_response.status_code == 200:
                        beverage_data = beverage_response.json()
                        await self.log_result(
                            "Recipe Generation API - Beverage", 
                            True, 
                            f"Generated beverage recipe: {beverage_data.get('title', 'Unknown')}",
                            {
                                "recipe_id": beverage_data.get("id"),
                                "title": beverage_data.get("title"),
                                "shopping_list_count": len(beverage_data.get("shopping_list", [])),
                                "category": "beverage"
                            }
                        )
                    else:
                        await self.log_result(
                            "Recipe Generation API - Beverage", 
                            False, 
                            f"Beverage recipe generation failed with status {beverage_response.status_code}",
                            {"response": beverage_response.text}
                        )
                    
                    return True
                else:
                    await self.log_result(
                        "Recipe Generation API - Cuisine", 
                        False, 
                        "Recipe response missing required fields",
                        {"response": data}
                    )
                    return False
            else:
                await self.log_result(
                    "Recipe Generation API - Cuisine", 
                    False, 
                    f"Recipe generation failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Recipe Generation API", False, f"Exception: {str(e)}")
            return False

    async def test_recipe_history_api(self):
        """Test recipe history API"""
        try:
            response = await self.client.get(f"{API_BASE}/recipes/history/{self.demo_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "recipes" in data:
                    recipes = data["recipes"]
                    total_recipes = len(recipes)
                    
                    # Analyze recipe categories
                    categories = {}
                    for recipe in recipes:
                        category = recipe.get("category", "unknown")
                        categories[category] = categories.get(category, 0) + 1
                    
                    await self.log_result(
                        "Recipe History API", 
                        True, 
                        f"Retrieved {total_recipes} recipes from history",
                        {
                            "total_recipes": total_recipes,
                            "categories": categories,
                            "sample_recipes": [
                                {
                                    "id": recipe.get("id"),
                                    "title": recipe.get("title"),
                                    "category": recipe.get("category")
                                } for recipe in recipes[:3]
                            ]
                        }
                    )
                    return True
                else:
                    await self.log_result(
                        "Recipe History API", 
                        False, 
                        "Response missing 'recipes' field",
                        {"response": data}
                    )
                    return False
            else:
                await self.log_result(
                    "Recipe History API", 
                    False, 
                    f"Request failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Recipe History API", False, f"Exception: {str(e)}")
            return False

    async def test_individual_recipe_details_api(self):
        """Test individual recipe details API"""
        try:
            if not self.test_recipe_id:
                await self.log_result(
                    "Individual Recipe Details API", 
                    False, 
                    "No test recipe ID available"
                )
                return False
            
            response = await self.client.get(f"{API_BASE}/recipes/{self.test_recipe_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["id", "title", "description", "ingredients", "instructions"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    await self.log_result(
                        "Individual Recipe Details API", 
                        True, 
                        f"Successfully retrieved recipe details: {data.get('title', 'Unknown')}",
                        {
                            "recipe_id": data.get("id"),
                            "title": data.get("title"),
                            "ingredients_count": len(data.get("ingredients", [])),
                            "instructions_count": len(data.get("instructions", [])),
                            "has_shopping_list": "shopping_list" in data,
                            "shopping_list_count": len(data.get("shopping_list", [])),
                            "fields_present": list(data.keys())
                        }
                    )
                    return True
                else:
                    await self.log_result(
                        "Individual Recipe Details API", 
                        False, 
                        f"Response missing required fields: {missing_fields}",
                        {"response": data, "missing_fields": missing_fields}
                    )
                    return False
            else:
                await self.log_result(
                    "Individual Recipe Details API", 
                    False, 
                    f"Request failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Individual Recipe Details API", False, f"Exception: {str(e)}")
            return False

    async def test_starbucks_generation_api(self):
        """Test Starbucks drink generation API"""
        try:
            response = await self.client.post(f"{API_BASE}/generate-starbucks-drink", json={
                "user_id": self.demo_user_id,
                "drink_type": "frappuccino",
                "flavor_inspiration": "vanilla"
            })
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["drink_name", "description", "base_drink", "modifications", "ordering_script"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    await self.log_result(
                        "Starbucks Generation API", 
                        True, 
                        f"Generated Starbucks drink: {data.get('drink_name', 'Unknown')}",
                        {
                            "drink_name": data.get("drink_name"),
                            "base_drink": data.get("base_drink"),
                            "modifications_count": len(data.get("modifications", [])),
                            "category": data.get("category"),
                            "has_ordering_script": bool(data.get("ordering_script"))
                        }
                    )
                    return True
                else:
                    await self.log_result(
                        "Starbucks Generation API", 
                        False, 
                        f"Response missing required fields: {missing_fields}",
                        {"response": data, "missing_fields": missing_fields}
                    )
                    return False
            else:
                await self.log_result(
                    "Starbucks Generation API", 
                    False, 
                    f"Request failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Starbucks Generation API", False, f"Exception: {str(e)}")
            return False

    async def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            response = await self.client.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                await self.log_result(
                    "Health Endpoint", 
                    True, 
                    f"Health check passed: {data.get('status', 'unknown')}",
                    {"response": data}
                )
                return True
            else:
                await self.log_result(
                    "Health Endpoint", 
                    False, 
                    f"Health check failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            await self.log_result("Health Endpoint", False, f"Exception: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all additional API tests"""
        print("🎯 Starting Additional API Testing")
        print("=" * 60)
        
        # Test 1: Demo user login
        if not await self.test_demo_user_login():
            print("❌ Cannot proceed without demo user login")
            return False
        
        # Test 2: Health endpoint
        await self.test_health_endpoint()
        
        # Test 3: Recipe generation API
        await self.test_recipe_generation_api()
        
        # Test 4: Recipe history API
        await self.test_recipe_history_api()
        
        # Test 5: Individual recipe details API
        await self.test_individual_recipe_details_api()
        
        # Test 6: Starbucks generation API
        await self.test_starbucks_generation_api()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 ADDITIONAL API TEST SUMMARY")
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
        
        await self.client.aclose()
        return passed == total

async def main():
    """Main test runner"""
    tester = AdditionalAPITester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All additional API tests passed!")
    else:
        print("\n⚠️ Some additional API tests failed. Please review the results above.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())