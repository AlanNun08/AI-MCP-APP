import requests
import json
import uuid
import time
import sys

def run_test(name, method, endpoint, expected_status, data=None, params=None, timeout=30):
    base_url = "https://3de015a9-d2f3-4c69-92f0-7a535d17381f.preview.emergentagent.com/api"
    url = f"{base_url}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    print(f"\n🔍 Testing {name}...")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
        else:
            print(f"❌ Unsupported method: {method}")
            return False, {}
        
        success = response.status_code == expected_status
        
        if success:
            print(f"✅ Passed - Status: {response.status_code}")
            try:
                return success, response.json()
            except:
                return success, {}
        else:
            print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"Response: {error_data}")
                return False, error_data
            except:
                print(f"Response: {response.text}")
                return False, {}
    except Exception as e:
        print(f"❌ Failed - Error: {str(e)}")
        return False, {}

def test_email_verification():
    print("\n" + "=" * 50)
    print("Testing Email Verification System")
    print("=" * 50)
    
    # Generate a unique email for testing
    email = f"test.user{uuid.uuid4()}@example.com"
    password = "SecureP@ssw0rd123"
    
    # Register user
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": password,
        "dietary_preferences": ["vegetarian"],
        "allergies": ["nuts"],
        "favorite_cuisines": ["italian", "mexican"]
    }
    
    success, response = run_test(
        "User Registration",
        "POST",
        "auth/register",
        200,
        data=user_data
    )
    
    if not success:
        return False
    
    # Get verification code
    success, code_response = run_test(
        "Get Verification Code",
        "GET",
        f"debug/verification-codes/{email}",
        200
    )
    
    if not success or 'codes' not in code_response or len(code_response['codes']) == 0:
        print("❌ Failed to get verification code")
        return False
    
    verification_code = code_response['codes'][0]['code']
    print(f"Retrieved verification code: {verification_code}")
    
    # Verify email
    verify_data = {
        "email": email,
        "code": verification_code
    }
    
    success, _ = run_test(
        "Email Verification",
        "POST",
        "auth/verify",
        200,
        data=verify_data
    )
    
    if not success:
        return False
    
    # Login with verified user
    login_data = {
        "email": email,
        "password": password
    }
    
    success, login_response = run_test(
        "Login with Verified User",
        "POST",
        "auth/login",
        200,
        data=login_data
    )
    
    if not success:
        return False
    
    # Test case-insensitive email handling
    email_parts = email.split('@')
    mixed_case_email = ''.join([c.upper() if i % 2 == 0 else c for i, c in enumerate(email_parts[0])]) + '@' + email_parts[1]
    
    login_data = {
        "email": mixed_case_email,
        "password": password
    }
    
    success, _ = run_test(
        "Login with Mixed Case Email",
        "POST",
        "auth/login",
        200,
        data=login_data
    )
    
    if not success:
        return False
    
    # Test duplicate email registration
    success, _ = run_test(
        "Duplicate Email Registration",
        "POST",
        "auth/register",
        400,
        data=user_data
    )
    
    # Test invalid verification code
    invalid_verify_data = {
        "email": email,
        "code": "999999"  # Invalid code
    }
    
    success, _ = run_test(
        "Invalid Verification Code",
        "POST",
        "auth/verify",
        400,
        data=invalid_verify_data
    )
    
    # Test resend verification code
    # Register a new user for this test
    resend_email = f"resend_{uuid.uuid4()}@example.com"
    
    resend_user_data = {
        "first_name": "Resend",
        "last_name": "Test",
        "email": resend_email,
        "password": "SecureP@ssw0rd456",
        "dietary_preferences": [],
        "allergies": [],
        "favorite_cuisines": []
    }
    
    success, _ = run_test(
        "Register User for Resend Test",
        "POST",
        "auth/register",
        200,
        data=resend_user_data
    )
    
    if not success:
        return False
    
    # Resend verification code
    resend_data = {
        "email": resend_email
    }
    
    success, _ = run_test(
        "Resend Verification Code",
        "POST",
        "auth/resend-code",
        200,
        data=resend_data
    )
    
    return True

