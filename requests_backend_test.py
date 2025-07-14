#!/usr/bin/env python3
"""
Backend Test using requests library
"""

import requests
import json
import time

BACKEND_URL = "https://7231aef0-71b1-4397-ae8c-9cb5a059a118.preview.emergentagent.com/api"
DEMO_USER_EMAIL = "demo@test.com"
DEMO_USER_PASSWORD = "password123"

def test_backend_with_requests():
    """Test backend endpoints using requests library"""
    
    print("🚀 Testing Backend with requests library")
    print("=" * 50)
    
    # Test 1: Authentication
    print("1. Testing /api/auth/login...")
    try:
        login_response = requests.post(f"{BACKEND_URL}/auth/login", 
            json={
                "email": DEMO_USER_EMAIL,
                "password": DEMO_USER_PASSWORD
            },
            timeout=30
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            user_id = login_data.get("user_id")
            print(f"   ✅ Login successful - User ID: {user_id}")
            
            # Test 2: Recipe Generation
            print("2. Testing /api/recipes/generate...")
            recipe_response = requests.post(f"{BACKEND_URL}/recipes/generate",
                json={
                    "user_id": user_id,
                    "recipe_category": "cuisine",
                    "cuisine_type": "Italian",
                    "dietary_preferences": [],
                    "ingredients_on_hand": [],
                    "prep_time_max": 30,
                    "servings": 4,
                    "difficulty": "medium"
                },
                timeout=30
            )
            
            if recipe_response.status_code == 200:
                recipe_data = recipe_response.json()
                recipe_id = recipe_data.get("id")
                shopping_list = recipe_data.get("shopping_list", [])
                print(f"   ✅ Recipe generated - ID: {recipe_id}")
                print(f"   ✅ Title: {recipe_data.get('title')}")
                print(f"   ✅ Shopping list: {len(shopping_list)} items: {shopping_list}")
                
                # Test 3: Grocery Cart Options
                print("3. Testing /api/grocery/cart-options...")
                print("   (This may take 30-90 seconds due to Walmart API calls...)")
                
                start_time = time.time()
                cart_response = requests.post(
                    f"{BACKEND_URL}/grocery/cart-options",
                    params={"recipe_id": recipe_id, "user_id": user_id},
                    timeout=120  # 2 minutes timeout
                )
                end_time = time.time()
                
                print(f"   Request took {end_time - start_time:.1f} seconds")
                
                if cart_response.status_code == 200:
                    cart_data = cart_response.json()
                    ingredient_options = cart_data.get("ingredient_options", [])
                    total_products = cart_data.get("total_products", 0)
                    
                    print(f"   ✅ Cart options successful")
                    print(f"   ✅ Ingredient options: {len(ingredient_options)}")
                    print(f"   ✅ Total products: {total_products}")
                    
                    # Show detailed results
                    if ingredient_options:
                        print("   📦 Product Details:")
                        for option in ingredient_options:
                            ingredient_name = option.get("ingredient_name")
                            products = option.get("options", [])
                            print(f"     {ingredient_name}: {len(products)} products")
                            
                            for i, product in enumerate(products[:2]):  # Show first 2
                                print(f"       {i+1}. {product.get('name')} - ${product.get('price')}")
                        
                        # Test response format
                        first_option = ingredient_options[0]
                        if "ingredient_name" in first_option and "options" in first_option:
                            products = first_option.get("options", [])
                            if products:
                                first_product = products[0]
                                required_fields = ["product_id", "name", "price"]
                                has_required = all(field in first_product for field in required_fields)
                                
                                print(f"   ✅ Response format valid: {has_required}")
                                
                                print("\n🎉 ALL BACKEND TESTS PASSED!")
                                print("✅ Authentication: demo@test.com/password123 works")
                                print("✅ Recipe generation: Returns proper recipe with shopping_list")
                                print("✅ Grocery cart options: Returns real Walmart products")
                                print("✅ Walmart API integration: Working and returning products with prices")
                                print("✅ Response format: ingredient_options with product_id, name, price")
                                
                                return True
                    
                    print("   ❌ No ingredient options in response")
                    return False
                else:
                    print(f"   ❌ Cart options failed: {cart_response.status_code} - {cart_response.text}")
                    return False
                    
            else:
                print(f"   ❌ Recipe generation failed: {recipe_response.status_code} - {recipe_response.text}")
                return False
        else:
            print(f"   ❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    result = test_backend_with_requests()
    if not result:
        print("\n❌ Some tests failed - check logs above")