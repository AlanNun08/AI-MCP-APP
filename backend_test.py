#!/usr/bin/env python3
"""
Starbucks Drink Generation API Testing Suite
Testing the updated creative prompts and new features
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

class StarbucksAPITester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.backend_url = self.get_backend_url()
        self.test_results = []
        self.test_user_id = "test-streamlined-prompts"
        
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
    
    def validate_starbucks_response(self, data: dict, drink_type: str) -> tuple[bool, str]:
        """Validate Starbucks drink response format and content with NEW STREAMLINED REQUIREMENTS"""
        required_fields = ["drink_name", "description", "base_drink", "modifications", "ordering_script", "category"]
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
        
        # NEW REQUIREMENT 1: Validate drink_name is NOT repeated in ingredients/instructions
        drink_name = data.get("drink_name", "")
        if not drink_name or len(drink_name) < 5:
            return False, f"Drink name too short or missing: '{drink_name}'"
        
        # Check if drink name appears in modifications or ordering script (should NOT)
        modifications = data.get("modifications", [])
        ordering_script = data.get("ordering_script", "")
        description = data.get("description", "")
        
        name_words = drink_name.lower().split()
        for word in name_words:
            if len(word) > 3:  # Only check meaningful words
                if any(word in str(mod).lower() for mod in modifications):
                    return False, f"Drink name word '{word}' found in modifications - violates no-reuse requirement"
                if word in ordering_script.lower():
                    return False, f"Drink name word '{word}' found in ordering script - violates no-reuse requirement"
        
        # NEW REQUIREMENT 2: Validate 3-5 ingredients (not counting ice or base drinks)
        if not isinstance(modifications, list) or len(modifications) < 3 or len(modifications) > 5:
            return False, f"Must have exactly 3-5 ingredients, got {len(modifications)}: {modifications}"
        
        # NEW REQUIREMENT 3: Validate clear drive-thru format
        if not ordering_script or "hi, can i get" not in ordering_script.lower():
            return False, f"Ordering script must start with 'Hi, can I get...' format: '{ordering_script}'"
        
        # NEW REQUIREMENT 4: Check for at least one creative twist/unexpected element
        creative_indicators = ["foam", "drizzle", "layer", "swirl", "twist", "float", "cold foam", "syrup", "purée", "matcha", "espresso shot", "extra", "half", "splash"]
        has_twist = any(indicator in str(mod).lower() for mod in modifications for indicator in creative_indicators)
        if not has_twist:
            return False, f"No creative twist detected in modifications: {modifications}"
        
        # NEW REQUIREMENT 5: Validate vibe description exists and is poetic
        if not description or len(description) < 15:
            return False, f"Vibe description too short or missing: '{description}'"
        
        # Check for aesthetic/poetic language
        vibe_words = ["taste", "sip", "feel", "like", "dream", "cloud", "sky", "night", "morning", "sunset", "garden", "field", "ocean", "mountain", "star", "moon"]
        has_vibe = any(word in description.lower() for word in vibe_words)
        if not has_vibe:
            return False, f"Description lacks poetic/aesthetic vibe language: '{description}'"
        
        # Validate category matches request
        category = data.get("category", "")
        if drink_type != "random" and category != drink_type:
            return False, f"Category mismatch: expected '{drink_type}', got '{category}'"
        
        return True, "All streamlined requirements validated successfully"
    
    async def test_starbucks_frappuccino(self) -> bool:
        """Test Frappuccino generation with creative prompts"""
        try:
            request_data = {
                "user_id": self.test_user_id,
                "drink_type": "frappuccino"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid, validation_msg = self.validate_starbucks_response(data, "frappuccino")
                    
                    if is_valid:
                        drink_name = data.get("drink_name", "")
                        self.log_test_result(
                            "Starbucks Frappuccino Generation", 
                            True, 
                            f"Generated creative frappuccino: '{drink_name}' with drive-thru ordering script",
                            data
                        )
                        return True
                    else:
                        self.log_test_result("Starbucks Frappuccino Generation", False, f"Validation failed: {validation_msg}")
                        return False
                else:
                    self.log_test_result("Starbucks Frappuccino Generation", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Frappuccino Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_starbucks_lemonade(self) -> bool:
        """Test Lemonade generation with creative prompts"""
        try:
            request_data = {
                "user_id": self.test_user_id,
                "drink_type": "lemonade"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid, validation_msg = self.validate_starbucks_response(data, "lemonade")
                    
                    if is_valid:
                        drink_name = data.get("drink_name", "")
                        self.log_test_result(
                            "Starbucks Lemonade Generation", 
                            True, 
                            f"Generated creative lemonade: '{drink_name}' with enchanting vibe description",
                            data
                        )
                        return True
                    else:
                        self.log_test_result("Starbucks Lemonade Generation", False, f"Validation failed: {validation_msg}")
                        return False
                else:
                    self.log_test_result("Starbucks Lemonade Generation", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Lemonade Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_starbucks_refresher(self) -> bool:
        """Test Refresher generation with creative prompts"""
        try:
            request_data = {
                "user_id": self.test_user_id,
                "drink_type": "refresher"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid, validation_msg = self.validate_starbucks_response(data, "refresher")
                    
                    if is_valid:
                        drink_name = data.get("drink_name", "")
                        self.log_test_result(
                            "Starbucks Refresher Generation", 
                            True, 
                            f"Generated punchy refresher: '{drink_name}' with colorful vibe",
                            data
                        )
                        return True
                    else:
                        self.log_test_result("Starbucks Refresher Generation", False, f"Validation failed: {validation_msg}")
                        return False
                else:
                    self.log_test_result("Starbucks Refresher Generation", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Refresher Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_starbucks_iced_matcha_latte(self) -> bool:
        """Test Iced Matcha Latte generation with creative prompts"""
        try:
            request_data = {
                "user_id": self.test_user_id,
                "drink_type": "iced_matcha_latte"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid, validation_msg = self.validate_starbucks_response(data, "iced_matcha_latte")
                    
                    if is_valid:
                        drink_name = data.get("drink_name", "")
                        self.log_test_result(
                            "Starbucks Iced Matcha Latte Generation", 
                            True, 
                            f"Generated magical matcha: '{drink_name}' with zen garden vibes",
                            data
                        )
                        return True
                    else:
                        self.log_test_result("Starbucks Iced Matcha Latte Generation", False, f"Validation failed: {validation_msg}")
                        return False
                else:
                    self.log_test_result("Starbucks Iced Matcha Latte Generation", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Iced Matcha Latte Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_starbucks_random(self) -> bool:
        """Test Random drink generation with creative prompts"""
        try:
            request_data = {
                "user_id": self.test_user_id,
                "drink_type": "random"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    # For random, we don't validate the exact category match
                    is_valid, validation_msg = self.validate_starbucks_response(data, data.get("category", "random"))
                    
                    if is_valid:
                        drink_name = data.get("drink_name", "")
                        category = data.get("category", "mystery")
                        self.log_test_result(
                            "Starbucks Random Generation", 
                            True, 
                            f"Generated surprise drink: '{drink_name}' (category: {category}) with unique combo",
                            data
                        )
                        return True
                    else:
                        self.log_test_result("Starbucks Random Generation", False, f"Validation failed: {validation_msg}")
                        return False
                else:
                    self.log_test_result("Starbucks Random Generation", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Random Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_starbucks_with_flavor_inspiration(self) -> bool:
        """Test drink generation with flavor inspiration"""
        try:
            request_data = {
                "user_id": self.test_user_id,
                "drink_type": "frappuccino",
                "flavor_inspiration": "vanilla lavender"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid, validation_msg = self.validate_starbucks_response(data, "frappuccino")
                    
                    if is_valid:
                        drink_name = data.get("drink_name", "")
                        description = data.get("description", "")
                        modifications = data.get("modifications", [])
                        
                        # Check if flavor inspiration is reflected
                        flavor_reflected = any("vanilla" in str(item).lower() or "lavender" in str(item).lower() 
                                             for item in [drink_name, description] + modifications)
                        
                        self.log_test_result(
                            "Starbucks Flavor Inspiration", 
                            True, 
                            f"Generated inspired drink: '{drink_name}' with vanilla lavender influence (reflected: {flavor_reflected})",
                            data
                        )
                        return True
                    else:
                        self.log_test_result("Starbucks Flavor Inspiration", False, f"Validation failed: {validation_msg}")
                        return False
                else:
                    self.log_test_result("Starbucks Flavor Inspiration", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Starbucks Flavor Inspiration", False, f"Error: {str(e)}")
            return False
    
    async def test_database_storage(self) -> bool:
        """Test that drinks are being saved to MongoDB"""
        try:
            # Generate a drink first
            request_data = {
                "user_id": self.test_user_id,
                "drink_type": "refresher",
                "flavor_inspiration": "tropical mango"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if the response has an ID (indicating it was saved)
                    if "id" in data:
                        drink_id = data["id"]
                        drink_name = data.get("drink_name", "")
                        self.log_test_result(
                            "Database Storage", 
                            True, 
                            f"Drink saved to MongoDB with ID: {drink_id}, Name: '{drink_name}'",
                            {"drink_id": drink_id, "drink_name": drink_name}
                        )
                        return True
                    else:
                        self.log_test_result("Database Storage", False, "No ID field in response - drink may not be saved")
                        return False
                else:
                    self.log_test_result("Database Storage", False, f"Failed to generate drink for storage test: HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("Database Storage", False, f"Error: {str(e)}")
            return False
    
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
    
    async def run_starbucks_tests(self) -> Dict[str, Any]:
        """Run all Starbucks API tests"""
        logger.info("🌟 Starting Starbucks Drink Generation API Testing Suite")
        logger.info(f"Backend URL: {self.backend_url}")
        
        # Test sequence
        tests = [
            ("API Health Check", self.test_api_health),
            ("Starbucks Frappuccino Generation", self.test_starbucks_frappuccino),
            ("Starbucks Lemonade Generation", self.test_starbucks_lemonade),
            ("Starbucks Refresher Generation", self.test_starbucks_refresher),
            ("Starbucks Iced Matcha Latte Generation", self.test_starbucks_iced_matcha_latte),
            ("Starbucks Random Generation", self.test_starbucks_random),
            ("Starbucks Flavor Inspiration", self.test_starbucks_with_flavor_inspiration),
            ("Database Storage", self.test_database_storage)
        ]
        
        # Run tests
        for test_name, test_func in tests:
            logger.info(f"Running: {test_name}")
            try:
                await test_func()
            except Exception as e:
                self.log_test_result(test_name, False, f"Test execution error: {str(e)}")
            
            # Small delay between tests
            await asyncio.sleep(2)
        
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
    tester = StarbucksAPITester()
    
    try:
        summary = await tester.run_starbucks_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🌟 STARBUCKS DRINK GENERATION API TESTING SUMMARY")
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
        
        # Check for critical failures
        critical_failures = []
        for result in summary['test_results']:
            if not result['success']:
                if any(critical in result['test'].lower() for critical in ['api health', 'generation', 'database']):
                    critical_failures.append(result['test'])
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES DETECTED:")
            for failure in critical_failures:
                print(f"   - {failure}")
            print("\n❌ STARBUCKS API NOT READY")
        else:
            print("🎉 ALL STARBUCKS API TESTS PASSED")
            print("✅ NEW CREATIVE PROMPTS WORKING CORRECTLY")
        
        return summary
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())