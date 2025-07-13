#!/usr/bin/env python3
"""
PRODUCTION WALMART INTEGRATION TEST
Test with working demo user to see if Walmart integration is actually fixed
"""

import asyncio
import httpx
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_walmart_with_demo_user():
    """Test Walmart integration with demo user to see if it's working"""
    base_url = "https://recipe-cart-app-1.emergent.host/api"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Login as demo user
            logger.info("🔍 Step 1: Login as demo user...")
            login_response = await client.post(f"{base_url}/auth/login", json={
                "email": "demo@test.com",
                "password": "password123"
            })
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                user_id = login_data.get("user", {}).get("id") or login_data.get("user_id")
                logger.info(f"✅ Demo user login successful - User ID: {user_id}")
            else:
                logger.error(f"❌ Demo user login failed: {login_response.status_code}")
                return
            
            # Step 2: Generate a new recipe
            logger.info("🔍 Step 2: Generate a new recipe...")
            recipe_request = {
                "user_id": user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "italian",
                "servings": 4,
                "difficulty": "medium"
            }
            
            recipe_response = await client.post(f"{base_url}/recipes/generate", json=recipe_request)
            
            if recipe_response.status_code == 200:
                recipe_data = recipe_response.json()
                recipe_id = recipe_data.get("id")
                recipe_title = recipe_data.get("title")
                shopping_list = recipe_data.get("shopping_list", [])
                
                logger.info(f"✅ Recipe generated: '{recipe_title}' (ID: {recipe_id})")
                logger.info(f"   Shopping list: {shopping_list}")
            else:
                logger.error(f"❌ Recipe generation failed: {recipe_response.status_code}")
                return
            
            # Step 3: Test Walmart integration with the new recipe
            logger.info("🔍 Step 3: Testing Walmart integration...")
            cart_response = await client.post(
                f"{base_url}/grocery/cart-options",
                params={"recipe_id": recipe_id, "user_id": user_id}
            )
            
            logger.info(f"Cart Options Response Status: {cart_response.status_code}")
            
            if cart_response.status_code == 200:
                cart_data = cart_response.json()
                
                # Check the response structure
                logger.info(f"Response keys: {list(cart_data.keys())}")
                
                if cart_data.get("status") == "no_products_found":
                    logger.error("❌ WALMART INTEGRATION STILL BROKEN!")
                    logger.error(f"   Status: {cart_data.get('status')}")
                    logger.error(f"   Message: {cart_data.get('message')}")
                    logger.error("   The fix did not work - still returning no products")
                else:
                    ingredient_options = cart_data.get("ingredient_options", [])
                    total_products = sum(len(opt.get("options", [])) for opt in ingredient_options)
                    
                    if total_products > 0:
                        logger.info(f"✅ WALMART INTEGRATION WORKING!")
                        logger.info(f"   Found {len(ingredient_options)} ingredient options")
                        logger.info(f"   Total products: {total_products}")
                        
                        # Show example products
                        for opt in ingredient_options[:3]:
                            ingredient_name = opt.get("ingredient_name")
                            products = opt.get("options", [])
                            logger.info(f"   {ingredient_name}: {len(products)} products")
                            for product in products[:2]:
                                logger.info(f"     - {product.get('name')} - ${product.get('price')} (ID: {product.get('product_id')})")
                    else:
                        logger.warning("⚠️ No products found but no error status")
            else:
                logger.error(f"❌ Cart options request failed: {cart_response.status_code}")
                logger.error(f"   Response: {cart_response.text}")
                
    except Exception as e:
        logger.error(f"💥 Test error: {str(e)}")

async def main():
    print("🔍 TESTING WALMART INTEGRATION WITH DEMO USER")
    print("=" * 60)
    print("This will test if the Walmart fix actually works")
    print("=" * 60)
    
    await test_walmart_with_demo_user()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())