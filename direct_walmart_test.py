#!/usr/bin/env python3
"""
Direct Walmart API Test - Testing specific recipe ID from logs
"""

import requests
import json

def test_specific_recipe():
    base_url = "https://buildyoursmartcart.com/api"
    
    # Test with the specific IDs from the review request
    user_id = "efe4c5cf-982c-43ef-bb9e-12bf6581a41b"
    recipe_id = "fc23ae90-e52f-4c66-87fb-7b544bcc7803"
    
    print(f"🧪 Testing Walmart API with specific recipe")
    print(f"👤 User ID: {user_id}")
    print(f"📋 Recipe ID: {recipe_id}")
    
    # First check if recipe exists
    print("\n🔍 Checking if recipe exists...")
    recipe_response = requests.get(f"{base_url}/recipes/{recipe_id}")
    print(f"Recipe check status: {recipe_response.status_code}")
    
    if recipe_response.status_code == 200:
        recipe_data = recipe_response.json()
        print(f"✅ Recipe found: {recipe_data.get('title', 'Unknown')}")
        print(f"🛒 Shopping list: {recipe_data.get('shopping_list', [])}")
    else:
        print("❌ Recipe not found")
        return False
    
    # Test cart options
    print("\n🛒 Testing cart options...")
    cart_response = requests.post(
        f"{base_url}/grocery/cart-options",
        params={"recipe_id": recipe_id, "user_id": user_id},
        timeout=60
    )
    
    print(f"Cart options status: {cart_response.status_code}")
    
    if cart_response.status_code == 200:
        cart_data = cart_response.json()
        ingredient_options = cart_data.get('ingredient_options', [])
        
        print(f"✅ Cart options created successfully")
        print(f"📦 Found options for {len(ingredient_options)} ingredients")
        
        total_products = 0
        real_products = 0
        mock_products = 0
        
        for i, ingredient_option in enumerate(ingredient_options):
            ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
            options = ingredient_option.get('options', [])
            
            print(f"\n📦 Ingredient {i+1}: {ingredient_name}")
            print(f"   🏪 Product Options: {len(options)}")
            
            for j, product in enumerate(options):
                product_id = product.get('product_id', '')
                name = product.get('name', 'Unknown')
                price = product.get('price', 0.0)
                
                total_products += 1
                
                # Check if this is a mock product ID
                if (product_id.startswith('10315') or 
                    product_id.startswith('walmart-') or 
                    product_id.startswith('mock-') or
                    not product_id.isdigit() or
                    len(product_id) < 6):
                    mock_products += 1
                    print(f"   ❌ Product {j+1}: {name} - ${price:.2f} (MOCK ID: {product_id})")
                else:
                    real_products += 1
                    print(f"   ✅ Product {j+1}: {name} - ${price:.2f} (Real ID: {product_id})")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Products: {total_products}")
        print(f"   Real Walmart Products: {real_products}")
        print(f"   Mock Products: {mock_products}")
        
        if real_products > 0 and mock_products == 0:
            print("🎉 SUCCESS: Walmart API integration is working perfectly!")
            return True
        elif mock_products > 0:
            print("⚠️ WARNING: Mock products detected")
            return False
        else:
            print("❌ FAILURE: No products found")
            return False
    else:
        try:
            error_data = cart_response.json()
            print(f"❌ Cart options failed: {error_data}")
        except:
            print(f"❌ Cart options failed: {cart_response.text}")
        return False

if __name__ == "__main__":
    print("🧪 Direct Walmart API Test")
    print("=" * 50)
    
    success = test_specific_recipe()
    
    if success:
        print("\n✅ Walmart API integration is working correctly!")
    else:
        print("\n❌ Issues detected with Walmart API integration")