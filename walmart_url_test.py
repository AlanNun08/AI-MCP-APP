#!/usr/bin/env python3
"""
Walmart URL Generation Testing Suite
Focused testing for the review request to ensure:
1. No problematic search URLs are generated
2. Only proper affiliate URLs are used
3. Error handling works correctly
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

class WalmartURLTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.backend_url = self.get_backend_url()
        self.test_results = []
        self.demo_user_id = "demo-user-walmart-test"
        self.demo_email = "demo@test.com"
        
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
    
    async def test_demo_user_login(self) -> bool:
        """Test login with demo user account"""
        try:
            login_data = {
                "email": self.demo_email,
                "password": "password123"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "success":
                        user_data = data.get("user", {})
                        self.demo_user_id = user_data.get("id", self.demo_user_id)
                        
                        self.log_test_result(
                            "Demo User Login", 
                            True, 
                            f"Successfully logged in demo user: {self.demo_email}",
                            {"user_id": self.demo_user_id}
                        )
                        return True
                    else:
                        self.log_test_result("Demo User Login", False, f"Login failed: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    self.log_test_result("Demo User Login", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Demo User Login", False, f"Error: {str(e)}")
            return False

    async def test_recipe_generation_for_walmart(self) -> bool:
        """Generate a recipe specifically for Walmart integration testing"""
        try:
            request_data = {
                "user_id": self.demo_user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "Italian",
                "dietary_preferences": ["vegetarian"],
                "prep_time_max": 30,
                "servings": 4,
                "difficulty": "medium"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/recipes/generate", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate recipe structure
                    required_fields = ["id", "title", "shopping_list"]
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_test_result("Recipe Generation for Walmart", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Store recipe ID for Walmart testing
                    self.test_recipe_id = data.get("id")
                    recipe_title = data.get("title", "")
                    shopping_list = data.get("shopping_list", [])
                    
                    self.log_test_result(
                        "Recipe Generation for Walmart", 
                        True, 
                        f"Generated recipe '{recipe_title}' with {len(shopping_list)} shopping items for Walmart testing",
                        {
                            "recipe_id": self.test_recipe_id,
                            "title": recipe_title,
                            "shopping_items": len(shopping_list)
                        }
                    )
                    return True
                else:
                    self.log_test_result("Recipe Generation for Walmart", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Recipe Generation for Walmart", False, f"Error: {str(e)}")
            return False

    async def test_walmart_cart_options_url_format(self) -> bool:
        """Test that Walmart cart options do NOT generate problematic search URLs"""
        try:
            if not hasattr(self, 'test_recipe_id') or not self.test_recipe_id:
                self.log_test_result("Walmart Cart Options URL Format", False, "No test recipe ID available")
                return False
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={self.test_recipe_id}&user_id={self.demo_user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check that response doesn't contain any search URLs
                    response_str = json.dumps(data)
                    
                    # Look for problematic search URL patterns
                    problematic_patterns = [
                        "https://www.walmart.com/search?q=",
                        "walmart.com/search",
                        "search?q=",
                        "+fresh+fruits+",
                        "+Lemon+juice"
                    ]
                    
                    found_problematic = []
                    for pattern in problematic_patterns:
                        if pattern in response_str:
                            found_problematic.append(pattern)
                    
                    if found_problematic:
                        self.log_test_result(
                            "Walmart Cart Options URL Format", 
                            False, 
                            f"Found problematic search URL patterns: {found_problematic}",
                            {"problematic_patterns": found_problematic}
                        )
                        return False
                    
                    # Validate that we get proper product structure instead
                    ingredient_options = data.get("ingredient_options", [])
                    if not ingredient_options:
                        self.log_test_result("Walmart Cart Options URL Format", False, "No ingredient options returned")
                        return False
                    
                    # Check that products have proper IDs and structure
                    total_products = 0
                    valid_products = 0
                    
                    for ingredient_option in ingredient_options:
                        options = ingredient_option.get("options", [])
                        for option in options:
                            total_products += 1
                            product_id = option.get("product_id", "")
                            product_name = option.get("name", "")
                            product_price = option.get("price", 0)
                            
                            # Validate product has proper structure (not search URL)
                            if product_id and product_name and isinstance(product_price, (int, float)) and product_price > 0:
                                valid_products += 1
                    
                    if valid_products == 0:
                        self.log_test_result("Walmart Cart Options URL Format", False, "No valid products with proper structure found")
                        return False
                    
                    self.log_test_result(
                        "Walmart Cart Options URL Format", 
                        True, 
                        f"✅ NO problematic search URLs found. Generated {total_products} valid products with proper structure",
                        {
                            "total_products": total_products,
                            "valid_products": valid_products,
                            "ingredient_count": len(ingredient_options)
                        }
                    )
                    return True
                else:
                    self.log_test_result("Walmart Cart Options URL Format", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_test_result("Walmart Cart Options URL Format", False, f"Error: {str(e)}")
            return False

    async def test_walmart_affiliate_url_format_only(self) -> bool:
        """Test that ONLY proper affiliate URLs are generated with correct format"""
        try:
            if not hasattr(self, 'test_recipe_id') or not self.test_recipe_id:
                self.log_test_result("Walmart Affiliate URL Format", False, "No test recipe ID available")
                return False
            
            # First get cart options
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={self.test_recipe_id}&user_id={self.demo_user_id}")
                
                if response.status_code != 200:
                    self.log_test_result("Walmart Affiliate URL Format", False, f"Failed to get cart options: {response.status_code}")
                    return False
                
                data = response.json()
                ingredient_options = data.get("ingredient_options", [])
                
                # Select products for cart creation
                selected_products = []
                for ingredient_option in ingredient_options[:3]:  # First 3 ingredients
                    options = ingredient_option.get("options", [])
                    if options:
                        first_option = options[0]
                        selected_products.append({
                            "ingredient_name": ingredient_option.get("ingredient_name"),
                            "product_id": first_option.get("product_id"),
                            "name": first_option.get("name"),
                            "price": first_option.get("price"),
                            "quantity": 1
                        })
                
                if not selected_products:
                    self.log_test_result("Walmart Affiliate URL Format", False, "No products available for cart creation")
                    return False
                
                # Create grocery cart
                cart_request = {
                    "user_id": self.demo_user_id,
                    "recipe_id": self.test_recipe_id,
                    "products": selected_products
                }
                
                cart_response = await client.post(f"{self.backend_url}/grocery/create-cart", json=cart_request)
                
                if cart_response.status_code == 200:
                    cart_data = cart_response.json()
                    walmart_url = cart_data.get("walmart_url", "")
                    
                    # CRITICAL TEST: Validate ONLY proper affiliate URL format
                    expected_affiliate_format = "https://affil.walmart.com/cart/addToCart?items="
                    
                    if not walmart_url:
                        self.log_test_result("Walmart Affiliate URL Format", False, "No Walmart URL generated")
                        return False
                    
                    # Check that it's NOT a search URL
                    if "search?q=" in walmart_url or "/search" in walmart_url:
                        self.log_test_result(
                            "Walmart Affiliate URL Format", 
                            False, 
                            f"❌ CRITICAL: Generated search URL instead of affiliate URL: {walmart_url}"
                        )
                        return False
                    
                    # Check that it uses the correct affiliate format
                    if not walmart_url.startswith(expected_affiliate_format):
                        self.log_test_result(
                            "Walmart Affiliate URL Format", 
                            False, 
                            f"❌ CRITICAL: URL doesn't use proper affiliate format. Expected: {expected_affiliate_format}*, Got: {walmart_url}"
                        )
                        return False
                    
                    # Validate that URL contains actual product IDs
                    product_ids = [prod.get("product_id", "") for prod in selected_products]
                    contains_product_ids = any(pid in walmart_url for pid in product_ids if pid)
                    
                    if not contains_product_ids:
                        self.log_test_result(
                            "Walmart Affiliate URL Format", 
                            False, 
                            f"❌ CRITICAL: Affiliate URL doesn't contain actual product IDs: {walmart_url}"
                        )
                        return False
                    
                    self.log_test_result(
                        "Walmart Affiliate URL Format", 
                        True, 
                        f"✅ PERFECT: Generated proper affiliate URL with format 'https://affil.walmart.com/cart/addToCart?items=PRODUCTID1,PRODUCTID2...' containing {len(selected_products)} real product IDs",
                        {
                            "walmart_url": walmart_url,
                            "product_count": len(selected_products),
                            "contains_product_ids": contains_product_ids,
                            "url_format_correct": walmart_url.startswith(expected_affiliate_format)
                        }
                    )
                    return True
                else:
                    # Test error handling - should return 500, not fallback search URLs
                    if cart_response.status_code == 500:
                        response_text = cart_response.text
                        
                        # Check that error response doesn't contain search URLs
                        if "search?q=" in response_text or "walmart.com/search" in response_text:
                            self.log_test_result(
                                "Walmart Affiliate URL Format", 
                                False, 
                                f"❌ CRITICAL: Error response contains fallback search URLs: {response_text}"
                            )
                            return False
                        else:
                            self.log_test_result(
                                "Walmart Affiliate URL Format", 
                                True, 
                                f"✅ GOOD: Error handling returns proper 500 error without fallback search URLs"
                            )
                            return True
                    else:
                        self.log_test_result("Walmart Affiliate URL Format", False, f"Unexpected error: {cart_response.status_code} - {cart_response.text}")
                        return False
        except Exception as e:
            self.log_test_result("Walmart Affiliate URL Format", False, f"Error: {str(e)}")
            return False

    async def test_complete_walmart_workflow_no_search_urls(self) -> bool:
        """Test complete workflow to ensure no search URLs are generated anywhere"""
        try:
            workflow_steps = []
            
            # Step 1: Recipe Generation
            recipe_success = await self.test_recipe_generation_for_walmart()
            workflow_steps.append(("Recipe Generation", recipe_success))
            
            if not recipe_success:
                self.log_test_result("Complete Walmart Workflow", False, "Recipe generation failed")
                return False
            
            # Step 2: Walmart Cart Options (check for no search URLs)
            cart_options_success = await self.test_walmart_cart_options_url_format()
            workflow_steps.append(("Cart Options (No Search URLs)", cart_options_success))
            
            # Step 3: Affiliate URL Generation (proper format only)
            affiliate_url_success = await self.test_walmart_affiliate_url_format_only()
            workflow_steps.append(("Affiliate URL (Proper Format)", affiliate_url_success))
            
            # Evaluate overall workflow
            all_passed = all(success for _, success in workflow_steps)
            
            if all_passed:
                self.log_test_result(
                    "Complete Walmart Workflow", 
                    True, 
                    f"✅ COMPLETE SUCCESS: All workflow steps passed. NO search URLs generated, ONLY proper affiliate URLs used.",
                    {"workflow_steps": workflow_steps}
                )
            else:
                failed_steps = [step for step, success in workflow_steps if not success]
                self.log_test_result(
                    "Complete Walmart Workflow", 
                    False, 
                    f"❌ WORKFLOW FAILED: Failed steps: {failed_steps}",
                    {"workflow_steps": workflow_steps}
                )
            
            return all_passed
        except Exception as e:
            self.log_test_result("Complete Walmart Workflow", False, f"Error: {str(e)}")
            return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Walmart URL validation tests"""
        logger.info("🚀 Starting Walmart URL Generation Testing Suite")
        logger.info("=" * 60)
        
        # Test sequence
        tests = [
            ("Demo User Login", self.test_demo_user_login),
            ("Recipe Generation for Walmart", self.test_recipe_generation_for_walmart),
            ("Walmart Cart Options URL Format", self.test_walmart_cart_options_url_format),
            ("Walmart Affiliate URL Format", self.test_walmart_affiliate_url_format_only),
            ("Complete Walmart Workflow", self.test_complete_walmart_workflow_no_search_urls)
        ]
        
        results = {}
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running: {test_name}")
            try:
                success = await test_func()
                results[test_name] = success
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ Test {test_name} crashed: {str(e)}")
                results[test_name] = False
                failed += 1
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("🏁 WALMART URL TESTING SUMMARY")
        logger.info("=" * 60)
        
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
        
        logger.info(f"\n📊 Results: {passed} passed, {failed} failed")
        
        # Critical findings
        if all(results.values()):
            logger.info("🎉 ALL TESTS PASSED - Walmart URL generation is working correctly!")
            logger.info("✅ NO problematic search URLs found")
            logger.info("✅ ONLY proper affiliate URLs generated")
            logger.info("✅ Error handling works correctly")
        else:
            logger.error("❌ SOME TESTS FAILED - Walmart URL generation has issues!")
            failed_tests = [name for name, success in results.items() if not success]
            logger.error(f"Failed tests: {failed_tests}")
        
        return {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/len(tests)*100):.1f}%",
            "results": results,
            "test_details": self.test_results
        }

async def main():
    """Main test runner"""
    tester = WalmartURLTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())