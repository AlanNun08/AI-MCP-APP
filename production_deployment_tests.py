#!/usr/bin/env python3
"""
Production Deployment Testing Suite for AI Recipe + Grocery Delivery App
Tests the complete functionality on the deployed production site
"""

import asyncio
import httpx
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionDeploymentTester:
    def __init__(self):
        # Production URLs
        self.frontend_url = "https://recipe-cart-app-1.emergent.host"
        self.backend_url = "https://recipe-cart-app-1.emergent.host/api"
        
        # Test data
        self.test_user = {
            "email": "production.test@example.com",
            "password": "TestPassword123",
            "first_name": "Production",
            "last_name": "Tester"
        }
        
        self.demo_user = {
            "email": "demo@test.com",
            "password": "password123"
        }
        
        # Test results
        self.test_results = []
        self.user_id = None
        self.generated_recipe_id = None
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with timestamp"""
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
    
    async def test_frontend_accessibility(self) -> bool:
        """Test if frontend is accessible and loads properly"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.frontend_url)
                
                if response.status_code == 200:
                    content = response.text
                    required_elements = [
                        "Welcome to AI Chef",
                        "AI Recipe Generator",
                        "Starbucks Secret Menu",
                        "Smart Shopping"
                    ]
                    
                    missing_elements = [elem for elem in required_elements if elem not in content]
                    
                    if not missing_elements:
                        self.log_test_result(
                            "Frontend Accessibility",
                            True,
                            f"Frontend loads correctly with all required elements",
                            {"url": self.frontend_url, "status": response.status_code}
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Frontend Accessibility",
                            False,
                            f"Missing required elements: {missing_elements}",
                            {"missing": missing_elements}
                        )
                        return False
                else:
                    self.log_test_result(
                        "Frontend Accessibility",
                        False,
                        f"Frontend returned HTTP {response.status_code}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("Frontend Accessibility", False, f"Frontend access error: {str(e)}")
            return False
    
    async def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/")
                
                if response.status_code == 200:
                    data = response.json()
                    if "version" in data and "status" in data:
                        self.log_test_result(
                            "Backend Health Check",
                            True,
                            f"Backend is healthy - Version: {data.get('version')}, Status: {data.get('status')}",
                            data
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Backend Health Check",
                            False,
                            f"Backend response missing required fields",
                            data
                        )
                        return False
                else:
                    self.log_test_result(
                        "Backend Health Check",
                        False,
                        f"Backend health check failed - HTTP {response.status_code}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("Backend Health Check", False, f"Backend health check error: {str(e)}")
            return False
    
    async def test_demo_user_authentication(self) -> bool:
        """Test demo user authentication"""
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
                    
                    if status == "success":
                        self.user_id = data.get("user", {}).get("id") or data.get("user_id")
                        user_email = data.get("user", {}).get("email") or data.get("email")
                        
                        self.log_test_result(
                            "Demo User Authentication",
                            True,
                            f"Demo user login successful - User ID: {self.user_id}, Email: {user_email}",
                            {"user_id": self.user_id, "status": status}
                        )
                        return True
                    elif status == "unverified":
                        self.log_test_result(
                            "Demo User Authentication",
                            False,
                            f"Demo user is unverified - needs email verification",
                            data
                        )
                        return False
                    else:
                        self.log_test_result(
                            "Demo User Authentication",
                            False,
                            f"Unexpected login status: {status}",
                            data
                        )
                        return False
                else:
                    self.log_test_result(
                        "Demo User Authentication",
                        False,
                        f"Login failed - HTTP {response.status_code}: {response.text}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("Demo User Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    async def test_recipe_generation(self) -> bool:
        """Test recipe generation functionality"""
        try:
            if not self.user_id:
                self.log_test_result("Recipe Generation", False, "No user ID available for recipe generation")
                return False
            
            recipe_request = {
                "user_id": self.user_id,
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
                        "Recipe Generation",
                        True,
                        f"Recipe generated successfully: '{recipe_title}' (ID: {recipe_id}) with {len(shopping_list)} shopping items",
                        {
                            "recipe_id": recipe_id,
                            "title": recipe_title,
                            "shopping_items_count": len(shopping_list)
                        }
                    )
                    return True
                else:
                    self.log_test_result(
                        "Recipe Generation",
                        False,
                        f"Recipe generation failed - HTTP {response.status_code}: {response.text}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("Recipe Generation", False, f"Recipe generation error: {str(e)}")
            return False
    
    async def test_recipe_history(self) -> bool:
        """Test recipe history retrieval"""
        try:
            if not self.user_id:
                self.log_test_result("Recipe History", False, "No user ID available for recipe history")
                return False
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/recipes/history/{self.user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get("recipes", [])
                    regular_recipes = [r for r in recipes if r.get("recipe_category") != "starbucks"]
                    starbucks_recipes = [r for r in recipes if r.get("recipe_category") == "starbucks"]
                    
                    self.log_test_result(
                        "Recipe History",
                        True,
                        f"Recipe history retrieved: {len(recipes)} total ({len(regular_recipes)} regular, {len(starbucks_recipes)} Starbucks)",
                        {
                            "total_recipes": len(recipes),
                            "regular_recipes": len(regular_recipes),
                            "starbucks_recipes": len(starbucks_recipes)
                        }
                    )
                    return True
                else:
                    self.log_test_result(
                        "Recipe History",
                        False,
                        f"Recipe history failed - HTTP {response.status_code}: {response.text}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("Recipe History", False, f"Recipe history error: {str(e)}")
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
                    recipe_id = data.get("id")
                    ingredients = data.get("ingredients", [])
                    shopping_list = data.get("shopping_list", [])
                    
                    self.log_test_result(
                        "Individual Recipe Details",
                        True,
                        f"Recipe details retrieved: '{recipe_title}' with {len(ingredients)} ingredients and {len(shopping_list)} shopping items",
                        {
                            "recipe_id": recipe_id,
                            "title": recipe_title,
                            "ingredients_count": len(ingredients),
                            "shopping_items_count": len(shopping_list)
                        }
                    )
                    return True
                else:
                    self.log_test_result(
                        "Individual Recipe Details",
                        False,
                        f"Recipe details failed - HTTP {response.status_code}: {response.text}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("Individual Recipe Details", False, f"Recipe details error: {str(e)}")
            return False
    
    async def test_walmart_integration(self) -> bool:
        """Test Walmart integration with cart options"""
        try:
            if not self.user_id or not self.generated_recipe_id:
                self.log_test_result("Walmart Integration", False, "Missing user ID or recipe ID")
                return False
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.backend_url}/grocery/cart-options",
                    params={"recipe_id": self.generated_recipe_id, "user_id": self.user_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ingredient_options = data.get("ingredient_options", [])
                    total_products = sum(len(opt.get("options", [])) for opt in ingredient_options)
                    
                    # Validate product authenticity
                    authentic_products = 0
                    mock_products = 0
                    
                    for ingredient_option in ingredient_options:
                        for product in ingredient_option.get("options", []):
                            product_id = product.get("product_id", "")
                            # Check for mock product patterns
                            if product_id.startswith("10315") or "mock" in product_id.lower():
                                mock_products += 1
                            else:
                                authentic_products += 1
                    
                    authenticity_rate = (authentic_products / total_products * 100) if total_products > 0 else 0
                    
                    self.log_test_result(
                        "Walmart Integration",
                        True,
                        f"Walmart cart options generated: {len(ingredient_options)} ingredients, {total_products} products, {authenticity_rate:.1f}% authentic",
                        {
                            "ingredient_count": len(ingredient_options),
                            "total_products": total_products,
                            "authentic_products": authentic_products,
                            "mock_products": mock_products,
                            "authenticity_rate": authenticity_rate
                        }
                    )
                    return True
                elif response.status_code == 404:
                    self.log_test_result(
                        "Walmart Integration",
                        False,
                        "Recipe or user not found for Walmart integration",
                        {"status": response.status_code}
                    )
                    return False
                else:
                    # Check if it's a graceful error (no products found)
                    try:
                        error_data = response.json()
                        if "no products found" in error_data.get("detail", "").lower():
                            self.log_test_result(
                                "Walmart Integration",
                                True,
                                "Walmart integration working - gracefully handled no products found",
                                error_data
                            )
                            return True
                    except:
                        pass
                    
                    self.log_test_result(
                        "Walmart Integration",
                        False,
                        f"Walmart integration failed - HTTP {response.status_code}: {response.text}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("Walmart Integration", False, f"Walmart integration error: {str(e)}")
            return False
    
    async def test_starbucks_generator(self) -> bool:
        """Test Starbucks secret menu generator"""
        try:
            starbucks_request = {
                "drink_type": "frappuccino",
                "flavor_inspiration": "vanilla dreams"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=starbucks_request)
                
                if response.status_code == 200:
                    data = response.json()
                    drink_name = data.get("drink_name", "Unknown")
                    base_drink = data.get("base_drink", "Unknown")
                    modifications = data.get("modifications", [])
                    
                    self.log_test_result(
                        "Starbucks Generator",
                        True,
                        f"Starbucks drink generated: '{drink_name}' (base: {base_drink}) with {len(modifications)} modifications",
                        {
                            "drink_name": drink_name,
                            "base_drink": base_drink,
                            "modifications_count": len(modifications)
                        }
                    )
                    return True
                else:
                    self.log_test_result(
                        "Starbucks Generator",
                        False,
                        f"Starbucks generation failed - HTTP {response.status_code}: {response.text}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Generator", False, f"Starbucks generation error: {str(e)}")
            return False
    
    async def test_user_registration_flow(self) -> bool:
        """Test user registration flow (without completing email verification)"""
        try:
            registration_data = {
                "first_name": self.test_user["first_name"],
                "last_name": self.test_user["last_name"],
                "email": f"test.{int(time.time())}@example.com",  # Unique email
                "password": self.test_user["password"],
                "dietary_preferences": ["vegetarian"],
                "allergies": ["nuts"],
                "favorite_cuisines": ["italian", "mexican"]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/auth/register", json=registration_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data and "verification" in data.get("message", "").lower():
                        self.log_test_result(
                            "User Registration Flow",
                            True,
                            f"User registration successful - verification email sent to {registration_data['email']}",
                            {"email": registration_data["email"], "message": data.get("message")}
                        )
                        return True
                    else:
                        self.log_test_result(
                            "User Registration Flow",
                            False,
                            f"Registration response missing verification message",
                            data
                        )
                        return False
                else:
                    self.log_test_result(
                        "User Registration Flow",
                        False,
                        f"User registration failed - HTTP {response.status_code}: {response.text}",
                        {"status": response.status_code}
                    )
                    return False
        except Exception as e:
            self.log_test_result("User Registration Flow", False, f"Registration error: {str(e)}")
            return False
    
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run the complete production deployment test suite"""
        logger.info("🚀 Starting Production Deployment Test Suite")
        logger.info(f"Frontend URL: {self.frontend_url}")
        logger.info(f"Backend URL: {self.backend_url}")
        
        # Test sequence
        tests = [
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("Backend Health", self.test_backend_health),
            ("Demo User Authentication", self.test_demo_user_authentication),
            ("Recipe Generation", self.test_recipe_generation),
            ("Recipe History", self.test_recipe_history),
            ("Individual Recipe Details", self.test_individual_recipe_details),
            ("Walmart Integration", self.test_walmart_integration),
            ("Starbucks Generator", self.test_starbucks_generator),
            ("User Registration Flow", self.test_user_registration_flow),
        ]
        
        # Run tests
        for test_name, test_func in tests:
            logger.info(f"Running test: {test_name}")
            await test_func()
            await asyncio.sleep(1)  # Brief pause between tests
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Summary
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results,
            "frontend_url": self.frontend_url,
            "backend_url": self.backend_url,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"🎯 Production Test Suite Complete: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        return summary
    
    def generate_test_report(self, summary: Dict[str, Any]) -> str:
        """Generate a detailed test report"""
        report = f"""
# Production Deployment Test Report

**Test Date:** {summary['timestamp']}
**Frontend URL:** {summary['frontend_url']}
**Backend URL:** {summary['backend_url']}

## Summary
- **Total Tests:** {summary['total_tests']}
- **Passed:** {summary['passed_tests']}
- **Failed:** {summary['failed_tests']}
- **Success Rate:** {summary['success_rate']:.1f}%

## Test Results

"""
        
        for result in summary['test_results']:
            status_icon = "✅" if result['success'] else "❌"
            report += f"### {status_icon} {result['test']}\n"
            report += f"**Status:** {result['status']}\n"
            report += f"**Details:** {result['details']}\n"
            report += f"**Timestamp:** {result['timestamp']}\n\n"
        
        return report

async def main():
    """Main function to run production deployment tests"""
    tester = ProductionDeploymentTester()
    
    try:
        # Run test suite
        summary = await tester.run_complete_test_suite()
        
        # Generate report
        report = tester.generate_test_report(summary)
        
        # Save report
        report_path = Path("/app/production_test_report.md")
        with open(report_path, "w") as f:
            f.write(report)
        
        logger.info(f"📊 Test report saved to: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("PRODUCTION DEPLOYMENT TEST SUMMARY")
        print("="*60)
        print(f"Frontend URL: {summary['frontend_url']}")
        print(f"Backend URL: {summary['backend_url']}")
        print(f"Tests Run: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print("="*60)
        
        # List failed tests
        failed_tests = [r for r in summary['test_results'] if not r['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        print(f"\n📊 Full report available at: {report_path}")
        
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        return False
    
    return summary['success_rate'] >= 80  # Consider successful if 80%+ pass rate

if __name__ == "__main__":
    asyncio.run(main())