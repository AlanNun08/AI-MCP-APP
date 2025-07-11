#!/usr/bin/env python3
"""
Test script to verify Walmart product search works with real user recipes
"""
import asyncio
import requests
import json
import os
from datetime import datetime

BACKEND_URL = "http://localhost:8001"

def test_user_authentication():
    """Test user login and get user info"""
    print("🔐 Testing user authentication...")
    
    # Try to login with test credentials
    login_data = {
        "email": "alannunezsilva0310@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Login successful! User ID: {user_data.get('user_id')}")
            return user_data.get('user_id')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_recipe_generation(user_id):
    """Test recipe generation and get recipe ID"""
    print("\n🍳 Testing recipe generation...")
    
    recipe_data = {
        "recipe_category": "beverage",
        "cuisine_type": "coffee", 
        "servings": 2,
        "user_id": user_id,
        "healthy_mode": False,
        "budget_mode": False
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/recipes/generate", json=recipe_data)
        print(f"Recipe generation response: {response.status_code}")
        
        if response.status_code == 200:
            recipe_data = response.json()
            recipe_id = recipe_data.get('id')
            recipe_title = recipe_data.get('title', 'Unknown')
            shopping_list = recipe_data.get('shopping_list', [])
            
            print(f"✅ Recipe generated successfully!")
            print(f"   Recipe ID: {recipe_id}")
            print(f"   Title: {recipe_title}")
            print(f"   Shopping List: {shopping_list}")
            return recipe_id, shopping_list
        else:
            print(f"❌ Recipe generation failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Recipe generation error: {str(e)}")
        return None, None

def test_walmart_cart_options(user_id, recipe_id):
    """Test Walmart cart options for the generated recipe"""
    print("\n🛒 Testing Walmart cart options...")
    
    try:
        url = f"{BACKEND_URL}/api/grocery/cart-options"
        params = {
            "recipe_id": recipe_id,
            "user_id": user_id
        }
        
        response = requests.post(url, params=params)
        print(f"Cart options response: {response.status_code}")
        
        if response.status_code == 200:
            cart_data = response.json()
            
            if 'error' in cart_data:
                print(f"❌ Cart options error: {cart_data['error']}")
                if 'debug_info' in cart_data:
                    print(f"   Debug info: {cart_data['debug_info']}")
                return False
            
            ingredient_options = cart_data.get('ingredient_options', [])
            print(f"✅ Cart options retrieved successfully!")
            print(f"   Found options for {len(ingredient_options)} ingredients")
            
            total_products = 0
            for i, option in enumerate(ingredient_options):
                ingredient_name = option.get('ingredient_name', 'Unknown')
                products = option.get('options', [])
                total_products += len(products)
                
                print(f"   Ingredient {i+1}: {ingredient_name} - {len(products)} products")
                
                # Show first 2 products for each ingredient
                for j, product in enumerate(products[:2]):
                    product_id = product.get('product_id', 'N/A')
                    product_name = product.get('name', 'N/A')
                    price = product.get('price', 0)
                    print(f"     Product {j+1}: {product_name} - ${price} (ID: {product_id})")
            
            print(f"   Total products found: {total_products}")
            return True
        else:
            print(f"❌ Cart options failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Cart options error: {str(e)}")
        return False

def test_existing_user_recipes(user_id):
    """Test Walmart cart options with existing user recipes"""
    print("\n📚 Testing existing user recipes...")
    
    try:
        # Get user recipe history
        response = requests.get(f"{BACKEND_URL}/api/recipes/history/{user_id}")
        print(f"Recipe history response: {response.status_code}")
        
        if response.status_code == 200:
            recipes = response.json()
            print(f"✅ Found {len(recipes)} existing recipes")
            
            # Test with first few existing recipes
            for i, recipe in enumerate(recipes[:3]):
                recipe_id = recipe.get('id')
                recipe_title = recipe.get('title', 'Unknown')
                shopping_list = recipe.get('shopping_list', [])
                
                print(f"\n   Testing recipe {i+1}: {recipe_title}")
                print(f"   Recipe ID: {recipe_id}")
                print(f"   Shopping List: {shopping_list}")
                
                # Test cart options for this recipe
                success = test_walmart_cart_options(user_id, recipe_id)
                if success:
                    print(f"   ✅ Walmart integration working for existing recipe!")
                else:
                    print(f"   ❌ Walmart integration failed for existing recipe")
        else:
            print(f"❌ Failed to get recipe history: {response.text}")
    except Exception as e:
        print(f"❌ Recipe history error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Testing Walmart Product Search with Real User Recipes")
    print("=" * 60)
    
    # Test 1: User authentication
    user_id = test_user_authentication()
    if not user_id:
        print("❌ Cannot proceed without user authentication")
        return
    
    # Test 2: Generate new recipe and test Walmart integration
    recipe_id, shopping_list = test_recipe_generation(user_id)
    if recipe_id and shopping_list:
        success = test_walmart_cart_options(user_id, recipe_id)
        if success:
            print("\n✅ NEW RECIPE TEST: Walmart integration working!")
        else:
            print("\n❌ NEW RECIPE TEST: Walmart integration failed")
    
    # Test 3: Test with existing user recipes
    test_existing_user_recipes(user_id)
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()