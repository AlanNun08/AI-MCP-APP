#!/usr/bin/env python3
"""
Quick Walmart Cart Test for Beverage Recipes
"""

import requests
import json
import uuid

def test_walmart_cart_with_beverage():
    base_url = "http://localhost:8001/api"
    
    # Create a test user
    test_email = f"walmart_test_{uuid.uuid4()}@example.com"
    user_data = {
        "first_name": "Walmart",
        "last_name": "Test",
        "email": test_email,
        "password": "SecureP@ssw0rd123",
        "dietary_preferences": [],
        "allergies": [],
        "favorite_cuisines": []
    }
    
    print("🔄 Creating test user...")
    response = requests.post(f"{base_url}/auth/register", json=user_data)
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.status_code}")
        return False
        
    user_id = response.json().get('user_id')
    print(f"✅ Created user: {user_id}")
    
    # Get verification code and verify
    code_response = requests.get(f"{base_url}/debug/verification-codes/{test_email}")
    if code_response.status_code == 200:
        code_data = code_response.json()
        verification_code = None
        if 'codes' in code_data and len(code_data['codes']) > 0:
            verification_code = code_data['codes'][0]['code']
        elif 'last_test_code' in code_data:
            verification_code = code_data['last_test_code']
            
        if verification_code:
            verify_data = {"email": test_email, "code": verification_code}
            verify_response = requests.post(f"{base_url}/auth/verify", json=verify_data)
            if verify_response.status_code == 200:
                print("✅ User verified")
            else:
                print("❌ Failed to verify user")
                return False
    
    # Generate beverage recipe
    print("🔄 Generating beverage recipe...")
    recipe_request = {
        "user_id": user_id,
        "recipe_category": "beverage",
        "servings": 4,
        "difficulty": "easy"
    }
    
    recipe_response = requests.post(f"{base_url}/recipes/generate", json=recipe_request, timeout=60)
    if recipe_response.status_code != 200:
        print(f"❌ Failed to generate recipe: {recipe_response.status_code}")
        return False
        
    recipe_data = recipe_response.json()
    recipe_id = recipe_data.get('id')
    shopping_list = recipe_data.get('shopping_list', [])
    
    print(f"✅ Generated beverage recipe: {recipe_data.get('title')}")
    print(f"📝 Shopping list: {shopping_list}")
    
    # Test Walmart cart options
    print("🔄 Testing Walmart cart options...")
    cart_response = requests.post(
        f"{base_url}/grocery/cart-options",
        params={"recipe_id": recipe_id, "user_id": user_id},
        timeout=30
    )
    
    if cart_response.status_code == 200:
        cart_data = cart_response.json()
        print(f"✅ Walmart cart options created successfully")
        print(f"📦 Found options for {len(cart_data.get('ingredient_options', []))} ingredients")
        
        # Test custom cart creation
        if cart_data.get('ingredient_options'):
            print("🔄 Testing custom cart creation...")
            
            # Create a sample custom cart with first product from each ingredient
            products = []
            for ingredient_option in cart_data['ingredient_options'][:3]:  # Test with first 3 ingredients
                if ingredient_option.get('options'):
                    first_option = ingredient_option['options'][0]
                    products.append({
                        "ingredient_name": ingredient_option['ingredient_name'],
                        "product_id": first_option['product_id'],
                        "name": first_option['name'],
                        "price": first_option['price'],
                        "quantity": 1
                    })
            
            custom_cart_data = {
                "user_id": user_id,
                "recipe_id": recipe_id,
                "products": products
            }
            
            custom_cart_response = requests.post(f"{base_url}/grocery/custom-cart", json=custom_cart_data)
            if custom_cart_response.status_code == 200:
                custom_cart = custom_cart_response.json()
                print(f"✅ Custom cart created successfully")
                print(f"💰 Total price: ${custom_cart.get('total_price', 0):.2f}")
                print(f"🛒 Walmart URL: {custom_cart.get('walmart_url', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to create custom cart: {custom_cart_response.status_code}")
                return False
        else:
            print("⚠️ No ingredient options found")
            return False
    else:
        print(f"❌ Failed to create cart options: {cart_response.status_code}")
        return False

if __name__ == "__main__":
    print("🧋 Testing Walmart Cart Integration with Beverage Recipes")
    print("=" * 60)
    
    success = test_walmart_cart_with_beverage()
    
    if success:
        print("\n✅ Walmart cart integration with beverage recipes is working!")
    else:
        print("\n❌ Issues detected with Walmart cart integration")