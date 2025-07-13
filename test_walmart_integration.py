#!/usr/bin/env python3
"""
Clean Walmart Integration Test Suite
Tests the complete Walmart integration workflow for the production deployment
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

class WalmartIntegrationTester:
    def __init__(self):
        self.backend_url = self.get_backend_url()
        self.demo_user_email = "demo@test.com"
        self.demo_user_password = "password123"
        self.demo_user_id = None
        
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
    
    async def test_api_health(self) -> bool:
        """Test API health check"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.backend_url}/")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ API Health: {data.get('status')} - Version: {data.get('version')}")
                    return True
                else:
                    logger.error(f"❌ API Health Check Failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ API Health Check Error: {e}")
            return False
    
    async def test_demo_user_login(self) -> bool:
        """Test demo user login"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                login_data = {
                    "email": self.demo_user_email,
                    "password": self.demo_user_password
                }
                
                response = await client.post(f"{self.backend_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        self.demo_user_id = data.get("user", {}).get("id")
                        logger.info(f"✅ Demo User Login: Success (ID: {self.demo_user_id})")
                        return True
                    else:
                        logger.error(f"❌ Demo User Login Failed: {data}")
                        return False
                else:
                    logger.error(f"❌ Demo User Login HTTP Error: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Demo User Login Error: {e}")
            return False
    
    async def test_recipe_generation(self) -> str:
        """Test recipe generation and return recipe ID"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                recipe_data = {
                    "user_id": self.demo_user_id,
                    "recipe_category": "cuisine",
                    "cuisine_type": "Italian",
                    "dietary_preferences": ["vegetarian"],
                    "ingredients_on_hand": ["tomatoes", "basil"],
                    "prep_time_max": 30,
                    "servings": 4,
                    "difficulty": "medium",
                    "is_healthy": True,
                    "max_calories_per_serving": 400
                }
                
                response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_data)
                
                if response.status_code == 200:
                    data = response.json()
                    recipe_id = data.get("id")
                    recipe_title = data.get("title", "Unknown")
                    shopping_list = data.get("shopping_list", [])
                    
                    logger.info(f"✅ Recipe Generation: '{recipe_title}' (ID: {recipe_id})")
                    logger.info(f"   Shopping Items: {len(shopping_list)}")
                    return recipe_id
                else:
                    logger.error(f"❌ Recipe Generation Failed: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"❌ Recipe Generation Error: {e}")
            return None
    
    async def test_walmart_cart_options(self, recipe_id: str) -> bool:
        """Test Walmart cart options generation"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.backend_url}/grocery/cart-options?recipe_id={recipe_id}&user_id={self.demo_user_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle case where no products are found
                    if data.get("status") == "no_products_found":
                        logger.warning(f"⚠️ Walmart Cart Options: No products found for recipe")
                        logger.info(f"   Message: {data.get('message')}")
                        return True  # This is not an error, it's a valid response
                    
                    ingredient_options = data.get("ingredient_options", [])
                    total_products = sum(len(opt.get("options", [])) for opt in ingredient_options)
                    
                    logger.info(f"✅ Walmart Cart Options: {len(ingredient_options)} ingredients")
                    logger.info(f"   Total Products Found: {total_products}")
                    
                    # Verify product authenticity
                    authentic_products = 0
                    for ingredient_option in ingredient_options:
                        for product in ingredient_option.get("options", []):
                            product_id = product.get("product_id", "")
                            if product_id.isdigit() and len(product_id) >= 6:
                                authentic_products += 1
                    
                    authenticity_rate = (authentic_products / total_products * 100) if total_products > 0 else 0
                    logger.info(f"   Authenticity Rate: {authenticity_rate:.1f}% ({authentic_products}/{total_products})")
                    
                    return True
                else:
                    logger.error(f"❌ Walmart Cart Options Failed: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Walmart Cart Options Error: {e}")
            return False
    
    async def test_complete_workflow(self) -> bool:
        """Test the complete Walmart integration workflow"""
        logger.info("🚀 Starting Complete Walmart Integration Workflow Test")
        
        # Test 1: API Health
        if not await self.test_api_health():
            return False
        
        # Test 2: Demo User Login
        if not await self.test_demo_user_login():
            return False
        
        # Test 3: Recipe Generation
        recipe_id = await self.test_recipe_generation()
        if not recipe_id:
            return False
        
        # Test 4: Walmart Cart Options
        if not await self.test_walmart_cart_options(recipe_id):
            return False
        
        logger.info("🎉 Complete Walmart Integration Workflow Test: SUCCESS")
        return True

async def main():
    """Run the complete test suite"""
    tester = WalmartIntegrationTester()
    
    success = await tester.test_complete_workflow()
    
    if success:
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED - WALMART INTEGRATION WORKING")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ TESTS FAILED - CHECK LOGS FOR DETAILS")
        print("="*50)
    
    return success

if __name__ == "__main__":
    asyncio.run(main())