def test_openai_integration():
    print("\n" + "=" * 50)
    print("Testing OpenAI Integration")
    print("=" * 50)
    
    # Create a user for testing
    email = f"openai_{uuid.uuid4()}@example.com"
    password = "SecureP@ssw0rd123"
    
    # Register user
    user_data = {
        "first_name": "OpenAI",
        "last_name": "Test",
        "email": email,
        "password": password,
        "dietary_preferences": ["vegetarian"],
        "allergies": [],
        "favorite_cuisines": ["italian"]
    }
    
    success, response = run_test(
        "User Registration for OpenAI Test",
        "POST",
        "auth/register",
        200,
        data=user_data
    )
    
    if not success:
        return False
    
    # Get verification code
    success, code_response = run_test(
        "Get Verification Code",
        "GET",
        f"debug/verification-codes/{email}",
        200
    )
    
    if not success or 'codes' not in code_response or len(code_response['codes']) == 0:
        print("❌ Failed to get verification code")
        return False
    
    verification_code = code_response['codes'][0]['code']
    
    # Verify email
    verify_data = {
        "email": email,
        "code": verification_code
    }
    
    success, _ = run_test(
        "Email Verification",
        "POST",
        "auth/verify",
        200,
        data=verify_data
    )
    
    if not success:
        return False
    
    # Login
    login_data = {
        "email": email,
        "password": password
    }
    
    success, login_response = run_test(
        "Login",
        "POST",
        "auth/login",
        200,
        data=login_data
    )
    
    if not success or 'user' not in login_response:
        return False
    
    user_id = login_response['user']['id']
    
    # Generate recipe
    recipe_request = {
        "user_id": user_id,
        "cuisine_type": "italian",
        "dietary_preferences": ["vegetarian"],
        "ingredients_on_hand": ["pasta", "tomatoes", "garlic"],
        "prep_time_max": 30,
        "servings": 2,
        "difficulty": "easy"
    }
    
    success, recipe_response = run_test(
        "Generate Recipe",
        "POST",
        "recipes/generate",
        200,
        data=recipe_request,
        timeout=60
    )
    
    if not success:
        return False
    
    recipe_id = recipe_response['id']
    
    # Get recipe
    success, _ = run_test(
        "Get Recipe",
        "GET",
        f"recipes/{recipe_id}",
        200
    )
    
    if not success:
        return False
    
    # Generate healthy recipe
    healthy_recipe_request = {
        "user_id": user_id,
        "cuisine_type": "mediterranean",
        "dietary_preferences": ["vegetarian"],
        "ingredients_on_hand": ["chickpeas", "olive oil", "tomatoes"],
        "prep_time_max": 30,
        "servings": 2,
        "difficulty": "medium",
        "is_healthy": True,
        "max_calories_per_serving": 400
    }
    
    success, healthy_recipe_response = run_test(
        "Generate Healthy Recipe",
        "POST",
        "recipes/generate",
        200,
        data=healthy_recipe_request,
        timeout=60
    )
    
    if not success:
        return False
    
    # Generate budget recipe
    budget_recipe_request = {
        "user_id": user_id,
        "cuisine_type": "american",
        "dietary_preferences": [],
        "ingredients_on_hand": ["potatoes", "onions", "beans"],
        "prep_time_max": 45,
        "servings": 4,
        "difficulty": "easy",
        "is_budget_friendly": True,
        "max_budget": 15.0
    }
    
    success, _ = run_test(
        "Generate Budget-Friendly Recipe",
        "POST",
        "recipes/generate",
        200,
        data=budget_recipe_request,
        timeout=60
    )
    
    return success

