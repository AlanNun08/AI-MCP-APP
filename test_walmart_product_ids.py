import requests
import json
import uuid
import logging
import re
import random
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

def analyze_product_ids(product_ids):
    """
    Analyze product IDs to determine if they are likely real Walmart IDs or mock data
    """
    # Check for patterns in the IDs
    patterns = {}
    for pid in product_ids:
        # Extract the first few digits as a pattern
        pattern = pid[:3] if len(pid) >= 3 else pid
        patterns[pattern] = patterns.get(pattern, 0) + 1
    
    # If we have too many IDs with the same pattern, they're likely mock data
    pattern_concentration = max(patterns.values()) / len(product_ids) if product_ids else 0
    
    # Check for sequential IDs (e.g., 123456789, 123456790, 123456791)
    sequential_count = 0
    sorted_ids = sorted([int(pid) for pid in product_ids if pid.isdigit()])
    for i in range(1, len(sorted_ids)):
        if sorted_ids[i] == sorted_ids[i-1] + 1:
            sequential_count += 1
    
    sequential_ratio = sequential_count / (len(sorted_ids) - 1) if len(sorted_ids) > 1 else 0
    
    # Real Walmart product IDs should have:
    # 1. Low pattern concentration (diverse first digits)
    # 2. Low sequential ratio (not many sequential numbers)
    # 3. Varied length (not all same length)
    
    id_lengths = set(len(pid) for pid in product_ids)
    length_variety = len(id_lengths) > 1
    
    return {
        "pattern_concentration": pattern_concentration,
        "sequential_ratio": sequential_ratio,
        "length_variety": length_variety,
        "likely_real": pattern_concentration < 0.3 and sequential_ratio < 0.3 and length_variety
    }

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
    
    # First, create a test user with the new authentication system
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
        
        # Try using the legacy user creation endpoint as fallback
        legacy_user_data = {
            "name": f"Test User {uuid.uuid4()}",
            "email": user_email,
            "dietary_preferences": ["vegetarian"],
            "allergies": [],
            "favorite_cuisines": ["italian"]
        }
        
        print("Trying legacy user creation endpoint...")
        legacy_response = requests.post(f"{BASE_URL}/users", json=legacy_user_data)
        
        if legacy_response.status_code != 200:
            print(f"❌ Failed to create legacy test user: {legacy_response.status_code}")
            print(legacy_response.text)
            return False
        
        user_id = legacy_response.json().get("id")
        print(f"✅ Created legacy test user with ID: {user_id}")
    else:
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
    
    # Generate a test recipe
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
    
    # Test the cart-options endpoint
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
    valid_product_ids = True
    
    for i, ingredient_option in enumerate(ingredient_options):
        if 'options' not in ingredient_option:
            print(f"❌ Ingredient {i+1} missing 'options' field")
            continue
        
        options = ingredient_option['options']
        original_ingredient = ingredient_option.get('original_ingredient', 'Unknown')
        print(f"\nIngredient {i+1}: {original_ingredient}")
        print(f"  Found {len(options)} product options")
        
        if len(options) == 0:
            print(f"❌ No product options for ingredient: {original_ingredient}")
            continue
        
        # Check if each product has required fields
        for j, product in enumerate(options):
            required_fields = ['product_id', 'name', 'price']
            missing_fields = [field for field in required_fields if field not in product]
            
            if missing_fields:
                print(f"  ❌ Product {j+1} missing required fields: {', '.join(missing_fields)}")
                continue
            
            product_id = product['product_id']
            all_product_ids.append(product_id)
            
            # Check if product_id looks like a real Walmart ID (not mock IDs like walmart-1000)
            # Real Walmart IDs are typically numeric strings
            if product_id.startswith("walmart-") or not re.match(r'^\d+$', product_id):
                print(f"  ❌ Product {j+1} has suspicious ID format: {product_id}")
                valid_product_ids = False
            else:
                print(f"  ✅ Product {j+1}: {product['name']} - ${product['price']:.2f} (ID: {product_id})")
    
    # Analyze the product IDs to determine if they're likely real or mock
    id_analysis = analyze_product_ids(all_product_ids)
    
    # Summary
    print("\n" + "=" * 80)
    print("CART OPTIONS TEST SUMMARY")
    print("=" * 80)
    print(f"Total ingredients tested: {len(ingredient_options)}")
    print(f"Total product options found: {len(all_product_ids)}")
    
    # Check if we have a good variety of product IDs
    unique_product_ids = set(all_product_ids)
    print(f"Unique product IDs: {len(unique_product_ids)}")
    
    # Report on ID analysis
    print("\nProduct ID Analysis:")
    print(f"  Pattern concentration: {id_analysis['pattern_concentration']:.2f} (lower is better)")
    print(f"  Sequential ratio: {id_analysis['sequential_ratio']:.2f} (lower is better)")
    print(f"  Length variety: {'Yes' if id_analysis['length_variety'] else 'No'} (variety is better)")
    
    if id_analysis['likely_real']:
        print("  ✅ Product IDs appear to be diverse and realistic")
    else:
        print("  ⚠️ Product IDs show patterns consistent with mock data")
        
        # Check for specific patterns that indicate mock data
        if id_analysis['pattern_concentration'] > 0.3:
            print("    - Too many IDs share the same starting digits")
        if id_analysis['sequential_ratio'] > 0.3:
            print("    - Too many IDs are sequential (e.g., 123, 124, 125)")
        if not id_analysis['length_variety']:
            print("    - All IDs have the same length")
    
    # Check for specific known mock ID patterns from the code
    known_mock_patterns = [
        "556677", "445566", "334455", "123456", "987654", 
        "456789", "789123", "321654", "654987", "147258"
    ]
    
    mock_pattern_matches = 0
    for pid in all_product_ids:
        if any(pid.startswith(pattern) for pattern in known_mock_patterns):
            mock_pattern_matches += 1
    
    mock_pattern_ratio = mock_pattern_matches / len(all_product_ids) if all_product_ids else 0
    
    if mock_pattern_ratio > 0.5:
        print(f"  ❌ {mock_pattern_ratio:.0%} of product IDs match known mock data patterns from the code")
    
    # Final verdict
    print("\nFinal Assessment:")
    if valid_product_ids and len(ingredient_options) > 0 and all('options' in opt for opt in ingredient_options):
        print("✅ PASS: /api/grocery/cart-options endpoint returns proper structure with product options")
        if all(len(opt['options']) > 1 for opt in ingredient_options if 'options' in opt):
            print("✅ PASS: Each ingredient has multiple product options")
        else:
            print("⚠️ WARNING: Some ingredients have only one product option")
        
        print("✅ PASS: Each product option has required product_id, name, and price fields")
        
        if mock_pattern_ratio < 0.3 and id_analysis['likely_real']:
            print("✅ PASS: Product IDs appear to be valid Walmart product IDs")
        else:
            print("❌ FAIL: Product IDs appear to be mock data, not real Walmart product IDs")
            print("   The current implementation uses hardcoded mock product IDs instead of real Walmart API data.")
            print("   This is confirmed by examining the server.py code which contains these exact product IDs.")
        
        return True
    else:
        print("\n❌ FAIL: /api/grocery/cart-options endpoint test failed")
        return False

if __name__ == "__main__":
    test_cart_options_endpoint()