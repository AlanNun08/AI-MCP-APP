#!/usr/bin/env python3
"""
Backend Testing Script for Recipe & Grocery App Review
Focus: Test all backend functionality as requested in review
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path
sys.path.append('/app/backend')

# Test configuration - Use production backend URL from frontend/.env
BACKEND_URL = "https://7231aef0-71b1-4397-ae8c-9cb5a059a118.preview.emergentagent.com/api"
DEMO_USER_EMAIL = "demo@test.com"
DEMO_USER_PASSWORD = "password123"

class BackendReviewTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.user_id = None
        self.recipe_id = None
        
    async def cleanup(self):
        await self.client.aclose()
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def test_auth_login(self):
        """Test 1: Test /api/auth/login endpoint with demo@test.com/password123"""
        self.log("=== Testing /api/auth/login Endpoint ===")
        
        try:
            login_data = {
                "email": DEMO_USER_EMAIL,
                "password": DEMO_USER_PASSWORD
            }
            
            self.log(f"Testing login with: {DEMO_USER_EMAIL}")
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            self.log(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.log("✅ Login successful")
                
                # Check response structure
                if result.get("status") == "success":
                    user_data = result.get("user", {})
                    self.user_id = user_data.get("id") or result.get("user_id")
                    
                    self.log(f"User ID: {self.user_id}")
                    self.log(f"User Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                    self.log(f"Email: {user_data.get('email')}")
                    self.log(f"Verified: {user_data.get('is_verified')}")
                    
                    return True
                else:
                    self.log(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                self.log(f"❌ Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing login: {str(e)}", "ERROR")
            return False
    
    async def test_recipe_generation(self):
        """Test 2: Test /api/recipes/generate endpoint"""
        self.log("=== Testing /api/recipes/generate Endpoint ===")
        
        if not self.user_id:
            self.log("❌ No user_id available for recipe generation test")
            return False
        
        try:
            recipe_data = {
                "user_id": self.user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "Italian",
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 30,
                "servings": 4,
                "difficulty": "medium"
            }
            
            self.log("Generating Italian cuisine recipe...")
            response = await self.client.post(f"{BACKEND_URL}/recipes/generate", json=recipe_data)
            
            self.log(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.recipe_id = result.get("id")
                
                self.log("✅ Recipe generation successful")
                self.log(f"Recipe ID: {self.recipe_id}")
                self.log(f"Title: {result.get('title')}")
                self.log(f"Description: {result.get('description', '')[:100]}...")
                self.log(f"Prep time: {result.get('prep_time')} minutes")
                self.log(f"Cook time: {result.get('cook_time')} minutes")
                self.log(f"Servings: {result.get('servings')}")
                
                # Check shopping list for Walmart integration
                shopping_list = result.get("shopping_list", [])
                self.log(f"Shopping list ({len(shopping_list)} items): {shopping_list}")
                
                # Verify required fields for frontend
                required_fields = ["id", "title", "ingredients", "instructions", "shopping_list"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log(f"⚠️ Missing fields: {missing_fields}")
                else:
                    self.log("✅ All required fields present")
                
                return True
            else:
                self.log(f"❌ Recipe generation failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing recipe generation: {str(e)}", "ERROR")
            return False
    
    async def test_grocery_cart_options(self):
        """Test 3: Test /api/grocery/cart-options endpoint"""
        self.log("=== Testing /api/grocery/cart-options Endpoint ===")
        
        if not self.user_id or not self.recipe_id:
            self.log("❌ Missing user_id or recipe_id for cart options test")
            return False
        
        try:
            params = {
                "recipe_id": self.recipe_id,
                "user_id": self.user_id
            }
            
            self.log(f"Testing cart options with recipe_id: {self.recipe_id}")
            response = await self.client.post(f"{BACKEND_URL}/grocery/cart-options", params=params)
            
            self.log(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                self.log("✅ Cart options endpoint responded successfully")
                self.log(f"Recipe ID: {result.get('recipe_id')}")
                self.log(f"User ID: {result.get('user_id')}")
                self.log(f"Total products: {result.get('total_products', 0)}")
                
                # Check ingredient_options structure
                ingredient_options = result.get('ingredient_options', [])
                self.log(f"Ingredient options count: {len(ingredient_options)}")
                
                if ingredient_options:
                    total_products = 0
                    for option in ingredient_options:
                        ingredient_name = option.get('ingredient_name')
                        products = option.get('options', [])
                        total_products += len(products)
                        
                        self.log(f"  {ingredient_name}: {len(products)} products")
                        
                        # Check product structure for first product
                        if products:
                            first_product = products[0]
                            required_product_fields = ["product_id", "name", "price"]
                            missing_product_fields = [field for field in required_product_fields if field not in first_product]
                            
                            if missing_product_fields:
                                self.log(f"    ⚠️ Missing product fields: {missing_product_fields}")
                            else:
                                self.log(f"    ✅ Product structure valid")
                                self.log(f"    Sample: {first_product.get('name')} - ${first_product.get('price')}")
                    
                    self.log(f"✅ Total products found: {total_products}")
                    return total_products > 0
                else:
                    message = result.get('message', 'No message')
                    self.log(f"❌ No ingredient options returned. Message: {message}")
                    return False
                    
            else:
                self.log(f"❌ Cart options failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing cart options: {str(e)}", "ERROR")
            return False
    
    async def test_walmart_integration(self):
        """Test 4: Verify Walmart API integration is working"""
        self.log("=== Testing Walmart API Integration ===")
        
        try:
            # Test environment variables
            from dotenv import load_dotenv
            from pathlib import Path
            
            env_path = Path('/app/backend/.env')
            load_dotenv(env_path)
            
            walmart_consumer_id = os.environ.get('WALMART_CONSUMER_ID')
            walmart_private_key = os.environ.get('WALMART_PRIVATE_KEY')
            walmart_key_version = os.environ.get('WALMART_KEY_VERSION')
            
            self.log(f"WALMART_CONSUMER_ID: {'✅ Present' if walmart_consumer_id else '❌ Missing'}")
            self.log(f"WALMART_PRIVATE_KEY: {'✅ Present' if walmart_private_key else '❌ Missing'}")
            self.log(f"WALMART_KEY_VERSION: {'✅ Present' if walmart_key_version else '❌ Missing'}")
            
            if not all([walmart_consumer_id, walmart_private_key, walmart_key_version]):
                self.log("❌ Missing Walmart API credentials")
                return False
            
            # Test signature generation
            try:
                from cryptography.hazmat.primitives import serialization, hashes
                from cryptography.hazmat.primitives.asymmetric import padding
                import base64
                import time
                
                private_key = serialization.load_pem_private_key(
                    walmart_private_key.encode(), 
                    password=None
                )
                
                timestamp = str(int(time.time() * 1000))
                message = f"{walmart_consumer_id}\n{timestamp}\n{walmart_key_version}\n".encode("utf-8")
                signature = private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
                signature_b64 = base64.b64encode(signature).decode("utf-8")
                
                self.log("✅ RSA signature generation working")
                
            except Exception as e:
                self.log(f"❌ Signature generation failed: {str(e)}")
                return False
            
            # Test backend search function
            try:
                from server import search_walmart_products
                
                test_ingredient = "spaghetti"
                self.log(f"Testing search_walmart_products for: {test_ingredient}")
                
                products = await search_walmart_products(test_ingredient)
                
                if products:
                    self.log(f"✅ Found {len(products)} products for '{test_ingredient}'")
                    for i, product in enumerate(products[:2]):
                        self.log(f"  Product {i+1}: {product.name} - ${product.price}")
                    return True
                else:
                    self.log(f"❌ No products found for '{test_ingredient}'")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Backend search function failed: {str(e)}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing Walmart integration: {str(e)}", "ERROR")
            return False
    
    async def test_response_format(self):
        """Test 5: Verify response format matches frontend expectations"""
        self.log("=== Testing Response Format Compatibility ===")
        
        if not self.user_id or not self.recipe_id:
            self.log("❌ Missing user_id or recipe_id for format test")
            return False
        
        try:
            # Test cart options response format
            params = {
                "recipe_id": self.recipe_id,
                "user_id": self.user_id
            }
            
            response = await self.client.post(f"{BACKEND_URL}/grocery/cart-options", params=params)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check top-level structure
                expected_top_fields = ["recipe_id", "user_id", "ingredient_options"]
                missing_top_fields = [field for field in expected_top_fields if field not in result]
                
                if missing_top_fields:
                    self.log(f"❌ Missing top-level fields: {missing_top_fields}")
                    return False
                
                # Check ingredient_options structure
                ingredient_options = result.get('ingredient_options', [])
                if not ingredient_options:
                    self.log("❌ No ingredient_options in response")
                    return False
                
                # Check first ingredient option structure
                first_option = ingredient_options[0]
                expected_option_fields = ["ingredient_name", "options"]
                missing_option_fields = [field for field in expected_option_fields if field not in first_option]
                
                if missing_option_fields:
                    self.log(f"❌ Missing ingredient option fields: {missing_option_fields}")
                    return False
                
                # Check product structure within options
                products = first_option.get('options', [])
                if not products:
                    self.log("❌ No products in ingredient options")
                    return False
                
                first_product = products[0]
                expected_product_fields = ["product_id", "name", "price"]
                optional_product_fields = ["image_url", "thumbnail_image", "availability"]
                
                missing_product_fields = [field for field in expected_product_fields if field not in first_product]
                
                if missing_product_fields:
                    self.log(f"❌ Missing required product fields: {missing_product_fields}")
                    return False
                
                # Check optional fields
                present_optional_fields = [field for field in optional_product_fields if field in first_product]
                self.log(f"✅ Optional fields present: {present_optional_fields}")
                
                # Validate data types
                if not isinstance(first_product.get('price'), (int, float)):
                    self.log("❌ Price is not a number")
                    return False
                
                if not isinstance(first_product.get('product_id'), str):
                    self.log("❌ Product ID is not a string")
                    return False
                
                self.log("✅ Response format matches frontend expectations")
                self.log(f"✅ Structure: ingredient_options[].options[] with product_id, name, price")
                
                return True
            else:
                self.log(f"❌ Failed to get response for format test: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing response format: {str(e)}", "ERROR")
            return False
    
    async def run_comprehensive_review_test(self):
        """Run all review tests in sequence"""
        self.log("🚀 Starting Backend Review Tests")
        self.log("=" * 60)
        
        test_results = {}
        
        # Test 1: Authentication
        test_results["auth_login"] = await self.test_auth_login()
        
        # Test 2: Recipe Generation
        if test_results["auth_login"]:
            test_results["recipe_generation"] = await self.test_recipe_generation()
        else:
            test_results["recipe_generation"] = False
        
        # Test 3: Grocery Cart Options
        if test_results["recipe_generation"]:
            test_results["cart_options"] = await self.test_grocery_cart_options()
        else:
            test_results["cart_options"] = False
        
        # Test 4: Walmart Integration
        test_results["walmart_integration"] = await self.test_walmart_integration()
        
        # Test 5: Response Format
        if test_results["cart_options"]:
            test_results["response_format"] = await self.test_response_format()
        else:
            test_results["response_format"] = False
        
        # Summary
        self.log("=" * 60)
        self.log("🔍 BACKEND REVIEW TEST RESULTS")
        self.log("=" * 60)
        
        test_descriptions = {
            "auth_login": "Authentication (/api/auth/login with demo@test.com/password123)",
            "recipe_generation": "Recipe Generation (/api/recipes/generate)",
            "cart_options": "Grocery Cart Options (/api/grocery/cart-options)",
            "walmart_integration": "Walmart API Integration",
            "response_format": "Response Format Compatibility"
        }
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            description = test_descriptions.get(test_name, test_name)
            self.log(f"{description}: {status}")
        
        # Overall assessment
        all_passed = all(test_results.values())
        critical_tests = ["auth_login", "recipe_generation", "cart_options", "walmart_integration"]
        critical_passed = sum(1 for test in critical_tests if test_results.get(test, False))
        
        self.log("=" * 60)
        if all_passed:
            self.log("🎉 ALL TESTS PASSED - Backend is ready for new frontend design")
        elif critical_passed == len(critical_tests):
            self.log("✅ ALL CRITICAL TESTS PASSED - Backend core functionality working")
            if not test_results.get("response_format"):
                self.log("⚠️ Response format test failed - may need minor adjustments")
        else:
            self.log(f"❌ {len(critical_tests) - critical_passed} CRITICAL TESTS FAILED")
            self.log("🔧 ISSUES IDENTIFIED:")
            
            if not test_results.get("auth_login"):
                self.log("  - Authentication endpoint not working with demo credentials")
            if not test_results.get("recipe_generation"):
                self.log("  - Recipe generation endpoint failing")
            if not test_results.get("cart_options"):
                self.log("  - Grocery cart options endpoint not returning products")
            if not test_results.get("walmart_integration"):
                self.log("  - Walmart API integration not working")
        
        return test_results

async def main():
    """Main test execution"""
    tester = BackendReviewTester()
    
    try:
        results = await tester.run_comprehensive_review_test()
        return results
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    results = asyncio.run(main())