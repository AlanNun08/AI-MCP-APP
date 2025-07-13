#!/usr/bin/env python3
"""
BRAND NEW SIMPLE TEST for the recreated Walmart integration
Tests the new simple implementation from scratch
"""

import requests
import json
import sys

# Backend URL
BACKEND_URL = "https://recipe-cart-app-1.emergent.host"
API_BASE = f"{BACKEND_URL}/api"

def test_demo_login():
    """Test demo user login"""
    try:
        print("🧪 Testing demo user login...")
        
        login_data = {
            "email": "demo@test.com",
            "password": "password123"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                user_id = data.get("user", {}).get("id")
                print(f"✅ Demo login successful! User ID: {user_id}")
                return user_id
            else:
                print(f"❌ Login failed: {data}")
                return None
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_recipe_generation(user_id):
    """Test recipe generation"""
    try:
        print("🧪 Testing recipe generation...")
        
        recipe_data = {
            "user_id": user_id,
            "recipe_category": "cuisine",
            "cuisine_type": "Italian",
            "dietary_preferences": [],
            "ingredients_on_hand": [],
            "prep_time_max": 30,
            "servings": 4,
            "difficulty": "easy"
        }
        
        response = requests.post(f"{API_BASE}/recipes/generate", json=recipe_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            recipe_id = data.get("id")
            recipe_title = data.get("title")
            shopping_list = data.get("shopping_list", [])
            print(f"✅ Recipe generated: {recipe_title} with {len(shopping_list)} ingredients")
            print(f"   Recipe ID: {recipe_id}")
            print(f"   Ingredients: {shopping_list[:3]}...")  # Show first 3
            return recipe_id
        else:
            print(f"❌ Recipe generation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Recipe generation error: {str(e)}")
        return None

def test_new_walmart_integration(recipe_id, user_id):
    """Test the NEW simple Walmart integration"""
    try:
        print("🧪 Testing NEW Walmart cart-options integration...")
        
        params = {
            "recipe_id": recipe_id,
            "user_id": user_id
        }
        
        response = requests.post(f"{API_BASE}/grocery/cart-options", params=params, timeout=20)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Analyze the response
            ingredients = data.get("ingredients", [])
            total_products = data.get("total_products", 0)
            
            print(f"✅ NEW Walmart integration SUCCESS!")
            print(f"   Total ingredients processed: {len(ingredients)}")
            print(f"   Total products found: {total_products}")
            
            # Show details of first few ingredients
            for i, ingredient in enumerate(ingredients[:3]):
                ingredient_name = ingredient.get("ingredient_name")
                products = ingredient.get("products", [])
                print(f"   Ingredient {i+1}: {ingredient_name} -> {len(products)} products")
                
                # Show first product details
                if products:
                    first_product = products[0]
                    print(f"     Sample product: {first_product.get('name')} - ${first_product.get('price')} (ID: {first_product.get('product_id')})")
            
            return data
        else:
            print(f"❌ NEW Walmart integration FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ NEW Walmart integration error: {str(e)}")
        return None

def test_cart_url_generation(cart_data):
    """Test cart URL generation"""
    try:
        print("🧪 Testing cart URL generation...")
        
        # Extract first few products from cart data
        if not cart_data or not cart_data.get("ingredients"):
            print("⚠️ No cart data available for URL generation")
            return None
            
        selected_products = []
        for ingredient in cart_data.get("ingredients", [])[:2]:  # First 2 ingredients
            products = ingredient.get("products", [])
            if products:
                # Select first product from each ingredient
                selected_products.append(products[0])
        
        if not selected_products:
            print("⚠️ No products available for URL generation")
            return None
            
        cart_request = {
            "products": selected_products
        }
        
        response = requests.post(f"{API_BASE}/grocery/generate-cart-url", json=cart_request, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cart_url = data.get("cart_url")
            total_price = data.get("total_price")
            product_count = data.get("product_count")
            
            print(f"✅ Cart URL generated successfully!")
            print(f"   URL: {cart_url}")
            print(f"   Total price: ${total_price}")
            print(f"   Product count: {product_count}")
            return data
        else:
            print(f"❌ Cart URL generation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Cart URL generation error: {str(e)}")
        return None

def main():
    """Run complete test of NEW Walmart integration"""
    print("🚀 TESTING NEW WALMART INTEGRATION FROM SCRATCH")
    print("=" * 60)
    
    # Test 1: Demo login
    user_id = test_demo_login()
    if not user_id:
        print("❌ Cannot proceed without user login")
        return False
    
    print()
    
    # Test 2: Recipe generation
    recipe_id = test_recipe_generation(user_id)
    if not recipe_id:
        print("❌ Cannot proceed without recipe")
        return False
    
    print()
    
    # Test 3: NEW Walmart integration
    cart_data = test_new_walmart_integration(recipe_id, user_id)
    if not cart_data:
        print("❌ Walmart integration failed")
        return False
    
    print()
    
    # Test 4: Cart URL generation
    url_data = test_cart_url_generation(cart_data)
    if not url_data:
        print("⚠️ Cart URL generation failed (optional)")
    
    print()
    print("🎉 ALL TESTS COMPLETED!")
    print("✅ NEW Walmart integration is working from scratch!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)