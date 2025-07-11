#!/usr/bin/env python3
"""
Test script to create a test user and verify Walmart integration
"""
import requests
import json
import time

BACKEND_URL = "http://localhost:8001"

def create_test_user():
    """Create a test user"""
    print("👤 Creating test user...")
    
    # Register test user
    registration_data = {
        "name": "Test User",
        "email": "test_walmart_user@example.com",
        "password": "testpassword123",
        "confirmPassword": "testpassword123",
        "dietary_preferences": ["None"],
        "allergies": ["None"],
        "favorite_cuisines": ["Italian"]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=registration_data)
        print(f"Registration response: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User registered successfully!")
            print(f"   User ID: {user_data.get('user_id')}")
            print(f"   Email: {user_data.get('email')}")
            return user_data.get('user_id'), user_data.get('email')
        else:
            print(f"❌ Registration failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return None, None

def verify_user(email, verification_code):
    """Verify user email"""
    print(f"\n✉️ Verifying user email: {email}")
    
    verification_data = {
        "email": email,
        "verification_code": verification_code
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/verify", json=verification_data)
        print(f"Verification response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Email verified successfully!")
            return True
        else:
            print(f"❌ Verification failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False

def login_user(email, password):
    """Login user"""
    print(f"\n🔐 Logging in user: {email}")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Login successful!")
            return user_data.get('user_id')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_recipe_and_walmart(user_id):
    """Test recipe generation and Walmart integration"""
    print(f"\n🍳 Testing recipe generation for user: {user_id}")
    
    # Test different recipe categories
    test_cases = [
        {"recipe_category": "beverage", "cuisine_type": "coffee", "name": "Coffee"},
        {"recipe_category": "cuisine", "cuisine_type": "italian", "name": "Italian Cuisine"},
        {"recipe_category": "snack", "cuisine_type": "acai bowls", "name": "Acai Bowl"}
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['name']} ---")
        
        recipe_data = {
            "recipe_category": test_case["recipe_category"],
            "cuisine_type": test_case["cuisine_type"],
            "servings": 2,
            "user_id": user_id,
            "healthy_mode": False,
            "budget_mode": False
        }
        
        try:
            # Generate recipe
            response = requests.post(f"{BACKEND_URL}/api/recipes/generate", json=recipe_data)
            print(f"Recipe generation response: {response.status_code}")
            
            if response.status_code == 200:
                recipe_data = response.json()
                recipe_id = recipe_data.get('id')
                recipe_title = recipe_data.get('title', 'Unknown')
                shopping_list = recipe_data.get('shopping_list', [])
                
                print(f"✅ Recipe generated: {recipe_title}")
                print(f"   Recipe ID: {recipe_id}")
                print(f"   Shopping List ({len(shopping_list)} items): {shopping_list}")
                
                # Test Walmart cart options
                print(f"\n   🛒 Testing Walmart cart options...")
                
                url = f"{BACKEND_URL}/api/grocery/cart-options"
                params = {
                    "recipe_id": recipe_id,
                    "user_id": user_id
                }
                
                cart_response = requests.post(url, params=params)
                print(f"   Cart options response: {cart_response.status_code}")
                
                if cart_response.status_code == 200:
                    cart_data = cart_response.json()
                    
                    if 'error' in cart_data:
                        print(f"   ❌ Cart options error: {cart_data['error']}")
                        if 'debug_info' in cart_data:
                            print(f"      Debug info: {cart_data['debug_info']}")
                    else:
                        ingredient_options = cart_data.get('ingredient_options', [])
                        total_products = sum(len(opt.get('options', [])) for opt in ingredient_options)
                        
                        print(f"   ✅ Cart options retrieved successfully!")
                        print(f"   Found {len(ingredient_options)} ingredient groups with {total_products} total products")
                        
                        # Show sample products
                        for i, option in enumerate(ingredient_options[:2]):
                            ingredient_name = option.get('ingredient_name', 'Unknown')
                            products = option.get('options', [])
                            print(f"      {ingredient_name}: {len(products)} products")
                            
                            for j, product in enumerate(products[:2]):
                                product_id = product.get('product_id', 'N/A')
                                product_name = product.get('name', 'N/A')
                                price = product.get('price', 0)
                                print(f"        - {product_name} (${price}) [ID: {product_id}]")
                else:
                    print(f"   ❌ Cart options failed: {cart_response.text}")
            else:
                print(f"❌ Recipe generation failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
        
        print(f"\n   Waiting 2 seconds before next test...")
        time.sleep(2)

def main():
    """Main test function"""
    print("🚀 Walmart Integration Test with Real User Recipes")
    print("=" * 60)
    
    # Create test user
    user_id, email = create_test_user()
    if not user_id:
        print("❌ Cannot proceed without creating user")
        return
    
    # For testing purposes, let's skip email verification and try to use the user directly
    # In production, this would require verification
    print(f"\n📝 Note: Using test user without email verification for testing purposes")
    print(f"   User ID: {user_id}")
    print(f"   Email: {email}")
    
    # Test recipe generation and Walmart integration
    test_recipe_and_walmart(user_id)
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()