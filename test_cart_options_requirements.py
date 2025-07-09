import requests
import json
import uuid
import logging
import re
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for API
BASE_URL = "http://localhost:8001/api"

def test_cart_options_endpoint():
    """
    Test the /api/grocery/cart-options endpoint to verify:
    1. The endpoint returns proper ingredient_options structure
    2. Each ingredient has multiple product options
    3. Each product option has real product_id, name, and price fields
    4. The product_ids are actual Walmart product IDs (not mock IDs like walmart-1000)
    """
    print("\n" + "=" * 80)
    print("TESTING /api/grocery/cart-options ENDPOINT")
    print("=" * 80)
    
    # Step 1: Create a test user
    user_email = f"test_{uuid.uuid4()}@example.com"
    user_password = "TestPassword123"
    
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": user_email,
        "password": user_password,
        "dietary_preferences": ["vegetarian"],
        "allergies": [],
        "favorite_cuisines": ["italian"]
    }
    
    print("\n1. Creating test user...")
    user_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    if user_response.status_code != 200:
        print(f"❌ Failed to create test user: {user_response.status_code}")
        print(user_response.text)
        return False
    
    user_id = user_response.json().get("user_id")
    print(f"✅ Created test user with ID: {user_id}")
    
    # Get verification code
    time.sleep(1)  # Wait a bit for the code to be stored
    code_response = requests.get(f"{BASE_URL}/debug/verification-codes/{user_email}")
    
    if code_response.status_code == 200 and 'codes' in code_response.json() and len(code_response.json()['codes']) > 0:
        verification_code = code_response.json()['codes'][0]['code']
        print(f"✅ Retrieved verification code: {verification_code}")
        
        # Verify email
        verify_data = {
            "email": user_email,
            "code": verification_code
        }
        
        verify_response = requests.post(f"{BASE_URL}/auth/verify", json=verify_data)
        
        if verify_response.status_code == 200:
            print("✅ Email verified successfully")
        else:
            print(f"⚠️ Email verification failed: {verify_response.status_code}")
            print(verify_response.text)
    else:
        print("⚠️ Could not retrieve verification code, continuing anyway")
    
    # Step 2: Generate a test recipe
    recipe_request = {
        "user_id": user_id,
        "cuisine_type": "italian",
        "dietary_preferences": ["vegetarian"],
        "ingredients_on_hand": ["pasta", "tomatoes", "garlic", "basil", "olive oil"],
        "prep_time_max": 30,
        "servings": 2,
        "difficulty": "easy"
    }
    
    print("\n2. Generating test recipe...")
    recipe_response = requests.post(f"{BASE_URL}/recipes/generate", json=recipe_request, timeout=60)
    
    if recipe_response.status_code != 200:
        print(f"❌ Failed to generate recipe: {recipe_response.status_code}")
        print(recipe_response.text)
        return False
    
    recipe_id = recipe_response.json().get("id")
    recipe_title = recipe_response.json().get("title")
    recipe_ingredients = recipe_response.json().get("ingredients")
    print(f"✅ Generated recipe '{recipe_title}' with ID: {recipe_id}")
    print(f"Recipe has {len(recipe_ingredients)} ingredients:")
    for i, ingredient in enumerate(recipe_ingredients):
        print(f"  {i+1}. {ingredient}")
    
    # Step 3: Test the cart-options endpoint
    print("\n3. Testing /api/grocery/cart-options endpoint...")
    cart_options_params = {
        "recipe_id": recipe_id,
        "user_id": user_id
    }
    
    cart_options_response = requests.post(f"{BASE_URL}/grocery/cart-options", params=cart_options_params)
    
    if cart_options_response.status_code != 200:
        print(f"❌ Failed to get cart options: {cart_options_response.status_code}")
        print(cart_options_response.text)
        return False
    
    cart_options = cart_options_response.json()
    
    # Verify the response structure
    if 'ingredient_options' not in cart_options:
        print("❌ Response missing 'ingredient_options' field")
        print(f"Response: {cart_options}")
        return False
    
    ingredient_options = cart_options['ingredient_options']
    print(f"✅ Response contains 'ingredient_options' with {len(ingredient_options)} ingredients")
    
    # Check if each ingredient has multiple options with required fields
    all_product_ids = []
    valid_structure = True
    multiple_options_count = 0
    
    for i, ingredient_option in enumerate(ingredient_options):
        if 'options' not in ingredient_option:
            print(f"❌ Ingredient {i+1} missing 'options' field")
            valid_structure = False
            continue
        
        options = ingredient_option['options']
        original_ingredient = ingredient_option.get('original_ingredient', 'Unknown')
        print(f"\nIngredient {i+1}: {original_ingredient}")
        print(f"  Found {len(options)} product options")
        
        if len(options) == 0:
            print(f"❌ No product options for ingredient: {original_ingredient}")
            valid_structure = False
            continue
        
        if len(options) > 1:
            multiple_options_count += 1
        
        # Check if each product has required fields
        for j, product in enumerate(options):
            required_fields = ['product_id', 'name', 'price']
            missing_fields = [field for field in required_fields if field not in product]
            
            if missing_fields:
                print(f"  ❌ Product {j+1} missing required fields: {', '.join(missing_fields)}")
                valid_structure = False
                continue
            
            product_id = product['product_id']
            all_product_ids.append(product_id)
            
            print(f"  ✅ Product {j+1}: {product['name']} - ${product['price']:.2f} (ID: {product_id})")
    
    # Check for mock data patterns
    known_mock_patterns = [
        "556677", "445566", "334455", "123456", "987654", 
        "456789", "789123", "321654", "654987", "147258"
    ]
    
    mock_pattern_matches = 0
    for pid in all_product_ids:
        if any(pid.startswith(pattern) for pattern in known_mock_patterns):
            mock_pattern_matches += 1
    
    mock_pattern_ratio = mock_pattern_matches / len(all_product_ids) if all_product_ids else 0
    
    # Step 4: Test the custom-cart endpoint with the product IDs
    print("\n4. Testing /api/grocery/custom-cart endpoint with product IDs...")
    
    # Select one product from each ingredient
    selected_products = []
    for ingredient_option in ingredient_options:
        if 'options' in ingredient_option and len(ingredient_option['options']) > 0:
            product = ingredient_option['options'][0]
            selected_products.append({
                "ingredient_name": ingredient_option.get('ingredient_name', 'item'),
                "product_id": product['product_id'],
                "name": product['name'],
                "price": product['price'],
                "quantity": 1
            })
    
    custom_cart_data = {
        "user_id": user_id,
        "recipe_id": recipe_id,
        "products": selected_products
    }
    
    custom_cart_response = requests.post(f"{BASE_URL}/grocery/custom-cart", json=custom_cart_data)
    
    if custom_cart_response.status_code != 200:
        print(f"❌ Failed to create custom cart: {custom_cart_response.status_code}")
        print(custom_cart_response.text)
    else:
        custom_cart = custom_cart_response.json()
        
        if 'walmart_url' in custom_cart:
            walmart_url = custom_cart['walmart_url']
            print(f"✅ Generated Walmart URL: {walmart_url}")
            
            # Check if all product IDs are in the URL
            product_ids = [p['product_id'] for p in selected_products]
            all_ids_in_url = all(pid in walmart_url for pid in product_ids)
            if all_ids_in_url:
                print("✅ All product IDs included in Walmart URL")
            else:
                print("❌ Not all product IDs found in Walmart URL")
        else:
            print("❌ Response missing 'walmart_url' field")
    
    # Summary
    print("\n" + "=" * 80)
    print("CART OPTIONS TEST SUMMARY")
    print("=" * 80)
    print(f"Total ingredients tested: {len(ingredient_options)}")
    print(f"Total product options found: {len(all_product_ids)}")
    print(f"Unique product IDs: {len(set(all_product_ids))}")
    
    if mock_pattern_ratio > 0.5:
        print(f"⚠️ {mock_pattern_ratio:.0%} of product IDs match known mock data patterns")
        print("⚠️ The implementation is using mock data instead of real Walmart API data")
        print("⚠️ This is confirmed by examining the server.py code which contains these exact product IDs")
    
    # Final assessment
    print("\nRequirement Assessment:")
    
    # Requirement 1: The endpoint returns proper ingredient_options structure
    if valid_structure:
        print("✅ PASS: 1. The endpoint returns proper ingredient_options structure")
    else:
        print("❌ FAIL: 1. The endpoint does not return proper ingredient_options structure")
    
    # Requirement 2: Each ingredient has multiple product options
    if multiple_options_count == len(ingredient_options):
        print("✅ PASS: 2. Each ingredient has multiple product options")
    else:
        print(f"⚠️ PARTIAL: 2. {multiple_options_count} out of {len(ingredient_options)} ingredients have multiple product options")
    
    # Requirement 3: Each product option has real product_id, name, and price fields
    if valid_structure:
        print("✅ PASS: 3. Each product option has product_id, name, and price fields")
    else:
        print("❌ FAIL: 3. Some product options are missing required fields")
    
    # Requirement 4: The product_ids are actual Walmart product IDs
    if mock_pattern_ratio < 0.3:
        print("✅ PASS: 4. The product_ids appear to be actual Walmart product IDs")
    else:
        print("❌ FAIL: 4. The product_ids are mock data, not actual Walmart product IDs")
        print("   The current implementation uses hardcoded mock product IDs instead of real Walmart API data.")
        print("   This is confirmed by examining the server.py code which contains these exact product IDs.")
        print("   The commented-out code in server.py shows that real Walmart API integration was attempted")
        print("   but is currently disabled due to 403 errors from the Walmart API.")
    
    return True

if __name__ == "__main__":
    test_cart_options_endpoint()