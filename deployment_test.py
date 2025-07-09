#!/usr/bin/env python3
import requests
import json
import time
import sys
import uuid
import logging
import random
from datetime import datetime, timedelta
import os

# Import the existing tester class
from backend_test import AIRecipeAppTester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_deployment_readiness_tests():
    """Run comprehensive deployment readiness tests for AI Chef app"""
    print("=" * 80)
    print("🚀 AI CHEF APP - DEPLOYMENT READINESS TESTING 🚀")
    print("=" * 80)
    
    # Get backend URL from frontend .env file
    backend_url = None
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.strip().split('=', 1)[1].strip('"\'')
                    break
    except Exception as e:
        print(f"⚠️ Error reading frontend .env file: {str(e)}")
    
    if not backend_url:
        print("⚠️ Could not find REACT_APP_BACKEND_URL in frontend .env, using default")
        backend_url = "http://localhost:8001"
    
    print(f"🔗 Using backend URL: {backend_url}")
    
    # Initialize tester with the correct backend URL
    tester = AIRecipeAppTester(base_url=backend_url)
    
    # Track test results for final report
    test_results = {
        "User Registration & Authentication": {
            "status": "Not Tested",
            "details": []
        },
        "Recipe Generation System": {
            "status": "Not Tested",
            "details": []
        },
        "Interactive Walmart Cart System": {
            "status": "Not Tested",
            "details": []
        },
        "Recipe History & Management": {
            "status": "Not Tested",
            "details": []
        },
        "Error Handling & Edge Cases": {
            "status": "Not Tested",
            "details": []
        }
    }
    
    # 1. User Registration & Authentication Flow
    print("\n" + "=" * 80)
    print("1. TESTING USER REGISTRATION & AUTHENTICATION FLOW")
    print("=" * 80)
    
    # Generate unique test user credentials
    timestamp = int(time.time())
    test_email = f"test_deploy_{timestamp}@example.com"
    test_password = f"SecureP@ss{timestamp % 1000}"
    
    # Test user registration
    print("\n🔍 Testing user registration with all required fields...")
    user_data = {
        "first_name": "Deploy",
        "last_name": "Test",
        "email": test_email,
        "password": test_password,
        "dietary_preferences": ["vegetarian", "low-carb"],
        "allergies": ["nuts", "shellfish"],
        "favorite_cuisines": ["italian", "mexican", "indian"]
    }
    
    register_success, register_response = tester.run_test(
        "User Registration",
        "POST",
        "auth/register",
        200,
        data=user_data
    )
    
    if register_success and 'user_id' in register_response:
        user_id = register_response['user_id']
        test_results["User Registration & Authentication"]["details"].append(
            "✅ User registration successful with all required fields"
        )
        
        # Test email verification system
        print("\n🔍 Testing email verification system...")
        code_success, code_response = tester.run_test(
            "Get Verification Code",
            "GET",
            f"debug/verification-codes/{test_email}",
            200
        )
        
        verification_code = None
        if code_success:
            if 'codes' in code_response and len(code_response['codes']) > 0:
                verification_code = code_response['codes'][0]['code']
                test_results["User Registration & Authentication"]["details"].append(
                    f"✅ Retrieved verification code: {verification_code}"
                )
            elif 'last_test_code' in code_response and code_response['last_test_code']:
                verification_code = code_response['last_test_code']
                test_results["User Registration & Authentication"]["details"].append(
                    f"✅ Retrieved verification code from last_test_code: {verification_code}"
                )
            else:
                test_results["User Registration & Authentication"]["details"].append(
                    "❌ No verification code found"
                )
        else:
            test_results["User Registration & Authentication"]["details"].append(
                "❌ Failed to retrieve verification code"
            )
        
        if verification_code:
            # Verify email
            verify_data = {
                "email": test_email,
                "code": verification_code
            }
            
            verify_success, verify_response = tester.run_test(
                "Email Verification",
                "POST",
                "auth/verify",
                200,
                data=verify_data
            )
            
            if verify_success:
                test_results["User Registration & Authentication"]["details"].append(
                    "✅ Email verification successful"
                )
                
                # Test login with verified account
                print("\n🔍 Testing login with verified account...")
                login_data = {
                    "email": test_email,
                    "password": test_password
                }
                
                login_success, login_response = tester.run_test(
                    "Login with Verified Account",
                    "POST",
                    "auth/login",
                    200,
                    data=login_data
                )
                
                if login_success and 'status' in login_response and login_response['status'] == 'success':
                    test_results["User Registration & Authentication"]["details"].append(
                        "✅ Login with verified account successful"
                    )
                    
                    # Test password reset functionality
                    print("\n🔍 Testing password reset functionality...")
                    reset_request = {
                        "email": test_email
                    }
                    
                    reset_success, reset_response = tester.run_test(
                        "Request Password Reset",
                        "POST",
                        "auth/forgot-password",
                        200,
                        data=reset_request
                    )
                    
                    if reset_success:
                        test_results["User Registration & Authentication"]["details"].append(
                            "✅ Password reset request successful"
                        )
                        
                        # Get reset code
                        reset_code_success, reset_code_response = tester.run_test(
                            "Get Password Reset Code",
                            "GET",
                            f"debug/verification-codes/{test_email}",
                            200
                        )
                        
                        reset_code = None
                        if reset_code_success:
                            if 'codes' in reset_code_response and len(reset_code_response['codes']) > 0:
                                reset_code = reset_code_response['codes'][0]['code']
                                test_results["User Registration & Authentication"]["details"].append(
                                    f"✅ Retrieved password reset code: {reset_code}"
                                )
                            elif 'last_test_code' in reset_code_response and reset_code_response['last_test_code']:
                                reset_code = reset_code_response['last_test_code']
                                test_results["User Registration & Authentication"]["details"].append(
                                    f"✅ Retrieved password reset code from last_test_code: {reset_code}"
                                )
                            else:
                                test_results["User Registration & Authentication"]["details"].append(
                                    "❌ No password reset code found"
                                )
                        else:
                            test_results["User Registration & Authentication"]["details"].append(
                                "❌ Failed to retrieve password reset code"
                            )
                        
                        if reset_code:
                            # Reset password
                            new_password = f"NewP@ss{timestamp % 1000}"
                            reset_data = {
                                "email": test_email,
                                "reset_code": reset_code,
                                "new_password": new_password
                            }
                            
                            reset_verify_success, reset_verify_response = tester.run_test(
                                "Reset Password",
                                "POST",
                                "auth/reset-password",
                                200,
                                data=reset_data
                            )
                            
                            if reset_verify_success:
                                test_results["User Registration & Authentication"]["details"].append(
                                    "✅ Password reset successful"
                                )
                                
                                # Test login with new password
                                login_new_data = {
                                    "email": test_email,
                                    "password": new_password
                                }
                                
                                login_new_success, login_new_response = tester.run_test(
                                    "Login with New Password",
                                    "POST",
                                    "auth/login",
                                    200,
                                    data=login_new_data
                                )
                                
                                if login_new_success and 'status' in login_new_response and login_new_response['status'] == 'success':
                                    test_results["User Registration & Authentication"]["details"].append(
                                        "✅ Login with new password successful"
                                    )
                                    # Update test_password for future tests
                                    test_password = new_password
                                else:
                                    test_results["User Registration & Authentication"]["details"].append(
                                        "❌ Login with new password failed"
                                    )
                            else:
                                test_results["User Registration & Authentication"]["details"].append(
                                    "❌ Password reset failed"
                                )
                    else:
                        test_results["User Registration & Authentication"]["details"].append(
                            "❌ Password reset request failed"
                        )
                else:
                    test_results["User Registration & Authentication"]["details"].append(
                        "❌ Login with verified account failed"
                    )
            else:
                test_results["User Registration & Authentication"]["details"].append(
                    "❌ Email verification failed"
                )
    else:
        test_results["User Registration & Authentication"]["details"].append(
            "❌ User registration failed"
        )
    
    # Set overall status for User Registration & Authentication
    success_count = sum(1 for detail in test_results["User Registration & Authentication"]["details"] if detail.startswith("✅"))
    total_count = len(test_results["User Registration & Authentication"]["details"])
    
    if success_count == total_count:
        test_results["User Registration & Authentication"]["status"] = "✅ Passed"
    elif success_count > 0:
        test_results["User Registration & Authentication"]["status"] = "⚠️ Partial"
    else:
        test_results["User Registration & Authentication"]["status"] = "❌ Failed"
    
    # 2. Recipe Generation System
    print("\n" + "=" * 80)
    print("2. TESTING RECIPE GENERATION SYSTEM")
    print("=" * 80)
    
    # Test basic recipe generation
    print("\n🔍 Testing basic recipe generation...")
    recipe_request = {
        "user_id": user_id,
        "cuisine_type": "italian",
        "dietary_preferences": ["vegetarian"],
        "ingredients_on_hand": ["pasta", "tomatoes", "garlic", "basil"],
        "prep_time_max": 30,
        "servings": 2,
        "difficulty": "medium"
    }
    
    recipe_success, recipe_response = tester.run_test(
        "Basic Recipe Generation",
        "POST",
        "recipes/generate",
        200,
        data=recipe_request,
        timeout=60  # Allow up to 60 seconds for recipe generation
    )
    
    if recipe_success and 'id' in recipe_response:
        recipe_id = recipe_response['id']
        test_results["Recipe Generation System"]["details"].append(
            f"✅ Basic recipe generation successful: {recipe_response.get('title', 'Untitled')}"
        )
        
        # Test healthy mode with calorie limits
        print("\n🔍 Testing healthy mode with calorie limits...")
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
        
        healthy_success, healthy_response = tester.run_test(
            "Healthy Recipe Generation",
            "POST",
            "recipes/generate",
            200,
            data=healthy_recipe_request,
            timeout=60
        )
        
        if healthy_success and 'id' in healthy_response:
            healthy_recipe_id = healthy_response['id']
            calories = healthy_response.get('calories_per_serving')
            
            if calories and calories <= 400:
                test_results["Recipe Generation System"]["details"].append(
                    f"✅ Healthy mode recipe generation successful with {calories} calories (under 400 limit)"
                )
            elif calories:
                test_results["Recipe Generation System"]["details"].append(
                    f"⚠️ Healthy mode recipe generated but with {calories} calories (exceeds 400 limit)"
                )
            else:
                test_results["Recipe Generation System"]["details"].append(
                    "⚠️ Healthy mode recipe generated but without calorie information"
                )
        else:
            test_results["Recipe Generation System"]["details"].append(
                "❌ Healthy mode recipe generation failed"
            )
        
        # Test budget mode with cost limits
        print("\n🔍 Testing budget mode with cost limits...")
        budget_recipe_request = {
            "user_id": user_id,
            "cuisine_type": "mexican",
            "dietary_preferences": [],
            "ingredients_on_hand": ["beans", "rice", "onions"],
            "prep_time_max": 45,
            "servings": 4,
            "difficulty": "easy",
            "is_budget_friendly": True,
            "max_budget": 15.0
        }
        
        budget_success, budget_response = tester.run_test(
            "Budget Recipe Generation",
            "POST",
            "recipes/generate",
            200,
            data=budget_recipe_request,
            timeout=60
        )
        
        if budget_success and 'id' in budget_response:
            budget_recipe_id = budget_response['id']
            test_results["Recipe Generation System"]["details"].append(
                f"✅ Budget mode recipe generation successful: {budget_response.get('title', 'Untitled')}"
            )
        else:
            test_results["Recipe Generation System"]["details"].append(
                "❌ Budget mode recipe generation failed"
            )
        
        # Test combined healthy + budget mode
        print("\n🔍 Testing combined healthy + budget mode...")
        combined_recipe_request = {
            "user_id": user_id,
            "cuisine_type": "asian",
            "dietary_preferences": ["low-carb"],
            "ingredients_on_hand": ["tofu", "broccoli", "ginger"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "medium",
            "is_healthy": True,
            "max_calories_per_serving": 350,
            "is_budget_friendly": True,
            "max_budget": 12.0
        }
        
        combined_success, combined_response = tester.run_test(
            "Combined Healthy & Budget Recipe Generation",
            "POST",
            "recipes/generate",
            200,
            data=combined_recipe_request,
            timeout=60
        )
        
        if combined_success and 'id' in combined_response:
            combined_recipe_id = combined_response['id']
            calories = combined_response.get('calories_per_serving')
            
            if calories and calories <= 350:
                test_results["Recipe Generation System"]["details"].append(
                    f"✅ Combined healthy & budget mode recipe generation successful with {calories} calories (under 350 limit)"
                )
            elif calories:
                test_results["Recipe Generation System"]["details"].append(
                    f"⚠️ Combined mode recipe generated but with {calories} calories (exceeds 350 limit)"
                )
            else:
                test_results["Recipe Generation System"]["details"].append(
                    "⚠️ Combined mode recipe generated but without calorie information"
                )
        else:
            test_results["Recipe Generation System"]["details"].append(
                "❌ Combined healthy & budget mode recipe generation failed"
            )
        
        # Verify recipe data structure and storage
        print("\n🔍 Verifying recipe data structure and storage...")
        get_recipe_success, get_recipe_response = tester.run_test(
            "Get Recipe by ID",
            "GET",
            f"recipes/{recipe_id}",
            200
        )
        
        if get_recipe_success:
            # Check if all required fields are present
            required_fields = ['title', 'description', 'ingredients', 'instructions', 'prep_time', 'cook_time', 'servings']
            missing_fields = [field for field in required_fields if field not in get_recipe_response]
            
            if not missing_fields:
                test_results["Recipe Generation System"]["details"].append(
                    "✅ Recipe data structure is complete with all required fields"
                )
            else:
                test_results["Recipe Generation System"]["details"].append(
                    f"⚠️ Recipe data structure is missing fields: {', '.join(missing_fields)}"
                )
        else:
            test_results["Recipe Generation System"]["details"].append(
                "❌ Failed to retrieve recipe by ID"
            )
    else:
        test_results["Recipe Generation System"]["details"].append(
            "❌ Basic recipe generation failed"
        )
    
    # Set overall status for Recipe Generation System
    success_count = sum(1 for detail in test_results["Recipe Generation System"]["details"] if detail.startswith("✅"))
    total_count = len(test_results["Recipe Generation System"]["details"])
    
    if success_count == total_count:
        test_results["Recipe Generation System"]["status"] = "✅ Passed"
    elif success_count > 0:
        test_results["Recipe Generation System"]["status"] = "⚠️ Partial"
    else:
        test_results["Recipe Generation System"]["status"] = "❌ Failed"
    
    # 3. Interactive Walmart Cart System
    print("\n" + "=" * 80)
    print("3. TESTING INTERACTIVE WALMART CART SYSTEM")
    print("=" * 80)
    
    if 'recipe_id' in locals():
        # Test cart-options endpoint
        print("\n🔍 Testing cart-options endpoint...")
        cart_options_success, cart_options_response = tester.run_test(
            "Cart Options Endpoint",
            "POST",
            "grocery/cart-options",
            200,
            params={"recipe_id": recipe_id, "user_id": user_id}
        )
        
        if cart_options_success and 'id' in cart_options_response:
            cart_options_id = cart_options_response['id']
            
            # Check if ingredient options are present
            if 'ingredient_options' in cart_options_response and len(cart_options_response['ingredient_options']) > 0:
                options_count = len(cart_options_response['ingredient_options'])
                test_results["Interactive Walmart Cart System"]["details"].append(
                    f"✅ Cart-options endpoint returned {options_count} ingredient options"
                )
                
                # Check if each ingredient has product options with required fields
                all_products_valid = True
                for ingredient_option in cart_options_response['ingredient_options']:
                    if 'options' not in ingredient_option or len(ingredient_option['options']) == 0:
                        all_products_valid = False
                        break
                    
                    for product in ingredient_option['options']:
                        if not all(field in product for field in ['product_id', 'name', 'price']):
                            all_products_valid = False
                            break
                
                if all_products_valid:
                    test_results["Interactive Walmart Cart System"]["details"].append(
                        "✅ All product options have required fields (product_id, name, price)"
                    )
                else:
                    test_results["Interactive Walmart Cart System"]["details"].append(
                        "❌ Some product options are missing required fields"
                    )
            else:
                test_results["Interactive Walmart Cart System"]["details"].append(
                    "❌ Cart-options endpoint did not return ingredient options"
                )
            
            # Test custom-cart creation with quantities
            print("\n🔍 Testing custom-cart creation with quantities...")
            
            # Create a list of products from the cart options
            products = []
            if 'ingredient_options' in cart_options_response:
                for ingredient_option in cart_options_response['ingredient_options']:
                    if 'options' in ingredient_option and len(ingredient_option['options']) > 0:
                        product = ingredient_option['options'][0]  # Take the first option for each ingredient
                        products.append({
                            "ingredient_name": ingredient_option.get('ingredient_name', 'item'),
                            "product_id": product.get('product_id', ''),
                            "name": product.get('name', ''),
                            "price": product.get('price', 0),
                            "quantity": random.randint(1, 3)  # Random quantity between 1 and 3
                        })
            
            # If no products were found in cart options, create some mock products
            if not products:
                products = [
                    {
                        "ingredient_name": "pasta",
                        "product_id": "123456789",
                        "name": "Barilla Pasta Penne 16oz",
                        "price": 1.99,
                        "quantity": 2
                    },
                    {
                        "ingredient_name": "tomatoes",
                        "product_id": "987654321",
                        "name": "Fresh Roma Tomatoes 2lb",
                        "price": 2.49,
                        "quantity": 1
                    },
                    {
                        "ingredient_name": "garlic",
                        "product_id": "789123456",
                        "name": "Fresh Garlic Bulb 3oz",
                        "price": 0.98,
                        "quantity": 3
                    }
                ]
            
            custom_cart_data = {
                "user_id": user_id,
                "recipe_id": recipe_id,
                "products": products
            }
            
            custom_cart_success, custom_cart_response = tester.run_test(
                "Custom Cart Creation",
                "POST",
                "grocery/custom-cart",
                200,
                data=custom_cart_data
            )
            
            if custom_cart_success and 'id' in custom_cart_response:
                custom_cart_id = custom_cart_response['id']
                test_results["Interactive Walmart Cart System"]["details"].append(
                    "✅ Custom-cart creation successful"
                )
                
                # Check if total price is calculated correctly
                if 'total_price' in custom_cart_response:
                    expected_total = sum(p['price'] * p['quantity'] for p in products)
                    actual_total = custom_cart_response['total_price']
                    
                    if abs(actual_total - expected_total) < 0.01:  # Allow for small floating-point differences
                        test_results["Interactive Walmart Cart System"]["details"].append(
                            f"✅ Total price calculated correctly: ${actual_total:.2f}"
                        )
                    else:
                        test_results["Interactive Walmart Cart System"]["details"].append(
                            f"❌ Total price calculation error: got ${actual_total:.2f}, expected ${expected_total:.2f}"
                        )
                else:
                    test_results["Interactive Walmart Cart System"]["details"].append(
                        "❌ Total price not included in custom-cart response"
                    )
                
                # Test affiliate URL generation
                if 'walmart_url' in custom_cart_response:
                    walmart_url = custom_cart_response['walmart_url']
                    
                    if 'affil.walmart.com' in walmart_url and 'items=' in walmart_url:
                        test_results["Interactive Walmart Cart System"]["details"].append(
                            "✅ Walmart affiliate URL generated correctly"
                        )
                        
                        # Check if all product IDs are in the URL
                        product_ids = [p['product_id'] for p in products]
                        all_ids_in_url = all(pid in walmart_url for pid in product_ids)
                        
                        if all_ids_in_url:
                            test_results["Interactive Walmart Cart System"]["details"].append(
                                "✅ All product IDs included in Walmart affiliate URL"
                            )
                        else:
                            test_results["Interactive Walmart Cart System"]["details"].append(
                                "❌ Not all product IDs found in Walmart affiliate URL"
                            )
                    else:
                        test_results["Interactive Walmart Cart System"]["details"].append(
                            "❌ Walmart affiliate URL format is incorrect"
                        )
                else:
                    test_results["Interactive Walmart Cart System"]["details"].append(
                        "❌ Walmart affiliate URL not included in custom-cart response"
                    )
            else:
                test_results["Interactive Walmart Cart System"]["details"].append(
                    "❌ Custom-cart creation failed"
                )
        else:
            test_results["Interactive Walmart Cart System"]["details"].append(
                "❌ Cart-options endpoint failed"
            )
    else:
        test_results["Interactive Walmart Cart System"]["details"].append(
            "❌ Cannot test Walmart cart system without a valid recipe ID"
        )
    
    # Set overall status for Interactive Walmart Cart System
    success_count = sum(1 for detail in test_results["Interactive Walmart Cart System"]["details"] if detail.startswith("✅"))
    total_count = len(test_results["Interactive Walmart Cart System"]["details"])
    
    if success_count == total_count:
        test_results["Interactive Walmart Cart System"]["status"] = "✅ Passed"
    elif success_count > 0:
        test_results["Interactive Walmart Cart System"]["status"] = "⚠️ Partial"
    else:
        test_results["Interactive Walmart Cart System"]["status"] = "❌ Failed"
    
    # 4. Recipe History & Management
    print("\n" + "=" * 80)
    print("4. TESTING RECIPE HISTORY & MANAGEMENT")
    print("=" * 80)
    
    if 'user_id' in locals():
        # Test recipe saving after generation
        print("\n🔍 Verifying recipe saving after generation...")
        
        # We've already generated recipes in the previous tests, so we just need to check if they're saved
        get_user_recipes_success, get_user_recipes_response = tester.run_test(
            "Get User Recipes",
            "GET",
            f"users/{user_id}/recipes",
            200
        )
        
        if get_user_recipes_success:
            recipes_count = len(get_user_recipes_response)
            
            if recipes_count > 0:
                test_results["Recipe History & Management"]["details"].append(
                    f"✅ Successfully retrieved {recipes_count} recipes for user"
                )
                
                # List recipe titles
                recipe_titles = [recipe.get('title', 'Untitled') for recipe in get_user_recipes_response]
                test_results["Recipe History & Management"]["details"].append(
                    f"✅ Recipe titles: {', '.join(recipe_titles)}"
                )
                
                # Test recipe retrieval for a specific recipe
                if 'recipe_id' in locals():
                    print("\n🔍 Testing recipe retrieval for a specific recipe...")
                    get_specific_recipe_success, get_specific_recipe_response = tester.run_test(
                        "Get Specific Recipe",
                        "GET",
                        f"recipes/{recipe_id}",
                        200
                    )
                    
                    if get_specific_recipe_success:
                        test_results["Recipe History & Management"]["details"].append(
                            f"✅ Successfully retrieved specific recipe: {get_specific_recipe_response.get('title', 'Untitled')}"
                        )
                    else:
                        test_results["Recipe History & Management"]["details"].append(
                            "❌ Failed to retrieve specific recipe"
                        )
            else:
                test_results["Recipe History & Management"]["details"].append(
                    "❌ No recipes found for user"
                )
        else:
            test_results["Recipe History & Management"]["details"].append(
                "❌ Failed to retrieve user recipes"
            )
    else:
        test_results["Recipe History & Management"]["details"].append(
            "❌ Cannot test recipe history without a valid user ID"
        )
    
    # Set overall status for Recipe History & Management
    success_count = sum(1 for detail in test_results["Recipe History & Management"]["details"] if detail.startswith("✅"))
    total_count = len(test_results["Recipe History & Management"]["details"])
    
    if success_count == total_count:
        test_results["Recipe History & Management"]["status"] = "✅ Passed"
    elif success_count > 0:
        test_results["Recipe History & Management"]["status"] = "⚠️ Partial"
    else:
        test_results["Recipe History & Management"]["status"] = "❌ Failed"
    
    # 5. Error Handling & Edge Cases
    print("\n" + "=" * 80)
    print("5. TESTING ERROR HANDLING & EDGE CASES")
    print("=" * 80)
    
    # Test invalid registration data
    print("\n🔍 Testing invalid registration data...")
    invalid_user_data = {
        "first_name": "Invalid",
        "last_name": "User",
        "email": "not-an-email",  # Invalid email format
        "password": "short",  # Too short password
        "dietary_preferences": [],
        "allergies": [],
        "favorite_cuisines": []
    }
    
    # We expect this to fail with 422 or 400 status code
    invalid_register_success, invalid_register_response = tester.run_test(
        "Invalid Registration Data",
        "POST",
        "auth/register",
        400,  # or 422, depending on how the API validates
        data=invalid_user_data
    )
    
    if invalid_register_success:
        test_results["Error Handling & Edge Cases"]["details"].append(
            "✅ Invalid registration data correctly rejected"
        )
    else:
        # Check if it failed with a different status code that still indicates validation
        if 'status_code' in locals() and invalid_register_response.get('status_code', 0) in [400, 422]:
            test_results["Error Handling & Edge Cases"]["details"].append(
                f"✅ Invalid registration data rejected with status {invalid_register_response.get('status_code')}"
            )
        else:
            test_results["Error Handling & Edge Cases"]["details"].append(
                "❌ Invalid registration data not properly validated"
            )
    
    # Test expired verification codes
    if 'test_email' in locals():
        print("\n🔍 Testing expired verification codes...")
        # We can't actually expire a code, but we can test with an invalid code
        expired_verify_data = {
            "email": test_email,
            "code": "000000"  # Invalid/expired code
        }
        
        # We expect this to fail with 400 status code
        expired_verify_success, expired_verify_response = tester.run_test(
            "Expired Verification Code",
            "POST",
            "auth/verify",
            400,
            data=expired_verify_data
        )
        
        if expired_verify_success:
            test_results["Error Handling & Edge Cases"]["details"].append(
                "✅ Invalid/expired verification code correctly rejected"
            )
        else:
            test_results["Error Handling & Edge Cases"]["details"].append(
                "❌ Invalid/expired verification code not properly handled"
            )
    
    # Test non-existent user login
    print("\n🔍 Testing non-existent user login...")
    nonexistent_login_data = {
        "email": f"nonexistent_{uuid.uuid4()}@example.com",
        "password": "SecureP@ssw0rd"
    }
    
    # We expect this to fail with 401 status code
    nonexistent_login_success, nonexistent_login_response = tester.run_test(
        "Non-existent User Login",
        "POST",
        "auth/login",
        401,
        data=nonexistent_login_data
    )
    
    if nonexistent_login_success:
        test_results["Error Handling & Edge Cases"]["details"].append(
            "✅ Non-existent user login correctly rejected"
        )
    else:
        test_results["Error Handling & Edge Cases"]["details"].append(
            "❌ Non-existent user login not properly handled"
        )
    
    # Test API timeout scenarios (we'll simulate by setting a very short timeout)
    print("\n🔍 Testing API timeout scenarios...")
    
    # Use recipe generation with a very short timeout to simulate timeout
    timeout_recipe_request = {
        "user_id": user_id if 'user_id' in locals() else str(uuid.uuid4()),
        "cuisine_type": "complex_cuisine_that_takes_time",
        "dietary_preferences": ["vegetarian", "gluten-free", "dairy-free", "low-carb"],
        "ingredients_on_hand": ["rare_ingredient_1", "rare_ingredient_2", "rare_ingredient_3"],
        "prep_time_max": 10,
        "servings": 10,
        "difficulty": "hard"
    }
    
    # We expect this to timeout with the short timeout
    timeout_success, timeout_response = tester.run_test(
        "API Timeout Scenario",
        "POST",
        "recipes/generate",
        200,
        data=timeout_recipe_request,
        timeout=1  # Very short timeout to simulate timeout
    )
    
    # This test is a bit tricky - if it times out, that's actually what we want to test
    # If it doesn't time out, the API is very fast which is also good
    if not timeout_success and 'error' in timeout_response and 'timeout' in timeout_response['error'].lower():
        test_results["Error Handling & Edge Cases"]["details"].append(
            "✅ API timeout scenario correctly detected"
        )
    else:
        test_results["Error Handling & Edge Cases"]["details"].append(
            "⚠️ API did not timeout with short timeout - either very fast or not handling timeouts properly"
        )
    
    # Set overall status for Error Handling & Edge Cases
    success_count = sum(1 for detail in test_results["Error Handling & Edge Cases"]["details"] if detail.startswith("✅"))
    total_count = len(test_results["Error Handling & Edge Cases"]["details"])
    
    if success_count == total_count:
        test_results["Error Handling & Edge Cases"]["status"] = "✅ Passed"
    elif success_count > 0:
        test_results["Error Handling & Edge Cases"]["status"] = "⚠️ Partial"
    else:
        test_results["Error Handling & Edge Cases"]["status"] = "❌ Failed"
    
    # Print final results
    print("\n" + "=" * 80)
    print("🚀 DEPLOYMENT READINESS TEST RESULTS 🚀")
    print("=" * 80)
    
    for category, result in test_results.items():
        print(f"\n{category}: {result['status']}")
        for detail in result['details']:
            print(f"  {detail}")
    
    # Calculate overall readiness
    passed_categories = sum(1 for result in test_results.values() if result['status'] == "✅ Passed")
    partial_categories = sum(1 for result in test_results.values() if result['status'] == "⚠️ Partial")
    failed_categories = sum(1 for result in test_results.values() if result['status'] == "❌ Failed")
    
    print("\n" + "=" * 80)
    if failed_categories == 0 and partial_categories <= 1:
        print("✅ OVERALL RESULT: APPLICATION IS READY FOR DEPLOYMENT")
        print("All critical systems are functioning correctly.")
    elif failed_categories <= 1 and passed_categories >= 3:
        print("⚠️ OVERALL RESULT: APPLICATION IS PARTIALLY READY FOR DEPLOYMENT")
        print("Most systems are functioning, but some issues need to be addressed.")
    else:
        print("❌ OVERALL RESULT: APPLICATION IS NOT READY FOR DEPLOYMENT")
        print("Critical issues need to be resolved before deployment.")
    print("=" * 80)
    
    return test_results

if __name__ == "__main__":
    run_deployment_readiness_tests()