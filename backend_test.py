#!/usr/bin/env python3
"""
Critical Issue Testing for Demo User Authentication and Walmart Integration
Testing the specific issues reported in the review request
"""

import asyncio
import httpx
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CriticalIssueTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.backend_url = self.get_backend_url()
        self.test_results = []
        
        # Demo user credentials from review request
        self.demo_user = {
            "email": "demo@test.com",
            "password": "password123"
        }
        
        self.demo_user_id = None
        self.generated_recipe_id = None
        
    def get_backend_url(self) -> str:
        """Get backend URL from frontend .env file"""
        try:
            frontend_env_path = "/app/frontend/.env"
            if os.path.exists(frontend_env_path):
                with open(frontend_env_path, 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            url = line.split('=', 1)[1].strip()
                            return f"{url}/api"
            
            # Fallback to localhost
            return "http://localhost:8001/api"
        except Exception as e:
            logger.warning(f"Could not read frontend .env: {e}, using localhost")
            return "http://localhost:8001/api"
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        logger.info(f"{status} - {test_name}: {details}")
    
    async def test_demo_user_authentication(self) -> bool:
        """Test demo user authentication - CRITICAL ISSUE"""
        try:
            login_data = {
                "email": self.demo_user["email"],
                "password": self.demo_user["password"]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    user_id = data.get("user_id")
                    email = data.get("email")
                    
                    if status == "success":
                        self.demo_user_id = user_id
                        self.log_test_result(
                            "Demo User Authentication", 
                            True, 
                            f"✅ LOGIN SUCCESS - Status: {status}, User ID: {user_id}, Email: {email}",
                            data
                        )
                        return True
                    elif status == "unverified":
                        self.log_test_result(
                            "Demo User Authentication", 
                            False, 
                            f"❌ CRITICAL ISSUE: Demo user returning 'unverified' status despite being verified in database. Status: {status}, User ID: {user_id}, Email: {email}",
                            data
                        )
                        return False
                    else:
                        self.log_test_result(
                            "Demo User Authentication", 
                            False, 
                            f"❌ Unexpected status: {status}",
                            data
                        )
                        return False
                else:
                    self.log_test_result("Demo User Authentication", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Demo User Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    async def test_demo_user_database_verification(self) -> bool:
        """Check demo user in database via debug endpoint"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/debug/user/{self.demo_user['email']}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data:
                        user = data["user"]
                        is_verified = user.get("is_verified", False)
                        user_id = user.get("id")
                        email = user.get("email")
                        
                        self.log_test_result(
                            "Demo User Database Check", 
                            True, 
                            f"Database record found - ID: {user_id}, Email: {email}, Verified: {is_verified}",
                            user
                        )
                        return True
                    else:
                        self.log_test_result("Demo User Database Check", False, f"User not found in database: {data}")
                        return False
                else:
                    self.log_test_result("Demo User Database Check", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Demo User Database Check", False, f"Database check error: {str(e)}")
            return False
    
    async def test_regular_recipe_generation(self) -> bool:
        """Generate a regular recipe (not Starbucks) for Walmart integration"""
        try:
            if not self.demo_user_id:
                self.log_test_result("Regular Recipe Generation", False, "No demo user ID available")
                return False
            
            recipe_request = {
                "user_id": self.demo_user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "italian",
                "servings": 4,
                "difficulty": "medium"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                
                if response.status_code == 200:
                    data = response.json()
                    recipe_title = data.get("title", "Unknown")
                    recipe_id = data.get("id")
                    shopping_list = data.get("shopping_list", [])
                    
                    self.generated_recipe_id = recipe_id
                    
                    self.log_test_result(
                        "Regular Recipe Generation", 
                        True, 
                        f"Regular recipe generated: '{recipe_title}' (ID: {recipe_id}) with {len(shopping_list)} shopping items",
                        {"recipe_id": recipe_id, "title": recipe_title, "shopping_items": len(shopping_list)}
                    )
                    return True
                else:
                    self.log_test_result("Regular Recipe Generation", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Regular Recipe Generation", False, f"Recipe generation error: {str(e)}")
            return False
    
    async def test_recipe_history_retrieval(self) -> bool:
        """Test recipe history retrieval"""
        try:
            if not self.demo_user_id:
                self.log_test_result("Recipe History Retrieval", False, "No demo user ID available")
                return False
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/recipes/history?user_id={self.demo_user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get("recipes", [])
                    regular_recipes = [r for r in recipes if r.get("recipe_category") != "starbucks"]
                    
                    self.log_test_result(
                        "Recipe History Retrieval", 
                        True, 
                        f"Recipe history retrieved: {len(recipes)} total recipes, {len(regular_recipes)} regular recipes available for Walmart integration",
                        {"total_recipes": len(recipes), "regular_recipes": len(regular_recipes)}
                    )
                    return True
                else:
                    self.log_test_result("Recipe History Retrieval", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Recipe History Retrieval", False, f"Recipe history error: {str(e)}")
            return False
    
    async def test_individual_recipe_details(self) -> bool:
        """Test individual recipe details endpoint"""
        try:
            if not self.generated_recipe_id:
                self.log_test_result("Individual Recipe Details", False, "No recipe ID available")
                return False
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/recipes/{self.generated_recipe_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipe_title = data.get("title", "Unknown")
                    ingredients = data.get("ingredients", [])
                    shopping_list = data.get("shopping_list", [])
                    
                    self.log_test_result(
                        "Individual Recipe Details", 
                        True, 
                        f"Recipe details retrieved: '{recipe_title}' with {len(ingredients)} ingredients and {len(shopping_list)} shopping items",
                        {"recipe_id": self.generated_recipe_id, "title": recipe_title, "ingredients_count": len(ingredients)}
                    )
                    return True
                else:
                    self.log_test_result("Individual Recipe Details", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Individual Recipe Details", False, f"Recipe details error: {str(e)}")
            return False
    
    async def test_walmart_cart_options(self) -> bool:
        """Test Walmart cart options generation - CRITICAL ISSUE"""
        try:
            if not self.generated_recipe_id or not self.demo_user_id:
                self.log_test_result("Walmart Cart Options", False, "No recipe ID or user ID available")
                return False
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={self.generated_recipe_id}&user_id={self.demo_user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    ingredient_options = data.get("ingredient_options", [])
                    
                    if ingredient_options:
                        total_products = 0
                        authentic_products = 0
                        
                        for ingredient in ingredient_options:
                            ingredient_name = ingredient.get("ingredient_name", "Unknown")
                            options = ingredient.get("options", [])
                            total_products += len(options)
                            
                            # Check for authentic Walmart products
                            for product in options:
                                product_id = product.get("product_id", "")
                                product_name = product.get("name", "")
                                price = product.get("price", 0)
                                
                                # Authentic products should have real IDs, names, and prices
                                if product_id and product_name and price > 0:
                                    authentic_products += 1
                        
                        authenticity_rate = (authentic_products / total_products * 100) if total_products > 0 else 0
                        
                        self.log_test_result(
                            "Walmart Cart Options", 
                            True, 
                            f"✅ Walmart integration working: {len(ingredient_options)} ingredients, {total_products} products, {authenticity_rate:.1f}% authenticity rate",
                            {
                                "ingredients_count": len(ingredient_options),
                                "total_products": total_products,
                                "authentic_products": authentic_products,
                                "authenticity_rate": f"{authenticity_rate:.1f}%"
                            }
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Walmart Cart Options", 
                            False, 
                            "❌ CRITICAL ISSUE: No ingredient options returned - Walmart integration not showing products",
                            data
                        )
                        return False
                else:
                    self.log_test_result("Walmart Cart Options", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Walmart Cart Options", False, f"Walmart integration error: {str(e)}")
            return False
    
    async def test_walmart_product_authenticity(self) -> bool:
        """Verify that Walmart products are authentic with real IDs and prices"""
        try:
            if not self.generated_recipe_id or not self.demo_user_id:
                self.log_test_result("Walmart Product Authenticity", False, "No recipe ID or user ID available")
                return False
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={self.generated_recipe_id}&user_id={self.demo_user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    ingredient_options = data.get("ingredient_options", [])
                    
                    authentic_products = []
                    mock_products = []
                    
                    for ingredient in ingredient_options:
                        for product in ingredient.get("options", []):
                            product_id = product.get("product_id", "")
                            product_name = product.get("name", "")
                            price = product.get("price", 0)
                            
                            # Check for mock data patterns
                            if "10315" in product_id or price == 0 or not product_name:
                                mock_products.append(product)
                            else:
                                authentic_products.append(product)
                    
                    total_products = len(authentic_products) + len(mock_products)
                    authenticity_rate = (len(authentic_products) / total_products * 100) if total_products > 0 else 0
                    
                    if len(mock_products) == 0:
                        self.log_test_result(
                            "Walmart Product Authenticity", 
                            True, 
                            f"✅ ALL PRODUCTS AUTHENTIC: {len(authentic_products)} authentic products, 0 mock products ({authenticity_rate:.1f}% authenticity)",
                            {
                                "authentic_products": len(authentic_products),
                                "mock_products": len(mock_products),
                                "authenticity_rate": f"{authenticity_rate:.1f}%"
                            }
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Walmart Product Authenticity", 
                            False, 
                            f"❌ MOCK DATA DETECTED: {len(authentic_products)} authentic, {len(mock_products)} mock products ({authenticity_rate:.1f}% authenticity)",
                            {
                                "authentic_products": len(authentic_products),
                                "mock_products": len(mock_products),
                                "authenticity_rate": f"{authenticity_rate:.1f}%"
                            }
                        )
                        return False
                else:
                    self.log_test_result("Walmart Product Authenticity", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Walmart Product Authenticity", False, f"Product authenticity check error: {str(e)}")
            return False
    
    async def run_critical_tests(self) -> Dict[str, Any]:
        """Run all critical issue tests"""
        logger.info("🚨 Starting Critical Issue Testing for Demo User and Walmart Integration")
        logger.info(f"Backend URL: {self.backend_url}")
        logger.info(f"Demo User: {self.demo_user['email']}")
        
        # Test sequence focusing on critical issues
        tests = [
            ("Demo User Database Check", self.test_demo_user_database_verification),
            ("Demo User Authentication", self.test_demo_user_authentication),
            ("Regular Recipe Generation", self.test_regular_recipe_generation),
            ("Recipe History Retrieval", self.test_recipe_history_retrieval),
            ("Individual Recipe Details", self.test_individual_recipe_details),
            ("Walmart Cart Options", self.test_walmart_cart_options),
            ("Walmart Product Authenticity", self.test_walmart_product_authenticity)
        ]
        
        # Run tests
        for test_name, test_func in tests:
            logger.info(f"Running: {test_name}")
            try:
                await test_func()
            except Exception as e:
                self.log_test_result(test_name, False, f"Test execution error: {str(e)}")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": f"{success_rate:.1f}%",
            "backend_url": self.backend_url,
            "demo_user": self.demo_user["email"],
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary

async def main():
    """Main test execution"""
    tester = CriticalIssueTester()
    
    try:
        summary = await tester.run_critical_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🚨 CRITICAL ISSUE TESTING SUMMARY")
        print("="*80)
        print(f"Backend URL: {summary['backend_url']}")
        print(f"Demo User: {summary['demo_user']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Test Completed: {summary['timestamp']}")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        critical_issues = []
        for result in summary['test_results']:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['test']}: {result['details']}")
            
            if not result['success']:
                critical_issues.append(result['test'])
        
        print("\n" + "="*80)
        
        # Determine overall status
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   - {issue}")
            print("\n❌ CRITICAL ISSUES NEED IMMEDIATE ATTENTION")
        else:
            print("🎉 ALL CRITICAL TESTS PASSED")
            print("✅ DEMO USER AND WALMART INTEGRATION WORKING")
        
        return summary
        
    except Exception as e:
        logger.error(f"Critical test execution failed: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())