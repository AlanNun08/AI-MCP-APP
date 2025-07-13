#!/usr/bin/env python3
"""
CRITICAL WALMART INTEGRATION TESTING SUITE
Testing the Walmart relevance filtering fix as requested in review
Focus: Verify that Walmart products are now being accepted and returned
"""

import asyncio
import httpx
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionDeploymentTester:
    def __init__(self):
        # Production URL from frontend .env
        self.production_url = "https://recipe-cart-app-1.emergent.host/api"
        self.localhost_url = "http://localhost:8001/api"
        self.test_results = []
        
        # Demo user credentials from review request
        self.demo_user = {
            "email": "demo@test.com",
            "password": "password123"
        }
        
        # Test user for comprehensive testing
        self.test_user = {
            "email": "production_test_2024@example.com",
            "password": "TestProd123!",
            "first_name": "Production",
            "last_name": "Tester"
        }
        
        self.demo_user_id = None
        self.test_user_id = None
        
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
    
    async def test_production_backend_health(self) -> bool:
        """Test production backend health and version"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.production_url}/")
                
                if response.status_code == 200:
                    data = response.json()
                    version = data.get('version', 'unknown')
                    status = data.get('status', 'unknown')
                    self.log_test_result(
                        "Production Backend Health", 
                        True, 
                        f"Production API responding - Version: {version}, Status: {status}"
                    )
                    return True
                else:
                    self.log_test_result("Production Backend Health", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Production Backend Health", False, f"Connection error: {str(e)}")
            return False
    
    async def test_demo_user_authentication_production(self) -> bool:
        """Test demo user authentication on production (critical issue from review)"""
        try:
            login_data = {
                "email": self.demo_user["email"],
                "password": self.demo_user["password"]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.production_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    user_id = data.get("user_id") or data.get("user", {}).get("id")
                    
                    if status == "success":
                        self.demo_user_id = user_id
                        self.log_test_result(
                            "Demo User Authentication (Production)", 
                            True, 
                            f"Demo user login successful - Status: {status}, User ID: {user_id}"
                        )
                        return True
                    elif status == "unverified":
                        self.log_test_result(
                            "Demo User Authentication (Production)", 
                            False, 
                            f"Demo user returns 'unverified' status (CRITICAL ISSUE) - Expected 'success'"
                        )
                        return False
                    else:
                        self.log_test_result(
                            "Demo User Authentication (Production)", 
                            False, 
                            f"Unexpected status: {status}"
                        )
                        return False
                else:
                    self.log_test_result("Demo User Authentication (Production)", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Demo User Authentication (Production)", False, f"Authentication error: {str(e)}")
            return False
    
    async def test_demo_user_authentication_localhost(self) -> bool:
        """Test demo user authentication on localhost for comparison"""
        try:
            login_data = {
                "email": self.demo_user["email"],
                "password": self.demo_user["password"]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.localhost_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    user_id = data.get("user_id") or data.get("user", {}).get("id")
                    
                    self.log_test_result(
                        "Demo User Authentication (Localhost)", 
                        True, 
                        f"Localhost login - Status: {status}, User ID: {user_id}"
                    )
                    return True
                else:
                    self.log_test_result("Demo User Authentication (Localhost)", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Demo User Authentication (Localhost)", False, f"Localhost authentication error: {str(e)}")
            return False
    
    async def test_starbucks_generator_production(self) -> bool:
        """Test Starbucks generator on production (missing user_id field issue)"""
        try:
            if not self.demo_user_id:
                # Try to get demo user ID first
                await self.test_demo_user_authentication_production()
                if not self.demo_user_id:
                    self.log_test_result("Starbucks Generator (Production)", False, "No demo user ID available")
                    return False
            
            starbucks_request = {
                "user_id": self.demo_user_id,
                "drink_type": "frappuccino",
                "flavor_inspiration": "vanilla caramel"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.production_url}/generate-starbucks-drink", json=starbucks_request)
                
                if response.status_code == 200:
                    data = response.json()
                    drink_name = data.get("drink_name", "Unknown")
                    category = data.get("category", "Unknown")
                    self.log_test_result(
                        "Starbucks Generator (Production)", 
                        True, 
                        f"Starbucks drink generated: '{drink_name}' ({category})"
                    )
                    return True
                else:
                    self.log_test_result("Starbucks Generator (Production)", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Generator (Production)", False, f"Starbucks generation error: {str(e)}")
            return False
    
    async def test_recipe_generation_production(self) -> bool:
        """Test recipe generation on production"""
        try:
            if not self.demo_user_id:
                self.log_test_result("Recipe Generation (Production)", False, "No demo user ID available")
                return False
            
            recipe_request = {
                "user_id": self.demo_user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "italian",
                "servings": 4,
                "difficulty": "medium"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.production_url}/recipes/generate", json=recipe_request)
                
                if response.status_code == 200:
                    data = response.json()
                    recipe_title = data.get("title", "Unknown")
                    shopping_list = data.get("shopping_list", [])
                    recipe_id = data.get("id")
                    self.log_test_result(
                        "Recipe Generation (Production)", 
                        True, 
                        f"Recipe generated: '{recipe_title}' with {len(shopping_list)} shopping items, ID: {recipe_id}"
                    )
                    return True
                else:
                    self.log_test_result("Recipe Generation (Production)", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Recipe Generation (Production)", False, f"Recipe generation error: {str(e)}")
            return False
    
    async def test_walmart_integration_production(self) -> bool:
        """Test complete Walmart integration workflow on production"""
        try:
            if not self.demo_user_id:
                self.log_test_result("Walmart Integration (Production)", False, "No demo user ID available")
                return False
            
            # First generate a recipe
            recipe_request = {
                "user_id": self.demo_user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "mexican",
                "servings": 4,
                "difficulty": "easy"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Generate recipe
                recipe_response = await client.post(f"{self.production_url}/recipes/generate", json=recipe_request)
                
                if recipe_response.status_code != 200:
                    self.log_test_result("Walmart Integration (Production)", False, "Failed to generate recipe for Walmart test")
                    return False
                
                recipe_data = recipe_response.json()
                recipe_id = recipe_data.get("id")
                
                if not recipe_id:
                    self.log_test_result("Walmart Integration (Production)", False, "No recipe ID returned")
                    return False
                
                # Test cart options endpoint
                cart_options_response = await client.post(f"{self.production_url}/grocery/cart-options?recipe_id={recipe_id}&user_id={self.demo_user_id}")
                
                if cart_options_response.status_code == 200:
                    cart_data = cart_options_response.json()
                    ingredient_options = cart_data.get("ingredient_options", [])
                    
                    if ingredient_options:
                        total_products = sum(len(ing.get("options", [])) for ing in ingredient_options)
                        
                        # Check for authentic Walmart products
                        authentic_count = 0
                        mock_count = 0
                        
                        for ingredient in ingredient_options:
                            for option in ingredient.get("options", []):
                                product_id = option.get("product_id", "")
                                if "10315" in product_id:
                                    mock_count += 1
                                else:
                                    authentic_count += 1
                        
                        authenticity_rate = (authentic_count / total_products * 100) if total_products > 0 else 0
                        
                        self.log_test_result(
                            "Walmart Integration (Production)", 
                            True, 
                            f"Walmart integration working: {len(ingredient_options)} ingredients, {total_products} products, {authenticity_rate:.1f}% authentic"
                        )
                        return True
                    else:
                        self.log_test_result("Walmart Integration (Production)", False, "No ingredient options returned")
                        return False
                else:
                    self.log_test_result("Walmart Integration (Production)", False, f"Cart options HTTP {cart_options_response.status_code}: {cart_options_response.text}")
                    return False
                    
        except Exception as e:
            self.log_test_result("Walmart Integration (Production)", False, f"Walmart integration error: {str(e)}")
            return False
    
    async def test_recipe_history_production(self) -> bool:
        """Test recipe history on production"""
        try:
            if not self.demo_user_id:
                self.log_test_result("Recipe History (Production)", False, "No demo user ID available")
                return False
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.production_url}/recipes/history/{self.demo_user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get("recipes", [])
                    regular_recipes = [r for r in recipes if r.get("category") != "starbucks"]
                    starbucks_recipes = [r for r in recipes if r.get("category") == "starbucks"]
                    
                    self.log_test_result(
                        "Recipe History (Production)", 
                        True, 
                        f"Recipe history retrieved: {len(recipes)} total ({len(regular_recipes)} regular, {len(starbucks_recipes)} Starbucks)"
                    )
                    return True
                else:
                    self.log_test_result("Recipe History (Production)", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Recipe History (Production)", False, f"Recipe history error: {str(e)}")
            return False
    
    async def test_individual_recipe_endpoint_production(self) -> bool:
        """Test individual recipe details endpoint on production"""
        try:
            if not self.demo_user_id:
                self.log_test_result("Individual Recipe Endpoint (Production)", False, "No demo user ID available")
                return False
            
            # First get recipe history to find a recipe ID
            async with httpx.AsyncClient(timeout=30.0) as client:
                history_response = await client.get(f"{self.production_url}/recipes/history/{self.demo_user_id}")
                
                if history_response.status_code != 200:
                    self.log_test_result("Individual Recipe Endpoint (Production)", False, "Failed to get recipe history")
                    return False
                
                history_data = history_response.json()
                recipes = history_data.get("recipes", [])
                regular_recipes = [r for r in recipes if r.get("category") != "starbucks"]
                
                if not regular_recipes:
                    self.log_test_result("Individual Recipe Endpoint (Production)", False, "No regular recipes found in history")
                    return False
                
                recipe_id = regular_recipes[0].get("id")
                if not recipe_id:
                    self.log_test_result("Individual Recipe Endpoint (Production)", False, "No recipe ID found")
                    return False
                
                # Test individual recipe endpoint
                recipe_response = await client.get(f"{self.production_url}/recipes/{recipe_id}")
                
                if recipe_response.status_code == 200:
                    recipe_data = recipe_response.json()
                    recipe_title = recipe_data.get("title", "Unknown")
                    ingredients = recipe_data.get("ingredients", [])
                    shopping_list = recipe_data.get("shopping_list", [])
                    
                    self.log_test_result(
                        "Individual Recipe Endpoint (Production)", 
                        True, 
                        f"Recipe details retrieved: '{recipe_title}' with {len(ingredients)} ingredients, {len(shopping_list)} shopping items"
                    )
                    return True
                else:
                    self.log_test_result("Individual Recipe Endpoint (Production)", False, f"HTTP {recipe_response.status_code}: {recipe_response.text}")
                    return False
                    
        except Exception as e:
            self.log_test_result("Individual Recipe Endpoint (Production)", False, f"Individual recipe endpoint error: {str(e)}")
            return False
    
    async def test_complete_walmart_workflow_production(self) -> bool:
        """Test the complete Walmart integration workflow end-to-end on production"""
        try:
            if not self.demo_user_id:
                self.log_test_result("Complete Walmart Workflow (Production)", False, "No demo user ID available")
                return False
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Step 1: Generate Recipe
                recipe_request = {
                    "user_id": self.demo_user_id,
                    "recipe_category": "cuisine",
                    "cuisine_type": "italian",
                    "servings": 4,
                    "difficulty": "medium"
                }
                
                recipe_response = await client.post(f"{self.production_url}/recipes/generate", json=recipe_request)
                if recipe_response.status_code != 200:
                    self.log_test_result("Complete Walmart Workflow (Production)", False, "Step 1 failed: Recipe generation")
                    return False
                
                recipe_data = recipe_response.json()
                recipe_id = recipe_data.get("id")
                recipe_title = recipe_data.get("title", "Unknown")
                
                # Step 2: Recipe History
                history_response = await client.get(f"{self.production_url}/recipes/history/{self.demo_user_id}")
                if history_response.status_code != 200:
                    self.log_test_result("Complete Walmart Workflow (Production)", False, "Step 2 failed: Recipe history")
                    return False
                
                # Step 3: Individual Recipe Details
                recipe_details_response = await client.get(f"{self.production_url}/recipes/{recipe_id}")
                if recipe_details_response.status_code != 200:
                    self.log_test_result("Complete Walmart Workflow (Production)", False, "Step 3 failed: Individual recipe details")
                    return False
                
                # Step 4: Walmart Cart Options
                cart_options_response = await client.post(f"{self.production_url}/grocery/cart-options?recipe_id={recipe_id}&user_id={self.demo_user_id}")
                if cart_options_response.status_code != 200:
                    self.log_test_result("Complete Walmart Workflow (Production)", False, "Step 4 failed: Walmart cart options")
                    return False
                
                cart_data = cart_options_response.json()
                ingredient_options = cart_data.get("ingredient_options", [])
                
                if not ingredient_options:
                    self.log_test_result("Complete Walmart Workflow (Production)", False, "Step 4 failed: No ingredient options")
                    return False
                
                # Step 5: Affiliate URL Generation (simulate product selection)
                selected_products = []
                for ingredient in ingredient_options[:3]:  # Select first 3 ingredients
                    options = ingredient.get("options", [])
                    if options:
                        selected_products.append({
                            "ingredient_name": ingredient.get("ingredient_name"),
                            "product_id": options[0].get("product_id"),
                            "name": options[0].get("name"),
                            "price": options[0].get("price", 0),
                            "quantity": 1
                        })
                
                if selected_products:
                    cart_request = {
                        "user_id": self.demo_user_id,
                        "recipe_id": recipe_id,
                        "products": selected_products
                    }
                    
                    cart_response = await client.post(f"{self.production_url}/grocery/create-cart", json=cart_request)
                    
                    if cart_response.status_code == 200:
                        cart_result = cart_response.json()
                        walmart_url = cart_result.get("walmart_url", "")
                        total_price = cart_result.get("total_price", 0)
                        
                        self.log_test_result(
                            "Complete Walmart Workflow (Production)", 
                            True, 
                            f"Complete workflow successful: Recipe '{recipe_title}' → {len(ingredient_options)} ingredients → {len(selected_products)} selected → Cart ${total_price:.2f}"
                        )
                        return True
                    else:
                        self.log_test_result("Complete Walmart Workflow (Production)", False, f"Step 5 failed: Cart creation HTTP {cart_response.status_code}")
                        return False
                else:
                    self.log_test_result("Complete Walmart Workflow (Production)", False, "Step 5 failed: No products to select")
                    return False
                    
        except Exception as e:
            self.log_test_result("Complete Walmart Workflow (Production)", False, f"Complete workflow error: {str(e)}")
            return False
    
    async def test_production_vs_localhost_comparison(self) -> bool:
        """Compare production vs localhost behavior"""
        try:
            # Test both endpoints
            production_health = await self.test_production_backend_health()
            
            # Test localhost health
            localhost_healthy = False
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{self.localhost_url}/")
                    localhost_healthy = response.status_code == 200
            except:
                localhost_healthy = False
            
            if production_health and localhost_healthy:
                self.log_test_result(
                    "Production vs Localhost Comparison", 
                    True, 
                    "Both production and localhost are responding"
                )
            elif production_health and not localhost_healthy:
                self.log_test_result(
                    "Production vs Localhost Comparison", 
                    True, 
                    "Production healthy, localhost not accessible (expected in production environment)"
                )
            elif not production_health and localhost_healthy:
                self.log_test_result(
                    "Production vs Localhost Comparison", 
                    False, 
                    "Production not responding but localhost is (routing issue)"
                )
            else:
                self.log_test_result(
                    "Production vs Localhost Comparison", 
                    False, 
                    "Neither production nor localhost responding"
                )
            
            return production_health
            
        except Exception as e:
            self.log_test_result("Production vs Localhost Comparison", False, f"Comparison error: {str(e)}")
            return False
    
    async def run_production_deployment_tests(self) -> Dict[str, Any]:
        """Run all production deployment tests"""
        logger.info("🚀 Starting Production Deployment Testing Suite")
        logger.info(f"Production URL: {self.production_url}")
        logger.info(f"Testing critical issues from review request")
        
        # Test sequence focusing on critical issues
        tests = [
            ("Production Backend Health", self.test_production_backend_health),
            ("Production vs Localhost Comparison", self.test_production_vs_localhost_comparison),
            ("Demo User Authentication (Production)", self.test_demo_user_authentication_production),
            ("Demo User Authentication (Localhost)", self.test_demo_user_authentication_localhost),
            ("Starbucks Generator (Production)", self.test_starbucks_generator_production),
            ("Recipe Generation (Production)", self.test_recipe_generation_production),
            ("Recipe History (Production)", self.test_recipe_history_production),
            ("Individual Recipe Endpoint (Production)", self.test_individual_recipe_endpoint_production),
            ("Walmart Integration (Production)", self.test_walmart_integration_production),
            ("Complete Walmart Workflow (Production)", self.test_complete_walmart_workflow_production)
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
            "production_url": self.production_url,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary

async def main():
    """Main test execution"""
    tester = ProductionDeploymentTester()
    
    try:
        summary = await tester.run_production_deployment_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 PRODUCTION DEPLOYMENT TESTING SUMMARY")
        print("="*80)
        print(f"Production URL: {summary['production_url']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Test Completed: {summary['timestamp']}")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in summary['test_results']:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['test']}: {result['details']}")
        
        print("\n" + "="*80)
        
        # Analyze critical issues from review request
        critical_issues = []
        demo_auth_issue = False
        walmart_issue = False
        
        for result in summary['test_results']:
            if not result['success']:
                if "Demo User Authentication (Production)" in result['test']:
                    demo_auth_issue = True
                    critical_issues.append("Demo user authentication returns 'unverified' on production")
                elif "Walmart Integration" in result['test']:
                    walmart_issue = True
                    critical_issues.append("Walmart integration not working on production")
                elif "Starbucks Generator" in result['test']:
                    critical_issues.append("Starbucks generator missing user_id field requirement")
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES FROM REVIEW REQUEST:")
            for issue in critical_issues:
                print(f"   - {issue}")
            
            if demo_auth_issue:
                print("\n🔍 ROUTING ISSUE DETECTED:")
                print("   Production domain appears to route to different backend than localhost")
                print("   Demo user works on localhost but fails on production")
            
            print("\n❌ PRODUCTION DEPLOYMENT HAS CRITICAL ISSUES")
        else:
            print("🎉 ALL CRITICAL ISSUES FROM REVIEW REQUEST RESOLVED")
            print("✅ PRODUCTION DEPLOYMENT READY")
        
        return summary
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())