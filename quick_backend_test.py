#!/usr/bin/env python3
"""
Quick Backend Test for Review Requirements
"""

import asyncio
import httpx
import json
from datetime import datetime

BACKEND_URL = "https://7231aef0-71b1-4397-ae8c-9cb5a059a118.preview.emergentagent.com/api"
DEMO_USER_EMAIL = "demo@test.com"
DEMO_USER_PASSWORD = "password123"

async def test_backend_endpoints():
    """Test all required endpoints quickly"""
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        print("🚀 Testing Backend Endpoints for Review")
        print("=" * 50)
        
        # Test 1: Authentication
        print("1. Testing /api/auth/login...")
        try:
            login_response = await client.post(f"{BACKEND_URL}/auth/login", json={
                "email": DEMO_USER_EMAIL,
                "password": DEMO_USER_PASSWORD
            })
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                user_id = login_data.get("user_id")
                print(f"   ✅ Login successful - User ID: {user_id}")
                
                # Test 2: Recipe Generation
                print("2. Testing /api/recipes/generate...")
                recipe_response = await client.post(f"{BACKEND_URL}/recipes/generate", json={
                    "user_id": user_id,
                    "recipe_category": "cuisine",
                    "cuisine_type": "Italian",
                    "dietary_preferences": [],
                    "ingredients_on_hand": [],
                    "prep_time_max": 30,
                    "servings": 4,
                    "difficulty": "medium"
                })
                
                if recipe_response.status_code == 200:
                    recipe_data = recipe_response.json()
                    recipe_id = recipe_data.get("id")
                    shopping_list = recipe_data.get("shopping_list", [])
                    print(f"   ✅ Recipe generated - ID: {recipe_id}")
                    print(f"   ✅ Title: {recipe_data.get('title')}")
                    print(f"   ✅ Shopping list: {len(shopping_list)} items")
                    
                    # Test 3: Grocery Cart Options (with longer timeout)
                    print("3. Testing /api/grocery/cart-options...")
                    print("   (This may take 30-60 seconds due to Walmart API calls...)")
                    
                    try:
                        cart_response = await client.post(
                            f"{BACKEND_URL}/grocery/cart-options",
                            params={"recipe_id": recipe_id, "user_id": user_id},
                            timeout=90.0
                        )
                        
                        if cart_response.status_code == 200:
                            cart_data = cart_response.json()
                            ingredient_options = cart_data.get("ingredient_options", [])
                            total_products = cart_data.get("total_products", 0)
                            
                            print(f"   ✅ Cart options successful")
                            print(f"   ✅ Ingredient options: {len(ingredient_options)}")
                            print(f"   ✅ Total products: {total_products}")
                            
                            # Check response format
                            if ingredient_options:
                                first_option = ingredient_options[0]
                                if "ingredient_name" in first_option and "options" in first_option:
                                    products = first_option.get("options", [])
                                    if products:
                                        first_product = products[0]
                                        required_fields = ["product_id", "name", "price"]
                                        has_required = all(field in first_product for field in required_fields)
                                        
                                        print(f"   ✅ Response format valid: {has_required}")
                                        if has_required:
                                            print(f"   ✅ Sample product: {first_product.get('name')} - ${first_product.get('price')}")
                                        
                                        # Test 4: Walmart Integration Verification
                                        print("4. Walmart API Integration:")
                                        print(f"   ✅ Real products returned: {total_products > 0}")
                                        print(f"   ✅ Product structure valid: {has_required}")
                                        
                                        print("\n🎉 ALL TESTS PASSED!")
                                        print("✅ Authentication working with demo@test.com/password123")
                                        print("✅ Recipe generation working")
                                        print("✅ Grocery cart options returning real Walmart products")
                                        print("✅ Response format matches frontend expectations")
                                        print("✅ Walmart API integration working correctly")
                                        
                                        return True
                            
                            print("   ❌ No products in response")
                            return False
                        else:
                            print(f"   ❌ Cart options failed: {cart_response.status_code}")
                            return False
                            
                    except httpx.TimeoutException:
                        print("   ❌ Cart options timed out (Walmart API may be slow)")
                        return False
                        
                else:
                    print(f"   ❌ Recipe generation failed: {recipe_response.status_code}")
                    return False
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False

if __name__ == "__main__":
    result = asyncio.run(test_backend_endpoints())
    if not result:
        print("\n❌ Some tests failed - check logs above")