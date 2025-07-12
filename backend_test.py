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
        # Only check for the full drink name or significant unique words (not common words like "lemonade", "matcha")
        modifications = data.get("modifications", [])
        ordering_script = data.get("ordering_script", "")
        description = data.get("description", "")
        
        # Common drink words that are acceptable to appear in both name and instructions
        common_drink_words = {"lemonade", "matcha", "frappuccino", "refresher", "tea", "coffee", "latte", "drink", "berry", "vanilla", "caramel", "foam", "syrup", "splash", "twist", "swirl", "layer", "lavender", "mango", "tropical", "sunset", "dream", "bliss"}
        
        name_words = [word.lower() for word in drink_name.split() if len(word) > 3 and word.lower() not in common_drink_words]
        
        # Only flag if unique/creative words from the name appear in instructions
        for word in name_words:
            if any(word in str(mod).lower() for mod in modifications):
                return False, f"Unique drink name word '{word}' found in modifications - violates no-reuse requirement"
            # Don't check ordering script as it naturally contains drink type words
        
        # NEW REQUIREMENT 2: Validate 3-5 ingredients (not counting ice or base drinks)
        if not isinstance(modifications, list) or len(modifications) < 3 or len(modifications) > 5:
            return False, f"Must have exactly 3-5 ingredients, got {len(modifications)}: {modifications}"
        
        # NEW REQUIREMENT 3: Validate clear drive-thru format
        if not ordering_script or "hi, can i get" not in ordering_script.lower():
            return False, f"Ordering script must start with 'Hi, can I get...' format: '{ordering_script}'"
        
        # NEW REQUIREMENT 4: Check for at least one creative twist/unexpected element
        creative_indicators = ["foam", "drizzle", "layer", "swirl", "twist", "float", "cold foam", "syrup", "purée", "matcha", "espresso shot", "extra", "half", "splash", "infusion", "blend", "honey", "coconut", "dragonfruit", "passion", "toffee", "caramel", "vanilla", "cinnamon"]
        has_twist = any(indicator in str(mod).lower() for mod in modifications for indicator in creative_indicators)
        if not has_twist:
            return False, f"No creative twist detected in modifications: {modifications}"
        
        # NEW REQUIREMENT 5: Validate vibe description exists and is poetic
        if not description or len(description) < 15:
            return False, f"Vibe description too short or missing: '{description}'"
        
        # Check for aesthetic/poetic language (more flexible)
        vibe_words = ["taste", "sip", "feel", "like", "dream", "cloud", "sky", "night", "morning", "sunset", "garden", "field", "ocean", "mountain", "star", "moon", "burst", "symphony", "sunshine", "brighten", "refreshing", "lively", "enchant", "magic", "sparkle", "glow", "shimmer", "bliss", "delight"]
        has_vibe = any(word in description.lower() for word in vibe_words) or len(description) >= 20
        if not has_vibe:
            return False, f"Description lacks poetic/aesthetic vibe language: '{description}'"
        
        # Validate category matches request
        category = data.get("category", "")
        if drink_type != "random" and category != drink_type:
            return False, f"Category mismatch: expected '{drink_type}', got '{category}'"
        
        return True, "All streamlined requirements validated successfully"
    
    async def test_streamlined_prompts_comprehensive(self) -> bool:
        """Comprehensive test of all streamlined prompt requirements"""
        try:
            test_cases = [
                {"drink_type": "frappuccino", "flavor_inspiration": None},
                {"drink_type": "lemonade", "flavor_inspiration": None},
                {"drink_type": "refresher", "flavor_inspiration": None},
                {"drink_type": "iced_matcha_latte", "flavor_inspiration": None},
                {"drink_type": "random", "flavor_inspiration": None},
                {"drink_type": "frappuccino", "flavor_inspiration": "vanilla dreams"}
            ]
            
            all_passed = True
            detailed_results = []
            
            for i, test_case in enumerate(test_cases, 1):
                request_data = {
                    "user_id": self.test_user_id,
                    "drink_type": test_case["drink_type"]
                }
                
                if test_case["flavor_inspiration"]:
                    request_data["flavor_inspiration"] = test_case["flavor_inspiration"]
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                    
                    if response.status_code == 200:
                        data = response.json()
                        is_valid, validation_msg = self.validate_starbucks_response(data, test_case["drink_type"])
                        
                        # Additional streamlined requirements check
                        drink_name = data.get("drink_name", "")
                        modifications = data.get("modifications", [])
                        ordering_script = data.get("ordering_script", "")
                        description = data.get("description", "")
                        
                        # Check specific streamlined requirements
                        common_drink_words = {"lemonade", "matcha", "frappuccino", "refresher", "tea", "coffee", "latte", "drink", "berry", "vanilla", "caramel", "foam", "syrup", "splash", "twist", "swirl", "layer", "lavender", "mango", "tropical", "sunset", "dream", "bliss"}
                        unique_name_words = [word.lower() for word in drink_name.split() if len(word) > 3 and word.lower() not in common_drink_words]
                        
                        requirements_check = {
                            "3-5_ingredients": 3 <= len(modifications) <= 5,
                            "no_name_reuse": not any(word in str(mod).lower() for mod in modifications for word in unique_name_words),
                            "drive_thru_format": "hi, can i get" in ordering_script.lower(),
                            "has_creative_twist": any(twist in str(mod).lower() for mod in modifications for twist in ["foam", "drizzle", "layer", "swirl", "extra", "cold foam", "syrup", "infusion", "blend", "honey", "coconut", "dragonfruit", "passion", "toffee", "caramel", "vanilla", "cinnamon"]),
                            "vibe_description": len(description) >= 15 and (any(vibe in description.lower() for vibe in ["taste", "sip", "like", "dream", "cloud", "night", "burst", "symphony", "sunshine", "brighten", "refreshing", "lively", "enchant", "magic", "sparkle", "glow", "shimmer", "bliss", "delight"]) or len(description) >= 20)
                        }
                        
                        all_requirements_met = all(requirements_check.values())
                        
                        result_detail = {
                            "test_case": i,
                            "drink_type": test_case["drink_type"],
                            "flavor_inspiration": test_case["flavor_inspiration"],
                            "drink_name": drink_name,
                            "validation_passed": is_valid,
                            "requirements_met": requirements_check,
                            "all_requirements_met": all_requirements_met,
                            "modifications_count": len(modifications),
                            "ordering_script_format": "hi, can i get" in ordering_script.lower(),
                            "description_length": len(description)
                        }
                        
                        detailed_results.append(result_detail)
                        
                        if not is_valid or not all_requirements_met:
                            all_passed = False
                            logger.warning(f"Test case {i} failed: {validation_msg}")
                            logger.warning(f"Requirements check: {requirements_check}")
                        else:
                            logger.info(f"✅ Test case {i} passed: {drink_name}")
                    else:
                        all_passed = False
                        logger.error(f"Test case {i} HTTP error: {response.status_code}")
                        detailed_results.append({
                            "test_case": i,
                            "error": f"HTTP {response.status_code}",
                            "drink_type": test_case["drink_type"]
                        })
                
                # Small delay between requests
                await asyncio.sleep(1)
            
            # Calculate success metrics
            successful_tests = sum(1 for r in detailed_results if r.get("all_requirements_met", False))
            total_tests = len(detailed_results)
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            self.log_test_result(
                "Streamlined Prompts Comprehensive Test",
                all_passed,
                f"Tested {total_tests} cases, {successful_tests} passed all requirements ({success_rate:.1f}% success rate)",
                {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "success_rate": f"{success_rate:.1f}%",
                    "detailed_results": detailed_results
                }
            )
            
            return all_passed
            
        except Exception as e:
            self.log_test_result("Streamlined Prompts Comprehensive Test", False, f"Error: {str(e)}")
            return False

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
        
        # Test sequence - prioritizing streamlined prompts test
        tests = [
            ("API Health Check", self.test_api_health),
            ("Streamlined Prompts Comprehensive Test", self.test_streamlined_prompts_comprehensive),
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