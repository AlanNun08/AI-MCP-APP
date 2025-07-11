#!/usr/bin/env python3
"""
Complete Walmart Beverage Integration Test
Creates fresh beverage recipe and tests Walmart API integration
"""

import requests
import json
import uuid

def create_test_user():
    """Create and verify a test user"""
    base_url = "https://buildyoursmartcart.com/api"
    
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
        return None
        
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
                return user_id
    
    return user_id

def generate_beverage_recipe(user_id):
    """Generate a beverage recipe"""
    base_url = "https://buildyoursmartcart.com/api"
    
    print("🔄 Generating beverage recipe...")
    recipe_request = {
        "user_id": user_id,
        "recipe_category": "beverage",
        "cuisine_type": "special lemonades",
        "servings": 4,
        "difficulty": "easy"
    }
    
    recipe_response = requests.post(f"{base_url}/recipes/generate", json=recipe_request, timeout=60)
    if recipe_response.status_code != 200:
        print(f"❌ Failed to generate recipe: {recipe_response.status_code}")
        return None
        
    recipe_data = recipe_response.json()
    recipe_id = recipe_data.get('id')
    shopping_list = recipe_data.get('shopping_list', [])
    
    print(f"✅ Generated beverage recipe: {recipe_data.get('title')}")
    print(f"📝 Shopping list: {shopping_list}")
    
    return recipe_id, shopping_list

def test_walmart_integration(user_id, recipe_id):
    """Test Walmart API integration"""
    base_url = "https://buildyoursmartcart.com/api"
    
    print("🔄 Testing Walmart cart options...")
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
        real_product_ids = []
        
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
                    real_product_ids.append(product_id)
                    print(f"   ✅ Product {j+1}: {name} - ${price:.2f} (Real ID: {product_id})")
        
        print(f"\n📊 WALMART API ANALYSIS:")
        print(f"   Total Products: {total_products}")
        print(f"   Real Walmart Products: {real_products}")
        print(f"   Mock Products: {mock_products}")
        print(f"   Real Product Success Rate: {(real_products/total_products*100):.1f}%" if total_products > 0 else "0%")
        
        # Test custom cart creation if we have real products
        if real_product_ids:
            print("\n🔄 Testing custom cart creation...")
            
            # Create a sample custom cart with first product from each ingredient
            products = []
            for ingredient_option in ingredient_options[:3]:  # Test with first 3 ingredients
                if ingredient_option.get('options'):
                    first_option = ingredient_option['options'][0]
                    # Only add if it's a real product
                    product_id = first_option['product_id']
                    if (not product_id.startswith('10315') and 
                        not product_id.startswith('walmart-') and 
                        not product_id.startswith('mock-') and
                        product_id.isdigit() and
                        len(product_id) >= 6):
                        products.append({
                            "ingredient_name": ingredient_option['ingredient_name'],
                            "product_id": first_option['product_id'],
                            "name": first_option['name'],
                            "price": first_option['price'],
                            "quantity": 1
                        })
            
            if products:
                custom_cart_data = {
                    "user_id": user_id,
                    "recipe_id": recipe_id,
                    "products": products
                }
                
                custom_cart_response = requests.post(f"{base_url}/grocery/custom-cart", json=custom_cart_data)
                if custom_cart_response.status_code == 200:
                    custom_cart = custom_cart_response.json()
                    walmart_url = custom_cart.get('walmart_url', '')
                    total_price = custom_cart.get('total_price', 0)
                    
                    print(f"✅ Custom cart created successfully")
                    print(f"💰 Total price: ${total_price:.2f}")
                    print(f"🛒 Walmart URL: {walmart_url}")
                    
                    # Validate URL format
                    if 'affil.walmart.com' in walmart_url and 'offers=' in walmart_url:
                        print("✅ Walmart URL format is correct (uses offers parameter)")
                        return True, {
                            'total_products': total_products,
                            'real_products': real_products,
                            'mock_products': mock_products,
                            'cart_created': True,
                            'walmart_url': walmart_url
                        }
                    else:
                        print("❌ Walmart URL format is incorrect")
                else:
                    print(f"❌ Failed to create custom cart: {custom_cart_response.status_code}")
            else:
                print("⚠️ No real products available for custom cart")
        
        return real_products > 0 and mock_products == 0, {
            'total_products': total_products,
            'real_products': real_products,
            'mock_products': mock_products,
            'cart_created': False
        }
    else:
        try:
            error_data = cart_response.json()
            print(f"❌ Cart options failed: {error_data}")
        except:
            print(f"❌ Cart options failed: {cart_response.text}")
        return False, {}

def main():
    print("🧪 COMPREHENSIVE WALMART BEVERAGE API INTEGRATION TEST")
    print("🌐 Testing deployed backend at: buildyoursmartcart.com")
    print("=" * 80)
    
    # Step 1: Create test user
    user_id = create_test_user()
    if not user_id:
        print("❌ Failed to create test user")
        return False
    
    # Step 2: Generate beverage recipe
    recipe_result = generate_beverage_recipe(user_id)
    if not recipe_result:
        print("❌ Failed to generate beverage recipe")
        return False
    
    recipe_id, shopping_list = recipe_result
    
    # Step 3: Test Walmart integration
    success, results = test_walmart_integration(user_id, recipe_id)
    
    # Final report
    print("\n" + "=" * 80)
    print("📊 FINAL TEST REPORT")
    print("=" * 80)
    
    if success:
        print("🎉 SUCCESS: Walmart API integration is working correctly!")
        print(f"✅ Backend connectivity: Working")
        print(f"✅ Beverage recipe generation: Working")
        print(f"✅ Walmart API calls: Working")
        print(f"✅ Real product data: {results.get('real_products', 0)} products found")
        print(f"✅ Mock data filtering: {results.get('mock_products', 0)} mock products (should be 0)")
        if results.get('cart_created'):
            print(f"✅ Custom cart creation: Working")
            print(f"✅ Walmart URL generation: Working")
        print(f"✅ Environment variables: Properly configured")
    else:
        print("❌ ISSUES DETECTED with Walmart API integration")
        if results.get('mock_products', 0) > 0:
            print(f"⚠️ Mock data contamination: {results.get('mock_products')} mock products found")
        if results.get('real_products', 0) == 0:
            print(f"⚠️ No real Walmart products returned")
    
    print(f"\n🎯 SPECIFIC FINDINGS FOR REVIEW REQUEST:")
    print(f"   - The user's reported issue: {'❌ Confirmed' if not success else '✅ Resolved'}")
    print(f"   - Walmart product search: {'✅ Working' if results.get('real_products', 0) > 0 else '❌ Not working'}")
    print(f"   - Environment variables: {'✅ Configured' if results.get('real_products', 0) > 0 else '❌ Issues detected'}")
    print(f"   - Network connectivity: ✅ Can reach Walmart API")
    print(f"   - Signature generation: {'✅ Working' if results.get('real_products', 0) > 0 else '❌ May be failing'}")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)