#!/usr/bin/env python3
"""
Additional Backend Tests for Specific Requirements
Testing case-insensitive email handling, beverage categories, and edge cases
"""

import asyncio
import httpx
import json
import logging
import os
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdditionalBackendTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.backend_url = self.get_backend_url()
        self.test_results = []
        
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
            return "http://localhost:8001/api"
        except Exception as e:
            logger.warning(f"Could not read frontend .env: {e}, using localhost")
            return "http://localhost:8001/api"
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        logger.info(f"{status} - {test_name}: {details}")
    
    async def test_case_insensitive_email(self) -> bool:
        """Test case-insensitive email handling"""
        try:
            # Clean up first
            await self.cleanup_test_data()
            
            # Register with lowercase email
            registration_data = {
                "first_name": "Case",
                "last_name": "Test",
                "email": "casetest@example.com",
                "password": "TestPass123!",
                "dietary_preferences": [],
                "allergies": [],
                "favorite_cuisines": []
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Register user
                response = await client.post(f"{self.backend_url}/auth/register", json=registration_data)
                
                if response.status_code != 200:
                    self.log_test_result("Case-Insensitive Email", False, f"Registration failed: {response.status_code}")
                    return False
                
                # Get verification code
                code_response = await client.get(f"{self.backend_url}/debug/verification-codes/casetest@example.com")
                if code_response.status_code != 200:
                    self.log_test_result("Case-Insensitive Email", False, "Could not get verification code")
                    return False
                
                code_data = code_response.json()
                verification_code = code_data.get("codes", [{}])[0].get("code")
                
                # Verify email
                verify_data = {"email": "casetest@example.com", "code": verification_code}
                verify_response = await client.post(f"{self.backend_url}/auth/verify", json=verify_data)
                
                if verify_response.status_code != 200:
                    self.log_test_result("Case-Insensitive Email", False, "Email verification failed")
                    return False
                
                # Test login with different case variations
                test_cases = [
                    "casetest@example.com",  # original
                    "CASETEST@EXAMPLE.COM",  # uppercase
                    "CaseTest@Example.Com",  # mixed case
                    "cAsEtEsT@eXaMpLe.CoM"   # random case
                ]
                
                for email_variant in test_cases:
                    login_data = {"email": email_variant, "password": "TestPass123!"}
                    login_response = await client.post(f"{self.backend_url}/auth/login", json=login_data)
                    
                    if login_response.status_code != 200:
                        self.log_test_result("Case-Insensitive Email", False, f"Login failed for {email_variant}")
                        return False
                    
                    login_result = login_response.json()
                    if login_result.get("status") != "success":
                        self.log_test_result("Case-Insensitive Email", False, f"Login not successful for {email_variant}")
                        return False
                
                self.log_test_result("Case-Insensitive Email", True, "All email case variations work correctly")
                return True
                
        except Exception as e:
            self.log_test_result("Case-Insensitive Email", False, f"Error: {str(e)}")
            return False
    
    async def test_beverage_categories(self) -> bool:
        """Test all beverage categories mentioned in requirements"""
        try:
            user_id = "beverage-test-user"
            
            beverage_types = [
                ("boba tea", "Boba Tea"),
                ("thai tea", "Thai Tea"),
                ("special lemonades", "Special Lemonade"),
                ("coffee", "Coffee")
            ]
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                for beverage_type, display_name in beverage_types:
                    recipe_request = {
                        "user_id": user_id,
                        "recipe_category": "beverage",
                        "cuisine_type": beverage_type,
                        "servings": 2,
                        "difficulty": "medium"
                    }
                    
                    response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                    
                    if response.status_code != 200:
                        self.log_test_result(f"Beverage - {display_name}", False, f"HTTP {response.status_code}")
                        continue
                    
                    data = response.json()
                    recipe_title = data.get("title", "Unknown")
                    shopping_list = data.get("shopping_list", [])
                    
                    if recipe_title and shopping_list:
                        self.log_test_result(f"Beverage - {display_name}", True, f"Generated '{recipe_title}' with {len(shopping_list)} ingredients")
                    else:
                        self.log_test_result(f"Beverage - {display_name}", False, "Missing title or shopping list")
                
                return True
                
        except Exception as e:
            self.log_test_result("Beverage Categories", False, f"Error: {str(e)}")
            return False
    
    async def test_starbucks_drink_types(self) -> bool:
        """Test all Starbucks drink types"""
        try:
            user_id = "starbucks-test-user"
            
            drink_types = [
                ("frappuccino", "Frappuccino"),
                ("refresher", "Refresher"),
                ("lemonade", "Lemonade"),
                ("iced_matcha_latte", "Iced Matcha Latte"),
                ("random", "Random")
            ]
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                for drink_type, display_name in drink_types:
                    starbucks_request = {
                        "user_id": user_id,
                        "drink_type": drink_type,
                        "flavor_inspiration": "tropical"
                    }
                    
                    response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=starbucks_request)
                    
                    if response.status_code != 200:
                        self.log_test_result(f"Starbucks - {display_name}", False, f"HTTP {response.status_code}")
                        continue
                    
                    data = response.json()
                    drink_name = data.get("drink_name", "Unknown")
                    ordering_script = data.get("ordering_script", "")
                    
                    if drink_name and ordering_script:
                        self.log_test_result(f"Starbucks - {display_name}", True, f"Generated '{drink_name}'")
                    else:
                        self.log_test_result(f"Starbucks - {display_name}", False, "Missing drink name or ordering script")
                
                return True
                
        except Exception as e:
            self.log_test_result("Starbucks Drink Types", False, f"Error: {str(e)}")
            return False
    
    async def test_database_connectivity(self) -> bool:
        """Test database operations"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test database clear (should work in non-production)
                response = await client.delete(f"{self.backend_url}/debug/clear-users")
                
                if response.status_code == 200:
                    data = response.json()
                    deleted_count = data.get("deleted", {})
                    self.log_test_result("Database Connectivity", True, f"Database operations working - cleared {sum(deleted_count.values())} documents")
                    return True
                else:
                    self.log_test_result("Database Connectivity", False, f"HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test_result("Database Connectivity", False, f"Error: {str(e)}")
            return False
    
    async def test_api_error_handling(self) -> bool:
        """Test API error handling"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test invalid endpoints
                invalid_tests = [
                    ("/auth/invalid-endpoint", "Invalid auth endpoint"),
                    ("/recipes/invalid", "Invalid recipe endpoint"),
                    ("/grocery/invalid", "Invalid grocery endpoint")
                ]
                
                for endpoint, description in invalid_tests:
                    response = await client.get(f"{self.backend_url}{endpoint}")
                    
                    # Should return 404 or 405, not 500
                    if response.status_code in [404, 405]:
                        continue
                    else:
                        self.log_test_result("API Error Handling", False, f"{description} returned {response.status_code}")
                        return False
                
                self.log_test_result("API Error Handling", True, "All invalid endpoints handled correctly")
                return True
                
        except Exception as e:
            self.log_test_result("API Error Handling", False, f"Error: {str(e)}")
            return False
    
    async def cleanup_test_data(self):
        """Clean up test data"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                await client.delete(f"{self.backend_url}/debug/cleanup-test-data")
        except Exception:
            pass  # Ignore cleanup errors
    
    async def run_additional_tests(self) -> Dict[str, Any]:
        """Run all additional tests"""
        logger.info("🚀 Starting Additional Backend Tests")
        logger.info(f"Backend URL: {self.backend_url}")
        
        # Test sequence
        tests = [
            ("Case-Insensitive Email Handling", self.test_case_insensitive_email),
            ("Beverage Categories", self.test_beverage_categories),
            ("Starbucks Drink Types", self.test_starbucks_drink_types),
            ("Database Connectivity", self.test_database_connectivity),
            ("API Error Handling", self.test_api_error_handling)
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
        await self.cleanup_test_data()
        
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
            "test_results": self.test_results
        }
        
        return summary

async def main():
    """Main test execution"""
    tester = AdditionalBackendTester()
    
    try:
        summary = await tester.run_additional_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🔍 ADDITIONAL BACKEND TESTING SUMMARY")
        print("="*80)
        print(f"Backend URL: {summary['backend_url']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in summary['test_results']:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['test']}: {result['details']}")
        
        print("\n" + "="*80)
        
        return summary
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())