def test_walmart_integration():
    print("\n" + "=" * 50)
    print("Testing Walmart Integration")
    print("=" * 50)
    
    # Create a user for testing
    email = f"walmart_{uuid.uuid4()}@example.com"
    password = "SecureP@ssw0rd123"
    
    # Register user
    user_data = {
        "first_name": "Walmart",
        "last_name": "Test",
        "email": email,
        "password": password,
        "dietary_preferences": ["vegetarian"],
        "allergies": [],
        "favorite_cuisines": ["italian"]
    }
    
    success, response = run_test(
        "User Registration for Walmart Test",
        "POST",
        "auth/register",
        200,
        data=user_data
    )
    
    if not success:
        return False
    
    # Get verification code
    success, code_response = run_test(
        "Get Verification Code",
        "GET",
        f"debug/verification-codes/{email}",
        200
    )
    
    if not success or 'codes' not in code_response or len(code_response['codes']) == 0:
        print("❌ Failed to get verification code")
        return False
    
    verification_code = code_response['codes'][0]['code']
    
    # Verify email
    verify_data = {
        "email": email,
        "code": verification_code
    }
    
    success, _ = run_test(
        "Email Verification",
        "POST",
        "auth/verify",
        200,
        data=verify_data
    )
    
    if not success:
        return False
    
    # Login
    login_data = {
        "email": email,
        "password": password
    }
    
    success, login_response = run_test(
        "Login",
        "POST",
        "auth/login",
        200,
        data=login_data
    )
    
    if not success or 'user' not in login_response:
        return False
    
    user_id = login_response['user']['id']
    
    # Generate recipe
    recipe_request = {
        "user_id": user_id,
        "cuisine_type": "italian",
        "dietary_preferences": ["vegetarian"],
        "ingredients_on_hand": ["pasta", "tomatoes", "garlic"],
        "prep_time_max": 30,
        "servings": 2,
        "difficulty": "easy"
    }
    
    success, recipe_response = run_test(
        "Generate Recipe",
        "POST",
        "recipes/generate",
        200,
        data=recipe_request,
        timeout=60
    )
    
    if not success:
        return False
    
    recipe_id = recipe_response['id']
    
    # Create grocery cart with options
    success, cart_options_response = run_test(
        "Create Grocery Cart with Options",
        "POST",
        "grocery/cart-options",
        200,
        params={"recipe_id": recipe_id, "user_id": user_id}
    )
    
    if not success:
        return False
    
    # Create custom cart
    custom_cart_data = {
        "user_id": user_id,
        "recipe_id": recipe_id,
        "products": [
            {
                "ingredient_name": "pasta",
                "product_id": "12345",
                "name": "Barilla Pasta",
                "price": 2.99,
                "quantity": 1
            },
            {
                "ingredient_name": "tomatoes",
                "product_id": "67890",
                "name": "Roma Tomatoes",
                "price": 1.99,
                "quantity": 2
            },
            {
                "ingredient_name": "garlic",
                "product_id": "54321",
                "name": "Fresh Garlic",
                "price": 0.99,
                "quantity": 1
            }
        ]
    }
    
    success, custom_cart_response = run_test(
        "Create Custom Cart",
        "POST",
        "grocery/custom-cart",
        200,
        data=custom_cart_data
    )
    
    if not success:
        return False
    
    # Verify Walmart URL format
    if 'walmart_url' in custom_cart_response:
        walmart_url = custom_cart_response['walmart_url']
        if 'affil.walmart.com' in walmart_url and 'items=' in walmart_url:
            print("✅ Walmart URL correctly formatted")
            
            # Check if all product IDs are in the URL
            product_ids = [p['product_id'] for p in custom_cart_data['products']]
            all_ids_in_url = all(pid in walmart_url for pid in product_ids)
            if all_ids_in_url:
                print("✅ All product IDs included in Walmart URL")
            else:
                print("⚠️ Not all product IDs found in Walmart URL")
        else:
            print("⚠️ Walmart URL format may be incorrect")
    
    return True

def main():
    print("=" * 50)
    print("AI Recipe & Grocery App API Test")
    print("=" * 50)
    
    # Test API root
    success, _ = run_test("API Root", "GET", "", 200)
    
    if not success:
        print("❌ API root test failed. Aborting further tests.")
        return 1
    
    # Test Email Verification System
    email_verification_success = test_email_verification()
    
    # Test OpenAI Integration
    openai_success = test_openai_integration()
    
    # Test Walmart Integration
    walmart_success = test_walmart_integration()
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Email Verification System: {'✅ PASSED' if email_verification_success else '❌ FAILED'}")
    print(f"OpenAI Integration: {'✅ PASSED' if openai_success else '❌ FAILED'}")
    print(f"Walmart Integration: {'✅ PASSED' if walmart_success else '❌ FAILED'}")
    print("=" * 50)
    
    return 0 if email_verification_success and openai_success and walmart_success else 1

if __name__ == "__main__":
    sys.exit(main())