#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for AI Recipe & Grocery App
Testing all critical features for production readiness
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

class BackendTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.backend_url = self.get_backend_url()
        self.test_results = []
        self.test_user_data = {
            "email": "test_comprehensive_2024@example.com",
            "password": "TestPass123!",
            "first_name": "Comprehensive",
            "last_name": "Tester"
        }
        self.user_id = None
        self.verification_code = None
        
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
    
    async def test_api_health(self) -> bool:
        """Test basic API connectivity"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        "API Health Check", 
                        True, 
                        f"API responding - Version: {data.get('version', 'unknown')}, Status: {data.get('status', 'unknown')}"
                    )
                    return True
                else:
                    self.log_test_result("API Health Check", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    async def test_user_registration(self) -> bool:
        """Test user registration system"""
        try:
            # Clean up any existing test user first
            await self.cleanup_test_user()
            
            registration_data = {
                "first_name": self.test_user_data["first_name"],
                "last_name": self.test_user_data["last_name"],
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"],
                "dietary_preferences": ["vegetarian"],
                "allergies": ["nuts"],
                "favorite_cuisines": ["italian", "mexican"]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/auth/register", json=registration_data)
                
                if response.status_code == 200:
                    data = response.json()
                    self.user_id = data.get("user_id")
                    self.log_test_result(
                        "User Registration", 
                        True, 
                        f"User registered successfully - ID: {self.user_id}"
                    )
                    return True
                else:
                    self.log_test_result("User Registration", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("User Registration", False, f"Registration error: {str(e)}")
            return False
    
    async def test_email_verification_code_generation(self) -> bool:
        """Test verification code generation and retrieval"""
        try:
            if not self.user_id:
                self.log_test_result("Email Verification Code", False, "No user ID available")
                return False
            
            # Get verification code from debug endpoint
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/debug/verification-codes/{self.test_user_data['email']}")
                
                if response.status_code == 200:
                    data = response.json()
                    codes = data.get("codes", [])
                    if codes:
                        self.verification_code = codes[0]["code"]
                        self.log_test_result(
                            "Email Verification Code", 
                            True, 
                            f"Verification code retrieved: {self.verification_code}"
                        )
                        return True
                    else:
                        self.log_test_result("Email Verification Code", False, "No verification codes found")
                        return False
                else:
                    self.log_test_result("Email Verification Code", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Email Verification Code", False, f"Code retrieval error: {str(e)}")
            return False
    
    async def test_email_verification(self) -> bool:
        """Test email verification process"""
        try:
            if not self.verification_code:
                self.log_test_result("Email Verification", False, "No verification code available")
                return False
            
            verify_data = {
                "email": self.test_user_data["email"],
                "code": self.verification_code
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/auth/verify", json=verify_data)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        "Email Verification", 
                        True, 
                        f"Email verified successfully - User: {data.get('user', {}).get('first_name', 'Unknown')}"
                    )
                    return True
                else:
                    self.log_test_result("Email Verification", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Email Verification", False, f"Verification error: {str(e)}")
            return False
    
    async def test_user_login(self) -> bool:
        """Test user login system"""
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        self.log_test_result(
                            "User Login", 
                            True, 
                            f"Login successful - User: {data.get('user', {}).get('first_name', 'Unknown')}"
                        )
                        return True
                    else:
                        self.log_test_result("User Login", False, f"Login failed: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    self.log_test_result("User Login", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("User Login", False, f"Login error: {str(e)}")
            return False
    
    async def test_password_reset_flow(self) -> bool:
        """Test password reset functionality"""
        try:
            # Request password reset
            reset_request = {"email": self.test_user_data["email"]}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/auth/forgot-password", json=reset_request)
                
                if response.status_code == 200:
                    self.log_test_result(
                        "Password Reset Request", 
                        True, 
                        "Password reset email sent successfully"
                    )
                    return True
                else:
                    self.log_test_result("Password Reset Request", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Password Reset Request", False, f"Password reset error: {str(e)}")
            return False
    
    async def test_recipe_generation_cuisine(self) -> bool:
        """Test cuisine recipe generation"""
        try:
            if not self.user_id:
                self.log_test_result("Recipe Generation - Cuisine", False, "No user ID available")
                return False
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "italian",
                "servings": 4,
                "difficulty": "medium",
                "is_healthy": True,
                "max_calories_per_serving": 400
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                
                if response.status_code == 200:
                    data = response.json()
                    recipe_title = data.get("title", "Unknown")
                    shopping_list = data.get("shopping_list", [])
                    self.log_test_result(
                        "Recipe Generation - Cuisine", 
                        True, 
                        f"Italian recipe generated: '{recipe_title}' with {len(shopping_list)} shopping items"
                    )
                    return True
                else:
                    self.log_test_result("Recipe Generation - Cuisine", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Recipe Generation - Cuisine", False, f"Recipe generation error: {str(e)}")
            return False
    
    async def test_recipe_generation_beverage(self) -> bool:
        """Test beverage recipe generation"""
        try:
            if not self.user_id:
                self.log_test_result("Recipe Generation - Beverage", False, "No user ID available")
                return False
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "beverage",
                "cuisine_type": "coffee",
                "servings": 2,
                "difficulty": "easy"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                
                if response.status_code == 200:
                    data = response.json()
                    recipe_title = data.get("title", "Unknown")
                    shopping_list = data.get("shopping_list", [])
                    self.log_test_result(
                        "Recipe Generation - Beverage", 
                        True, 
                        f"Coffee beverage generated: '{recipe_title}' with {len(shopping_list)} shopping items"
                    )
                    return True
                else:
                    self.log_test_result("Recipe Generation - Beverage", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Recipe Generation - Beverage", False, f"Beverage generation error: {str(e)}")
            return False
    
    async def test_recipe_generation_snack(self) -> bool:
        """Test snack recipe generation"""
        try:
            if not self.user_id:
                self.log_test_result("Recipe Generation - Snack", False, "No user ID available")
                return False
            
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "snack",
                "cuisine_type": "acai bowls",
                "servings": 2,
                "difficulty": "easy",
                "is_healthy": True,
                "max_calories_per_serving": 300
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                
                if response.status_code == 200:
                    data = response.json()
                    recipe_title = data.get("title", "Unknown")
                    shopping_list = data.get("shopping_list", [])
                    self.log_test_result(
                        "Recipe Generation - Snack", 
                        True, 
                        f"Acai bowl snack generated: '{recipe_title}' with {len(shopping_list)} shopping items"
                    )
                    return True
                else:
                    self.log_test_result("Recipe Generation - Snack", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Recipe Generation - Snack", False, f"Snack generation error: {str(e)}")
            return False
    
    async def test_starbucks_drink_generation(self) -> bool:
        """Test Starbucks secret menu drink generation"""
        try:
            if not self.user_id:
                self.log_test_result("Starbucks Drink Generation", False, "No user ID available")
                return False
            
            starbucks_request = {
                "user_id": self.user_id,
                "drink_type": "frappuccino",
                "flavor_inspiration": "vanilla caramel"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=starbucks_request)
                
                if response.status_code == 200:
                    data = response.json()
                    drink_name = data.get("drink_name", "Unknown")
                    category = data.get("category", "Unknown")
                    self.log_test_result(
                        "Starbucks Drink Generation", 
                        True, 
                        f"Starbucks drink generated: '{drink_name}' ({category})"
                    )
                    return True
                else:
                    self.log_test_result("Starbucks Drink Generation", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Drink Generation", False, f"Starbucks generation error: {str(e)}")
            return False
    
    async def test_walmart_integration(self) -> bool:
        """Test Walmart product search and cart generation"""
        try:
            if not self.user_id:
                self.log_test_result("Walmart Integration", False, "No user ID available")
                return False
            
            # First generate a recipe to get ingredients
            recipe_request = {
                "user_id": self.user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "mexican",
                "servings": 4,
                "difficulty": "easy"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Generate recipe
                recipe_response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                
                if recipe_response.status_code != 200:
                    self.log_test_result("Walmart Integration", False, "Failed to generate recipe for Walmart test")
                    return False
                
                recipe_data = recipe_response.json()
                recipe_id = recipe_data.get("id")
                
                if not recipe_id:
                    self.log_test_result("Walmart Integration", False, "No recipe ID returned")
                    return False
                
                # Test cart options endpoint (POST with query parameters)
                cart_options_response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={recipe_id}&user_id={self.user_id}")
                
                if cart_options_response.status_code == 200:
                    cart_data = cart_options_response.json()
                    ingredient_options = cart_data.get("ingredient_options", [])
                    
                    if ingredient_options:
                        total_products = sum(len(ing.get("options", [])) for ing in ingredient_options)
                        self.log_test_result(
                            "Walmart Integration", 
                            True, 
                            f"Walmart cart options generated: {len(ingredient_options)} ingredients, {total_products} total products"
                        )
                        return True
                    else:
                        self.log_test_result("Walmart Integration", False, "No ingredient options returned")
                        return False
                else:
                    self.log_test_result("Walmart Integration", False, f"Cart options HTTP {cart_options_response.status_code}: {cart_options_response.text}")
                    return False
                    
        except Exception as e:
            self.log_test_result("Walmart Integration", False, f"Walmart integration error: {str(e)}")
            return False
    
    async def test_recipe_history(self) -> bool:
        """Test recipe history retrieval"""
        try:
            if not self.user_id:
                self.log_test_result("Recipe History", False, "No user ID available")
                return False
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/recipes/history?user_id={self.user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get("recipes", [])
                    self.log_test_result(
                        "Recipe History", 
                        True, 
                        f"Recipe history retrieved: {len(recipes)} recipes found"
                    )
                    return True
                else:
                    self.log_test_result("Recipe History", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Recipe History", False, f"Recipe history error: {str(e)}")
            return False
    
    async def cleanup_test_user(self):
        """Clean up test user data"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Try to clean up test data
                await client.delete(f"{self.backend_url}/debug/cleanup-test-data")
        except Exception:
            pass  # Ignore cleanup errors
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend tests"""
        logger.info("🚀 Starting Comprehensive Backend Testing Suite")
        logger.info(f"Backend URL: {self.backend_url}")
        
        # Test sequence
        tests = [
            ("API Health Check", self.test_api_health),
            ("User Registration", self.test_user_registration),
            ("Email Verification Code Generation", self.test_email_verification_code_generation),
            ("Email Verification", self.test_email_verification),
            ("User Login", self.test_user_login),
            ("Password Reset Flow", self.test_password_reset_flow),
            ("Recipe Generation - Cuisine", self.test_recipe_generation_cuisine),
            ("Recipe Generation - Beverage", self.test_recipe_generation_beverage),
            ("Recipe Generation - Snack", self.test_recipe_generation_snack),
            ("Starbucks Drink Generation", self.test_starbucks_drink_generation),
            ("Walmart Integration", self.test_walmart_integration),
            ("Recipe History", self.test_recipe_history)
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
        
        # Cleanup
        await self.cleanup_test_user()
        
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
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary

async def main():
    """Main test execution"""
    tester = BackendTester()
    
    try:
        summary = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print("="*80)
        print(f"Backend URL: {summary['backend_url']}")
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
        
        # Determine overall status
        critical_failures = []
        for result in summary['test_results']:
            if not result['success']:
                if any(critical in result['test'].lower() for critical in ['api health', 'registration', 'login', 'recipe generation']):
                    critical_failures.append(result['test'])
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES DETECTED:")
            for failure in critical_failures:
                print(f"   - {failure}")
            print("\n❌ BACKEND NOT READY FOR PRODUCTION")
        else:
            print("🎉 ALL CRITICAL SYSTEMS OPERATIONAL")
            print("✅ BACKEND READY FOR PRODUCTION")
        
        return summary
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())