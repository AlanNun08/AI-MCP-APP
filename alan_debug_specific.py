#!/usr/bin/env python3
"""
Specific debug test for alan.nunez0310@icloud.com cart-options 500 error
This test will try various scenarios to reproduce the exact 500 error condition
"""

import asyncio
import httpx
import json
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlanSpecificDebugger:
    def __init__(self):
        self.backend_url = self.get_backend_url()
        self.target_user_email = "alan.nunez0310@icloud.com"
        self.target_user_id = None
        
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
    
    async def get_user_info(self):
        """Get user information"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/debug/user/{self.target_user_email}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data:
                        user_data = data["user"]
                        self.target_user_id = user_data.get("id")
                        logger.info(f"✅ Found user: {self.target_user_id}")
                        logger.info(f"   Email: {user_data.get('email')}")
                        logger.info(f"   Verified: {user_data.get('is_verified')}")
                        logger.info(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                        return True
                    else:
                        logger.error(f"❌ User not found: {data}")
                        return False
                else:
                    logger.error(f"❌ Failed to get user: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Exception getting user: {e}")
            return False
    
    async def get_user_recipes(self):
        """Get user's recipes"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/recipes/history/{self.target_user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get("recipes", [])
                    
                    logger.info(f"✅ Found {len(recipes)} total recipes")
                    
                    # Categorize recipes
                    regular_recipes = []
                    starbucks_recipes = []
                    
                    for recipe in recipes:
                        if "shopping_list" in recipe and "drink_name" not in recipe:
                            regular_recipes.append(recipe)
                        elif "drink_name" in recipe or "ordering_script" in recipe:
                            starbucks_recipes.append(recipe)
                    
                    logger.info(f"   Regular recipes: {len(regular_recipes)}")
                    logger.info(f"   Starbucks recipes: {len(starbucks_recipes)}")
                    
                    # Print details of regular recipes
                    for i, recipe in enumerate(regular_recipes[:5]):
                        logger.info(f"   Recipe {i+1}: {recipe.get('title', 'Unknown')} (ID: {recipe.get('id')})")
                        shopping_list = recipe.get('shopping_list', [])
                        logger.info(f"     Shopping items: {len(shopping_list)}")
                        if shopping_list:
                            logger.info(f"     Sample items: {shopping_list[:3]}")
                    
                    return regular_recipes
                else:
                    logger.error(f"❌ Failed to get recipes: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"❌ Exception getting recipes: {e}")
            return []
    
    async def test_cart_options_scenarios(self, recipes):
        """Test various scenarios that might cause 500 errors"""
        logger.info("🧪 Testing various cart-options scenarios...")
        
        scenarios_tested = 0
        errors_found = 0
        
        for i, recipe in enumerate(recipes[:10]):  # Test first 10 recipes
            recipe_id = recipe.get("id")
            recipe_title = recipe.get("title", "Unknown")
            shopping_list = recipe.get("shopping_list", [])
            
            logger.info(f"\n🔍 Testing Recipe {i+1}: {recipe_title}")
            logger.info(f"   Recipe ID: {recipe_id}")
            logger.info(f"   Shopping items: {len(shopping_list)}")
            
            # Scenario 1: Normal request
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={recipe_id}&user_id={self.target_user_id}")
                    
                    scenarios_tested += 1
                    
                    if response.status_code == 500:
                        errors_found += 1
                        logger.error(f"🚨 500 ERROR found for recipe: {recipe_title}")
                        logger.error(f"   Error response: {response.text}")
                        
                        # Try to get more details about the error
                        try:
                            error_data = response.json()
                            logger.error(f"   Error JSON: {error_data}")
                        except:
                            logger.error(f"   Raw error text: {response.text}")
                        
                        # Analyze the shopping list for this problematic recipe
                        logger.info(f"   Problematic shopping list analysis:")
                        for j, item in enumerate(shopping_list):
                            logger.info(f"     Item {j+1}: '{item}' (length: {len(item)})")
                            if len(item) > 100:
                                logger.warning(f"       ⚠️ Very long item: {len(item)} characters")
                            if any(char in item for char in ['&', '<', '>', '"', "'"]):
                                logger.warning(f"       ⚠️ Special characters detected")
                            if not all(ord(char) < 128 for char in item):
                                logger.warning(f"       ⚠️ Non-ASCII characters detected")
                        
                    elif response.status_code == 200:
                        logger.info(f"   ✅ Success: {response.status_code}")
                        # Check if response has valid data
                        try:
                            data = response.json()
                            ingredient_options = data.get("ingredient_options", [])
                            logger.info(f"   Generated options for {len(ingredient_options)} ingredients")
                        except:
                            logger.warning(f"   ⚠️ Success but invalid JSON response")
                    else:
                        logger.warning(f"   ⚠️ Unexpected status: {response.status_code}")
                        if response.status_code >= 400:
                            logger.warning(f"   Error response: {response.text}")
            
            except asyncio.TimeoutError:
                logger.error(f"   ⏰ Timeout error for recipe: {recipe_title}")
                errors_found += 1
            except Exception as e:
                logger.error(f"   💥 Exception for recipe: {recipe_title} - {e}")
                errors_found += 1
            
            # Scenario 2: Test with malformed user_id
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={recipe_id}&user_id=invalid-user-id")
                    scenarios_tested += 1
                    
                    if response.status_code == 500:
                        errors_found += 1
                        logger.error(f"🚨 500 ERROR with invalid user_id for recipe: {recipe_title}")
                        logger.error(f"   Error response: {response.text}")
            except Exception as e:
                logger.error(f"   💥 Exception with invalid user_id: {e}")
            
            # Scenario 3: Test with malformed recipe_id
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id=invalid-recipe-id&user_id={self.target_user_id}")
                    scenarios_tested += 1
                    
                    if response.status_code == 500:
                        errors_found += 1
                        logger.error(f"🚨 500 ERROR with invalid recipe_id")
                        logger.error(f"   Error response: {response.text}")
            except Exception as e:
                logger.error(f"   💥 Exception with invalid recipe_id: {e}")
            
            # Small delay between recipe tests
            await asyncio.sleep(1)
        
        logger.info(f"\n📊 Test Results:")
        logger.info(f"   Scenarios tested: {scenarios_tested}")
        logger.info(f"   500 errors found: {errors_found}")
        logger.info(f"   Error rate: {(errors_found/scenarios_tested*100):.1f}%" if scenarios_tested > 0 else "N/A")
        
        return errors_found > 0
    
    async def test_edge_cases(self):
        """Test edge cases that might cause 500 errors"""
        logger.info("\n🧪 Testing edge cases...")
        
        edge_cases = [
            # Missing parameters
            f"{self.backend_url}/grocery/cart-options",
            f"{self.backend_url}/grocery/cart-options?recipe_id=",
            f"{self.backend_url}/grocery/cart-options?user_id=",
            f"{self.backend_url}/grocery/cart-options?recipe_id=test",
            f"{self.backend_url}/grocery/cart-options?user_id=test",
            # Very long IDs
            f"{self.backend_url}/grocery/cart-options?recipe_id={'a'*1000}&user_id={self.target_user_id}",
            f"{self.backend_url}/grocery/cart-options?recipe_id={self.target_user_id}&user_id={'b'*1000}",
            # Special characters
            f"{self.backend_url}/grocery/cart-options?recipe_id=test%20with%20spaces&user_id={self.target_user_id}",
            f"{self.backend_url}/grocery/cart-options?recipe_id=test&user_id=test%20with%20spaces",
        ]
        
        errors_found = 0
        
        for i, url in enumerate(edge_cases):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url)
                    
                    if response.status_code == 500:
                        errors_found += 1
                        logger.error(f"🚨 500 ERROR in edge case {i+1}")
                        logger.error(f"   URL: {url}")
                        logger.error(f"   Error response: {response.text}")
                    else:
                        logger.info(f"   Edge case {i+1}: {response.status_code}")
            
            except Exception as e:
                logger.error(f"   💥 Exception in edge case {i+1}: {e}")
            
            await asyncio.sleep(0.5)
        
        return errors_found > 0
    
    async def run_comprehensive_debug(self):
        """Run comprehensive debug test"""
        logger.info("🚀 Starting Comprehensive Debug for alan.nunez0310@icloud.com")
        logger.info("=" * 80)
        
        # Step 1: Get user info
        logger.info("📋 Step 1: Getting user information...")
        if not await self.get_user_info():
            logger.error("❌ Cannot proceed without user information")
            return False
        
        # Step 2: Get user recipes
        logger.info("\n📋 Step 2: Getting user recipes...")
        recipes = await self.get_user_recipes()
        if not recipes:
            logger.error("❌ No regular recipes found for testing")
            return False
        
        # Step 3: Test cart-options scenarios
        logger.info("\n📋 Step 3: Testing cart-options scenarios...")
        found_500_errors = await self.test_cart_options_scenarios(recipes)
        
        # Step 4: Test edge cases
        logger.info("\n📋 Step 4: Testing edge cases...")
        found_edge_case_errors = await self.test_edge_cases()
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("🎯 COMPREHENSIVE DEBUG SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Target User: {self.target_user_email}")
        logger.info(f"User ID: {self.target_user_id}")
        logger.info(f"Regular Recipes Found: {len(recipes)}")
        logger.info(f"500 Errors in Normal Scenarios: {'YES' if found_500_errors else 'NO'}")
        logger.info(f"500 Errors in Edge Cases: {'YES' if found_edge_case_errors else 'NO'}")
        
        if found_500_errors or found_edge_case_errors:
            logger.info("🚨 500 ERRORS DETECTED - Check logs above for details")
            return True
        else:
            logger.info("✅ NO 500 ERRORS FOUND - System appears to be working correctly for this user")
            return False

async def main():
    debugger = AlanSpecificDebugger()
    await debugger.run_comprehensive_debug()

if __name__ == "__main__":
    asyncio.run(main())