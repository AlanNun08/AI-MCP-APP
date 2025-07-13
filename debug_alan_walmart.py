#!/usr/bin/env python3
"""
DEBUG WALMART INTEGRATION FOR ALAN.NUNEZ0310@ICLOUD.COM
Testing the actual production issue the user is experiencing
"""

import asyncio
import httpx
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlanWalmartDebugger:
    def __init__(self):
        self.base_url = "https://recipe-cart-app-1.emergent.host/api"
        self.user_email = "alan.nunez0310@icloud.com"
        
    async def debug_alan_walmart_issue(self):
        """Debug the Walmart integration issue for Alan's account"""
        try:
            # Step 1: Get Alan's user info
            logger.info("🔍 Step 1: Getting Alan's user information...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                user_response = await client.get(f"{self.base_url}/debug/user/{self.user_email}")
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    user_id = user_data.get("id")
                    logger.info(f"✅ Found Alan's account - User ID: {user_id}")
                    logger.info(f"   Email: {user_data.get('email')}")
                    logger.info(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                    logger.info(f"   Verified: {user_data.get('is_verified')}")
                else:
                    logger.error(f"❌ Could not find Alan's user: {user_response.status_code}")
                    return
                
                # Step 2: Get Alan's recipe history
                logger.info("🔍 Step 2: Getting Alan's recipe history...")
                history_response = await client.get(f"{self.base_url}/recipes/history/{user_id}")
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    recipes = history_data.get("recipes", [])
                    regular_recipes = [r for r in recipes if r.get("recipe_category") != "starbucks"]
                    
                    logger.info(f"✅ Found {len(recipes)} total recipes ({len(regular_recipes)} regular recipes)")
                    
                    if not regular_recipes:
                        logger.warning("⚠️ No regular recipes found for Walmart integration testing")
                        return
                    
                    # Step 3: Test Walmart integration with Alan's recipes
                    logger.info("🔍 Step 3: Testing Walmart integration with Alan's recipes...")
                    
                    for i, recipe in enumerate(regular_recipes[:3]):  # Test first 3 recipes
                        recipe_id = recipe.get("id")
                        recipe_title = recipe.get("title", "Unknown")
                        shopping_list = recipe.get("shopping_list", [])
                        
                        logger.info(f"\n--- Testing Recipe {i+1}: {recipe_title} ---")
                        logger.info(f"Recipe ID: {recipe_id}")
                        logger.info(f"Shopping List: {shopping_list}")
                        
                        # Test cart-options endpoint
                        cart_response = await client.post(
                            f"{self.base_url}/grocery/cart-options",
                            params={"recipe_id": recipe_id, "user_id": user_id}
                        )
                        
                        logger.info(f"Cart Options Response Status: {cart_response.status_code}")
                        
                        if cart_response.status_code == 200:
                            cart_data = cart_response.json()
                            
                            # Check for no_products_found status
                            if cart_data.get("status") == "no_products_found":
                                logger.error(f"❌ PROBLEM FOUND: Recipe '{recipe_title}' returns 'no_products_found'")
                                logger.error(f"   Message: {cart_data.get('message')}")
                                logger.error(f"   This is the exact issue Alan is experiencing!")
                                
                                # Let's examine what ingredients are causing the issue
                                logger.info("🔍 Debugging individual ingredients...")
                                for ingredient in shopping_list[:3]:  # Test first 3 ingredients
                                    logger.info(f"   Testing ingredient: '{ingredient}'")
                                    # This would require calling the Walmart API function directly
                                    
                            else:
                                ingredient_options = cart_data.get("ingredient_options", [])
                                total_products = sum(len(opt.get("options", [])) for opt in ingredient_options)
                                
                                logger.info(f"✅ Found {len(ingredient_options)} ingredient options with {total_products} total products")
                                
                                # Show some example products
                                for opt in ingredient_options[:2]:
                                    ingredient_name = opt.get("ingredient_name")
                                    products = opt.get("options", [])
                                    logger.info(f"   {ingredient_name}: {len(products)} products")
                                    for product in products[:2]:
                                        logger.info(f"     - {product.get('name')} - ${product.get('price')} (ID: {product.get('product_id')})")
                        else:
                            logger.error(f"❌ Cart options failed: {cart_response.status_code}")
                            logger.error(f"   Response: {cart_response.text}")
                            
                else:
                    logger.error(f"❌ Could not get recipe history: {history_response.status_code}")
                    
        except Exception as e:
            logger.error(f"💥 Debug error: {str(e)}")
    
    async def test_single_ingredient_walmart_search(self, ingredient: str):
        """Test Walmart search for a single ingredient"""
        try:
            logger.info(f"🔍 Testing Walmart search for ingredient: '{ingredient}'")
            
            # This would call the Walmart API function directly
            # For now, let's check the backend logs after calling the API
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Make a simple request that would trigger Walmart API call
                response = await client.get(f"{self.base_url}/")
                logger.info(f"Backend health check: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ingredient test error: {str(e)}")

async def main():
    """Main function to debug Alan's Walmart integration issue"""
    debugger = AlanWalmartDebugger()
    
    print("🔍 DEBUGGING WALMART INTEGRATION FOR ALAN.NUNEZ0310@ICLOUD.COM")
    print("=" * 70)
    print("This will test the exact issue the user is experiencing in production")
    print("=" * 70)
    
    await debugger.debug_alan_walmart_issue()
    
    print("\n" + "=" * 70)
    print("DEBUG COMPLETE - CHECK LOGS ABOVE FOR ISSUES")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())